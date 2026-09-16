# X / newsletter 科技记者风格简报 → TLDR Chinese 小红书「科技资讯」

> 调研日期：2026-09-16（美东）  
> 用途：重写 `SKILL.md` 时的语感参照。体裁名：**科技资讯**（不是「咨询」）。  
> 长度原则：**跟着新闻走，不硬卡字数**——短讯可短；只有值得讲因果/利害的才写解读体（约 250–400 字量级，可略伸缩）。

---

## 0. 调研来源与 blockers（诚实记录）

| 渠道 | 结果 |
|---|---|
| Platformer（Casey Newton） | ✅ 全文可读：`platformer.news`（Ghost）。采样《The AI safety vibe shift》(2026-09-10) |
| Sources（Alex Heath） | ⚠️ 多数付费；✅ 免费 intro + 播客导语页（Baseten CEO, 2026-09-15） |
| Hayden Field / The Verge | ✅ 全文可读 |
| Mark Gurman | ✅ Mastodon / LinkedIn 短帖；Bloomberg 全文常付费墙 |
| Karen Hao / Parmy Olson | ✅ 书摘与引用（Empire of AI / Bloomberg 财经判断句） |
| 阑夕 @foxshuo | ✅ twiscan 镜像可读近期长帖 |
| 向阳乔木 @vista8 | ✅ twiscan；偏产品/亲测，新闻解读密度低于阑夕 |
| Caiwei Chen @CaiweiC | ✅ MIT TR 报道全文 |
| indigo / 芦义 @indigo11 | ✅ indigox.me 长文；X 本人短帖未稳定抓到 |
| x.com 直连 / Nitter / XCancel | ❌ 2026-09 起 Nitter/XCancel 因法律压力大面积停服（TechCrunch 2026-09-15）；改用 twiscan、topicdigg、Mastodon、作者站、newsletter |

**取样偏好说明：** 以 NEWS/分析号为主。`@vista8` 偏工具亲测，作「口语证据密度」对照，不当主模板。纯 prompt/教程号未纳入。

---

## 1. Account sample table

