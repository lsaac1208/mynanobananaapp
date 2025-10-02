Nano-Banana AI 绘图应用 全栈架构文档
1. 引言 (Introduction)
本文件概述了 Nano-Banana AI 绘图应用的完整全栈架构，包括后端系统、前端实现及其集成。它将作为AI驱动开发中唯一的、权威的技术真相来源，确保整个技术栈的一致性。
启动模板或现有项目 (Starter Template or Existing Project)
我们决定从零开始构建，不使用特定的启动模板，以获得最大的灵活性。
2. 高层架构 (High Level Architecture)
技术摘要 (Technical Summary)
本应用将采用一个务实且高效的全栈架构。后端是一个基于Flask的单体应用，它将处理所有业务逻辑、用户认证和API请求，并直接与一个集成的SQLite数据库文件进行交互。前端是一个现代化的Vue.js单页应用(SPA)，它将为用户提供丰富、响应迅速的界面。前后端代码将统一管理在一个Monorepo（单一代码仓库）中，以简化开发和部署流程。
平台与基础设施选择 (Platform and Infrastructure Choice)
平台: 自托管 (Self-Hosted)
推荐方案: 单个VPS（虚拟专用服务器）。
关键服务组件: Nginx, Gunicorn。
仓库结构 (Repository Structure)
结构: Monorepo (单一代码仓库)
管理工具: npm Workspaces
高层架构图 (High Level Architecture Diagram)
graph TD
    subgraph 用户设备 (User Device)
        A[浏览器 Browser]
    end
    subgraph VPS服务器 (VPS Server)
        B[Nginx]
        C[Vue.js 前端静态文件]
        D[Gunicorn]
        E[Flask 后端应用]
        F[SQLite 数据库文件]
    end
    A -- HTTPS请求 --> B
    B -- / (根路径) --> C
    B -- /api/* (API请求) --> D
    D -- WSGI --> E
    E <--> F


架构模式 (Architectural Patterns)
单体架构 (Monolithic Architecture): 后端是一个单一的部署单元。
单页应用 (Single Page Application - SPA): 前端是一个Vue SPA。
REST API: 前后端之间通过RESTful API进行通信。
仓库模式 (Repository Pattern): 在后端，我们将使用仓库模式来隔离业务逻辑与数据访问。
3. 技术栈 (Tech Stack)
技术栈表格 (Technology Stack Table)
类别 (Category)
技术 (Technology)
版本 (Version)
用途 (Purpose)
理由 (Rationale)
前端语言
TypeScript
~5.4
前端开发语言
为Vue提供类型安全，减少错误，提升代码质量。
前端框架
Vue.js
~3.4
构建用户界面
用户指定的核心框架，响应式且性能优秀。
UI组件库
Element Plus
~2.7
提供预制UI组件
与Vue 3完美集成，组件丰富，加速UI开发。
前端状态管理
Pinia
~2.1
集中管理前端状态
Vue官方推荐，轻量、直观且对TypeScript支持友好。
前端构建工具
Vite
~5.2
开发服务器与打包
Vue生态首选，提供极速的开发体验和优化的打包。
后端语言
Python
~3.11
后端开发语言
Flask的运行基础，成熟稳定，生态丰富。
后端框架
Flask
~3.0
构建后端API
用户指定的核心框架，轻量、灵活，适合快速开发。
API风格
REST
n/a
前后端通信
业界标准，易于理解和实现。
数据库
SQLite
~3.37+
应用数据库
用户指定，轻量级的本地文件数据库，适合MVP。
认证
Flask-JWT-Extended
~4.6
JWT认证
为Flask应用提供简单、安全的JWT令牌管理。
前端测试
Vitest & Testing Library
最新
单元/组件测试
与Vite无缝集成，专注于用户行为的测试范式。
后端测试
Pytest
~8.1
单元/集成测试
Python社区事实上的标准，功能强大，易于编写。
端到端测试
Playwright
~1.44
浏览器自动化测试
现代化的E2E测试框架，支持所有主流浏览器。
CI/CD
GitHub Actions
n/a
自动化构建与部署
与GitHub深度集成，配置简单，生态丰富。
基础设施即代码
Bash Scripts
n/a
自动化服务器配置
对于单个VPS，使用简单的Shell脚本进行环境配置最直接。

4. 数据模型 (Data Models)
模型: 用户 (User)
用途: 代表系统中的注册用户，管理其认证凭据和追踪其图片生成次数余额。
关键属性: id (整数), email (字符串), password_hash (字符串), credits (整数)。
TypeScript 接口:
export interface User {
  id: number;
  email: string;
  credits: number;
}


关系: 一个用户可以拥有多个“作品”。
模型: 作品 (Creation)
用途: 代表由用户生成的单张图片。它存储了输出结果和输入参数，用于用户的个人画廊。
关键属性: id (整数), user_id (整数), prompt (文本), image_url (字符串), model_used (字符串), size (字符串), created_at (日期时间)。
TypeScript 接口:
export interface Creation {
  id: number;
  userId: number;
  prompt: string;
  imageUrl: string;
  modelUsed: string;
  size: string;
  createdAt: string; // ISO 8601 format
}


关系: 一个“作品”只属于一个用户。
5. API规范 (API Specification)
openapi: 3.0.1
info:
  title: "Nano-Banana AI 绘图应用 API"
  version: "1.0.0"
  description: "用于驱动 Nano-Banana AI 绘图应用前端的核心API。"
servers:
  - url: "/api"

paths:
  /register:
    post:
      summary: "用户注册"
      # ... (完整的 OpenAPI 路径定义)
  /login:
    post:
      summary: "用户登录"
      # ...
  /users/me:
    get:
      summary: "获取当前用户信息"
      # ...
  /generate/text-to-image:
    post:
      summary: "文生图"
      # ...
  /generate/image-to-image:
    post:
      summary: "图生图"
      # ...
  /gallery:
    get:
      summary: "获取用户画廊"
      # ...
  /admin/add-credits:
    post:
      summary: "(管理员) 添加次数"
      # ...

components:
  securitySchemes:
    bearerAuth: { type: http, scheme: bearer, bearerFormat: JWT }
  schemas:
    User: { # ... (完整的 OpenAPI 组件定义) }
    Creation: { # ... }
    AuthRequest: { # ... }
    LoginResponse: { # ... }
    TextGenRequest: { # ... }
    ImageGenRequest: { # ... }
    AddCreditsRequest: { # ... }


6. 组件 (Components)
组件: 前端应用 (Vue SPA)
职责: 渲染所有用户界面、处理用户交互、管理前端状态，并通过REST API与后端进行通信。
技术: Vue.js, Pinia, Vite, Element Plus。
组件: 后端API (Flask App)
职责: 提供REST API，处理所有业务逻辑，管理数据库持久化，并安全地调用外部AI服务。
内部模块: 认证模块, 用户管理模块, AI生成模块, 画廊模块, 管理模块。
技术: Flask, SQLite, Pytest, Gunicorn。
组件交互图
graph TD
    User[用户] --> FE[前端应用 (Vue SPA)]
    FE -- API 请求 --> BE[后端API (Flask App)]
    subgraph 后端内部模块
        BE -- 操作 --> Auth[认证模块]
        BE -- 操作 --> UserMgmt[用户管理模块]
        BE -- 操作 --> Gen[AI生成模块]
        BE -- 操作 --> Gallery[画廊模块]
    end
    BE -- 读/写 --> DB[(SQLite 数据库)]
    Gen -- 第三方API调用 --> ExtAPI[外部 nano-banana API]


7. 外部API (External APIs)
API: openai-hk.com / nano-banana API
用途: 提供核心的“文生图”和“图生图”AI模型服务。
基础URL: https://api.openai-hk.com
认证方式: Bearer Token。
使用的关键接口: POST /v1/images/generations, POST /v1/images/edits。
8. 核心工作流 (Core Workflows)
sequenceDiagram
    actor User as 用户
    participant Browser as 浏览器 (Vue SPA)
    participant Backend as 后端 (Flask App)
    participant DB as 数据库 (SQLite)
    participant ExtAPI as 外部API (nano-banana)
    
    User->>Browser: 1. 点击“生成”按钮
    Browser->>Backend: 2. POST /api/generate/text-to-image
    
    Backend->>DB: 3. 查询用户剩余次数
    DB-->>Backend: 4. 返回用户次数
    
    alt 次数充足 (Credits > 0)
        Backend->>ExtAPI: 5. POST /v1/images/generations (携带平台密钥)
        ExtAPI-->>Backend: 6. 返回生成的图片URL
        
        Backend->>DB: 7. 更新用户次数 (credits = credits - 1)
        Backend->>DB: 8. 保存新的作品记录
        
        Backend-->>Browser: 9. 200 OK (返回作品数据)
        Browser->>User: 10. 显示图片 & 更新UI
    else 次数不足 (Credits <= 0)
        Backend-->>Browser: 402 Payment Required (次数不足错误)
        Browser->>User: 显示“次数不足”提示
    end


9. 数据库模式 (Database Schema)
-- 用户表 (Users Table)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    credits INTEGER NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX idx_users_email ON users (email);

-- 作品表 (Creations Table)
CREATE TABLE creations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    image_url TEXT NOT NULL,
    model_used TEXT NOT NULL,
    size TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX idx_creations_user_id ON creations (user_id);


10. 前端架构 (Frontend Architecture)
组件组织: 按功能和复用性划分 (common, layouts, views)。
组件模板: 使用Vue 3 <script setup> 语法和TypeScript。
状态管理: 使用Pinia，按功能模块划分store (user.ts, gallery.ts)。
路由架构: 使用 vue-router 并通过全局导航守卫实现受保护路由。
服务层: 配置全局 axios 实例，封装API请求。
11. 后端架构 (Backend Architecture)
服务架构: 使用Flask Blueprints按功能模块组织路由。
数据库架构: 使用仓库模式 (Repository Pattern) 隔离业务逻辑和数据库查询。
认证架构: 使用JWT进行无状态认证，通过 @jwt_required() 装饰器保护接口。
12. 统一的项目结构 (Unified Project Structure)
nano-banana-app/
├── apps/
│   ├── frontend/
│   └── backend/
├── docs/
├── packages/
│   └── shared-types/
└── package.json


13. 开发工作流 (Development Workflow)
本地设置: 详细说明了 git clone, npm install, pip install 等步骤。
开发命令: 定义了 npm run dev, npm run dev:frontend, npm run dev:backend 等脚本。
环境变量: 提供了 .env.example 模板。
14. 部署架构 (Deployment Architecture)
部署策略: 定义了如何将前端静态文件部署到Nginx，以及如何使用Gunicorn和systemd运行后端Flask应用。
CI/CD: 提供了使用GitHub Actions的自动化部署流水线示例。
15. 安全与性能 (Security and Performance)
安全要求: 包括CSP, XSS防护, 密码哈希, 速率限制, 密钥管理等。
性能优化: 包括代码分割, 图片懒加载, 浏览器缓存, 数据库索引等。
16. 测试策略 (Testing Strategy)
测试金字塔: 定义了单元测试、集成测试、端到端测试的策略。
测试示例: 为Vitest, Pytest, Playwright提供了代码示例。
17. 编码规范 (Coding Standards)
关键规则: 强制类型共享、使用服务层和仓库层等。
命名约定: 为文件、变量、CSS、API路由、数据库表提供了统一的命名约定。
18. 错误处理策略 (Error Handling Strategy)
错误流程: 使用序列图展示了统一的错误处理流程。
错误响应格式: 定义了标准的JSON错误响应体。
实现示例: 提供了前后端的错误处理代码示例。
19. 监控与可观测性 (Monitoring and Observability)
监控技术栈: 推荐使用Sentry, Flask日志, systemd进程监控和UptimeRobot进行健康检查。
关键指标: 列出了需要关注的前后端关键性能和健康指标。
