---
title: "feat: 发信从 Mailgun 迁到 Resend（Broadcasts）+ 退订问卷"
type: feat
status: active
date: 2026-10-09
---

# feat: 发信从 Mailgun 迁到 Resend（Broadcasts）+ 退订问卷

## Summary

Mailgun 开始收费，整个项目的发信改用 Resend：

- 确认订阅邮件走 Resend 的 transactional 接口（`POST /emails`），每天只有几封。
- 每日简报改用 Resend Broadcasts：订阅者同步成 Resend 的 contacts，放进一个 segment，每天创建并发送一个 broadcast。Marketing 免费版 1000 个联系人以内不限发送量，现有约 86 个已确认订阅者。
- 退订改成我们自己的页面：邮件里的退订链接打开前端 `/unsubscribe?token=...`，用户点"确认退订"并可选填原因。Mongo 里记录谁、什么时候、因为什么退订，同时把 Resend 的 contact 标成 unsubscribed。
- 每次群发前跑一次双向同步，修复 Mongo 和 Resend 之间的漂移（比如有人点了邮件客户端自带的一键退订，只有 Resend 知道）。

TLDR 用一个独立的 Resend 账号（不跟 favly 共用 team），所以这个账号里的 contacts 全是 TLDR 订阅者。

---

## 关键事实（已核实）

- Resend API：base `https://api.resend.com`，`Authorization: Bearer <key>`，必须带 User-Agent（`requests` 默认的就行），默认限流每 team 10 req/s。
- Broadcast 创建：`POST /broadcasts`，必填 `segment_id`、`from`、`subject`；`html` 支持 contact properties 占位符；`send: true` 创建即发送。Audiences 已改名 Segments，不要用 `audience_id`。文档：https://resend.com/docs/api-reference/broadcasts/create-broadcast
- Contact：全局实体，按 email 唯一。字段 `email`、`first_name`、`last_name`、`unsubscribed`（全局退订，true 后不再收任何 broadcast）、`properties`（自定义属性 map）、`segments`（`[{id}]`）。文档：https://resend.com/docs/api-reference/contacts/create-contact
- 自定义 contact property 要先创建定义才能用（`POST /contact-properties`，`key` + `type: "string"`）。文档：https://resend.com/docs/dashboard/contacts/properties
- Broadcast 内容里的占位符写法：`{{{contact.<key>}}}`，可带 fallback `{{{contact.<key>|fallback}}}`。
- 其余接口（list contacts 的分页与过滤参数、按 email 更新 contact、把已有 contact 加进 segment）实现时去 https://resend.com/docs/llms.txt 里找对应页面核实，**不要凭记忆写字段名**。

---

## 环境变量

`config.py` 删掉 `MAILGUN_API_KEY`、`MAILGUN_DOMAIN`，新增：

| 名字 | 说明 |
|---|---|
| `RESEND_API_KEY` | Full access key（要管 contacts 和 broadcasts） |
| `RESEND_SEGMENT_ID` | "TLDR 科技日推" segment 的 id |
| `MAIL_FROM_DOMAIN` | 默认 `tldrnewsletter.cn` |

`.env.production.example` 和 `VERCEL_*.md`、`LOCAL_DEVELOPMENT.md` 里提到 Mailgun 环境变量的地方同步替换，只改变量名和一句说明，不要重写文档。

---

## 后端

### 1. `api/services/resend_client.py`（新建，纯 requests，不 import flask / models）

一个薄封装类 `ResendClient(api_key, segment_id, from_domain)`，方法：

- `send_email(to, subject, html, from_name, from_local)` → `POST /emails`
- `create_contact(email, unsubscribe_token)` → 带 `properties.unsubscribe_token`、`segments=[{id: segment_id}]`、`unsubscribed=False`
- `update_contact(email, *, unsubscribed=None, unsubscribe_token=None)`
- `list_contacts()` → 翻完所有分页，返回 `[{id, email, unsubscribed}]`
- `ensure_contact_property(key)` → 不存在就创建（string 类型），幂等
- `send_broadcast(subject, html, name)` → `send: true`，返回 broadcast id

非 2xx 时记录 `response.text` 并抛异常（自定义 `ResendError` 即可）。不加重试。

### 2. 简报 HTML

把 `generate_newsletter_html` 从 `mailgun_service.py` 原样搬到新模块 `api/services/newsletter_email.py`，改成纯函数 `generate_newsletter_html(newsletter, frontend_url)`，不再读 `current_app`。正文模板保持不变，只改页脚退订链接：

```
{frontend_url}/unsubscribe?token={{{contact.unsubscribe_token}}}
```

注意原函数是 f-string，三重花括号在 f-string 里要转义。建议把占位符放进一个普通字符串常量再插进去，别在 f-string 里数花括号。

### 3. Subscriber 模型和退订事件

`api/models/subscriber.py`：

