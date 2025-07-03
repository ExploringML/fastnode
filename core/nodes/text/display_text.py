from core.nodes import register_node  # your global registry

register_node("display_text", {
    "version": "1.0.0",
    "type": "text",
    "displayName": "Result (text)",
    "category": "Core",
    "clientOnly": True,
	"inputs": ["value"],
	    "params": {
        "text": {
            "type": "string",
            "ui": "text_readonly",
            "default": ""
        }
    },
    "actions": [
      {"label": "Reset", "action": "reset"},
      {"label": "Delete", "action": "delete"},
    ]
})
