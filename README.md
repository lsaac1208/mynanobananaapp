# Nano-Banana AI绘图应用

> 基于Vue.js和Flask的企业级AI图片生成平台 | 完整的配置管理 | 智能推荐系统 | 用户行为分析

[![Vue.js](https://img.shields.io/badge/Vue.js-3.4-4FC08D?logo=vue.js)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)](https://flask.palletsprojects.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## ✨ 核心特性

### 🎨 AI图片生成
- **文生图**: 输入文本提示词生成图片，支持nano-banana系列模型
- **图生图**: 上传参考图片+提示词生成新图片
- **模型选择**: nano-banana (12s), nano-banana-hd (28s)
- **尺寸支持**: 1:1, 4:3, 16:9等多种比例
- **次数管理**: 每次生成消耗1次数，失败自动退还

### 🔐 企业级认证系统
- JWT认证系统（2小时访问令牌，30天刷新令牌）
- 防暴力破解（失败5次后锁定账户15分钟）
- 令牌黑名单机制（退出登录后令牌立即失效）
- 密码强度验证（至少8位，包含大小写字母和数字）

### ⚙️ 配置组管理系统
- **灵活配置**: 支持创建多个API配置组
- **热更新**: 切换配置无需重启服务
- **安全存储**: API密钥使用Fernet加密（AES-128-CBC + HMAC-SHA256）
- **启用互斥**: 同时只能启用一个配置组
- **保护机制**: 已启用的配置组无法删除

### 🖼️ 个人画廊系统
- 网格/列表视图切换，响应式适配
- 作品分类管理（艺术、摄影、设计等）
- 标签系统和关键词搜索
- 收藏功能和统计信息
- 图片查看、下载、删除

### 🧠 智能推荐系统 (Phase 2)
- **AI驱动推荐**: 基于用户行为的智能化体验优化
- **模型推荐**: 根据提示词特征推荐最适合模型
- **提示词优化**: 自动提示词增强建议
- **相似作品**: 基于语义的智能作品关联
- **偏好学习**: 自动学习用户使用模式

### 📊 数据分析仪表板 (Phase 2)
- **性能监控**: 生成时间趋势、错误率监控、负载分析
- **用户行为**: 活跃时段、偏好模型、使用模式分析
- **系统洞察**: 健康度评估、智能优化建议
- **统计可视化**: 用户增长、生成统计、运营指标

### 👥 管理员功能
- 用户搜索（支持邮箱模糊匹配）
- 次数充值（为用户添加生图次数）
- 用户详情查看（作品统计、使用数据）
- 系统配置管理（API配置组切换）
- 安全审计日志（操作记录追踪）

### 📱 响应式设计
- 完美适配桌面（1200px+）、平板（768px）、移动端（430px）
- 卡片式操作面板，现代化交互动画
- 渐变背景、悬停效果、颜色编码图标

## 🚀 快速开始

### 环境要求

- **Node.js** 18+ 和 npm 9+
- **Python** 3.11+
- **操作系统**: macOS, Linux, Windows (WSL2)

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/yourname/mynanobananaapp.git
cd mynanobananaapp

# 安装前端依赖
npm install

# 安装后端依赖
cd apps/backend
pip install -r requirements.txt
cd ../..
```

### 配置环境变量

**开发环境**可以使用默认配置（已在`config.py`中预置）。

**生产环境必须**设置以下环境变量：

```bash
# 生产环境必需的环境变量
export SECRET_KEY="your-secret-key-change-in-production"
export JWT_SECRET_KEY="your-jwt-secret-key"
export ENCRYPTION_KEY="your-fernet-encryption-key"  # 使用cryptography.fernet生成
export OPENAI_HK_API_KEY="hk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export CORS_ORIGINS="https://your-domain.com"
```

### 启动开发环境

```bash
# 方式1: 同时启动前后端（推荐）
npm run dev

# 方式2: 分别启动
npm run dev:frontend  # 前端 http://localhost:3001
npm run dev:backend   # 后端 http://localhost:5000
```

访问应用:
- **前端界面**: http://localhost:3001
- **后端API**: http://localhost:5000
- **健康检查**: http://localhost:5000/health

### 管理员账户

系统预置管理员账户（仅ID=1用户拥有管理权限）:

```
邮箱: admin@test.com
密码: Admin123
```

**管理员功能入口**:
- 用户管理: http://localhost:3001/admin/users
- 数据仪表板: http://localhost:3001/admin/dashboard
- 系统设置: http://localhost:3001/admin/settings

## 🏗️ 项目架构

### Monorepo结构

```
mynanobananaapp/
├── apps/
│   ├── frontend/              # Vue.js 3 + TypeScript前端应用
│   │   ├── src/
│   │   │   ├── views/         # 页面组件
│   │   │   │   ├── auth/      # LoginView.vue, RegisterView.vue
│   │   │   │   ├── app/       # Generate.vue, Gallery.vue, Profile.vue
│   │   │   │   └── admin/     # UserManagement.vue, Dashboard.vue, SystemSettings.vue
│   │   │   ├── components/    # 可复用组件
│   │   │   │   ├── common/    # Header.vue, Sidebar.vue等
│   │   │   │   └── layouts/   # AppMain.vue, AdminLayout.vue
│   │   │   ├── services/      # API服务层
│   │   │   │   ├── api.ts     # 核心API客户端（userApi, galleryApi）
│   │   │   │   └── adminApi.ts # 管理员API客户端
│   │   │   ├── stores/        # Pinia状态管理
│   │   │   │   ├── auth.ts    # 认证状态
│   │   │   │   └── gallery.ts # 画廊状态
│   │   │   ├── router/        # Vue Router配置
│   │   │   │   └── index.ts   # 路由定义和权限守卫
│   │   │   └── types/         # TypeScript类型定义
│   │   └── vite.config.ts
│   │
│   └── backend/               # Flask 3 + Python后端API
│       ├── app/
│       │   ├── views/         # API蓝图（Flask Blueprints）
│       │   │   ├── auth.py    # 认证接口 (register, login, logout, refresh)
│       │   │   ├── user.py    # 用户接口 (me, update_password)
│       │   │   ├── generate.py # AI生成接口 (text-to-image, image-to-image, system-insights)
│       │   │   ├── gallery.py # 画廊接口 (CRUD, 搜索, 统计)
│       │   │   ├── admin.py   # 管理员接口 (add-credits, search, user-details)
│       │   │   ├── config_groups.py # 配置组接口 (CRUD, toggle)
│       │   │   └── recommendations.py # 推荐接口 (smart-suggestions)
│       │   ├── services/      # 业务逻辑层
│       │   │   └── ai_generator.py # AIGeneratorService（异步调用nano-banana API）
│       │   ├── utils/         # 工具函数
│       │   │   ├── response.py # APIResponse统一响应格式
│       │   │   ├── encryption.py # ConfigEncryption加密工具
│       │   │   └── permissions.py # 权限验证装饰器
│       │   ├── database.py    # 数据库连接和管理
│       │   └── __init__.py    # 应用工厂模式
│       ├── migrations/        # 数据库迁移脚本
│       ├── instance/          # SQLite数据库文件
│       │   └── database.db    # 生产数据库（20张表）
│       ├── config.py          # 应用配置
│       ├── requirements.txt   # Python依赖
│       └── run.py             # 启动入口
│
├── packages/
│   └── shared-types/          # 共享TypeScript类型定义
│
├── docs/                      # 项目文档
│   ├── prd.md                 # 产品需求文档
│   ├── architecture.md        # 架构设计文档
│   ├── GALLERY_OPTIMIZATION_REPORT.md # 画廊优化文档
│   ├── DASHBOARD_USER_COUNT_FIX.md # 仪表板修复文档
│   └── SYSTEM_SETTINGS_IMPLEMENTATION.md # 系统设置实施文档
│
├── package.json               # 工作空间配置
├── CLAUDE.md                  # Claude Code指令文档（AI助手上下文）
└── README.md                  # 本文件
```

### 技术栈

#### 前端技术
- **Vue.js 3.4** - 渐进式JavaScript框架，Composition API
- **TypeScript 5.3** - 类型安全的JavaScript超集
- **Vite 5** - 快速的前端构建工具和开发服务器
- **Element Plus** - Vue 3企业级UI组件库
- **Pinia** - Vue官方状态管理库
- **Vue Router** - Vue官方路由管理
- **Axios** - HTTP客户端（120s超时，自动刷新令牌）

#### 后端技术
- **Flask 3.0** - 轻量级Python Web框架
- **SQLite3** - 轻量级关系数据库（直接集成，无ORM）
- **Flask-JWT-Extended** - JWT认证扩展
- **Flask-CORS** - 跨域资源共享支持
- **aiohttp** - 异步HTTP客户端（调用nano-banana API，180s超时）
- **cryptography** - Fernet加密（保护API密钥）
- **werkzeug.security** - 密码哈希工具

#### 开发工具
- **Vitest** - 快速的单元测试框架
- **Pytest** - Python测试框架
- **Playwright** - 端到端测试
- **ESLint** - JavaScript/TypeScript代码检查
- **Flake8** - Python代码检查

## 📊 数据库架构

### 核心表结构 (20张表)

#### 1. 用户认证表

**users** - 用户基础信息
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    credits INTEGER NOT NULL DEFAULT 0,  -- 可用生成次数
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at DATETIME,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until DATETIME
);
```

**jwt_blacklist** - JWT令牌黑名单
```sql
CREATE TABLE jwt_blacklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jti TEXT NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. 配置组表 (Phase 3)

**config_groups** - API配置组
```sql
CREATE TABLE config_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 0,  -- 同时只能有一个active
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER
);
```

**system_settings** - 系统配置项
```sql
CREATE TABLE system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    key TEXT NOT NULL,  -- 'openai_hk_base_url' 或 'openai_hk_api_key'
    value TEXT,         -- API Key使用Fernet加密存储
    is_encrypted BOOLEAN NOT NULL DEFAULT 0,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES config_groups (id) ON DELETE CASCADE,
    UNIQUE (group_id, key)
);
```

#### 3. 作品表

**creations** - AI生成作品
```sql
CREATE TABLE creations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    image_url TEXT NOT NULL,
    model_used TEXT NOT NULL,
    size TEXT NOT NULL,
    generation_time REAL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_favorite BOOLEAN NOT NULL DEFAULT 0,
    tags TEXT,
    category TEXT,
    is_public BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

