import os
import json
import requests
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Load keys and endpoints
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Retrieve tool list dynamically via MCP
def list_tools():
    payload = {
        "jsonrpc": "2.0",
        "id": "list-tools-1",
        "method": "tools/list",
        "params": {}
    }
    resp = requests.post(MCP_SERVER_URL, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json().get("result", [])

# Invoke a tool via MCP
def call_tool(name, tool_input, call_id="call-1"):
    payload = {
        "jsonrpc": "2.0",
        "id": call_id,
        "method": "tools/call",
        "params": {"name": name, "input": tool_input}
    }
    resp = requests.post(MCP_SERVER_URL, json=payload, timeout=5)
    resp.raise_for_status()
    return resp.json().get("result")

# Main chat endpoint
def ask_claude(query):
    # 1) Fetch available tools
    tools = list_tools()

    # 2) Ask Claude with tool definitions
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system="You are a helpful assistant.",
        messages=[{"role": "user", "content": query}],
        tools=tools
    )

    # 3) Check for tool_use
    tool_use = next((block for block in response.content if block.type == "tool_use"), None)

    if tool_use:
        name = tool_use.name
        inp = tool_use.input
        # Invoke the tool via MCP
        result = call_tool(name, inp, call_id=tool_use.id)

        # 4) Send tool_result back
        followup_messages = [
            {"role": "user", "content": query},
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result, ensure_ascii=False)
                }
            ]}
        ]
        followup = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=followup_messages
        )
        return followup

    # 5) No tool usage, return direct response
    return response

if __name__ == "__main__":
    print("Claude MCP client 시작. 종료하려면 'exit' 입력.")
    while True:
        prompt = input("질문: ")
        if prompt.strip().lower() in ["exit", "quit"]:
            break
        answer = ask_claude(prompt)
        for block in answer.content:
            if block.type == "text":
                print("Assistant: ", block.text)