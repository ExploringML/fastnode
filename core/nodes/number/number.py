from core.nodes import register_node  # your global registry

register_node("number", {
    "version": "1.0.0",
    "type": "number",
    "displayName": "Number 1",
    "category": "Core",
    "clientOnly": True,
    "outputs": ["value"],
    "params": {
        "value": {
            "type": "int",
            "ui": "number",
            "default": 0,
            "min": -999,
            "max": 999
        }
    },
     "actions": [
        {"label": "Reset", "action": "reset"},
        {"label": "Delete", "action": "delete"},
        {"label": "Log ID", "action": "logId"},
    ]
})
