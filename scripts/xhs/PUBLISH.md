# 小红书发布规程

> **状态：选择器尚未经过真实发布验证。**
> 下面的流程基于 ego-browser 的 helper 契约和小红书创作平台的公开发布流程写成，
> 但没有真的发过一篇。第一次发布必须有人在旁边看着，逐条确认下方「首次验证清单」，
> 把实际的按钮文案和输入框定位方式回填进来之后，再删掉这段提示。

## 前置条件

- 当天流水线已经跑过（`prepare` → 会话里排序写文案 → `build`，或者 `auto`）
- 产物在 `scripts/xhs/output/<日期>/<序号>/`，含 `01.png`…`04.png` 和 `note.json`
- ego-browser 可用，且用户的小红书登录态在浏览器里是有效的

## 触发方式

运营者在 Claude Code 会话里说「发第 N 篇」。没有定时发布，没有批量发布——
每次发布都由人明确指定哪一篇。

## Task space 约定

固定用 `xhs-publish` 这个名字，跨轮次复用同一个空间：

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('xhs-publish')
cliLog('task space id: ' + task.id)
EOF
```

后续每一轮 heredoc 都以 `useOrCreateTaskSpace('xhs-publish')` 开头。
只有在用户交还控制权之后，才改用 `takeOverTaskSpace`。

## 发布步骤

### 0. 读取产物

先读 `scripts/xhs/output/<日期>/<序号>/note.json` 拿到标题、正文、标签和图片文件名。
图片要用**绝对路径**传给 `uploadFile`。

### 1. 打开发布页并确认登录态

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('xhs-publish')
await openOrReuseTab('https://creator.xiaohongshu.com/publish/publish', { wait: true, timeout: 30 })
cliLog(await pageInfo())
cliLog(await snapshotText())
EOF
```

从 snapshot 判断当前是发布页还是登录页。**看到登录页就立刻走「登录态失效」流程，不要尝试绕过。**

### 2. 切到图文发布

创作平台默认可能停在「上传视频」。用可见文本定位切到图文那一栏——
小红书前端的 class 名是混淆的，改版后文本比 class 稳定得多。

```bash
await click('loc=text:上传图文')
```

### 3. 上传图片

按序号顺序逐张上传，保证封面是第一张：

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('xhs-publish')
const dir = '/绝对路径/scripts/xhs/output/2026-08-10/01'
for (const name of ['01.png', '02.png', '03.png', '04.png']) {
  await uploadFile('input[type="file"]', `${dir}/${name}`)
  await wait(1)
}
cliLog(await snapshotText())
EOF
```

上传完必须用 snapshot 或截图确认张数和顺序都对，再往下走。

### 4. 填标题

标题是普通 input，`fillInput` 应该可以直接写：

```bash
await fillInput('loc=placeholder:填写标题', '<note.json 里的 title>')
```

### 5. 填正文

**正文大概率是富文本编辑器，不要默认 `fillInput` 能写进去。**
ego-browser 的指引里明确说了：富文本/虚拟化编辑器要先做一次小的写入探针，
确认文字真的落在目标位置，否则改走视觉流程（截图 → `click([x, y])` → `typeText`）。

先探针，再写全文：

```bash
await click('loc=placeholder:输入正文描述')
await typeText('测试')
// 截图确认「测试」两个字出现在正文区域，而不是别的地方
```

探针通过后清空，再写完整正文。

### 6. 标签

小红书的话题标签通常要在正文区输入 `#关键词` 后从下拉里选中才算生效，
直接把 `#标签` 当纯文本打进去可能不会关联话题。
逐个输入并从下拉确认，每个之间留一点时间。

### 7. 发布前最后确认

发布是不可逆的。点发布按钮**之前**先截图，把图交给运营者确认：

```bash
cliLog(await captureScreenshot())
```

得到明确的「发」之后再点。

### 8. 回写状态

发布成功后把这条记录标成已发布：

```python
from api.models.xhs_post import XhsPost, STATUS_PUBLISHED
from datetime import datetime

post = XhsPost.objects(source_url='<note.json 里的 source_url>').first()
post.status = STATUS_PUBLISHED
post.published_at = datetime.utcnow()
post.save()
```

### 9. 收尾

```bash
ego-browser nodejs <<'EOF'
await completeTaskSpace('xhs-publish', { keep: false })
EOF
```

## 登录态失效

Cookie 会周期性过期，频率未知。检测到未登录时：

```bash
ego-browser nodejs <<'EOF'
const task = await useOrCreateTaskSpace('xhs-publish')
const r = await handOffTaskSpace(task.id)
cliLog(JSON.stringify(r))
EOF
```

然后明确告诉运营者：「小红书登录态失效了，浏览器控制权已经交给你，扫码登录后回一句『继续』。」

等到运营者明确说继续，再 `takeOverTaskSpace('xhs-publish')` 续跑。

## 绝对不做的事

- **不自动重试。** 发布失败就停下来报告，重试可能造成重复发布。
- **不自己 `takeOverTaskSpace` 抢回控制权。** 只有在运营者明确说继续之后才接管。
- **不换账号、不改任何账号设置。**
- **不把失败当成功回报。** 没有在页面上看到发布成功的确认，就是没成功。
- **不在没有人明确确认的情况下点发布按钮。**

## 人工兜底

浏览器这条路挂了（页面改版、检测拦截、登录反复失效）随时可以放弃自动化：
`scripts/xhs/output/<日期>/<序号>/` 里的 PNG 和 `note.json` 本身就是可以直接用的成品，
AirDrop 到手机上手动发，五分钟的事。**不要为了跑通自动化而反复重试。**

## 首次验证清单

第一次真实发布时逐条确认，然后把实际值回填到上面对应的步骤里：

- [ ] 发布页的真实 URL（`/publish/publish` 是否还有效）
- [ ] 「上传图文」入口的实际可见文本
- [ ] 文件 input 的实际选择器，以及是否支持多选一次传完
- [ ] 上传后图片顺序是否与传入顺序一致（封面必须是第一张）
- [ ] 标题输入框的实际 placeholder 文案
- [ ] 正文编辑器是不是富文本，`fillInput` 探针是否成功
- [ ] 标签是在正文里打 `#` 触发下拉，还是有独立的标签输入区
- [ ] 发布按钮的实际文案，以及点完之后的成功确认长什么样
- [ ] 全程有没有触发验证码或风控提示

验证完成后，删掉本文件顶部的状态提示，并把这份清单换成实际记录。
