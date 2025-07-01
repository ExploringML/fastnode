from core.nodes import NODE_REGISTRY
from utils.ws import safe_send
from core.executor import evaluate_workflow

async def handle_evaluate_node(data, send):
    node_type = data.get("nodeType")
    node_id = data.get("nodeId")
    inputs = data.get("inputs", {})
    params = data.get("params", {})
    req_id = data.get("requestId")

    if not node_type or node_type not in NODE_REGISTRY:
        await safe_send(send, {
            "type": "node-result",
            "requestId": req_id,
            "error": f"Unknown nodeType: {node_type}"
        })
        return

    handler = NODE_REGISTRY[node_type].get("handler")
    if not callable(handler):
        await safe_send(send, {
            "type": "node-result",
            "requestId": req_id,
            "error": f"No handler for nodeType: {node_type}"
        })
        return

    try:
        result = handler(inputs, params)
        await safe_send(send, {
            "type": "node-result",
            "requestId": req_id,
            "nodeId": node_id,
            "result": result
        })
    except Exception as e:
        await safe_send(send, {
            "type": "node-result",
            "requestId": req_id,
            "error": str(e)
        })

# Handles a full workflow execution request
async def handle_run_workflow(data, send):
    workflow = data.get("workflow")
    target_ids = data.get("targetIds", [])

    if not workflow:
        await safe_send(send, {
            "type": "error",
            "message": "No workflow provided."
        })
        return

    await safe_send(send, {
        "type": "status",
        "status": "evaluating"
    })

    try:
        result = evaluate_workflow(workflow, NODE_REGISTRY, target_ids)

        await safe_send(send, {
            "type": "workflow-result",
            "nodes": result["nodes"],
            "edges": result["edges"]
        })

    except Exception as err:
        await safe_send(send, {
            "type": "error",
            "message": str(err)
        })

# Handles a single node execution (bypasses workflow DAG)
async def handle_run_node(data, send):
    node_name = data.get("node")
    inputs = data.get("inputs", {})

    node = NODE_REGISTRY.get(node_name)
    if not node:
        await safe_send(send, {
            "type": "error",
            "message": f"Unknown node: {node_name}"
        })
        return

    handler = node.get("handler")
    if not callable(handler):
        await safe_send(send, {
            "type": "error",
            "message": f"No valid handler for node: {node_name}"
        })
        return

    try:
        outputs = handler(inputs)
        await safe_send(send, {
            "type": "node-result",
            "node": node_name,
            "outputs": outputs
        })
    except Exception as e:
        await safe_send(send, {
            "type": "error",
            "node": node_name,
            "message": str(e)
        })