- `Subscriber` 加 `unsubscribe_token = StringField()`，新建订阅时用 `secrets.token_urlsafe(32)` 生成；加一个 `ensure_unsubscribe_token()` 方法给老数据懒生成。
- 新建 `UnsubscribeEvent`（collection `unsubscribe_events`），每次退订一条，保留历史（同一个人退订、重订、再退订会有多条）：
  - `email`、`subscriber_id`
  - `subscribed_at`、`confirmed_at`（从 Subscriber 拷过来，以后能算"订了多久才退"）
  - `unsubscribed_at`
  - `source`：`page`（我们的退订页）/ `resend`（同步时发现 Resend 那边退订了，比如邮箱客户端的一键退订）
  - `reasons`：`ListField(StringField())`，只接受白名单 key
  - `comment`：自由填写，trim 后截断到 500 字

退订原因白名单（key 存库，中文只在前端显示）：

| key | 前端文案 |
|---|---|
| `too_frequent` | 每天一封太多了，看不过来 |
| `not_relevant` | 内容和我关心的方向不太相关 |
| `quality` | 翻译或摘要质量不够好 |
| `read_elsewhere` | 我更习惯在网站、小红书等地方看 |
| `read_original` | 我直接看英文原版 TLDR 了 |
| `email_issue` | 邮件经常进垃圾箱，或者显示有问题 |
| `no_time` | 最近太忙，暂时不需要 |
| `other` | 其他 |

### 4. 同步逻辑 `api/services/subscriber_sync.py`

拆成两层，方便测试：

- 纯函数 `plan_sync(resend_contacts, subscribers) -> SyncPlan`，输入是两边的简单数据（email、unsubscribed / confirmed、is_active），不碰网络和数据库。
- `run_sync(client, dry_run=False)` 读 Mongo 和 Resend、调 `plan_sync`、执行动作，返回各类动作的计数。

规则（email 一律 lower-case 后比较）：

1. Resend 里 `unsubscribed=True`，Mongo 里是 confirmed 且 active → Mongo 标成 inactive（`is_active=False`，`unsubscribed_at=now`），写一条 `UnsubscribeEvent(source='resend', reasons=[])`。
2. Mongo 里 confirmed 且 active，Resend 里没有这个 contact → 创建 contact（先 `ensure_unsubscribe_token()`）。
3. Resend 里 `unsubscribed=False`，但 Mongo 里没有这个人或者他不是 active+confirmed → Resend 里 update 成 `unsubscribed=True`（我们页面退订时 Resend 调用失败的补偿，以及老数据清理）。

规则 1 成立的前提是：Mongo 里 confirmed 的人，Resend 那边一定在确认时被设成过 `unsubscribed=False`。所以确认订阅那一步的 Resend 调用必须是同步、失败即整体失败的（见下面第 5 节）。

### 5. 路由改动（`api/routes.py`）

- **删掉** `MailgunService` 的 import 和所有使用；删掉 `api/services/mailgun_service.py`、`scripts/test_mailgun.py`。
- 加一个小工厂函数 `_resend()` 从 `current_app.config` 构造 `ResendClient`。
- `POST /api/subscribe`：
  - "已订阅"判断改成 `existing.confirmed and existing.is_active`。
  - 之前退订过（confirmed 但 inactive）的人重新订阅：重置 `confirmed=False`、`is_active=True`、新的 `confirmation_token`，走正常的确认邮件流程（重新 double opt-in）。
  - 确认邮件用 `send_email` 发，From `【太长不看】科技日推 <confirm@{MAIL_FROM_DOMAIN}>`，模板沿用 `_get_confirmation_template` 的 HTML（一起搬进 `newsletter_email.py`）。
- `GET /api/confirm/<token>`：确认时先 `ensure_unsubscribe_token()`，再在 Resend 建 contact（已存在就 update 成 `unsubscribed=False` 并加进 segment、写入 token），**Resend 调用成功后**才 `confirm_subscription()`。Resend 失败就重定向到 `/subscription/error`，不改 Mongo。
- `POST /api/unsubscribe`（新）：body `{token, reasons, comment}`。
  - token 找不到 → 404。
  - 已经 inactive → 200，`{already: true}`，不重复写事件。
  - 否则：Mongo 标 inactive、写 `UnsubscribeEvent(source='page')`，然后调 Resend `update_contact(unsubscribed=True)`；这一步失败只记日志，不报给用户（同步规则 3 会补）。
  - 加 `@limiter.limit("20 per hour")`。
- `GET /api/unsubscribe/token-status?token=...`（新，给前端页面初始化用）：返回 `{valid, already_unsubscribed}`，不改任何状态。
- `GET /api/unsubscribe/<subscriber_id>`（老链接，已发出去的 Mailgun 邮件里还有）：**不再删除订阅者，也不直接退订**。按 id 找到人，`ensure_unsubscribe_token()`，302 到 `{FRONTEND_URL}/unsubscribe?token=...`；找不到就 302 到 `{FRONTEND_URL}/unsubscribe`（页面显示链接无效）。GET 不改状态，是为了防止邮箱的链接安全扫描器把人误退订。
  - 注意新的 `GET /api/unsubscribe/token-status` 和这个 `<subscriber_id>` 路由会冲突，路由顺序或路径要处理好（比如状态接口换成 `/api/unsubscribe-status`）。
