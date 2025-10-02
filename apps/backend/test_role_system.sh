#!/bin/bash

# 测试角色权限系统的完整功能

echo "=== 角色权限系统功能测试 ==="
echo

# 1. 测试管理员登录
echo "1. 测试管理员用户登录..."
ADMIN_RESPONSE=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"Admin123!@#"}')

echo "响应: $ADMIN_RESPONSE"
ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ADMIN_TOKEN" ]; then
  echo "❌ 管理员登录失败"
else
  echo "✅ 管理员登录成功，Token: ${ADMIN_TOKEN:0:20}..."

  # 2. 测试管理员访问管理员API
  echo
  echo "2. 测试管理员访问管理员API (获取用户列表)..."
  SEARCH_RESULT=$(curl -s -X GET "http://localhost:5000/api/admin/users/search" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

  echo "响应: $SEARCH_RESULT"
  if echo "$SEARCH_RESULT" | grep -q "users"; then
    echo "✅ 管理员可以访问管理员API"
  else
    echo "❌ 管理员无法访问管理员API"
  fi
fi

echo
echo "3. 测试普通用户登录..."
USER_RESPONSE=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@test.com","password":"Test123!@#"}')

echo "响应: $USER_RESPONSE"
USER_TOKEN=$(echo $USER_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$USER_TOKEN" ]; then
  echo "⚠️  普通用户登录失败（可能用户不存在或密码错误）"
else
  echo "✅ 普通用户登录成功，Token: ${USER_TOKEN:0:20}..."

  # 4. 测试普通用户访问管理员API（应该被拒绝）
  echo
  echo "4. 测试普通用户访问管理员API (应该被拒绝)..."
  FORBIDDEN_RESULT=$(curl -s -X GET "http://localhost:5000/api/admin/users/search" \
    -H "Authorization: Bearer $USER_TOKEN")

  echo "响应: $FORBIDDEN_RESULT"
  if echo "$FORBIDDEN_RESULT" | grep -q -E "权限|forbidden|INSUFFICIENT"; then
    echo "✅ 普通用户被正确拒绝访问管理员API"
  else
    echo "❌ 普通用户可以访问管理员API（权限控制失效！）"
  fi
fi

echo
echo "=== 测试完成 ==="