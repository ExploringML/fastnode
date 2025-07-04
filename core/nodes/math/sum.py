from core.nodes import register_node

# 1. Define the actual Python handler for this node
def sum_handler(inputs, params=None):
    x = inputs.get("x", 0)
    y = inputs.get("y", 0)
    return {"result": x + y}

# 2. Register the node including the handler reference
register_node("sum", {
    "version": "1.0.0",
    "type": "number",
    "displayName": "Sum",
    "category": "Core",
    "clientOnly": False,
    "inputs": ["x", "y"],
    "outputs": ["result"],
    "handler": sum_handler,  # 🔧 Link to backend execution
    "actions": [
        {"label": "Reset", "action": "reset"},
        {"label": "Delete", "action": "delete"},
    ]
})
