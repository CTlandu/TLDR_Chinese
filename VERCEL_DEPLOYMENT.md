# Vercel 部署指南

本项目是一个 Vue 3 + Flask 的全栈应用，可以完全部署在 Vercel 上。

## 项目结构说明

```
TLDR_Chinese/
├── src/              # Vue 3 前端代码
├── api/              # Flask 后端 API
│   └── index.py      # Vercel serverless 入口
├── vercel.json       # Vercel 配置文件
└── requirements.txt  # Python 依赖
```

## 部署步骤

### 方式一：通过 Vercel Dashboard（推荐，简单直观）

#### 1. 准备代码仓库
确保代码已推送到 GitHub、GitLab 或 Bitbucket。

```bash
git add .
git commit -m "Add Vercel configuration"
git push origin main
```

#### 2. 连接 Vercel

1. 访问 [https://vercel.com](https://vercel.com)
2. 使用 GitHub 账号登录
3. 点击 **"Add New Project"**
4. 选择你的 `TLDR_Chinese` 仓库
5. 点击 **"Import"**

#### 3. 配置项目

Vercel 会自动检测到：
- ✅ 前端：Vue 3 + Vite
- ✅ 后端：Python Flask

**Build & Development Settings**（通常自动配置，无需修改）：
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

#### 4. 配置环境变量

在 Vercel Dashboard 中，进入项目设置页面，找到 **"Environment Variables"** 部分，添加以下环境变量：

**必需的环境变量：**

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `MONGODB_URI` | MongoDB 连接字符串 | `mongodb+srv://user:pass@cluster.mongodb.net/tldrchinese` |
| `MAILGUN_API_KEY` | Mailgun API 密钥 | `key-xxxxxxxxxxxxx` |
| `MAILGUN_DOMAIN` | Mailgun 域名 | `mg.yourdomain.com` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | `sk-xxxxxxxxxxxxx` |
| `ERNIE_API_KEY` | 百度文心一言 API Key | `your-api-key` |
| `ERNIE_SECRET_KEY` | 百度文心一言 Secret Key | `your-secret-key` |
| `NEWSLETTER_API_KEY` | Newsletter API 密钥 | 自定义一个安全的字符串 |
| `FLASK_ENV` | Flask 环境 | `production` |
| `FRONTEND_URL` | 前端 URL | `https://your-app.vercel.app` |
| `BACKEND_URL` | 后端 URL | `https://your-app.vercel.app` |
| `VITE_API_URL` | 前端 API 地址 | 留空（使用相对路径）或 `https://your-app.vercel.app` |

**注意事项：**
- `FRONTEND_URL` 和 `BACKEND_URL` 在首次部署时可以先留空，部署完成后再填入实际的 Vercel 域名
- 所有环境变量都应该添加到 **Production**、**Preview** 和 **Development** 环境

#### 5. 部署

1. 点击 **"Deploy"** 按钮
2. 等待构建完成（通常 2-5 分钟）
3. 部署成功后会显示你的应用 URL，例如：`https://tldr-chinese.vercel.app`

#### 6. 更新环境变量

部署成功后：
1. 复制你的 Vercel 应用 URL
2. 回到 **Environment Variables** 设置
3. 更新 `FRONTEND_URL` 和 `BACKEND_URL` 为实际的 URL
4. 重新部署（会自动触发）

---

### 方式二：使用 Vercel CLI（适合开发者）

#### 1. 安装 Vercel CLI

```bash
npm install -g vercel
```

#### 2. 登录 Vercel

```bash
vercel login
```

#### 3. 部署项目

在项目根目录运行：

```bash
# 首次部署（会创建项目并部署到预览环境）
vercel

# 部署到生产环境
vercel --prod
```

#### 4. 设置环境变量

使用 CLI 设置环境变量：

```bash
# 设置生产环境变量
vercel env add MONGODB_URI production
vercel env add MAILGUN_API_KEY production
vercel env add MAILGUN_DOMAIN production
# ... 依此类推
```

或者在 Vercel Dashboard 中手动添加（更方便）。

---

## 自定义域名（可选）

### 添加自定义域名

1. 在 Vercel Dashboard 中，进入项目设置
2. 找到 **"Domains"** 部分
3. 点击 **"Add"**
4. 输入你的域名，如 `www.tldrnewsletter.cn`
5. 按照 Vercel 提供的 DNS 配置说明，在你的域名服务商处添加记录：
   - **A 记录** 或 **CNAME 记录**（根据 Vercel 指示）
6. 等待 DNS 传播（可能需要几分钟到几小时）

### DNS 配置示例

假设你使用的是 `tldrnewsletter.cn`：

```
类型: A
名称: @
值: 76.76.21.21

类型: CNAME
名称: www
值: cname.vercel-dns.com
```

---

## 常见问题

### 1. API 请求失败（CORS 错误）

**原因**：后端 CORS 配置中没有包含你的 Vercel 域名。

**解决方案**：更新 `api/__init__.py` 和 `api/routes.py` 中的 `allowed_origins`，添加你的 Vercel 域名：

```python
allowed_origins = [
    "https://your-app.vercel.app",
    "https://www.your-domain.com",
    # ...其他域名
]
```

### 2. MongoDB 连接超时

**原因**：Vercel serverless functions 有 10 秒的执行时间限制。

**解决方案**：
- 确保 MongoDB Atlas 白名单中包含 `0.0.0.0/0`（允许所有 IP）
- 优化数据库查询
- 考虑使用连接池和缓存

### 3. 函数执行时间超限

**原因**：Vercel 免费版函数最多执行 10 秒。

**解决方案**：
- 优化慢查询
- 将长时间任务改为后台任务
- 升级到 Vercel Pro 计划（60 秒限制）

### 4. 静态资源 404

**原因**：`vercel.json` 路由配置不正确。

**解决方案**：确保 `vercel.json` 中的路由顺序正确（已在配置文件中处理）。

### 5. 环境变量不生效

**原因**：环境变量只在构建时或运行时生效，需要重新部署。

**解决方案**：
- 修改环境变量后，手动触发重新部署
- 或者推送一个新的 commit 触发自动部署

---

## 监控和日志

### 查看部署日志

1. 在 Vercel Dashboard 中进入项目
2. 点击 **"Deployments"** 标签
3. 选择一个部署，查看详细日志

### 查看运行时日志

1. 点击 **"Functions"** 标签
2. 选择一个函数（如 `api/index.py`）
3. 查看实时日志和错误信息

### 性能监控

Vercel 提供了内置的性能监控：
- 页面加载时间
- API 响应时间
- 函数执行时间

在项目 Dashboard 的 **"Analytics"** 标签中查看。

---

## 本地开发

### 前端开发

```bash
npm install
npm run dev
```

访问：`http://localhost:5173`

### 后端开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行后端
python run.py
```

访问：`http://localhost:5000`

### 使用 Vercel Dev（推荐）

Vercel CLI 提供了本地开发环境，可以模拟生产环境：

```bash
vercel dev
```

这会同时运行前端和后端，并自动处理路由。

---

## 成本说明

### Vercel 免费版限制

- ✅ 100 GB 带宽/月
- ✅ 无限的网站和 API
- ✅ Serverless Function 执行：100 GB-Hours
- ✅ 10 秒函数执行时间
- ⚠️ 每次部署最多 12,000 个文件

对于大多数个人项目来说，免费版完全足够。

### 如需升级

如果你的项目流量较大或需要更长的函数执行时间，可以考虑：
- **Vercel Pro**：$20/月
  - 1 TB 带宽
  - 60 秒函数执行时间
  - 优先支持

---

## 更新和维护

### 自动部署

连接 GitHub 后，每次推送到主分支都会自动触发部署：

```bash
git add .
git commit -m "Update feature"
git push origin main
```

### 手动部署

如果需要手动部署：

```bash
vercel --prod
```

### 回滚

在 Vercel Dashboard 中：
1. 进入 **"Deployments"**
2. 找到想要回滚到的版本
3. 点击 **"..."** → **"Promote to Production"**

---

## 技术支持

### 官方文档

- [Vercel 文档](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)
- [Vite 部署指南](https://vitejs.dev/guide/static-deploy.html#vercel)

### 社区支持

- [Vercel Discord](https://discord.gg/vercel)
- [Vercel GitHub Discussions](https://github.com/vercel/vercel/discussions)

---

## 安全最佳实践

1. **环境变量**：永远不要在代码中硬编码敏感信息
2. **API 密钥**：定期轮换 API 密钥
3. **CORS**：只允许可信的域名访问 API
4. **MongoDB**：使用强密码，限制 IP 访问（如果可能）
5. **速率限制**：已通过 Flask-Limiter 实现，确保配置得当

---

## 故障排查清单

部署失败时，按以下顺序检查：

- [ ] 所有环境变量都已正确设置
- [ ] `requirements.txt` 包含所有必要的依赖
- [ ] `vercel.json` 配置正确
- [ ] MongoDB 连接字符串正确且可访问
- [ ] 后端代码在本地可以正常运行
- [ ] 前端构建命令 `npm run build` 可以成功执行
- [ ] 检查 Vercel 部署日志中的错误信息

---

祝你部署成功！🚀

