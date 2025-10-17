# 401认证错误修复方案

## 🔍 问题分析

从截图看到：
- ✅ 登录成功（能进入系统）
- ❌ 所有/api/analytics/*请求返回401 UNAUTHORIZED
- ❌ /api/refresh也返回401

## 根本原因

**CORS配置问题！**

服务器上的CORS_ORIGINS环境变量可能：
1. 未设置（使用默认的localhost）
2. 不包含 `http://nanobanana.100yse.com`

导致：
- 预检请求（OPTIONS）可能通过
- 但实际请求被CORS拦截
- 后端返回401而不是正常响应

## 解决方案

### 在宝塔服务器上配置环境变量

**Python项目管理器** → 找到项目 → **环境管理** → 添加/修改：

```bash
CORS_ORIGINS=http://nanobanana.100yse.com,https://nanobanana.100yse.com,http://106.14.160.150
```

**重要：** 包含所有可能的访问域名！

---

## 快速修复步骤

### 步骤1：SSH到服务器

```bash
ssh root@106.14.160.150
```

### 步骤2：修改环境变量

```bash
cd /www/wwwroot/mynanobananaapp/apps/backend

# 编辑.env文件
nano .env
```

添加或修改：
```bash
CORS_ORIGINS=http://nanobanana.100yse.com,https://nanobanana.100yse.com,http://106.14.160.150,http://localhost:3001
```

保存（Ctrl+O, Enter, Ctrl+X）

### 步骤3：重启后端

在宝塔面板：
**Python项目管理器** → 找到项目 → **重启**

或通过命令：
```bash
pkill -f gunicorn
cd /www/wwwroot/mynanobananaapp/apps/backend
gunicorn -w 4 -b 0.0.0.0:52036 --daemon wsgi:app
```

### 步骤4：测试

清除浏览器缓存，重新登录测试。

---

## 验证环境变量

SSH到服务器检查：

```bash
cd /www/wwwroot/mynanobananaapp/apps/backend

# 检查.env文件
cat .env | grep CORS

# 或检查Python能否读取
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('CORS_ORIGINS:', os.getenv('CORS_ORIGINS'))"
```

---

## 其他可能的问题

### 问题1：JWT密钥不一致

确保服务器上设置了：
```bash
SECRET_KEY=你的生产密钥
JWT_SECRET_KEY=你的JWT密钥
```

### 问题2：Token格式问题

检查localStorage中的token：
- 在浏览器控制台输入：`localStorage.getItem('access_token')`
- 应该看到类似：`eyJ0eXAiOiJKV1QiLCJhb...`

### 问题3：后端未正确启动

检查：
```bash
ps aux | grep gunicorn
curl http://127.0.0.1:52036/api/health
```

---

## 完整的环境变量示例

在服务器 `/www/wwwroot/mynanobananaapp/apps/backend/.env`：

```bash
# 安全密钥
SECRET_KEY=production-secret-key-change-this
JWT_SECRET_KEY=jwt-secret-key-change-this  
ENCRYPTION_KEY=你的Fernet密钥

# API配置
OPENAI_HK_API_KEY=hk-你的真实API密钥
OPENAI_HK_BASE_URL=https://api.openai-hk.com

# CORS配置（关键！）
CORS_ORIGINS=http://nanobanana.100yse.com,https://nanobanana.100yse.com,http://106.14.160.150

# Flask环境
FLASK_ENV=production
```

---

**立即修复：在宝塔面板添加CORS_ORIGINS环境变量！**

