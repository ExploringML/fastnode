from core.nodes import register_node

# ✅ Define options as a list of [value, label] pairs
# This lets you show a user-friendly name in the UI.
MODEL_OPTIONS = [
    ["runwayml/stable-diffusion-v1-5", "Stable Diffusion 1.5"],
    ["stabilityai/stable-diffusion-2-1-base", "Stable Diffusion 2.1"]
]

register_node("load_sd_model", {
    "version": "1.0.0",
    "type": "image_gen",
    "displayName": "Load SD Model",
    "category": "AI",
    "clientOnly": True,
    "outputs": ["model"],
    "showOutputOnEdge": False,
    "params": {
        "model": {
            "type": "string",
            "ui": "select",
            "options": MODEL_OPTIONS,
            "default": MODEL_OPTIONS[0][0]
        }
    },
    "actions": [
        {"label": "Reset", "action": "reset"},
        {"label": "Delete", "action": "delete"},
    ]
})