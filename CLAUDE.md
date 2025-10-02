# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**Nano-Banana AI 绘图应用** (mynanobananaapp) - 一个功能完整的企业级AI图片生成平台，集成了nano-banana模型，提供文生图、图生图、智能推荐、性能监控等完整功能。

**技术栈**: Vue.js 3 + TypeScript + Flask + SQLite + JWT + Element Plus

## 系统架构

### Monorepo结构
```
mynanobananaapp/
├── apps/
│   ├── frontend/          # Vue.js 3.4 + TypeScript + Vite
│   │   ├── src/
│   │   │   ├── views/
│   │   │   │   ├── app/           # 用户界面
│   │   │   │   │   ├── AppMain.vue       # 主框架
│   │   │   │   │   ├── Generate.vue      # AI生成页面
│   │   │   │   │   ├── Gallery.vue       # 作品画廊
│   │   │   │   │   └── Profile.vue       # 个人中心
│   │   │   │   ├── admin/         # 管理员界面
│   │   │   │   │   ├── AdminLayout.vue   # 管理框架
│   │   │   │   │   ├── Dashboard.vue     # 数据仪表板
│   │   │   │   │   ├── UserManagement.vue # 用户管理
│   │   │   │   │   └── SystemSettings.vue # 系统设置
│   │   │   │   ├── Home.vue
│   │   │   │   └── LoginView.vue
│   │   │   ├── services/
│   │   │   │   └── api.ts         # Axios API客户端
│   │   │   ├── stores/            # Pinia状态管理
│   │   │   └── router/            # Vue Router配置
│   │   └── package.json
│   └── backend/           # Flask 3.0 + Python 3.11
│       ├── app/
│       │   ├── views/             # API端点
│       │   │   ├── auth.py        # 认证API
│       │   │   ├── user.py        # 用户API
│       │   │   ├── generate.py    # AI生成API
│       │   │   ├── gallery.py     # 画廊API
│       │   │   ├── admin.py       # 管理员API
│       │   │   └── config_groups.py # 配置管理API
│       │   ├── services/
│       │   │   ├── ai_generator.py # AI生成服务
│       │   │   └── encryption_service.py # 加密服务
│       │   ├── database.py        # 数据库模型
│       │   └── utils/             # 工具函数
│       ├── migrations/            # 数据库迁移
│       ├── instance/              # SQLite数据库
│       └── app.py                 # Flask应用入口
├── docs/                  # 项目文档
└── package.json          # 根配置
```

## 核心功能模块

### 1. 用户认证系统 ✅
- **JWT认证**: 2小时访问令牌 + 30天刷新令牌
- **安全特性**: 密码哈希、登录限制、令牌黑名单
- **用户模型**: email, password_hash, credits, is_active, last_login_at

### 2. AI图片生成 ✅
- **文生图**: 文本提示词 → AI图片
- **图生图**: 参考图片 + 文本提示 → 新图片
- **模型支持**: nano-banana (12s), nano-banana-hd (28s, 4K高清)
- **尺寸支持**: 1x1, 4x3, 3x4, 16x9, 9x16, 2x3, 3x2
- **次数系统**: 基于credits的消费模式

### 3. 画廊管理系统 ✅
- **作品展示**: 网格/列表视图，响应式布局
- **完整功能**: 查看、下载、删除、收藏、分类、标签
- **搜索筛选**: 关键词搜索、分类筛选、收藏筛选
- **统计信息**: 用户作品统计、分类分布
- **图片优化**: fit="contain"完整显示，防止裁剪

### 4. 智能推荐系统 ✅ (Phase 2)
- **提示词优化**: AI驱动的提示词增强建议
- **模型推荐**: 基于内容特征智能推荐模型
- **尺寸建议**: 基于用户偏好和内容类型
- **用户偏好学习**: 自动学习使用模式
- **推荐效果分析**: 接受率、满意度追踪

