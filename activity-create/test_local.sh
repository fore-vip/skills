#!/bin/bash

# 本地测试 activity-create skill
# 模拟 npx skills add fore-vip/skills -s activity-create

echo "███████╗██╗ ██╗██╗██╗ ██╗ ███████╗"
echo "██╔════╝██║ ██╔╝██║██║ ██║ ██╔════╝"
echo "███████╗█████╔╝ ██║██║ ██║ ███████╗"
echo "╚════██║██╔═██╗ ██║██║ ██║ ╚════██║"
echo "███████║██║ ██╗██║███████╗███████║"
echo "╚══════╝╚═╝ ╚═╝╚═╝╚══════╝╚══════╝"
echo ""
echo "Testing activity-create skill locally..."
echo ""

# 检查 SKILL.md 是否存在
SKILL_FILE="/Users/codes/git/ai/skills/activity-create/SKILL.md"

if [ ! -f "$SKILL_FILE" ]; then
    echo "❌ SKILL.md not found at: $SKILL_FILE"
    exit 1
fi

echo "✅ SKILL.md found"
echo ""

# 解析 SKILL.md 头部信息
echo "📦 Skill Information:"
echo "─────────────────────────────────────"
grep -A 5 "^---" "$SKILL_FILE" | grep -E "^(name|description|version|license):" | sed 's/^/   /'
echo ""

# 测试 MCP 端点
echo "🧪 Testing MCP Endpoints:"
echo "─────────────────────────────────────"

# 测试 1: tools/list
echo -n "1. GET /mcp/tools/list ... "
TOOLS_RESPONSE=$(curl -s https://api.fore.vip/mcp/tools/list)
if echo "$TOOLS_RESPONSE" | grep -q '"jsonrpc":"2.0"'; then
    echo "✅ Pass"
else
    echo "❌ Fail"
    echo "   Response: $TOOLS_RESPONSE"
fi

# 测试 2: tools/call (创建测试活动)
echo -n "2. POST /mcp/tools/call ... "
TEST_RESPONSE=$(curl -s -X POST https://api.fore.vip/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_activity",
    "arguments": {
      "content": "本地测试活动",
      "start_time": 1711094400000,
      "end_time": 1711108800000,
      "address": "测试地址",
      "range": 0,
      "pay": false
    }
  }')

if echo "$TEST_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Pass"
    ACTIVITY_ID=$(echo "$TEST_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['content'][0]['text'])" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
    echo "   Activity ID: $ACTIVITY_ID"
else
    echo "❌ Fail"
    echo "   Response: $TEST_RESPONSE"
fi

echo ""
echo "─────────────────────────────────────"
echo ""

# 显示文档路径
echo "📚 Documentation:"
echo "   - SKILL.md:        $SKILL_FILE"
echo "   - SKILL_cn.md:     /Users/codes/git/ai/skills/activity-create/SKILL_cn.md"
echo "   - Test Plan:       /Users/codes/.jvs/.openclaw/workspace/MCP_TEST_PLAN.md"
echo "   - Test Report:     /Users/codes/.jvs/.openclaw/workspace/MCP_TEST_REPORT.md"
echo ""

# 模拟对话示例
echo "💬 Example Conversation:"
echo "─────────────────────────────────────"
echo "User: 我想创建一个周末 AI 体验活动"
echo ""
echo "Assistant: 好的！我来帮你创建这个 AI 体验活动。请问："
echo "   1. 活动什么时候开始？(日期和具体时间)"
echo "   2. 预计持续多久？(结束时间)"
echo "   3. 活动地点在哪里？(可选)"
echo "   4. 是否收取门票？(可选)"
echo ""
echo "─────────────────────────────────────"
echo ""

# 安装说明
echo "📦 Installation (when published):"
echo "   npx skills add fore-vip/skills -s activity-create"
echo ""
echo "   Or with flags:"
echo "   npx skills add fore-vip/skills -s activity-create --yes --global"
echo ""

echo "✅ Local test completed!"
