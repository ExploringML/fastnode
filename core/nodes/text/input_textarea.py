from core.nodes import register_node

register_node("textarea_input", {
    "version": "1.0.0",
    "type": "text",
    "displayName": "Prompt",
    "category": "Core",
    "clientOnly": True,
    "outputs": ["prompt"],
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