### 5. 性能监控系统 ✅ (Phase 2)
- **性能指标**: 生成时间、错误率、系统负载
- **用户行为**: 操作模式、活跃时段、设备分析
- **每日统计**: 用户增长、生成统计、系统健康度
- **系统洞察**: 综合分析和优化建议

### 6. 管理员功能 ✅
- **Dashboard**: 系统统计、性能分析、数据可视化
- **用户管理**: 搜索、详情、次数充值、用户操作
- **系统设置**: API配置管理、加密存储、热更新
- **权限控制**: 基于用户ID的管理员验证

### 7. 配置管理系统 ✅ (Phase 3)
- **配置组**: 多配置管理，启用互斥机制
- **加密存储**: Fernet AES-128加密API密钥
- **热更新**: 配置修改立即生效，无需重启
- **安全特性**: 前端脱敏显示、后端解密使用

## 数据库架构

### 核心表结构 (20张表)

#### 用户与认证
```sql
-- 用户表
users (id, email, password_hash, credits, is_active, created_at, last_login_at, failed_login_attempts, locked_until)

-- JWT黑名单
jwt_blacklist (id, jti, created_at)

-- 角色系统 (Phase 4)
roles (id, name, description, created_at)
user_roles (id, user_id, role_id)
permissions (id, name, description, created_at)
role_permissions (id, role_id, permission_id)
```

#### AI生成与作品
```sql
-- 作品表
creations (id, user_id, prompt, image_url, model_used, size, generation_time,
           is_favorite, tags, category, visibility, created_at)

-- 配置组
api_config_groups (id, name, description, is_active, openai_hk_base_url,
                   openai_hk_api_key_encrypted, created_at, updated_at)

-- 系统设置
system_settings (id, group_id, key, value, is_encrypted, updated_at)
```

#### 智能推荐 (Phase 2)
```sql
-- 用户偏好
user_preferences (id, user_id, preferred_model, preferred_sizes, favorite_styles,
                  preferred_categories, style_keywords, quality_preference,
                  generation_speed_preference, updated_at)

-- 智能推荐
smart_recommendations (id, user_id, recommendation_type, content, confidence_score,
                       reasoning, is_accepted, created_at)

-- 提示词优化
prompt_optimizations (id, user_id, original_prompt, optimized_prompt,
                      optimization_type, improvements, quality_score, is_applied)

-- 相似作品
creation_similarities (id, creation_id, similar_creation_id, similarity_score,
                       similarity_type, created_at)

-- 推荐分析
recommendation_analytics (id, recommendation_id, user_id, action_type,
                          effectiveness_score, created_at)
```

#### 性能分析 (Phase 2)
```sql
-- 性能指标
performance_metrics (id, user_id, operation_type, model_used, generation_time,
                     api_response_time, success, error_message, server_load,
                     memory_usage_mb, created_at)

-- 用户会话
user_sessions (id, user_id, session_start, session_end, page_views,
               generations_count, device_type, browser, created_at)

-- 用户行为
user_behaviors (id, user_id, session_id, action_type, action_details,
                page_url, duration_seconds, created_at)

-- 每日统计
daily_stats (id, date, total_users, active_users, new_registrations,
             total_generations, successful_generations, avg_generation_time,
             total_credits_consumed, peak_concurrent_users, error_rate)

-- 用户删除记录
user_deletions (id, user_id, email, deletion_reason, deleted_by,
                creations_count, total_credits, deleted_at)
```

## API接口规范