#### 4. Phase 2 企业级分析表 (11张表)

**user_sessions** - 用户会话跟踪
- 实时监控用户活动、页面访问、生成次数

**performance_metrics** - 性能指标收集
- AI生成时间、API响应时间、系统负载监控

**user_behaviors** - 用户行为分析
- 操作模式识别、偏好学习、使用时段分析

**daily_stats** - 每日统计汇总
- 用户增长、生成成功率、系统健康度追踪

**user_preferences** - 用户偏好配置
- 个性化设置自动学习、偏好模式识别

**smart_recommendations** - 智能推荐记录
- 模型推荐、提示词优化、尺寸建议

**prompt_optimizations** - 提示词优化历史
- 自动提示词增强、质量关键词添加

**creation_similarity** - 相似作品关联
- 基于语义的智能作品关联和发现

**recommendation_analytics** - 推荐效果分析
- 接受率统计、有效性评估、持续优化

**recommendation_feedback** - 推荐反馈记录
- 用户对推荐的反馈和评价

**user_recommendation_stats** - 用户推荐统计
- 每个用户的推荐效果统计

完整数据库架构详见 [CLAUDE.md](./CLAUDE.md#数据库结构)

## 🎨 核心功能

### 1. 用户认证系统 ✅

**功能特性**:
- 邮箱密码注册和登录
- JWT令牌认证（2小时访问令牌，30天刷新令牌）
- 自动令牌刷新机制
- 密码强度验证（至少8位，包含大小写字母和数字）
- 防暴力破解（失败5次后锁定账户15分钟）
- 令牌黑名单和安全退出

**技术实现**:
- Flask-JWT-Extended
- werkzeug.security密码哈希
- SQLite用户表和JWT黑名单表

### 2. AI图片生成 ✅

**功能特性**:
- **文生图**: 输入文本提示词生成图片
- **图生图**: 上传参考图片+提示词生成新图片
- **模型选择**: nano-banana (约12s), nano-banana-hd (约28s)
- **尺寸支持**: 1:1, 4:3, 16:9等多种比例
- **次数管理**: 每次生成消耗1次数，失败自动退还
- **进度指示**: 实时生成状态、服务器负载显示、智能时间预估
- **错误处理**: 超时重试、降级策略、用户友好提示

**技术实现**:
- aiohttp异步调用nano-banana API
- AIGeneratorService业务逻辑层
- 前端120s超时，后端180s超时
- 智能重试机制和错误恢复

**性能数据**:
- nano-banana: 平均生成时间 ~12秒
- nano-banana-hd: 平均生成时间 ~28秒
- 超时后75.6%性能提升（从49s降至12s）

### 3. 画廊管理系统 ✅

**功能特性**:
- 网格/列表视图切换，响应式适配
- 作品分类管理（艺术、摄影、设计、抽象、其他）
- 标签系统和关键词搜索
- 收藏功能和统计信息
- 图片查看、下载、删除
- 分页支持（每页20条）

**技术实现**:
- Element Plus卡片和图片组件
- 完整的CRUD API
- fit="contain"完整图片显示（已修复裁剪问题）
- 分层预览策略（缩略图→对话框→全屏预览）

**最近修复**:
- ✅ 图片裁剪问题（fit="cover" → fit="contain"）
- ✅ 双重图片查看器冲突（移除缩略图的preview属性）
- ✅ 对话框宽度优化（80% → 90%）

### 4. 智能推荐系统 ✅ (Phase 2)

**功能特性**:
- **智能提示词优化**: 基于最佳实践的自动提示词增强建议
- **模型智能推荐**: 根据提示词特征和用户历史推荐最适合模型
- **尺寸智能建议**: 基于内容类型和用户偏好的尺寸推荐
- **用户偏好学习**: 自动学习用户使用模式，个性化推荐体验
- **推荐效果追踪**: 接受率、有效性评分、持续优化机制

**技术实现**:
- 6个数据库表支持推荐系统
- AI驱动的推荐算法
- 用户偏好自动学习
- 推荐效果分析和优化

### 5. 性能监控系统 ✅ (Phase 2)

**功能特性**:
- **用户会话跟踪**: 实时监控用户活动、页面访问、生成次数
- **性能指标收集**: AI生成时间、API响应时间、系统负载监控
- **用户行为分析**: 操作模式识别、偏好学习、使用时段分析
- **每日统计汇总**: 用户增长、生成成功率、系统健康度追踪

**技术实现**:
- 11个分析表支持性能监控
- 实时数据收集和分析
- 管理员数据仪表板可视化

**最近修复** (2025-10-01):
- ✅ 仪表板用户统计错误（显示7个用户实际2个）
- ✅ API返回系统级统计而非用户级统计
- ✅ 数据语义混淆修复（用户数 vs 作品数）

### 6. 管理员功能 ✅

**功能特性**:
- **用户管理**: 搜索用户（邮箱模糊匹配）、查看详情、用户统计
- **次数充值**: 为用户添加生图次数，包含详细操作日志
- **数据仪表板**: 系统洞察、性能分析、用户行为可视化
- **系统设置**: API配置组管理、配置热更新、连接测试
- **权限控制**: 基于用户ID的严格权限验证（仅ID=1）

**技术实现**:
- AdminLayout专用布局组件
- 管理员路由保护和权限守卫
- 完整的管理员API端点

### 7. 配置管理系统 ✅ (Phase 3)

**功能特性**:
- **配置组管理**: 创建、启用、禁用、删除API配置组
- **热更新**: 切换配置无需重启服务
- **安全存储**: API密钥使用Fernet加密（AES-128-CBC + HMAC-SHA256）
- **启用互斥**: 同时只能启用一个配置组
- **保护机制**: 已启用的配置组无法删除
- **前端脱敏**: API Key展示为 `hk-****...****` 格式

**技术实现**:
- 2个数据库表：config_groups, system_settings
- ConfigEncryption加密工具类
- 基于Flask SECRET_KEY派生Fernet加密密钥
- AIGeneratorService每次生成前重新加载配置

## 📡 API文档

### 认证接口

- `POST /api/register` - 用户注册
  - 请求体: `{ email, password }`
  - 响应: `{ success, message, data: { user } }`

- `POST /api/login` - 用户登录
  - 请求体: `{ email, password }`
  - 响应: `{ success, data: { access_token, refresh_token, user } }`

- `POST /api/logout` - 用户登出
  - Headers: `Authorization: Bearer <token>`
  - 响应: `{ success, message }`

- `POST /api/refresh` - 刷新JWT令牌
  - Headers: `Authorization: Bearer <refresh_token>`
  - 响应: `{ success, data: { access_token } }`

- `GET /api/check-token` - 验证令牌有效性
  - Headers: `Authorization: Bearer <token>`
  - 响应: `{ success, data: { valid: true } }`

### 用户接口

- `GET /api/users/me` - 获取当前用户信息
  - Headers: `Authorization: Bearer <token>`
  - 响应: `{ success, data: { user: { id, email, credits, ... } } }`

- `PUT /api/users/me/password` - 修改密码
  - Headers: `Authorization: Bearer <token>`
  - 请求体: `{ old_password, new_password }`
  - 响应: `{ success, message }`

### AI生成接口

- `POST /api/generate/text-to-image` - 文生图
  - Headers: `Authorization: Bearer <token>`
  - 请求体: `{ prompt, model, size }`
  - 响应: `{ success, data: { image_url, creation_id, generation_time } }`

- `POST /api/generate/image-to-image` - 图生图
  - Headers: `Authorization: Bearer <token>`
  - 请求体: `FormData { prompt, model, size, image }`
  - 响应: `{ success, data: { image_url, creation_id, generation_time } }`

- `GET /api/generate/models` - 获取可用模型列表
  - 响应: `{ success, data: { models: [...], sizes: [...] } }`

### 画廊接口

- `GET /api/gallery` - 获取用户作品
  - Headers: `Authorization: Bearer <token>`
  - 查询参数: `page, per_page, category, is_favorite, search`
  - 响应: `{ success, data: { creations: [...], total, page, per_page } }`

- `DELETE /api/gallery/:id` - 删除作品
  - Headers: `Authorization: Bearer <token>`
  - 响应: `{ success, message }`

- `PUT /api/gallery/:id/favorite` - 更新收藏状态
  - Headers: `Authorization: Bearer <token>`
  - 请求体: `{ is_favorite }`
  - 响应: `{ success, data: { is_favorite } }`

- `PUT /api/gallery/:id/tags` - 更新作品标签
  - Headers: `Authorization: Bearer <token>`
  - 请求体: `{ tags }`
  - 响应: `{ success, data: { tags } }`

- `GET /api/gallery/stats` - 获取统计信息
  - Headers: `Authorization: Bearer <token>`
  - 响应: `{ success, data: { total, favorites, categories: [...] } }`

### 管理员接口

- `POST /api/admin/add-credits` - 为用户添加次数
  - Headers: `Authorization: Bearer <token>`（仅ID=1）
  - 请求体: `{ user_id, credits }`
  - 响应: `{ success, message, data: { new_credits } }`

- `GET /api/admin/users/search` - 搜索用户
  - Headers: `Authorization: Bearer <token>`（仅ID=1）
  - 查询参数: `query`（支持邮箱模糊匹配，为空返回所有用户）
  - 响应: `{ success, data: { users: [...] } }`

- `GET /api/admin/users/:id` - 获取用户详情
  - Headers: `Authorization: Bearer <token>`（仅ID=1）
  - 响应: `{ success, data: { user, stats: { ... } } }`

- `GET /api/admin/config-groups` - 获取所有配置组
  - Headers: `Authorization: Bearer <token>`（仅ID=1）
  - 响应: `{ success, data: { config_groups: [...] } }`

- `POST /api/admin/config-groups` - 创建配置组
  - Headers: `Authorization: Bearer <token>`（仅ID=1）
  - 请求体: `{ name, description, base_url, api_key }`
  - 响应: `{ success, data: { config_group } }`

- `PUT /api/admin/config-groups/:id/toggle` - 切换配置启用状态
  - Headers: `Authorization: Bearer <token>`（仅ID=1）
  - 响应: `{ success, message }`

- `DELETE /api/admin/config-groups/:id` - 删除配置组
  - Headers: `Authorization: Bearer <token>`（仅ID=1）
  - 响应: `{ success, message }`

### 分析接口 (Phase 2)

- `GET /api/analytics/performance` - 系统性能分析
  - Headers: `Authorization: Bearer <token>`（仅ID=1）
  - 响应: 生成时间趋势、错误率、负载分析

- `GET /api/analytics/user-behavior` - 用户行为分析
  - Headers: `Authorization: Bearer <token>`（仅ID=1）
  - 响应: 活跃时段、偏好模型、使用模式

- `GET /api/analytics/system-insights` - 系统综合洞察
  - Headers: `Authorization: Bearer <token>`（仅ID=1）
  - 响应: 用户统计、作品统计、性能洞察、推荐统计

- `GET /api/analytics/daily-stats` - 每日统计数据
  - Headers: `Authorization: Bearer <token>`（仅ID=1）
  - 响应: 每日用户增长、生成统计、运营指标

### 推荐接口 (Phase 2)

- `POST /api/recommendations/smart-suggestions` - 获取智能建议
  - Headers: `Authorization: Bearer <token>`
  - 请求体: `{ prompt, current_model?, current_size? }`
  - 响应: 模型推荐、提示词优化、尺寸建议

- `GET /api/recommendations/user-preferences` - 获取用户偏好
  - Headers: `Authorization: Bearer <token>`
  - 响应: 用户偏好配置

- `POST /api/recommendations/learn-preferences` - 学习用户偏好
  - Headers: `Authorization: Bearer <token>`
  - 请求体: `{ action, data }`
  - 响应: 学习结果

完整API规范详见 [CLAUDE.md](./CLAUDE.md#api接口结构)

## 🔐 安全特性

### 认证与授权
- ✅ JWT访问令牌（2小时有效期）和刷新令牌（30天）
- ✅ 令牌黑名单机制（退出登录后令牌立即失效）
- ✅ 密码强度验证（至少8位，包含大小写字母和数字）
- ✅ 防暴力破解（失败5次后锁定账户15分钟）
- ✅ 管理员权限严格验证（仅ID=1用户）

### 数据安全
- ✅ 密码哈希存储（werkzeug.security）
- ✅ API密钥Fernet加密（AES-128-CBC + HMAC-SHA256）
- ✅ 外键约束强制执行（`PRAGMA foreign_keys = ON`）
- ✅ WAL模式提升并发性能和数据一致性
- ✅ 前端API Key脱敏显示（`hk-****...****`）

### 生产环境安全
- ✅ 强制环境变量配置（SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY）
- ✅ CORS配置限制（默认只允许localhost:3000和3001）
- ✅ 安全审计日志（管理员操作记录追踪）
- ✅ 生产环境变量验证（启动时检查必需配置）

### 待实施
- ⏳ API速率限制（防止滥用）
- ⏳ 输入验证增强（XSS、SQL注入防护）
- ⏳ OWASP安全合规检查

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
npm run test

# 前端单元测试
npm run test:frontend

# 后端单元测试
cd apps/backend && pytest

# E2E测试
npm run test:e2e
```

### 测试覆盖率
- 前端单元测试: 目标 80%+
- 后端单元测试: 目标 80%+
- E2E测试: 核心用户流程覆盖

### 手动测试脚本

项目包含多个Shell脚本用于手动测试：

```bash
# 完整系统功能测试
./test_api_decrypt.py         # 测试API加密解密
./test_crud_final.sh           # 测试CRUD操作
./test_settings_full_flow.sh   # 测试系统设置完整流程（12项测试）
./verify_settings_fix.sh       # 验证设置修复
```

## 📦 部署

### 构建生产版本

```bash
# 构建前端
npm run build

# 构建产物位于 apps/frontend/dist/
```

### 生产环境部署

#### 使用Gunicorn + Nginx

1. **安装Gunicorn**:
```bash
cd apps/backend
pip install gunicorn
```

2. **启动Gunicorn**:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 180 run:app
```

3. **配置Nginx**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/apps/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 180s;
    }
}
```

#### 环境变量配置

生产环境**必须**设置以下环境变量：
```bash
# 安全密钥（必须修改）
SECRET_KEY=<your-secret-key>
JWT_SECRET_KEY=<your-jwt-secret>
ENCRYPTION_KEY=<fernet-key>

