#!/usr/bin/env python3
"""
移除generate.py中的智能推荐API代码
"""

# 读取文件
with open('/Users/wang/Documents/MyCode/mynanobananaapp/apps/backend/app/views/generate.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 保留前815行,删除第816行之后的所有内容
new_lines = lines[:815]

# 写回文件
with open('/Users/wang/Documents/MyCode/mynanobananaapp/apps/backend/app/views/generate.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ 智能推荐API代码已从generate.py中移除")
print(f"原始行数: {len(lines)}")
print(f"删除后行数: {len(new_lines)}")
print(f"删除了 {len(lines) - len(new_lines)} 行代码")
