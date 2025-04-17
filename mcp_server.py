from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 1) MCP Tools metadata
TOOLS = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather information for a specific location. Please use English city names (e.g., 'Seoul' instead of '서울', 'New York' instead of '뉴욕').",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name in English (e.g., Seoul, Tokyo, London)"}
            },
            "required": ["location"]
        }
    }
    # {
    #     "name": "get_stock_data",
    #     "description": "Get the current stock data for a specific symbol.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "symbol": {"type": "string", "description": "Stock symbol"}
    #         },
    #         "required": ["symbol"]
    #     }
    # }
]

# Weather API endpoint (could be localhost or external URL)
WEATHER_API_URL = os.getenv("WEATHER_API_URL", "http://localhost:5001/get_weather")
# STOCK_API_URL = os.getenv("STOCK_API_URL", "http://localhost:5002/stock")

@app.route("/mcp", methods=["POST"])
def mcp_endpoint():
    req = request.get_json()
    jsonrpc = req.get("jsonrpc")
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    # Basic JSON-RPC validation
    if jsonrpc != "2.0" or not req_id:
        return jsonify({"jsonrpc": "2.0", "id": req_id,
                        "error": {"code": -32600, "message": "Invalid Request"}}), 400

    # tools/list: return registered tools
    if method == "tools/list":
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": TOOLS})

    # tools/call: invoke a specific tool
    if method == "tools/call":
        tool_name = params.get("name")
        tool_input = params.get("input", {})

        if tool_name == "get_current_weather":
            try:
                # Call the weather API
                resp = requests.post(WEATHER_API_URL, json=tool_input)
                resp.raise_for_status()
                weather_data = resp.json()
                # Return as tool_result
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": weather_data
                })
            except requests.exceptions.RequestException as e:
                print(f"Error calling Weather API: {e}")
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32000,
                        "message": f"Weather API error: {str(e)}"
                    }
                }), 500
        # elif tool_name == "get_stock_data":
        #     resp = requests.get(f"{STOCK_API_URL}/{tool_input['symbol']}")
        #     resp.raise_for_status()
        #     stock_data = resp.json()
        #     return jsonify({
        #         "jsonrpc": "2.0",
        #         "id": req_id,
        #         "result": stock_data
        #     })
        else:
            return jsonify({"jsonrpc": "2.0", "id": req_id,
                            "error": {"code": -32601, "message": "Tool not found"}}), 404
    # Method not supported
    return jsonify({"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32601, "message": "Method not found"}}), 404

if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)