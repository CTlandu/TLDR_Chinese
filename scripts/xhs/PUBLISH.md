# 小红书发布规程

选择器和步骤在 2026-08-10 用真实账号走到了发布按钮前一步，全部实测过。**发布按钮本身尚未点过**，点下去之后的确认页长什么样、成功后跳转到哪，还是未知。

## 前置条件

- 当天流水线已经跑过（`prepare` → 会话里排序写文案 → `build`）
- 产物在 `scripts/xhs/output/<日期>/<序号>/`，含 `01.png`…`05.png` 和 `note.json`
- ego-browser 可用，小红书登录态有效

## 触发方式

运营者在 Claude Code 会话里说「发第 N 篇」。没有定时发布，没有批量发布。

## Task space

固定用 `xhs-publish`，跨轮次复用：

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('xhs-publish')
EOF
```

---

## 实测流程

### 1. 打开发布页并确认登录态

```js
await openOrReuseTab('https://creator.xiaohongshu.com/publish/publish', { wait: true, timeout: 40 })
await wait(4)
const txt = await js(String.raw`document.body.innerText.slice(0, 300)`)
```

文本里出现账号名（例如 `Colin兰度`）说明已登录。出现登录页立刻走「登录态失效」流程。

### 2. 切到「上传图文」

页面默认停在「上传视频」。**`loc=text:上传图文` 不是合法选择器**，ego-browser 只认 `loc=css:` / `loc=role:` / `loc=href:` / `@N`。用 JS 点：

```js
await js(String.raw`
  (() => {
    const els = Array.from(document.querySelectorAll('span.title'))
      .filter(e => e.innerText.trim() === '上传图文');
    els[els.length - 1].click();
    return true;
  })()
`)
```

页面有 6 个文本为「上传图文」的元素，取最后一个。

### 3. 上传图片：必须一次传完

编辑区有三个 file input：

| 位置 | accept | multiple | 用途 |
|---|---|---|---|
| `div.img-list` 第一个 | `.jpg,.jpeg,.png,.webp` | true | 批量上传 |
| `div.img-list` 第二个 | 同上 | false | 单张替换 |
| `.file-relation-container` | `.pdf,.doc,…` | false | 文档附件，无关 |

```js
const dir = '/绝对路径/scripts/xhs/output/2026-08-08/02'
const files = ['01.png','02.png','03.png','04.png','05.png'].map(n => `${dir}/${n}`)
await uploadFile('input[type="file"]', files)
await wait(8)
```

**`uploadFile` 接受路径数组，一次传完。绝对不要循环单张上传**——单张上传的 change 事件是延迟生效的，循环 5 次的结果是 10 张（第一次 1 张 + 延迟到账的 4 张 + 后来的 5 张），而且当时查计数器只显示 1 张，看不出错。

传完必须核对张数：

```js
await js(String.raw`
  (() => {
    const t = document.querySelector('.publish-page-content-media');
    const m = (t ? t.innerText : '').match(/(\d+)\s*\/\s*18/);
    return { counter: m ? m[0] : 'n/a', thumbs: document.querySelectorAll('div.img-list img').length };
  })()
`)
```

期望 `5/18` 和 5 张缩略图。数量不对就重载页面从头来，别在页面上删删补补。

平台限制：单篇最多 18 张，单张最大 32MB，推荐 3:4 到 2:1、分辨率不低于 720×960。我们的 2160×2880 正好 3:4。

### 4. 填标题

普通 input，`fillInput` 直接可用：

```js
await fillInput('input[placeholder="填写标题会有更多赞哦"]', note.title)
```

### 5. 填正文：必须用 JS 抢焦点

正文是 TipTap 富文本（`div.tiptap.ProseMirror`）。**`click()` 点不进去，焦点会留在标题框上，`typeText` 的内容会追加到标题里**——这个坑踩过，标题变成了 `AI设计出了自然界没有的病毒探针`。按坐标点击同样无效。

唯一可靠的做法是 JS 直接 focus 并把光标塞到末尾：

```js
const focusEnd = String.raw`
  (() => {
    const e = document.querySelector('div.tiptap.ProseMirror');
    e.focus();
    const r = document.createRange(); r.selectNodeContents(e); r.collapse(false);
    const s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
    return true;
  })()
`
await js(focusEnd)
```

确认 `document.activeElement.className` 含 `ProseMirror-focused` 之后再输入。分段输入，段间敲 Enter：

```js
const paras = body.split('\n\n')
for (let i = 0; i < paras.length; i++) {
  await typeText(paras[i])
  if (i < paras.length - 1) { await pressKey('Enter'); await wait(1) }
  await wait(1)
}
```

正文文本不能靠 `process.env` 传进来（沙箱里拿不到 `process`）。用脚本把 JSON 编码后的字符串直接嵌进 heredoc。

### 6. 话题标签：自动化不可靠，需要人工补

**这是唯一没能自动化成功的环节。**

在正文里打 `#关键词` 会触发一个话题下拉（`div.tippy-content .items .item`，每项带浏览量），点选之后正文里会变成真话题（`#科技[话题]#`）。但这个下拉**只在第一次触发成功，之后无论怎么试都不再出现**：换行再打、单独打 `#` 再打词、点 UI 上的「话题」按钮，全部无效。原因未查明。