# API配置（可选，可通过配置组管理）
OPENAI_HK_API_KEY=<api-key>
OPENAI_HK_BASE_URL=https://api.openai-hk.com

# CORS配置
CORS_ORIGINS=https://your-domain.com

# 数据库配置（可选）
DATABASE_PATH=/path/to/database.db
```

#### 数据库初始化

```bash
cd apps/backend

# 运行数据库迁移
sqlite3 instance/database.db < migrations/add_role_system.sql

# 创建管理员用户（如果需要）
python -c "from app import create_app; app = create_app(); ..."
```

## 🛠️ 开发指南

### 代码规范

#### 前端
- 使用ESLint + TypeScript进行代码检查
- 组件命名采用PascalCase
- 使用Composition API编写Vue组件
- 优先使用TypeScript类型定义
- API调用统一使用services层

#### 后端
- 遵循PEP 8编码规范
- 使用Flake8进行代码检查
- 蓝图模式组织API路由
- 使用类型提示 (Type Hints)
- 统一使用APIResponse返回响应

### 添加新功能

#### 添加新的API接口
1. 在 `apps/backend/app/views/` 创建或修改蓝图文件
2. 使用统一的 `APIResponse` 工具返回响应
3. 添加JWT装饰器保护需要认证的路由
4. 在前端 `services/api.ts` 或 `services/adminApi.ts` 添加对应方法

**示例**:
```python
# apps/backend/app/views/example.py
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.response import APIResponse

