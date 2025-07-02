from core.nodes import register_node

register_node("textarea_input", {
    "version": "1.0.0",
    "type": "text",
    "displayName": "Text Input",
    "category": "Core",
    "clientOnly": True,
    "outputs": ["text"],
	"showOutputOnEdge": False,
    "params": {
        "text": {
            "type": "string",
            "ui": "text_textarea",
            "default": "",
        }
    },
    "actions": [
        {"label": "Reset", "action": "reset"},
        {"label": "Delete", "action": "delete"},
    ]
})
