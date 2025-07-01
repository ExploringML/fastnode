from core.nodes import register_node  # your global registry

register_node("number3", {
    "version": "1.0.0",
    "type": "number",
    "displayName": "Number 3",
    "category": "Core",
    "clientOnly": True,
    "outputs": ["value", "value2", "value3"],
    "params": {
        "value": {
            "type": "int",
            "ui": "number",
            "default": 0,
            "min": -999,
            "max": 999
        },
        "value2": {
            "type": "int",
            "ui": "number",
            "default": 1,
            "min": -999,
            "max": 999
        },
        "value3": {
            "type": "int",
            "ui": "number",
            "default": 2,
            "min": -999,
            "max": 999
        },
    },
     "actions": [
        {"label": "Reset", "action": "reset"},
        {"label": "Delete", "action": "delete"},
        {"label": "Log ID", "action": "logId"},
    ]
})
