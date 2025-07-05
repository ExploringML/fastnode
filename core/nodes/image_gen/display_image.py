from core.nodes import register_node

# This node has no backend handler because it's client-side.
# Its only job is to define the UI and its connections.

register_node(
    "display_image",
    {
        "version": "1.0.0",
        "displayName": "Display Image",
        "category": "Core",
        "clientOnly": True,
        "inputs": ["image"],
        "outputs": ["image"],
        "params": {
            "image": {
                "type": "string",
                "ui": "image",
                "default": ""
            }
        },
        "actions": [
            {"label": "Delete", "action": "delete"},
        ]
    },
)