### 认证接口
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/refresh` - 刷新令牌
- `POST /api/logout` - 退出登录

### AI生成接口
- `GET /api/generate/models` - 获取可用模型和尺寸
- `POST /api/generate/text-to-image` - 文生图 (120s超时)
- `POST /api/generate/image-to-image` - 图生图 (120s超时)

### 画廊接口
- `GET /api/gallery` - 获取作品列表 (分页、筛选、搜索)
- `DELETE /api/gallery/:id` - 删除作品
- `PUT /api/gallery/:id/favorite` - 更新收藏状态
- `PUT /api/gallery/:id/tags` - 更新标签
- `PUT /api/gallery/:id/category` - 更新分类
- `GET /api/gallery/categories` - 获取分类列表
- `GET /api/gallery/stats` - 获取统计信息

### 智能推荐接口 (Phase 2)
- `POST /api/recommendations/smart-suggestions` - 获取智能建议
- `GET /api/recommendations/user-preferences` - 获取用户偏好
- `PUT /api/recommendations/user-preferences` - 更新用户偏好
- `GET /api/recommendations/similar-creations/:id` - 相似作品推荐
- `POST /api/recommendations/feedback` - 记录推荐反馈
- `GET /api/recommendations/analytics` - 推荐效果分析

### 性能分析接口 (Phase 2)
- `GET /api/analytics/performance` - 系统性能分析
- `GET /api/analytics/user-behavior` - 用户行为分析
- `GET /api/analytics/popular-actions` - 热门操作统计
- `GET /api/analytics/daily-stats` - 每日统计数据
- `GET /api/analytics/system-insights` - 系统综合洞察 (已修复)

### 管理员接口
- `POST /api/admin/add-credits` - 添加用户次数
- `GET /api/admin/users/search` - 搜索用户
- `GET /api/admin/users/:id` - 获取用户详情
- `GET /api/admin/config-groups` - 获取配置组列表
- `POST /api/admin/config-groups` - 创建配置组
- `PUT /api/admin/config-groups/:id/toggle` - 切换启用状态
- `DELETE /api/admin/config-groups/:id` - 删除配置组
- `GET /api/admin/settings` - 获取系统设置
- `PUT /api/admin/settings` - 更新系统设置
- `POST /api/admin/settings/test-connection` - 测试API连接

## 技术细节

### 前端技术栈
- **框架**: Vue.js 3.4 + Composition API
- **语言**: TypeScript 5.x
- **构建**: Vite 5.x
- **UI库**: Element Plus
- **状态**: Pinia
- **路由**: Vue Router 4
- **HTTP**: Axios (120s超时配置)

### 后端技术栈
- **框架**: Flask 3.0
- **语言**: Python 3.11
- **数据库**: SQLite3 (WAL模式)
- **认证**: Flask-JWT-Extended
- **加密**: cryptography (Fernet)
- **HTTP**: aiohttp (异步)

### 外部API集成
- **nano-banana API**: api.openai-hk.com
- **认证方式**: Bearer token (加密存储)
- **模型**: nano-banana (~12s), nano-banana-hd (~28s)
- **端点**: /v1/images/generations, /v1/images/edits

### 安全特性
- ✅ API密钥Fernet加密存储 (AES-128-CBC + HMAC-SHA256)
- ✅ 密码Werkzeug哈希处理
- ✅ JWT无状态认证 (2小时访问令牌)
- ✅ 外键约束强制执行
- ✅ CORS配置限制 (localhost:3000, 3001)
- ✅ 生产环境环境变量验证
- ✅ 管理员权限严格验证 (ID=1)
- ✅ 前端脱敏显示API密钥

### 性能优化
- ✅ SQLite WAL模式提升并发
- ✅ 配置热更新机制
- ✅ 前端120s超时适配AI生成
- ✅ 异步HTTP客户端 (aiohttp)
- ✅ 详细性能日志监控 (6个监控点)

## 开发命令

```bash
# 开发环境
npm run dev              # 同时启动前后端
npm run dev:frontend     # 仅启动Vue.js (port 3000)
npm run dev:backend      # 仅启动Flask (port 5000)

# 测试
npm run test            # 运行所有测试
npm run test:frontend   # Vitest测试
npm run test:backend    # Pytest测试
npm run test:e2e        # Playwright E2E测试