当前做法：把标签作为**纯文本**跟在正文末尾。

```js
await typeText('#科技 #人工智能 #AI #生物科技 #前沿科技 #科技资讯 #科普 #每日AI')
```

纯文本 `#标签` 在小红书上通常仍会被解析成话题，但不保证关联到官方话题页，影响的是发现流量。

**如果要真话题标签，发布前由人手动在正文里点选一遍。** 这一步大概 30 秒，不值得为它继续跟自动化较劲。

### 7. 发布前确认（强制）

发布不可逆。点按钮**之前**先截图交给运营者：

```js
cliLog(await captureScreenshot())
```

得到明确的「发」之后再点。发布按钮在页面底部，文本 `发布`，旁边是 `暂存离开`（存草稿）。

### 8. 回写状态

```python
from api.models.xhs_post import XhsPost, STATUS_PUBLISHED
from datetime import datetime

post = XhsPost.objects(source_url='<note.json 里的 source_url>').first()
post.status = STATUS_PUBLISHED
post.published_at = datetime.utcnow()
post.save()
```

需要 MongoDB 凭据。`api` 数据源模式下才有 `XhsPost` 记录；`--source api` 跑出来的产物没有对应记录，这一步跳过。

### 9. 收尾

```js
await completeTaskSpace('xhs-publish', { keep: false })
```

---

## 登录态失效

```js
const r = await handOffTaskSpace(task.id)
```

然后明确告诉运营者：「小红书登录态失效了，浏览器控制权已经交给你，扫码登录后回一句『继续』。」

等运营者明确说继续，再 `takeOverTaskSpace('xhs-publish')` 续跑。

## 绝对不做的事

- **不自动重试。** 发布失败就停下报告，重试可能造成重复发布。
- **不自己 `takeOverTaskSpace` 抢回控制权。**
- **不换账号、不改任何账号设置。**
- **不把失败当成功回报。** 没在页面上看到发布成功的确认，就是没成功。
- **不在没有人明确确认的情况下点发布按钮。**

## 人工兜底

浏览器这条路挂了随时可以放弃：`scripts/xhs/output/<日期>/<序号>/` 里的 PNG 和 `note.json` 本身就是成品，AirDrop 到手机手动发，五分钟的事。不要为了跑通自动化反复重试。

## 仍未验证

- 点下「发布」之后的确认弹窗、成功提示、跳转目标
- 是否会触发验证码或风控
- 话题下拉为什么只触发一次
