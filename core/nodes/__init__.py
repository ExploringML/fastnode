import importlib, pkgutil
import json

NODE_REGISTRY = {}

def register_node(name, meta):
    if name in NODE_REGISTRY:
        print(f"⚠️ Duplicate node name registered: {name}")
    NODE_REGISTRY[name] = meta

# auto-import all node modules
for mod in pkgutil.walk_packages(__path__, prefix=f"{__name__}."):
    importlib.import_module(mod.name)

def get_node_registry():
    try:
        json.dumps(NODE_REGISTRY)
    except TypeError as e:
        print("🧨 JSON serialization error:", e)
        import pprint
        pprint.pprint(NODE_REGISTRY)

    clean_nodes = {}

    for name, meta in NODE_REGISTRY.items():
        clean_meta = {}

        for k, v in meta.items():
            if callable(v):
                print(f"🔍 Skipping callable key '{k}' in node '{name}'")
                continue
            if k == "handler":
                print(f"🔍 Skipping explicit 'handler' key in node '{name}'")
                continue
            clean_meta[k] = v

        clean_nodes[name] = clean_meta

    return {
        "version": "1.0.0",
        "nodes": clean_nodes
    }
