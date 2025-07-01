def evaluate_workflow(workflow, registry, target_ids):
    from collections import deque

    nodes = {n["id"]: n for n in workflow["nodes"]}
    edges = workflow["edges"]

    # Build graph: targetId -> list of input nodes
    graph = {}
    for edge in edges:
        graph.setdefault(edge["target"], []).append({
            "source": edge["source"],
            "handle": edge["targetHandle"]
        })

    results = {}
    visited = set()
    queue = deque(target_ids)

    while queue:
        id = queue.popleft()
        if id in visited:
            continue
        visited.add(id)

        node = nodes.get(id)
        if not node:
            continue

        meta = registry.get(node["data"]["type"])
        if not meta or "handler" not in meta:
            continue

        inputs = {}
        for edge in graph.get(id, []):
            src_id = edge["source"]
            src_node = nodes.get(src_id)
            if src_node:
                inputs[edge["handle"]] = src_node["data"].get("value")

        output = meta["handler"](inputs)
        node["data"]["value"] = next(iter(output.values()))  # crude but works
        results[id] = output

    return {
        "nodes": list(nodes.values()),
        "edges": edges
    }
