# Vercel 快速部署指南 🚀

这是一个快速参考指南，完整文档请查看 [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)。

## 5 分钟快速部署

### 1️⃣ 推送代码到 GitHub

```bash
git add .
git commit -m "准备部署到 Vercel"
git push origin main
```

### 2️⃣ 导入项目到 Vercel

1. 访问 [vercel.com](https://vercel.com) 并登录
2. 点击 **"Add New Project"**
3. 选择你的 `TLDR_Chinese` 仓库
4. 点击 **"Import"**

### 3️⃣ 配置环境变量

在项目设置 → Environment Variables 中添加：

```
MONGODB_URI=mongodb+srv://...
MAILGUN_API_KEY=key-xxx
MAILGUN_DOMAIN=mg.yourdomain.com
DEEPSEEK_API_KEY=sk-xxx
ERNIE_API_KEY=your-key
ERNIE_SECRET_KEY=your-secret
NEWSLETTER_API_KEY=随机生成一个安全密钥
FLASK_ENV=production
```

**先不填的（部署后再填）：**
```
FRONTEND_URL=（部署后填写 Vercel 域名）
BACKEND_URL=（部署后填写 Vercel 域名）
VITE_API_URL=（可以留空）
```

### 4️⃣ 部署

点击 **"Deploy"** 按钮，等待 2-5 分钟。

### 5️⃣ 完成配置

部署成功后：
1. 复制你的应用 URL（如 `https://tldr-chinese.vercel.app`）
2. 回到环境变量设置
3. 填写 `FRONTEND_URL` 和 `BACKEND_URL`
4. Vercel 会自动重新部署

---

## 已创建的文件

本次配置已自动创建以下文件：

- ✅ `vercel.json` - Vercel 配置文件
- ✅ `api/index.py` - Serverless function 入口
- ✅ `.vercelignore` - 忽略不必要的文件

---

## 常见问题速查

### ❌ API 请求 404

**解决**：确保 `VITE_API_URL` 环境变量正确设置或留空。

### ❌ CORS 错误

**解决**：在 `api/__init__.py` 和 `api/routes.py` 中添加你的 Vercel 域名到 `allowed_origins`。

### ❌ MongoDB 连接失败

**解决**：
1. 检查 `MONGODB_URI` 是否正确
2. 在 MongoDB Atlas 中将 `0.0.0.0/0` 添加到 IP 白名单

### ❌ 环境变量不生效

**解决**：修改环境变量后需要重新部署（手动或推送新的 commit）。

---

## 本地测试

### 模拟 Vercel 环境

```bash
# 安装 Vercel CLI
npm i -g vercel

# 运行本地开发服务器（模拟 Vercel）
vercel dev
```

### 传统开发方式

**前端：**
```bash
npm install
npm run dev
```

**后端：**
```bash
pip install -r requirements.txt
python run.py
```

---

## 使用 CLI 部署（替代方案）

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录
vercel login

# 部署到预览环境
vercel

# 部署到生产环境
vercel --prod
```

---

## 下一步

- 📖 查看 [完整部署指南](./VERCEL_DEPLOYMENT.md)
- 🌐 配置[自定义域名](./VERCEL_DEPLOYMENT.md#自定义域名可选)
- 📊 查看 Vercel Analytics 监控性能
- 🔒 启用 Vercel 防火墙（Pro 功能）

---

## 支持

遇到问题？查看：
- [完整部署文档](./VERCEL_DEPLOYMENT.md)
- [Vercel 官方文档](https://vercel.com/docs)
- [Vercel Discord 社区](https://discord.gg/vercel)

祝部署顺利！🎉

