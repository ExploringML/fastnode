from core.nodes import register_node

register_node("image_model_selector", {
    "version": "1.0.0",
    "type": "image_gen",
    "displayName": "Image Model",
    "category": "Core",
    "clientOnly": True,
    "outputs": ["model"],
    "showOutputOnEdge": False,
    "params": {
        "model": {
            "type": "string",
            "ui": "select",
            "default": "gpt-image-1",
            "options": [ 
                ["gpt-image-1",   "gpt-image-1"],
                ["dall-e-3",      "DALL·E 3"],
            ],
        }
    },
    "actions": [
        { "label": "Reset",  "action": "reset" },
        { "label": "Delete", "action": "delete" },
    ]
})
