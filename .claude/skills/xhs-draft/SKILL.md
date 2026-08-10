---
name: xhs-draft
description: 把 scripts/xhs 流水线产出的某一篇笔记填进小红书创作平台并存成草稿，供人工检查后手动发布。用户说「把第 N 篇存草稿」「发第 N 篇」「上传到小红书」时使用。全部步骤在 2026-08-10 实测通过。
---

# 小红书存草稿

把选定的那篇笔记的图片、标题、正文、标签全部填好，然后**存草稿**，停在那里。

**绝不点「发布」。** 发布由人在草稿箱里检查完自己点。这是刻意的分工——自动发布省下的两分钟不值它的脆弱度，而人工过一眼是内容质量的最后一道闸。

## 前置

- 当天流水线跑过，产物在 `scripts/xhs/output/<日期>/<序号>/`，含 `01.png`… 和 `note.json`
- ego-browser 可用，小红书登录态有效

## 整体流程

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('xhs-publish')
EOF
```

固定用 `xhs-publish` 这个 task space，跨轮次复用。

### 1. 打开发布页，确认登录

```js
await openOrReuseTab('https://creator.xiaohongshu.com/publish/publish', { wait: true, timeout: 40 })
await wait(4)
const txt = await js(String.raw`document.body.innerText.slice(0, 300)`)
```

文本里出现账号名说明已登录。同时记下起始草稿数，收尾时要对比：

```js
const before = await js(String.raw`
  (() => { const m = document.body.innerText.match(/草稿箱\((\d+)\)/); return m ? m[1] : null; })()
`)
```

看到登录页就走「登录态失效」流程，不要尝试绕过。

### 2. 切到「上传图文」

页面默认停在「上传视频」。**`loc=text:xxx` 不是合法选择器**，ego-browser 只认 `loc=css:` / `loc=role:` / `loc=href:` / `@N`。用 JS 点，页面上有 6 个文本为「上传图文」的元素，取最后一个：

```js
await js(String.raw`
  (() => {
    const e = Array.from(document.querySelectorAll('span.title'))
      .filter(x => x.innerText.trim() === '上传图文');
    e[e.length - 1].click();
    return true;
  })()
`)
await wait(4)
```

### 3. 上传图片：一次传完，不要循环

```js
const dir = '/绝对路径/scripts/xhs/output/2026-08-08/02'
const files = ['01.png','02.png','03.png','04.png','05.png'].map(n => `${dir}/${n}`)
await uploadFile('input[type="file"]', files)
await wait(9)
```

**`uploadFile` 接受路径数组。绝对不要循环单张上传。** 单张上传的 change 事件是延迟生效的：循环 5 次之后立刻查计数器只显示 1 张，看起来只成功了一张，于是你会想「再传一次」，结果几秒后 4 张延迟到账，加上重传的 5 张，最后变成 10 张重复图。

传完必须核对：

```js
await js(String.raw`
  (() => {
    const t = document.querySelector('.publish-page-content-media');
    const m = (t ? t.innerText : '').match(/(\d+)\s*\/\s*18/);
    return { counter: m ? m[0] : 'n/a', thumbs: document.querySelectorAll('div.img-list img').length };
  })()
`)
```

期望 `5/18` 和 5 张缩略图。**数量不对就重载页面从头来**，不要在页面上删删补补——那会留下更多垃圾草稿。

平台限制：单篇最多 18 张，单张 32MB，推荐 3:4 到 2:1、不低于 720×960。流水线出的 2160×2880 正好 3:4。

### 4. 标题

普通 input，直接填：

```js
await fillInput('input[placeholder="填写标题会有更多赞哦"]', note.title)
```

### 5. 正文：必须用 JS 抢焦点

正文是 TipTap 富文本（`div.tiptap.ProseMirror`）。**`click()` 点不进去，按坐标点也不行**，焦点会留在标题框上，`typeText` 的内容会追加进标题——踩过这个坑，标题变成了 `AI设计出了自然界没有的病毒探针`。

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

输入前先确认焦点真的过去了：

```js
await js(String.raw`(() => String(document.activeElement.className).includes('ProseMirror-focused'))()`)
```

拿到 `true` 再分段输入，段间敲 Enter：

```js
const paras = body.split('\n\n')
for (let i = 0; i < paras.length; i++) {
  await typeText(paras[i])
  if (i < paras.length - 1) { await pressKey('Enter'); await wait(1) }
  await wait(1)
}
```

正文文本**不能靠 `process.env` 传进来**，ego-browser 沙箱里没有 `process`。用脚本把 JSON 编码后的字符串直接嵌进 heredoc 再管道给 `ego-browser nodejs`。

### 6. 标签

把标签作为纯文本跟在正文末尾一起输入即可（第 5 步的 body 里就该包含它们）。

想把它们变成**真话题**（关联官方话题页，影响发现流量）的话：在正文里打完 `#关键词` 后，光标停在词尾会弹出下拉 `div.tippy-content .items .item`，每项带浏览量，选**文本精确匹配**的那项，不要选第一项（打 `#科技` 时第一项是 `#科技数码howto`）。

