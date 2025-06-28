import importlib, pkgutil

NODE_REGISTRY = {}

def register_node(name, meta):
    NODE_REGISTRY[name] = meta

# auto-import all node modules
for mod in pkgutil.walk_packages(__path__, prefix=f"{__name__}."):
    importlib.import_module(mod.name)

def get_node_registry():
    return {"version": "1.0.0", "nodes": NODE_REGISTRY}