# 构建
npm run build           # 构建生产版本
npm run build:frontend  # 构建Vue.js SPA
```

## 项目状态

### ✅ 已完成功能 (2025-10-01)

**Phase 1: 项目基础** ✅
- Monorepo架构搭建
- Vue.js + Flask基础框架
- 用户认证系统 (JWT)
- 数据库模型设计

**Phase 2: AI生成功能** ✅
- 文生图完整实现
- 图生图完整实现
- 次数管理系统
- 性能监控和日志

**Phase 3: 画廊管理** ✅
- 作品展示和管理
- 搜索筛选功能
- 收藏和分类系统
- 响应式设计优化

**Phase 4: 企业级增强** ✅
- 智能推荐系统
- 性能监控分析
- 管理员Dashboard
- 配置管理系统

**Phase 5: UI/UX优化** ✅
- Profile页面卡片式设计
- 画廊图片完整显示修复
- Dashboard数据统计修复
- 响应式布局完善

### 📊 当前系统状态

**服务运行**:
- ✅ 前端: http://localhost:3000
- ✅ 后端: http://localhost:5000

**数据统计**:
- 数据库表: 20张
- 用户数: 2个
- 作品数: 7个
- 配置组: 1个 (已启用)

**性能指标**:
- 普通模型: ~12秒/张
- HD模型: ~28秒/张
- 前端超时: 120秒
- 后端超时: 180秒

### 🐛 已修复问题

1. **性能问题** (2025-10-01):
   - Demo API密钥导致49s生成 → 真实密钥12s (75.6%提升)
   - HD模型401错误 → 完全修复，28s正常生成

2. **画廊显示问题** (2025-10-01):
   - 图片裁剪 → fit="contain"完整显示
   - 双重预览冲突 → 分层预览策略

3. **Dashboard统计错误** (2025-10-01):
   - 用户数显示7 → 修复为2 (数据混淆问题)

## 文件组织模式

### 前端 (Vue.js)
- **组件**: 按功能和复用性组织
- **状态**: Pinia store按功能模块 (auth, user, gallery)
- **API**: 全局axios实例，统一错误处理
- **路由**: 受保护路由，管理员权限验证

### 后端 (Flask)
- **Blueprints**: 按功能模块组织 (auth, user, generate, gallery, admin)
- **Services**: 业务逻辑层 (ai_generator, encryption)
- **Database**: 直接SQLite3集成，Repository模式
- **Utils**: 工具函数和装饰器

## 开发指南

### 添加新功能
1. **后端**: 在对应Blueprint添加路由和逻辑
2. **数据库**: 在migrations/创建迁移SQL
3. **前端**: 在services/api.ts添加API调用
4. **UI**: 在views/对应目录创建Vue组件

### 数据库迁移
```bash
cd apps/backend
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('instance/database.db')
with open('migrations/your_migration.sql') as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
EOF
```

### 配置管理
- **开发环境**: `.env` (不提交)
- **生产环境**: 环境变量
- **API配置**: 数据库config_groups表，Web界面管理

## 相关文档

### 技术文档
- `PERFORMANCE_SOLUTION.md` - 性能优化完整报告
- `GALLERY_OPTIMIZATION_REPORT.md` - 画廊优化详情
- `GALLERY_DOUBLE_IMAGE_FIX.md` - 双重图片修复
- `DASHBOARD_USER_COUNT_FIX.md` - Dashboard统计修复

### 系统架构
- `docs/SYSTEM_ARCHITECTURE.md` - 系统架构设计
- `docs/API_SPECIFICATION.md` - API接口规范
- `docs/DATABASE_SCHEMA.md` - 数据库架构

## 注意事项

### 开发环境
- Node.js >= 18.x
- Python >= 3.11
- SQLite3 >= 3.35

### 重要提醒
- ⚠️ 绝不暴露API密钥到前端
- ⚠️ 管理员权限仅ID=1用户
- ⚠️ 配置修改后自动热更新
- ⚠️ 画廊图片使用fit="contain"避免裁剪
- ⚠️ Dashboard统计使用系统级数据，非个人数据