| Handle / 出处 | 语言 | 擅长 | 2–4 句 verbatim 摘录（每条 ≤2 句） | 可观察模式 |
|---|---|---|---|---|
| **@CaseyNewton** / Platformer | EN | 把平台新闻写成「话语转向」；数字+伦理披露自然嵌进叙述 | 「Moments before I sent out that edition, though, a recently departed Anthropic researcher published an X post that brought the subject to the center of conversation.」 / 「Of course, back then, Anthropic wasn’t a $965 billion company heading toward what could be the biggest initial public offering of all time.」 / Mastodon 短讯式：「New in Platformer: months ago, Meta discussed ending funding to its Oversight Board. But today… the board said Meta has increased its funding by $13 million…」 | Hook = 时间/反差一句；利害用市值/监管/舆情自然带出；短帖几乎无 emoji；结尾常「right people are listening / here’s hoping」式克制收束 |
| **@alexeheath** / Sources | EN | 内线语气 + 数字堆栈；一句话立住「为什么现在聊这个」 | 「I’ve leaked many internal meetings and product roadmaps.」 / 「Who controls talent, distribution, and compute in the years ahead will define the next era.」 / 「Baseten’s growth gives a sense of what’s happening: The company raised funding at a $5 billion valuation in January and again at $13 billion in June.… token volume has grown 40 times year over year, with revenue up roughly tenfold…」 | 短句；事实→规模→竞争位次；很少鸡汤；利害 = 谁拿走算力/分发/人才；几乎不用 emoji |
| **Hayden Field** (The Verge AI) | EN | 新闻导语式：一句事件 + 一句 stakes | 「OpenAI’s next big model is here: GPT-6 Astra. The company calls it a “generational leap in capability” for areas like cybersecurity, professional work, software engineering, science, and computer use.」 / 「Anthropic spent this week in hot water over cybersecurity. A researcher’s resignation letter went viral, just before the company released details about four models going rogue.」 | 标题即因果；正文前两句把「发生了什么 + 为何烫手」说完；引语带身份；句长中等、标点干净；无 emoji |
| **Mark Gurman–style** (Bloomberg / Mastodon) | EN | 短爆料：BREAKING + 产品名 + 合作方 + 上线范围 | 「BREAKING: Apple will launch Apple Upgrade next week, an iPhone, iPad, Mac and Apple Watch leasing/subscription program. It’s partnering with Klarna to launch in the U.S. at online and retail stores.」 | 信息密度极高；几乎零形容词；无 emoji；留给读者自己算利害 |
| **Karen Hao / Parmy Olson（分析侧）** | EN | 用一组数字把「神话」拆成利益分配 | 「…the data “raises an uncomfortable prospect: that this supposedly revolutionary technology might never deliver on its promise of broad economic transformation, but instead just concentrate more wealth at the top.”」(Bloomberg via Hao 引用) / 「As I finished writing this book in January 2025, OpenAI topped a $157 billion valuation.… Since ChatGPT, the six largest tech giants together have seen their market caps increase $8 trillion.」 | 利害 = 财富/权力集中；数字成对出现（估值 vs 真实生产力）；不喊口号 |
| **阑夕 @foxshuo** | ZH | 中文互联网评论王：数字墙 + 因果链 + 口语比喻 | 「晚点LatePost那期讲模型蒸馏的播客其实还蛮有料的，比如字节的部分。张一鸣不让Seed蒸馏，同时允许暂时落后，是有野心和抱负的…」 / 「红果短剧8月热度榜Top 10，9部AI剧，1部真人剧。…4月热度榜Top 10，0部AI剧，10部真人剧。所以纵向的看，暑假是一个转折点…」 / 「豆包的最低档会员就是68块钱一个月了，像是Kimi也是49块钱一个月的起价，越过了30块钱一个月这个标准；30块钱一个月就是手游里的月卡…」 | Hook 常「省流/锐评/纵向一看」；数字成串；利害用「组织依赖/耗不起黄金年龄/调控无效」说人话；emoji 偶发（⋯⋯🥵🤩）不堆在分析段；收尾常一句刺点或「干就完了」 |
| **向阳乔木 @vista8** | ZH | 亲测口语；新闻帖也带「数据→一句判断」 | 「AI 生成内容的数量增长有多快？据中国网络视听协会的数据：今年上半年国内各平台上线了 36.7 万部微短剧，其中超过 74% 是 AI 生成的，平均每天新增超过 1500 部 AI 短剧。」 / 「Dario 真惨，放慢 AI 发展速度是不可能的... 需要被监管的应该是具体应用，不是 AI 智能本身。」 | 问句开场；数字紧跟；判断短；emoji/「哈哈哈」多见于产品帖，新闻帖少；结尾常开放问或类比 |
| **Caiwei Chen @CaiweiC** / MIT TR | EN（双语记者） | 现场感报道；把「中国科技在场」写成可感知事实 | 「Chinese exhibitors accounted for nearly a quarter of all companies at the show…」 / 「“We added AI” is slapped onto everything from the reasonable (PCs, phones, TVs…) to the deranged (slippers, hair dryers, bed frames).」 / 「Did you know two Chinese brands basically dominate the market for home cleaning robots in the US…?」 | 第一人称现场；具体品类+反差；利害 = 供应链/迭代速度；句式口语但不碎 |
| **indigo / 芦义 @indigo11** | ZH | 长文转译：概念钩子 + 产业判断（适合「解读体」借鉴，不适合整段贴 XHS） | 「现在，软件应用范式已经转移，AI Agent 就是新 SaaS。」 / 「软件吞噬世界，AI 吞噬软件！」 | 金句密度高；对 XHS 要用其**压缩后的产业判断**，避免长篇理论脚手架 |

### 长文节奏（Platformer / Sources）可借一点

- **Platformer**：叙事弧 = 事件 → 个人观感 → 宏观数字 → 「所以现在不一样了」→ 克制收尾。中间穿插引语与 view count，不写「为什么重要：」。
- **Sources intro**：简历式 cred 一句带过 → 行业地面在晃 → **谁控制 talent / distribution / compute**。适合我们「利害段」的一句话骨架。

---

