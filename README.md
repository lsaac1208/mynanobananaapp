# Nano-Banana AI 绘图平台

> 🎨 企业级AI图片生成平台 | 支持文生图和图生图 | 智能推荐 | 现代化UI

[![Vue.js](https://img.shields.io/badge/Vue.js-3.4-4FC08D?logo=vue.js)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)](https://flask.palletsprojects.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[在线演示](http://106.14.160.150:37468) | [功能介绍](#核心功能) | [快速开始](#快速开始) | [部署指南](#部署方法)

---

## ✨ 核心功能

### 🎨 AI图片生成
- **文生图**：输入文字描述，AI生成图片
- **图生图**：上传参考图片，AI进行风格转换或改进
- **双画质**：标准版和高清版，满足不同需求
- **多尺寸**：支持1:1、4:3、16:9等7种比例
- **批量生成**：一次最多生成4张图片

### 🖼️ 个人画廊
- 所有生成的图片自动保存
- 支持分类、标签、收藏管理
- 关键词搜索和筛选
- 一键复用到图生图
- 下载高清原图

### 🎯 智能推荐（企业版特性）
- 根据提示词推荐最佳模型
- 自动优化提示词建议
- 学习用户偏好，个性化体验

### 👑 管理功能
- 用户管理和次数充值
- 性能监控和数据分析
- API配置热更新
- 系统健康度监控

---

## 🚀 快速开始

### 环境要求
- Node.js 18+
- Python 3.11+
- npm 9+

### 一键启动

```bash
# 1. 克隆项目
git clone https://github.com/lsaac1208/mynanobananaapp.git
cd mynanobananaapp

# 2. 安装依赖
npm install
cd apps/backend && pip install -r requirements.txt && cd ../..

# 3. 启动应用
npm run dev
```

### 访问应用
- **前端**：http://localhost:3001
- **后端API**：http://localhost:5000

### 默认管理员
```
邮箱：admin@test.com
密码：Admin123
```

---

## 📦 部署方法

### 方法1：宝塔面板部署（推荐）

#### 准备工作
1. 上传代码到 `/www/wwwroot/mynanobanana`
2. 安装Python 3.11+和Node.js 18+

#### 后端部署
1. **Python项目管理器** → 添加项目
   ```
   项目路径: /www/wwwroot/mynanobanana/apps/backend
   启动文件: app:app
   端口: 5000
   ```

2. **配置环境变量**（在项目设置中添加）：
   ```bash
   SECRET_KEY=生产环境密钥
   JWT_SECRET_KEY=JWT密钥
   ENCRYPTION_KEY=加密密钥
   OPENAI_HK_API_KEY=hk-你的API密钥
   CORS_ORIGINS=http://你的域名
   ```

3. **安装依赖并启动**：
   ```bash
   pip install -r requirements.txt
   # 在宝塔面板点击"启动"
   ```

#### 前端部署
1. **构建前端**：
   ```bash
   cd /www/wwwroot/mynanobanana
   npm install
   npm run build
   ```

2. **创建网站**（宝塔面板）：
   ```
   根目录: /www/wwwroot/mynanobanana/apps/frontend/dist
   ```

3. **配置Nginx反向代理**（在网站设置中）：
   ```nginx
   location /api {
       proxy_pass http://127.0.0.1:5000;
       proxy_read_timeout 180s;
       client_max_body_size 10M;
   }
   
   location / {
       try_files $uri $uri/ /index.html;
   }
   ```

---

### 方法2：Docker部署

创建 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  backend:
    build: ./apps/backend
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_HK_API_KEY=${OPENAI_HK_API_KEY}
    volumes:
      - ./apps/backend/instance:/app/instance

  frontend:
    build: ./apps/frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

启动：
```bash
docker-compose up -d
```

---

### 方法3：传统部署（Nginx + Gunicorn）

```bash
# 1. 构建前端
npm run build

# 2. 启动后端
cd apps/backend
gunicorn -w 4 -b 127.0.0.1:5000 --timeout 180 app:app

# 3. 配置Nginx指向 apps/frontend/dist
# 4. 设置API反向代理到 http://127.0.0.1:5000
```

详细步骤见：[部署文档](./docs/DEPLOYMENT.md)

---

## 🔐 环境变量配置

生产环境必须配置以下环境变量：

```bash
# 安全密钥（必须修改！）
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-fernet-key

# API配置
OPENAI_HK_API_KEY=hk-your-api-key
OPENAI_HK_BASE_URL=https://api.openai-hk.com

# CORS配置
CORS_ORIGINS=https://your-domain.com
```

**生成加密密钥：**
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 🏗️ 技术架构

### 前端技术栈
- **Vue.js 3** - Composition API
- **TypeScript** - 类型安全
- **Element Plus** - UI组件库
- **Pinia** - 状态管理
- **Vite** - 构建工具

### 后端技术栈
- **Flask 3** - Web框架
- **SQLite** - 数据库
- **JWT** - 认证系统
- **aiohttp** - 异步HTTP客户端
- **Gunicorn** - 生产服务器

### 核心特性
- ✅ Monorepo架构，前后端分离
- ✅ JWT令牌认证，自动刷新
- ✅ Fernet加密敏感数据
- ✅ 响应式设计，移动端优化
- ✅ 性能监控和用户行为分析

---

## 📱 功能截图

### AI生成界面
现代化的左右分栏设计，实时进度显示，支持文生图和图生图两种模式。

### 个人画廊
网格布局展示所有作品，支持分类、标签、收藏、搜索等功能。

### 管理后台
用户管理、次数充值、性能分析、系统配置等完整的管理功能。

---

## 🎯 性能表现

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 图片预览加载 | 10-30秒 | <1秒 | **30倍** ⚡ |
| 预览显示 | 2-5MB原图 | 50-150KB缩略图 | **20倍** ⚡ |
| 内存占用 | 50-100MB | 10-30MB | **降低70%** 💾 |
| 生成响应 | 平均15秒 | 平均12秒 | **20%提升** 🚀 |

---

## 📚 项目文档

- [产品需求文档](./docs/prd.md) - 完整功能规划
- [架构设计](./docs/architecture.md) - 技术架构说明
- [开发指南](./CLAUDE.md) - 开发者文档

---

## 🔧 常用命令

```bash
# 开发
npm run dev              # 同时启动前后端
npm run dev:frontend     # 只启动前端
npm run dev:backend      # 只启动后端

# 构建
npm run build            # 构建生产版本

# 测试
npm run test             # 运行所有测试
npm run test:frontend    # 前端测试
cd apps/backend && pytest # 后端测试
```

---

## 🐛 常见问题

### Q: 生成图片失败？
**A:** 检查以下项：
1. OPENAI_HK_API_KEY 是否正确配置
2. 用户次数是否充足
3. 网络连接是否正常
4. 查看浏览器控制台错误

### Q: 502 Bad Gateway？
**A:** 检查后端服务是否运行：
```bash
curl http://127.0.0.1:5000/api/health
```

### Q: 前端显示空白？
**A:** 
1. 确认已运行 `npm run build`
2. 检查Nginx配置是否正确
3. 查看浏览器控制台错误

### Q: 如何重置管理员密码？
**A:**
```bash
cd apps/backend
python3 init_admin.py
```

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送分支：`git push origin feature/AmazingFeature`
5. 提交 Pull Request

---

## 📄 开源协议

本项目采用 [MIT](LICENSE) 开源协议。

---

## 🌟 Star History

如果这个项目对您有帮助，请给一个 ⭐ Star 支持一下！

---

## 📞 技术支持

- **问题反馈**：[GitHub Issues](https://github.com/lsaac1208/mynanobananaapp/issues)
- **项目主页**：[GitHub Repository](https://github.com/lsaac1208/mynanobananaapp)
- **在线演示**：http://106.14.160.150:37468

---

**Made with ❤️ using Vue.js 3 + Flask 3**