- `_send_newsletter_to_subscribers(newsletter)`：
  1. `run_sync`，失败只记日志、继续发（同步失败不该挡住当天的简报）。
  2. Mongo 里 confirmed+active 为 0 → 照旧返回"没有已确认的订阅者"。
  3. `generate_newsletter_html(newsletter, FRONTEND_URL)`，`send_broadcast(subject, html, name=f"TLDR {date}")`，From `太长不看 | 科技日推 <newsletter@{MAIL_FROM_DOMAIN}>`，不设 reply-to（域名没有收信）。
  4. 成功后写 `newsletter.email_sent_at`，并在 `DailyNewsletter` 上加 `email_broadcast_id` 字段存 broadcast id。
  5. 返回 JSON 带 `broadcast_id`、`subscriber_count`、同步计数。
- `POST /api/test/send_newsletter`：现在完全没鉴权，换成 Resend 后每调一次就占一封每日 transactional 额度，别人刷它能把确认邮件的额度耗光。加上和 `/api/send_daily_newsletter` 一样的 `X-API-Key` 校验。实现上用 `send_email` 发给测试地址，HTML 里的退订占位符替换成一个明显的假 token。
- `GET /api/subscriber-count`：查询改成 `confirmed=True, is_active=True`（以前退订直接删文档，现在会留 inactive 记录）。`base_count` 不动。

### 6. 迁移脚本 `scripts/sync_resend_contacts.py`

参照 `scripts/update_articles.py` 连库的写法。流程：`ensure_contact_property('unsubscribe_token')` → 给所有缺 token 的 subscriber 补 token → `run_sync`。默认 dry-run 只打印计划，`--apply` 才执行。上线前手动跑一次，把现有订阅者导进 Resend。

---

## 前端

- 新增 `src/views/UnsubscribeView.vue`，路由 `/unsubscribe`（`noindex`）。视觉照 tldr.tech 的克制风格，用项目里现有的 Tailwind / daisyUI 写法，参考现有 `UnsubscribedView.vue` 和 `SubscriptionSuccess.vue` 的结构。禁止渐变光晕、玻璃拟态、emoji 图标。
- 状态：
  - 加载：调 token 状态接口。
  - 无效 token / 没有 token：一句"链接无效或已过期"加返回首页按钮。
  - 已退订：一句"你已经退订了"加返回首页按钮。
  - 正常：标题"确定不再接收【太长不看】科技日推？"；下面是可选的原因多选（上表 8 项，checkbox）和一个可选的文本框（选了"其他"时文本框必须可见，没选也可以填）；主按钮"确认退订"。明确写一句"原因可以不填"。
  - 提交成功：显示退订成功（沿用现有 `UnsubscribedView` 的文案），加一句"谢谢你的反馈"（只有填了原因才显示）。
- 后端地址的拼法沿用前端现有调用 API 的方式（先 grep 现有订阅表单怎么请求 `/api/subscribe`）。
- 现有 `/unsubscribed` 路由和页面保留不动。

---

## 依赖

不加 `resend` SDK，用已有的 `requests`。`requirements.txt` 不变。

---

## 测试（pytest，放 `tests/`，沿用 `conftest.py` 的 `load_module` 方式加载纯模块）

- `resend_client`：monkeypatch `requests`，验证 URL、header、body 字段名，分页翻完，非 2xx 抛异常。
- `plan_sync`：覆盖三条规则，外加大小写不同的 email、Mongo 有但 unconfirmed 的人不被推到 Resend、两边一致时不产生动作。
- `generate_newsletter_html`：输出里含 `{{{contact.unsubscribe_token}}}` 且只出现一次三重花括号形式，不含 `%recipient`。
- 退订原因白名单过滤和 comment 截断（如果放在纯函数里）。

路由层不强求测试（`api/__init__` 会拉起整套 flask + mongo），但改完要 `python -c "import api.routes"` 级别能导入（在装了 requirements 的环境里；装不了就跳过并在汇报里说明）。前端跑 `npm run build` 确认能编译。

---

## 不做

- 不接 Resend webhook（同步在群发前做就够了）。
- 不做退订数据的后台页面，数据先在 Mongo 里攒着。
- 不改简报正文模板的视觉。
- 不碰 xhs 流水线和其它无关代码，不顺手重构 `routes.py`。

---

## 上线顺序（由主会话执行，agent 不用做）

1. 新 Resend 账号：验证 `tldrnewsletter.cn`（DNSPod 加记录），建 segment，建 full access API key。
2. Vercel 配 `RESEND_API_KEY`、`RESEND_SEGMENT_ID`、`MAIL_FROM_DOMAIN`。
3. 本地用生产库跑 `scripts/sync_resend_contacts.py`（先 dry-run 再 `--apply`）。
4. 自己的邮箱作为测试订阅者走一遍：订阅 → 确认 → `/api/test/send_newsletter` → 检查邮件里退订链接的 token 被正确替换 → 退订页提交原因 → Mongo 和 Resend 状态都对。
5. 合并部署，第二天看 cron 的 broadcast 是否发出。
