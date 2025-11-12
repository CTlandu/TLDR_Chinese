# 本地开发指南

本文档介绍如何在本地运行 TLDR Chinese 全栈项目（Vue 3 前端 + Flask 后端）。

## 📋 前置要求

确保已安装：
- **Node.js** ≥ 18.0.0
- **Python** ≥ 3.8
- **pip**（Python 包管理器）
- **MongoDB**（可选，使用云端 MongoDB Atlas）

---

## 🚀 快速开始

### 方法一：使用单独终端运行（推荐）

#### 1️⃣ 安装依赖

**前端依赖（Vue 3）：**
```bash
npm install
```

**后端依赖（Flask）：**
```bash
pip install -r requirements.txt
```

#### 2️⃣ 配置环境变量

复制并编辑 `.env.local` 文件：
```bash
cp .env.local .env
```

编辑 `.env` 文件，填入你的实际配置：
```env
# MongoDB 配置
MONGODB_URI=mongodb+srv://your_username:your_password@cluster.mongodb.net/

# API Keys（如果需要测试完整功能）
DEEPSEEK_API_KEY=your_key_here
MAILGUN_API_KEY=your_key_here
MAILGUN_DOMAIN=your_domain_here

# 本地开发 URLs
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:5000
```

#### 3️⃣ 启动后端服务器（终端1）

```bash
# 方式1：使用 Flask 开发服务器
python run.py

# 方式2：使用 Flask CLI
flask run --port=5000 --debug
```

后端应该运行在：`http://localhost:5000`

#### 4️⃣ 启动前端开发服务器（终端2）

打开**新的终端窗口**，运行：
```bash
npm run dev
```

前端应该运行在：`http://localhost:5173`

#### 5️⃣ 访问应用

在浏览器打开：`http://localhost:5173`

---

## 🔧 详细配置说明

### 后端配置（Flask）

**文件位置：** `run.py`

```python
# run.py 已经配置好，直接运行即可
python run.py
```

**API 端点测试：**
```bash
# 测试后端是否运行
curl http://localhost:5000/api/hello

# 测试订阅者数量
curl http://localhost:5000/api/subscriber-count
```

### 前端配置（Vue 3）

**环境变量：** 创建 `.env.development` 文件：
```env
# 本地开发时，前端访问本地后端
VITE_API_URL=http://localhost:5000
```

**或者使用相对路径（需要配置代理）：**

在 `vite.config.js` 中添加代理配置：
```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
})
```

---

## 📂 项目结构

```
TLDR_Chinese/
├── api/                    # Flask 后端
│   ├── __init__.py        # Flask 应用初始化
│   ├── routes.py          # API 路由
│   ├── models/            # 数据模型
│   └── services/          # 业务逻辑
├── src/                   # Vue 3 前端
│   ├── components/        # Vue 组件
│   ├── views/             # 页面视图
│   ├── router/            # 路由配置
│   ├── composables/       # Composition API
│   └── main.js            # 入口文件
├── run.py                 # 后端启动脚本
├── config.py              # 后端配置
├── requirements.txt       # Python 依赖
├── package.json           # Node.js 依赖
└── vite.config.js         # Vite 配置
```

---

## 🛠️ 常用命令

### 前端命令
```bash
# 安装依赖
npm install

# 开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 后端命令
```bash
# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python run.py

# 运行测试脚本
python scripts/test_mongodb.py
python scripts/test_mailgun.py
```

---

## 🐛 常见问题

### 1. 前端无法连接后端

**问题：** 浏览器控制台显示 CORS 错误或连接失败

**解决方案：**
- 确保后端正在运行：`http://localhost:5000`
- 检查 `.env.development` 中的 `VITE_API_URL` 配置
- 查看后端日志确认 CORS 配置正确

### 2. MongoDB 连接失败

**问题：** 后端启动时报 MongoDB 连接错误

**解决方案：**
- 检查 `.env` 文件中的 `MONGODB_URI` 是否正确
- 确认 MongoDB Atlas IP 白名单包含你的 IP
- 测试连接：`python scripts/test_mongodb.py`

### 3. 端口被占用

**问题：** 端口 5000 或 5173 已被使用

**解决方案：**
```bash
# 查找并关闭占用端口的进程
# macOS/Linux:
lsof -ti:5000 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# 或者更改端口
# 后端：python run.py --port=5001
# 前端：在 vite.config.js 中修改端口
```

### 4. Python 依赖安装失败

**问题：** pip install 报错

**解决方案：**
```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 5. 前端构建失败

**问题：** npm run build 报错

**解决方案：**
```bash
# 清除缓存并重新安装
rm -rf node_modules package-lock.json
npm install

# 使用 legacy peer deps
npm install --legacy-peer-deps
```

---

## 🔍 调试技巧

### 前端调试
- 使用 Vue DevTools 浏览器扩展
- 检查浏览器控制台（F12）
- 查看 Network 标签页检查 API 请求

### 后端调试
- 查看终端输出的日志
- 使用 Postman 或 curl 测试 API
- 检查 Flask 调试模式是否启用

### API 测试示例
```bash
# 测试获取最新文章
curl http://localhost:5000/api/latest-articles

# 测试订阅功能
curl -X POST http://localhost:5000/api/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

---

## 📝 开发工作流

1. **创建新功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **开发并测试**
   - 前端：修改 `src/` 中的文件
   - 后端：修改 `api/` 中的文件
   - 实时预览：两个服务器都支持热重载

3. **提交更改**
   ```bash
   git add .
   git commit -m "描述你的更改"
   git push origin feature/your-feature-name
   ```

4. **部署到 Vercel**
   - 推送到 `master` 分支会自动触发 Vercel 部署
   - 推送到其他分支会创建预览部署

---

## 🎯 环境变量说明

### 必需的环境变量
- `MONGODB_URI` - MongoDB 连接字符串
- `FRONTEND_URL` - 前端 URL（用于 CORS 和重定向）
- `BACKEND_URL` - 后端 URL（用于邮件链接等）

### 可选的环境变量（用于完整功能）
- `DEEPSEEK_API_KEY` - DeepSeek AI 翻译
- `MAILGUN_API_KEY` - 邮件发送
- `MAILGUN_DOMAIN` - Mailgun 域名
- `NEWSLETTER_API_KEY` - Newsletter API
- `ERNIE_API_KEY` - 文心一言 API
- `ERNIE_SECRET_KEY` - 文心一言密钥

---

## 📚 相关文档

- [Vercel 部署指南](./VERCEL_DEPLOYMENT.md)
- [Vercel 快速开始](./VERCEL_QUICKSTART.md)
- [Vercel 检查清单](./VERCEL_CHECKLIST.md)

---

## 💡 提示

- 开发时保持两个终端窗口打开（前端 + 后端）
- 使用 Git 管理代码，经常提交
- 测试完整功能前，确保配置了所有必需的 API keys
- 本地开发使用 `http://localhost`，生产环境使用 HTTPS

---

## 🆘 需要帮助？

如果遇到问题：
1. 查看本文档的"常见问题"部分
2. 检查终端和浏览器控制台的错误信息
3. 查看项目的 GitHub Issues
4. 联系项目维护者

祝你开发愉快！🚀

