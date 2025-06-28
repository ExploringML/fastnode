from core.nodes import register_node  # your global registry

register_node("number", {
    "version": "1.0.0",
    "type": "number",
    "displayName": "Number",
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
    }
})
