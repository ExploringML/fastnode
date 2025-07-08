from core.nodes import register_node
from pathlib import Path

# This function should scan your cache, but we'll ensure the correct default
def get_cached_model_options():
    hf_cache_dir = Path.home() / ".cache/huggingface/hub"
    if not hf_cache_dir.is_dir(): return []
    options = []
    for p in hf_cache_dir.glob("models--*"):
        if p.is_dir() and "stable-diffusion" in p.name:
            hub_id = p.name[len("models--"):].replace("--", "/")
            options.append([hub_id, hub_id])
    return options

CACHED_MODEL_OPTIONS = get_cached_model_options()
# ✅ Set the default to the exact ID from your working script
DEFAULT_MODEL = "sd-legacy/stable-diffusion-v1-5"

register_node(
    "load_sd_model",
    {
        "displayName": "Load SD Model",
        "category": "AI",
        "showOutputOnEdge": False,
        "clientOnly": True,
        "outputs": ["model"],
        "params": {
            "model": {
                "ui": "select", 
                "options": CACHED_MODEL_OPTIONS,
                "default": DEFAULT_MODEL
            }
        },
        "actions": [{"label": "Delete", "action": "delete"}]
    }
)