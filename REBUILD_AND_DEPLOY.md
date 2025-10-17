# 重新构建和部署指南

## ✅ Vite配置已修复！

**修复内容：**
- 简化代码分割策略
- 避免模块初始化顺序错误
- 修复 "Cannot access 'Xa' before initialization" 错误

---

## 🚀 在本地Mac重新构建

### 步骤1：拉取最新代码

```bash
cd /Users/wang/Documents/MyCode/mynanobananaapp
git pull origin master
```

### 步骤2：清除缓存

```bash
cd apps/frontend

# 清除构建缓存
rm -rf dist node_modules/.vite
```

### 步骤3：重新构建

```bash
npm run build
```

**预期输出：**
```
✓ 类型检查通过
✓ 构建完成
✓ dist/index.html
✓ dist/assets/...

构建成功！
```

### 步骤4：打包dist文件夹

```bash
cd /Users/wang/Documents/MyCode/mynanobananaapp/apps/frontend
tar -czf dist.tar.gz dist/

# 生成文件：dist.tar.gz（约1-3MB）
```

---

## 📤 上传到服务器

### 方法1：通过宝塔文件管理器

1. 打开宝塔面板 → **文件**
2. 进入 `/www/wwwroot/mynanobananaapp/apps/frontend/`
3. 备份旧的dist：重命名为 `dist.bak`
4. 上传 `dist.tar.gz`
5. 解压

### 方法2：通过SCP命令

```bash
# 在本地Mac执行
cd /Users/wang/Documents/MyCode/mynanobananaapp/apps/frontend

scp dist.tar.gz root@106.14.160.150:/www/wwwroot/mynanobananaapp/apps/frontend/
```

然后SSH到服务器：
```bash
ssh root@106.14.160.150

cd /www/wwwroot/mynanobananaapp/apps/frontend
mv dist dist.bak
tar -xzf dist.tar.gz
```

---

## 🧪 验证部署

### 1. 清除浏览器缓存

重要！按 `Ctrl+Shift+R` 或 `Cmd+Shift+R` 强制刷新

### 2. 访问网站

```
http://nanobanana.100yse.com
```

### 3. 检查控制台

按 F12 打开开发者工具，查看：
- ✅ 无ReferenceError错误
- ✅ 看到登录页面
- ✅ 可以正常操作

---

## 🎯 快速命令汇总

```bash
# 本地Mac
cd /Users/wang/Documents/MyCode/mynanobananaapp
git pull origin master
cd apps/frontend
rm -rf dist node_modules/.vite
npm run build
tar -czf dist.tar.gz dist/

# 上传dist.tar.gz到服务器

# 服务器
cd /www/wwwroot/mynanobananaapp/apps/frontend
mv dist dist.bak
tar -xzf dist.tar.gz

# 浏览器强制刷新
Ctrl+Shift+R (或 Cmd+Shift+R)
```

---

## 🔄 如果还有问题

### 问题1：构建失败
```bash
# 清理node_modules重新安装
rm -rf node_modules package-lock.json
npm install
npm run build
```

### 问题2：还是空白
```bash
# 检查dist/index.html是否存在
ls -la apps/frontend/dist/

# 检查Nginx配置
# 确保root指向正确路径
```

### 问题3：API连接失败
```bash
# 检查后端是否运行
curl http://127.0.0.1:52036/api/health

# 检查Nginx代理配置
```

---

**现在请在您的Mac终端执行构建命令！**