example_bp = Blueprint('example', __name__, url_prefix='/api/example')

@example_bp.route('/hello', methods=['GET'])
@jwt_required()
def hello():
    user_id = get_jwt_identity()
    return APIResponse.success(data={'message': f'Hello, user {user_id}!'})
```

#### 添加新的前端页面
1. 在 `apps/frontend/src/views/` 创建页面组件
2. 在 `router/index.ts` 添加路由配置
3. 使用Pinia store管理状态
4. 使用Element Plus组件构建界面

**示例**:
```typescript
// apps/frontend/src/router/index.ts
{
  path: '/example',
  name: 'Example',
  component: () => import('@/views/app/Example.vue'),
  meta: { requiresAuth: true }
}
```

### 调试技巧

#### 后端调试
```bash
# 启用Flask调试模式
export FLASK_ENV=development
npm run dev:backend

# 查看后端日志
tail -f apps/backend/logs/app.log
```

#### 前端调试
- 使用Vue DevTools浏览器扩展
- 在Vite配置中启用source maps
- 使用浏览器开发者工具Network和Console面板

#### 数据库调试
```bash
# 进入SQLite命令行
cd apps/backend/instance
sqlite3 database.db

# 常用SQL查询
sqlite> SELECT * FROM users;
sqlite> SELECT COUNT(*) FROM creations;
sqlite> .schema users
sqlite> .tables
```

## 📊 项目状态

### 当前版本
**Phase 3+ 完成** - 企业级AI绘图平台 (更新于2025-10-01)

### 系统统计 (2025-10-01)
- 🚀 服务状态: 前端(localhost:3001) + 后端(localhost:5000) 正常运行
- 📊 数据库架构: 20个表完整
- 👥 用户数据: 2个用户（包含admin@test.com管理员）
- 🎨 AI作品: 7个生成作品
- 🔧 配置组: 1个已启用配置组（default-config）

### 已完成功能 ✅

#### Phase 1: 项目基础与核心用户系统
- ✅ Monorepo架构搭建（apps/frontend, apps/backend, packages）
- ✅ Vue.js 3 + TypeScript + Vite前端框架
- ✅ Flask 3 + SQLite3后端框架
- ✅ 用户注册登录系统
- ✅ JWT认证和令牌管理

#### Phase 2: AI绘图功能
- ✅ 文生图功能（nano-banana, nano-banana-hd）
- ✅ 图生图功能
- ✅ 次数管理和消费记录
- ✅ 生成历史和状态管理
- ✅ 异步处理和错误恢复

#### Phase 3: 画廊与管理
- ✅ 个人画廊系统（分类、标签、收藏）
- ✅ 响应式设计（桌面、平板、移动端）
- ✅ 管理员功能（用户管理、次数充值）
- ✅ 配置组系统（灵活的API配置管理）

#### Phase 2+ 企业级增强
- ✅ 性能监控与用户行为分析（11个分析表）
- ✅ 智能推荐系统（6个推荐表）
- ✅ 管理员数据仪表板
- ✅ 增强进度指示器
- ✅ 超时处理优化

#### Phase 3+ 安全加固
- ✅ 外键约束强制执行
- ✅ CORS配置修复（3000+3001端口）
- ✅ JWT令牌优化（24h→2h）
- ✅ 生产环境变量强制验证
- ✅ 统一API响应格式
- ✅ Fernet加密系统

### 最近修复 🐛

#### 2025-10-01: 仪表板用户统计修复
- **问题**: Dashboard显示"总用户数: 7"，实际只有2个用户
- **原因**: API返回用户的作品数而非系统用户数
- **修复**: 重写 `/api/analytics/system-insights` 统计逻辑
- **详情**: [DASHBOARD_USER_COUNT_FIX.md](./DASHBOARD_USER_COUNT_FIX.md)

#### 2025-09-30: 画廊显示优化
- **问题1**: 图片被裁剪，无法完整显示
- **修复**: 将 `fit="cover"` 改为 `fit="contain"`
- **问题2**: 双重图片查看器冲突
- **修复**: 移除缩略图的preview属性，使用分层预览策略
- **详情**: [GALLERY_OPTIMIZATION_REPORT.md](./docs/GALLERY_OPTIMIZATION_REPORT.md)

#### 2025-09-29: 性能优化
- **问题**: 生成超时后等待49秒才返回错误
- **修复**: 优化超时处理，前端120s，后端180s
- **效果**: 75.6%性能提升（从49s降至12s）

#### 2025-09-29: UI现代化
- **Profile页面**: 卡片式操作面板，渐变背景，交互动画
- **响应式优化**: 桌面3列、平板单列、移动端自适应
- **登录体验**: 重定向修复，Element Plus图标兼容

### 后续计划

根据当前系统状态，建议按以下优先级进行后续开发：

#### 🥇 第一优先级：性能监控和系统稳定性
- APM应用性能监控集成
- 数据库查询性能优化和慢查询检测
- API响应时间监控和错误率统计
- 系统资源监控(内存、CPU)和告警
- 结构化日志系统和错误跟踪

#### 🥈 第二优先级：安全加固和防护
- API速率限制和防滥用保护
- 输入验证增强(XSS、SQL注入防护)
- 安全审计日志增强
- 敏感数据加密和保护
- OWASP安全合规检查

#### 🥉 第三优先级：测试覆盖
- 单元测试覆盖率提升至80%+
- E2E测试完整覆盖核心流程
- API集成测试
- 性能测试和压力测试

#### 💡 第四优先级：功能增强
- 社交功能（作品分享）
- 批量生成
- 历史记录管理
- 数据导出功能
- 多语言支持

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 如何贡献
1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 开发规范
- 遵循项目代码规范（ESLint, Flake8）
- 编写清晰的commit message
- 添加必要的测试
- 更新相关文档

### 报告问题
- 使用GitHub Issues报告Bug
- 提供详细的复现步骤
- 包含系统环境信息
- 附上错误日志和截图

## 📚 相关文档

- [产品需求文档 (PRD)](./docs/prd.md) - 完整的产品需求和功能规划
- [架构设计文档](./docs/architecture.md) - 系统架构和技术选型
- [Claude Code指令](./CLAUDE.md) - 项目开发指引和完整状态跟踪
- [画廊优化报告](./docs/GALLERY_OPTIMIZATION_REPORT.md) - 画廊显示优化详情
- [仪表板修复文档](./DASHBOARD_USER_COUNT_FIX.md) - 用户统计修复详情
- [系统设置实施文档](./docs/SYSTEM_SETTINGS_IMPLEMENTATION.md) - 配置管理实施详情

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🌟 技术亮点

### 架构设计
- ✅ Monorepo架构，前后端分离
- ✅ Flask应用工厂模式
- ✅ Vue.js Composition API
- ✅ Repository模式数据访问
- ✅ 统一API响应格式

### 安全性
- ✅ JWT令牌认证和刷新
- ✅ Fernet加密敏感数据
- ✅ 防暴力破解机制
- ✅ CORS跨域保护
- ✅ 外键约束和数据一致性

### 性能优化
- ✅ 异步HTTP客户端（aiohttp）
- ✅ SQLite WAL模式
- ✅ 智能超时和重试机制
- ✅ 前端路由懒加载
- ✅ 配置热更新（无需重启）

### 用户体验
- ✅ 响应式设计（移动端优化）
- ✅ 实时进度指示
- ✅ 智能推荐系统
- ✅ 卡片式现代UI
- ✅ 错误友好提示

### 可维护性
- ✅ TypeScript类型安全
- ✅ 清晰的项目结构
- ✅ 完整的文档体系
- ✅ 统一的代码规范
- ✅ 详细的错误日志

---

**技术支持**: 如有问题，请提交 [Issue](https://github.com/yourname/mynanobananaapp/issues)

**项目文档**: 完整文档详见 [docs](./docs) 目录

**开发者**: 基于Vue.js 3 + Flask 3构建的企业级AI绘图平台 | MIT License
