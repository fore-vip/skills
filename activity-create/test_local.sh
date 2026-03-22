#!/bin/bash

# activity-create skill 本地测试脚本
# 用于验证 MCP Server 调用逻辑

echo "========================================="
echo "activity-create skill 本地测试"
echo "========================================="
echo ""

# MCP 端点
MCP_URL="https://api.fore.vip/mcp/create_activity"

echo "测试 1: 创建活动（成功场景）"
echo "-------------------------------------------"

RESPONSE=$(curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "skill 测试活动",
    "start_time": 1711094400000,
    "address": "测试地址",
    "wx": "test123"
  }')

echo "响应：$RESPONSE" | jq .

if echo "$RESPONSE" | jq -e '.success == true' > /dev/null 2>&1; then
    echo "✅ 测试 1 通过：创建活动成功"
    ACTIVITY_ID=$(echo "$RESPONSE" | jq -r '.id')
    echo "活动 ID: $ACTIVITY_ID"
    echo "活动 URL: https://fore.vip/st?id=$ACTIVITY_ID"
else
    echo "❌ 测试 1 失败：创建活动失败"
    echo "错误：$(echo "$RESPONSE" | jq -r '.error.message')"
fi

echo ""
echo "测试 2: 参数验证（content 太短）"
echo "-------------------------------------------"

RESPONSE=$(curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "A",
    "start_time": 1711094400000,
    "address": "测试地址",
    "wx": "test123"
  }')

echo "响应：$RESPONSE" | jq .

if echo "$RESPONSE" | jq -e '.success == false' > /dev/null 2>&1; then
    echo "✅ 测试 2 通过：参数验证正确"
else
    echo "❌ 测试 2 失败：应该拒绝短 content"
fi

echo ""
echo "测试 3: 参数验证（缺少必需参数）"
echo "-------------------------------------------"

RESPONSE=$(curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "测试活动",
    "start_time": 1711094400000
  }')

echo "响应：$RESPONSE" | jq .

if echo "$RESPONSE" | jq -e '.success == false' > /dev/null 2>&1; then
    echo "✅ 测试 3 通过：缺少参数验证正确"
else
    echo "❌ 测试 3 失败：应该拒绝缺少必需参数的请求"
fi

echo ""
echo "========================================="
echo "测试完成"
echo "========================================="
