#!/bin/bash

echo "🚀 开始测试 nano-banana-hd 高清模型..."
echo "⏰ 开始时间: $(date '+%H:%M:%S')"
echo ""

START_TIME=$(date +%s)

curl -X POST https://api.openai-hk.com/v1/images/generations \
  -H 'Authorization: Bearer hk-z3pube100001739337bad3455bc8f18e6c1dfb50bfe5e8e3' \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nano-banana-hd",
    "prompt": "a beautiful sunset over the ocean with sailing boats",
    "n": 1,
    "size": "16x9"
  }' 2>&1

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo "⏱️ HD模型生成耗时: ${ELAPSED}秒"
echo "⏰ 结束时间: $(date '+%H:%M:%S')"