## 2. Shared style patterns → 我们的 XHS「科技资讯」

### 先选模式（强制）

| 模式 | 何时用 | 体量 | 结构重心 |
|---|---|---|---|
| **短讯** | 单一事实、产品上线、人事、财报数字、无复杂因果；读者 5 秒能懂 | **短而密**：约 80–200 字（可更短）；不硬凑到 250 | 标题 + 1–3 句证据 +（可选）半句利害 + 轻互动 |
| **解读** | 有组织/监管/商业闭环/用户代价；需要「所以呢」 | **约 250–400 字**（可 ±50）；宁可少一段也不注水 | 标题 / 导语 / 证据 / 利害 / 收尾问句 |

**选模规则（可执行）：**

1. 素材里若只有「谁发布了什么 + 参数/价格」，且无第二层后果 → **短讯**。  
2. 素材里出现 ≥2 个可连的利害节点（钱、权、规则、用户、竞争位次、组织）→ **解读**。  
3. 不确定时：先写短讯；若写完发现少一句「所以对谁有影响」就憋得慌 → 升解读，而不是反过来灌水。

### Do（两种模式通用）

| Do | 从谁学 | 落到 XHS |
|---|---|---|
| **主谓宾，谁干了什么** | Field / Gurman / 阑夕 | 禁定语后置英译腔 |
| **数字成对/成串** | Heath「$5B→$13B、40×」；阑夕「68/49/30、Top10 纵向」 | 每个关键主张至少一个硬数；形容词换成数 |
| **利害用具体人/组织说话** | Newton「$965B company」；阑夕「字节耗得起，但我耗不起」 | 写「谁买单/谁被锁死/谁抢到入口」，不写「深远影响」 |
| **因果嵌在句子里，不贴小标题** | Field 标题即因果；Newton 用 Of course / Until recently | 禁用「为什么重要：」「跟你的关系：」 |
| **口语但有信息** | 阑夕「活久见」「拔鹅毛」；vista8 问句开场 | 允许「其实」「说白了」；不允许空口头禅连发 |
| **信源具体** | 全员记者习惯 | TechCrunch / 华尔街日报 / 公司财报 / 协会名，不写「据悉」 |
| **收尾开放、贴本条** | 中文号评论区传统 | 问句跟新闻绑死；短讯可用半句；解读必须有 |

### Don’t（AI 味杀手）

| Don’t | 为什么像 AI |
|---|---|
| 硬凑 250–400 字 | 短讯被注水 = 最大 AI 味 |
| `为什么重要：` / `先说不用慌` / `值得注意的是` | 讲解脚手架 |
| `这不仅仅是A，而是B` / 三项整齐排比 / 格言收尾 | 可引用感 |
| 破折号串长句、定语后置 | 英译腔 |
| emoji 刷屏或纯工具教程口吻 | 偏离科技资讯；产品号另说 |
| 文本卡片图、金句海报 | 产品决策：停做；**只保留原文配图** |
| 「革命性突破」「引发广泛关注」 | 零信息形容词 |

### 句长 / 标点 / emoji（压缩规则）

- **句长：** 中文以 15–35 字短句为主；解读体允许 1–2 句稍长因果句，但拆开比硬连好。  
- **标点：** 中文逗号/句号/省略号（⋯⋯）可学阑夕；少用破折号；感叹号最多 1 个。  
- **emoji：** 解读正文 **0–1 个**（多在互动句末 👇）；短讯标题可 0；证据段不要 emoji。  
- **中英文间不加空格**（沿用现有 SKILL）。

---

## 3. 结构模板（一篇笔记）

### A. 短讯模式

```
标题（10–16字，主谓宾，可数字前置）
导语兼证据：1–2 句说清谁做了什么 + 关键数字/信源
（可选）半句利害：对谁有影响，不展开
收尾：一句轻问或「你怎么看这条？」类短互动（仍要贴题）
```

**例骨架：**  
`OpenAI放出GPT-6 Astra` → `面向Plus到企业用户分批上线，自称「进入AGI时代」，同时强调过了关键网络安全门槛。` → `上一次模型越狱还没凉透。` → `这回你更信能力，还是更信护栏？`

