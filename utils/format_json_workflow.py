DEFAULT_META = {
    "version": "1.0.0",
    "category": "Core",
    "clientOnly": False,
    "params": {},
    "actions": [
        {"label": "Reset", "action": "reset"},
        {"label": "Delete", "action": "delete"}
    ]
}

def normalize_node_meta(node):
    meta = node.get("data", {}).get("meta", {})
    # Merge defaults only for missing keys
    normalized_meta = {**DEFAULT_META, **meta}
    node["data"]["meta"] = normalized_meta
    return node
