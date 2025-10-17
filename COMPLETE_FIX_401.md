# 401错误完整修复方案

## 🔍 当前状态

- ✅ config.py 已硬编码CORS域名
- ✅ .env 文件包含正确的CORS配置
- ❌ 后端可能未重启，配置未生效
- ❌ 浏览器中的token可能是旧密钥签发的

---

## 🚀 完整修复步骤（按顺序执行）

### 步骤1：在服务器更新代码

```bash
ssh root@106.14.160.150

cd /www/wwwroot/mynanobananaapp

# 拉取最新代码（包含CORS硬编码修复）
git pull origin master

# 应该看到：apps/backend/config.py 已更新
```

### 步骤2：完全停止旧进程

```bash
# 杀死所有gunicorn进程
pkill -9 -f gunicorn

# 确认已停止
ps aux | grep gunicorn
# 应该没有输出
```

### 步骤3：重新启动后端

```bash
cd /www/wwwroot/mynanobananaapp/apps/backend

# 启动（使用新的配置）
gunicorn -w 4 -b 0.0.0.0:52036 --daemon wsgi:app

# 等待2秒
sleep 2

# 验证启动成功
ps aux | grep gunicorn
# 应该看到4-5个gunicorn进程
```

### 步骤4：测试健康检查

```bash
curl http://127.0.0.1:52036/api/health

# 应该返回：
# {"status":"healthy"}
```

### 步骤5：测试CORS

```bash
curl -H "Origin: http://nanobanana.100yse.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://127.0.0.1:52036/api/analytics/performance

# 应该返回CORS头，不应该有错误
```

---

## 🌐 浏览器端操作

### 步骤6：完全清除浏览器数据

**非常重要！必须清除所有数据！**

1. 按 `Ctrl+Shift+Delete`（Mac: `Cmd+Shift+Delete`）
2. 选择：
   - ✅ Cookie和其他网站数据
   - ✅ 缓存的图片和文件
   - ✅ 托管应用数据（如果有）
3. 时间范围：**全部时间**
4. 点击 **清除数据**

### 步骤7：关闭所有标签页

**完全关闭浏览器，然后重新打开**

### 步骤8：重新登录

1. 访问：`http://nanobanana.100yse.com`
2. 登录：
   ```
   邮箱：admin@test.com
   密码：Admin123
   ```
3. 打开控制台（F12）查看是否还有401错误

---

## 🔍 深度诊断（如果还是401）

### 在浏览器控制台执行：

```javascript
// 1. 清除旧token
localStorage.clear()

// 2. 刷新页面
location.reload()

// 3. 重新登录后检查token
console.log('Token:', localStorage.getItem('access_token'))

// 4. 手动测试API（替换YOUR_TOKEN为实际token）
fetch('/api/analytics/system-insights', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
  }
}).then(r => {
  console.log('Status:', r.status)
  return r.json()
}).then(console.log)
```

---

## 🐛 如果还是失败

### 检查后端日志

在宝塔面板：
**Python项目管理器** → 项目 → **日志**

查找包含 "401" 或 "UNAUTHORIZED" 的行，看具体错误信息。

### 或通过SSH查看：

```bash
cd /www/wwwroot/mynanobananaapp/apps/backend
tail -f backend.log

# 然后在浏览器重新登录，观察日志输出
```

---

## 🔧 终极解决方案（如果以上都不行）

### 修改后端临时禁用JWT验证（仅测试用）

SSH到服务器：

```bash
cd /www/wwwroot/mynanobananaapp/apps/backend

# 创建临时测试端点
cat > test_cors.py << 'EOF'
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='*')

@app.route('/test')
def test():
    return jsonify({'status': 'ok', 'message': 'CORS working!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
EOF

# 启动测试
python3 test_cors.py
```

然后访问：`http://nanobanana.100yse.com:5001/test`

如果能访问，说明是JWT配置问题。

---

## 📋 必须执行的核心步骤

**服务器端（SSH）：**
```bash
cd /www/wwwroot/mynanobananaapp
git pull origin master
cd apps/backend
pkill -9 -f gunicorn
gunicorn -w 4 -b 0.0.0.0:52036 --daemon wsgi:app
```

**浏览器端：**
1. 清除所有数据（Ctrl+Shift+Delete）
2. 完全关闭浏览器
3. 重新打开并登录

---

**请严格按照顺序执行这些步骤！特别是清除浏览器数据和重启后端！** 🔑