### B. 解读模式（≈250–400 字）

```
标题：停手钩子（数字 / 反常事实 / 被曝式）—— 不要疑问句标题硬凑
导语：1 句发生了什么 + 1 句「为什么现在烫」（因果嵌入，无小标题）
证据段：2–4 个硬事实（数字、引语带身份、时间线）；可纵向对比
利害段：1–2 句写清钱/权/规则/用户代价（学 Heath 的 talent·distribution·compute，或阑夕的组织人性）
收尾问句：开放、可争论、跟本条绑定 + 可选 👇
```

**不要**再按「正文卡 2–3 张」写；图侧只放**原文图片**，文案是一条连续笔记。

---

## 4. 五组 before → after（去 AI 味微例）

### ① 英译腔标题 → 主谓宾

| Before | After |
|---|---|
| 地球上没有过的病毒，AI设计的 | 美国科学家用AI造出了16种新病毒 |

### ② 形容词 → 数字对

| Before | After |
|---|---|
| Meta给出极低价token，换你的数据拿去训练 | Meta便宜档每百万输出token只要20美分，不到贵档十分之一；想用便宜档就得同意反馈拿去训agent |

### ③ 脚手架小标题 → 嵌进句子（解读）

| Before | After |
|---|---|
| 为什么重要：这标志着AI安全讨论进入主流。跟你的关系：监管可能加速。 | Anthropic市值叙事已经到千亿级了，同一套「AI可能杀死人类」的话，以前是圈内自嗨，现在国会和对手党派都在跟——安全话术终于有政治杠杆了。 |

### ④ 短讯被灌水 → 短讯该短

| Before（硬凑解读） | After（短讯） |
|---|---|
| Apple将推出设备租赁订阅计划Apple Upgrade，与Klarna合作……（后接三段「这意味着消费电子金融化」「值得注意的是」……凑满300字） | Apple下周推Apple Upgrade：iPhone到Watch都能租，和Klarna合作，先在美国线上线下开。硬件又朝「分期默认」挪了一步。你会为了新机直接租吗？ |

### ⑤ 格言收尾 → 利害问句

| Before | After |
|---|---|
| 能力先到，规矩后到。未来已来。 | 模型越狱和研究员公开辞职叠在同一周——你更担心能力跑太快，还是公司自己管不住？评论区说说👇 |

---

## 5. Recommended voice one-liner

**像阑夕写短评论、像 Field 写导语：一句说清谁干了什么，数字钉死事实，利害落到人/钱/规则上；短讯干脆，解读才展开——听起来是中文科技资讯号，不是外媒摘要，更不是 AI 课件。**

---

## 6. 给下一步改 `SKILL.md` 的直接指令（可粘贴）

1. 体裁统一称 **科技资讯**；删除「每篇必须 250–400 / 必须 2–3 张正文卡」的硬约束。  
2. 增加 **短讯 / 解读** 选模规则（见 §2）。  
3. 视觉：停止文本卡片图；只保留原文配图。  
4. 文案结构按 §3；禁用清单保留并加上「硬凑字数」。  
5. 语感校准：动笔前扫本文件 §1 摘录，不扫工具教程号。

---

## Appendix: 原文锚点（便于复核）

- Platformer: https://www.platformer.news/ai-safety-vibe-shift-coxon-anthropic/  
- Sources intro: https://sources.news/p/introducing-sources  
- Sources Baseten: https://sources.news/p/basetens-ceo-every-company-own-ai  
- Verge Field Astra: https://www.theverge.com/ai-artificial-intelligence/989601/openai-gpt-6-astra-release  
- Verge Field Anthropic: https://www.theverge.com/ai-artificial-intelligence/994064/anthropic-spent-this-week-in-hot-water-over-cybersecurity  
- Caiwei Chen CES: MIT Technology Review, 2026-01-12  
- 阑夕 / 乔木镜像：twiscan.com（X 官方登录墙与 Nitter 停服期间的替代）  
- Gurman Mastodon BREAKING（Apple Upgrade / Klarna）  
- Hao / Olson 财富集中判断句：Empire of AI 书摘引用 Bloomberg
