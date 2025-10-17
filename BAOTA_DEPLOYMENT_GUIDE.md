# 宝塔面板部署指南

## 🚀 快速部署（推荐方案）

### 准备工作

#### 在本地Mac上：
```bash
cd /Users/wang/Documents/MyCode/mynanobananaapp

# 拉取最新代码
git pull origin master

# 构建前端
cd apps/frontend
npm run build

# 构建产物在：apps/frontend/dist/
```

---

## 📦 方式1：只上传必要文件（推荐）

### 本地打包

```bash
cd /Users/wang/Documents/MyCode/mynanobananaapp

# 创建部署包（只包含必要文件）
tar -czf mynanobanana-deploy.tar.gz \
  --exclude='apps/backend/__pycache__' \
  --exclude='apps/backend/*.pyc' \
  --exclude='apps/backend/*.log' \
  --exclude='apps/backend/database.db' \
  apps/backend \
  apps/frontend/dist

# 生成的文件：mynanobanana-deploy.tar.gz (约2-5MB)
```

### 上传到服务器

1. 打开宝塔面板 → **文件**
2. 进入 `/www/wwwroot/`
3. 创建目录 `mynanobananaapp`（如果不存在）
4. 上传 `mynanobanana-deploy.tar.gz`
5. 右键 → **解压**

---

## 🔧 后端配置（Python项目管理器）

### 1. 添加项目

打开 **Python项目管理器** → **添加项目**

配置如下：
```
项目名称: mynanobanana
项目路径: /www/wwwroot/mynanobananaapp/apps/backend
Python版本: 3.11 或 3.12
框架: Other
启动方式: gunicorn
启动文件: wsgi:app  ← 重要！使用wsgi而不是app
端口: 5000
进程数: 4
是否开机启动: 是
```

### 2. 配置环境变量

在项目设置 → **环境变量** 中添加：

```bash
SECRET_KEY=your-production-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this
ENCRYPTION_KEY=your-fernet-encryption-key
OPENAI_HK_API_KEY=hk-your-actual-api-key
OPENAI_HK_BASE_URL=https://api.openai-hk.com
CORS_ORIGINS=http://106.14.160.150,http://your-domain.com
DATABASE_PATH=/www/wwwroot/mynanobananaapp/apps/backend/instance/database.db
```

**生成加密密钥：**
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. 安装依赖

在项目管理器点击 **终端** 或使用SSH：

```bash
cd /www/wwwroot/mynanobananaapp/apps/backend
pip3.12 install -r requirements.txt
```

### 4. 初始化数据库

```bash
cd /www/wwwroot/mynanobananaapp/apps/backend

# 确保instance目录存在
mkdir -p instance

# 初始化管理员账户
python3 init_admin.py
```

### 5. 启动项目

在Python项目管理器中点击 **启动**

验证：
```bash
curl http://127.0.0.1:5000/api/health
# 预期: {"status": "healthy"}
```

---

## 🌐 前端配置（网站管理）

### 1. 添加站点

打开 **网站** → **添加站点**

```
域名: your-domain.com (或使用IP: 106.14.160.150)
根目录: /www/wwwroot/mynanobananaapp/apps/frontend/dist
PHP版本: 纯静态
```

### 2. 配置Nginx

网站设置 → **配置文件**，添加以下配置：

```nginx
server {
    listen 80;
    server_name _;  # 或你的域名
    
    # 根目录
    root /www/wwwroot/mynanobananaapp/apps/frontend/dist;
    index index.html;
    
    # 访问日志
    access_log /www/wwwroot/mynanobananaapp/logs/access.log;
    error_log /www/wwwroot/mynanobananaapp/logs/error.log;
    
    # 前端路由（Vue Router history模式）
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }
    
    # API反向代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # AI生成需要长超时（重要！）
        proxy_read_timeout 180s;
        proxy_connect_timeout 180s;
        proxy_send_timeout 180s;
        
        # 文件上传限制
        client_max_body_size 10M;
        
        # 禁用缓存
        add_header Cache-Control "no-store, no-cache, must-revalidate";
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
    
    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }
}
```

保存并重载Nginx。

---

## ✅ 验证部署

### 1. 检查后端

```bash
curl http://127.0.0.1:5000/api/health
# 预期: {"status": "healthy"}
```

### 2. 检查前端

浏览器访问：`http://106.14.160.150`

预期：看到登录页面

### 3. 测试登录

```
邮箱: admin@test.com
密码: Admin123
```

---

## 🐛 常见问题

### Q: Worker exited with code 4
**A:** 这是启动文件配置问题，确保使用 `wsgi:app` 而不是 `app:app`

### Q: Failed to find attribute 'app'
**A:** 命名冲突，需要使用 `wsgi.py` 而不是 `app.py`

### Q: ModuleNotFoundError
**A:** 依赖未安装，执行：
```bash
cd /www/wwwroot/mynanobananaapp/apps/backend
pip3.12 install -r requirements.txt
```

### Q: 数据库锁定
**A:** 确保只有一个进程访问数据库，重启项目

---

## 🔄 更新部署

```bash
# 在服务器上
cd /www/wwwroot/mynanobananaapp
git pull origin master

# 重新构建前端（如果需要）
cd apps/frontend
npm run build

# 在宝塔面板重启Python项目
```

---

## 📞 需要帮助？

如果遇到问题：

1. 查看后端日志（Python项目管理器 → 日志）
2. 查看Nginx日志（网站 → 日志）
3. 检查环境变量是否配置
4. 确认端口5000未被占用

---

**使用 wsgi:app 启动文件是最标准和可靠的方式！**