```js
const info = await js(String.raw`
  (() => {
    const items = Array.from(document.querySelectorAll('div.tippy-content .items .item'));
    if (!items.length) return { ok: false };
    const hit = items.find(e => (e.innerText||'').split('\n')[0].trim() === window.__want);
    const t = hit || items[0];
    const r = t.getBoundingClientRect();
    return { ok: true, exact: !!hit, picked: (t.innerText||'').split('\n')[0],
             xy: [Math.round(r.x + 50), Math.round(r.y + r.height/2)] };
  })()
`)
```

选中后正文里会变成 `#科技[话题]#`。

**已知问题：连续快速选多个标签会失败。** 一个循环里 7 秒内连发 7 次查询，下拉全部不出现；隔几分钟单独再试就正常。推测是话题搜索接口被限流，**没有验证过**。要批量转真话题的话，每个之间留足间隔（10 秒以上）再试。

纯文本 `#标签` 在小红书上通常仍会被解析成话题，只是不保证关联官方话题页。存草稿场景下，让人在发布前手动点选也就 30 秒，不值得跟限流较劲。

### 7. 存草稿

底栏的「暂存离开」和「发布」在一个自定义元素 `xhs-publish-btn` 里，**closed shadow DOM，从外面查不到文本**，`document.querySelectorAll('*')` 按 textContent 匹配一定失败。只能按坐标点，但可以用容器相对位置算，不依赖窗口尺寸：

```js
const pos = await js(String.raw`
  (() => {
    const c = document.querySelector('xhs-publish-btn');
    if (!c) return null;
    const r = c.getBoundingClientRect();
    return {
      draft:   [Math.round(r.x + r.width * 0.415), Math.round(r.y + r.height / 2)],
      publish: [Math.round(r.x + r.width * 0.581), Math.round(r.y + r.height / 2)]
    };
  })()
`)
```

**点之前先截图确认。** 两个按钮只差 143px，点错就是直接发布出去，不可逆：

```js
cliLog(await captureScreenshot())
```

截图里确认左边灰色的是「暂存离开」、右边红色的是「发布」，然后点 `pos.draft`。

点完等 8 秒，URL 会变成 `?from=tab_switch`。

### 8. 核对草稿数

```js
await gotoAndWait('https://creator.xiaohongshu.com/publish/publish', { timeout: 40 })
await wait(5)
const after = await js(String.raw`
  (() => { const m = document.body.innerText.match(/草稿箱\((\d+)\)/); return m ? m[1] : null; })()
`)
```

比起始值多 1 才算成功。

### 9. 收尾

```js
await completeTaskSpace('xhs-publish', { keep: true })
```

用 `keep: true` 把页面留着，运营者要去草稿箱检查。然后告诉他：草稿已存好，去创作服务平台的草稿箱检查后手动发布。

## 离开页面会自动存草稿

编辑器里有内容时，关标签页或跳走都会自动存一份草稿。**中途放弃、重来、为了调试传张图，每一次都会留下一份垃圾草稿。**

所以：想好了再开始填，尽量一次跑完。跑歪了的话，记得提醒运营者去草稿箱删掉多余的。

## 绝对不做的事

- **不点「发布」。** 这个 skill 的终点是草稿箱。
- **不自动重试。** 失败就停下报告。
- **不自己 `takeOverTaskSpace` 抢回控制权。** 只有运营者明确说继续之后才接管。
- **不换账号、不改任何账号设置。**
- **不把失败当成功回报。** 草稿数没涨就是没存上。

## 登录态失效

```js
const r = await handOffTaskSpace(task.id)
```

然后明确告诉运营者：登录态失效了，浏览器控制权已交给你，扫码登录后回一句「继续」。等他明确说继续，再 `takeOverTaskSpace('xhs-publish')` 续跑。

## 人工兜底

浏览器这条路挂了随时可以放弃。`scripts/xhs/output/<日期>/<序号>/` 里的 PNG 和 `note.json` 本身就是成品，AirDrop 到手机手动发，五分钟的事。不要为了跑通自动化反复重试。

## 仍未验证

- 点「发布」之后的确认弹窗、成功提示、跳转目标（刻意没试）
- 话题下拉连续调用失败是不是限流
- 是否会触发验证码或风控
