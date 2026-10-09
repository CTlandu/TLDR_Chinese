# Vercel 部署检查清单 ✅

## 🚨 重要：在 Vercel Dashboard 中检查

### 1️⃣ 环境变量检查

进入 **Settings → Environment Variables**，确认：

#### ❌ 不要设置（或删除）：
```bash
VITE_API_URL
```
**如果设置了 `VITE_API_URL`，请删除它！**这会导致跨域问题。

#### ✅ 必须设置：
```bash
MONGODB_URI=你的MongoDB连接字符串
RESEND_API_KEY=你的Resend密钥（Full access）
RESEND_SEGMENT_ID=Resend里每日简报segment的id
MAIL_FROM_DOMAIN=tldrnewsletter.cn
DEEPSEEK_API_KEY=你的DeepSeek密钥
ERNIE_API_KEY=你的百度API密钥
ERNIE_SECRET_KEY=你的百度Secret密钥
NEWSLETTER_API_KEY=自定义一个安全字符串
FLASK_ENV=production
FRONTEND_URL=https://tldr-chinese.vercel.app（部署后填）
BACKEND_URL=https://tldr-chinese.vercel.app（部署后填）
```

### 2️⃣ Functions 检查

**如何查看：**
1. Vercel Dashboard → 选择项目
2. 点击顶部 **"Deployments"** 标签
3. 点击最新的部署记录
4. 点击 **"Functions"** 标签

**检查结果：**
✅ 应该看到：`api/index.py` 
- 如果看到了 → 说明 API 已部署 ✅
- 如果看不到或没有 Functions 标签 → API 没有部署，需要修复 ❌

**快速测试：** 直接访问 `https://你的域名.vercel.app/api/subscriber-count`，应该返回 JSON 数据

### 3️⃣ 构建日志检查

进入 **Deployments → 最新部署 → Building** 标签：

检查是否有以下内容：
```
✅ Installing Python dependencies...
✅ pip install -r requirements.txt
✅ Building frontend...
✅ npm run build
```

如果有错误，查看具体错误信息。

### 4️⃣ 测试 API 端点

部署成功后，在浏览器中直接访问：

```
https://你的域名.vercel.app/api/subscriber-count
```

**预期结果：**
```json
{
  "count": 4738,
  "success": true
}
```

如果返回 404 或其他错误，说明 API 没有正确部署。

---

## 🔧 常见问题修复

### 问题 1：API 返回 404

**原因：**Vercel 没有识别到 Python functions

**解决方案：**
1. 确保 `api/index.py` 存在
2. 确保 `requirements.txt` 在项目根目录
3. 检查 `vercel.json` 配置是否正确
4. 重新部署

### 问题 2：CORS 错误（跨域）

**原因：**`VITE_API_URL` 环境变量设置错误

**解决方案：**
1. 进入 Vercel Dashboard → Environment Variables
2. **删除** `VITE_API_URL` 变量（或设置为空）
3. 重新部署

### 问题 3：前端调用了生产域名而不是预览域名

**症状：**
```
Access to XMLHttpRequest at 'https://tldr-chinese.vercel.app/api/...' 
from origin 'https://tldr-chinese-xxx.vercel.app' has been blocked
```

**原因：**`VITE_API_URL` 环境变量设置为生产域名

**解决方案：**
1. 删除 `VITE_API_URL` 环境变量
2. 确保前端代码使用相对路径：`/api/...`（不带域名）
3. 重新部署

### 问题 4：MongoDB 连接失败

**原因：**MongoDB Atlas IP 白名单限制

**解决方案：**
1. 登录 MongoDB Atlas
2. Network Access → Add IP Address
3. 添加 `0.0.0.0/0`（允许所有 IP）
4. 保存并等待生效

---

## 📝 部署后验证步骤

### 1. 检查首页
```
https://你的域名.vercel.app/
```
✅ 应该看到订阅者数量（如 4738+ 订阅者）

### 2. 检查 Newsletter 页面
```
https://你的域名.vercel.app/newsletter/2025-11-12
```
✅ 应该显示当天的新闻内容

### 3. 检查浏览器控制台
按 F12 打开开发者工具：
- **Console** 标签：不应该有 CORS 或 404 错误
- **Network** 标签：API 请求应该返回 200 状态码

---

## 🎯 正确的 API 调用方式

### ✅ 正确（使用相对路径）：
```javascript
const API_URL = import.meta.env.VITE_API_URL || '';
const response = await axios.get(`${API_URL}/api/subscriber-count`);
// 实际请求：/api/subscriber-count（相对路径）
```

### ❌ 错误（硬编码域名）：
```javascript
const API_URL = 'https://tldr-chinese.vercel.app';
const response = await axios.get(`${API_URL}/api/subscriber-count`);
// 实际请求：https://tldr-chinese.vercel.app/api/subscriber-count（跨域）
```

---

## 🚀 重新部署

修改配置后，需要触发重新部署：

### 方法 1：通过 Git
```bash
git add .
git commit -m "Fix deployment configuration"
git push origin main
```

### 方法 2：通过 Vercel Dashboard
1. 进入 **Deployments**
2. 点击最新部署旁边的 **...** 按钮
3. 选择 **Redeploy**

---

## 📞 需要帮助？

如果按照上述步骤仍有问题：

1. **截图 Vercel 部署日志**（Building 和 Functions 标签）
2. **截图浏览器控制台错误**
3. **提供 Vercel 部署 URL**

这样可以更快定位问题！

