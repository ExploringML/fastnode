"""
WebSocket message routing for FastNode
──────────────────────────────────────
• evaluate-node   → execute a single node handler (used by traversal.js)
• run-workflow    → execute a whole DAG  (your existing logic)
• run-node        → legacy single-node call (kept for completeness)
"""

from core.nodes import NODE_REGISTRY
from core.executor import evaluate_workflow
from utils.ws import safe_send
import inspect

# ────────────────────────────────────────────────────────────────
# 1. Helper – call handler safely and emit node-result frame
# ────────────────────────────────────────────────────────────────
async def _dispatch_node(handler, *, req_id, node_id, inputs, params, send):
    print(f"🟡 Dispatching {handler.__name__}, async={inspect.iscoroutinefunction(handler)}")

    try:
        sig = inspect.signature(handler)
        kwargs = {}

        if 'send' in sig.parameters:
            kwargs['send'] = send
        if 'request_id' in sig.parameters:
            kwargs['request_id'] = req_id

        if inspect.iscoroutinefunction(handler):
            result = await handler(inputs, params, **kwargs)
        else:
            result = handler(inputs, params, **kwargs)

        await safe_send(send, {
            "type": "node-result",
            "requestId": req_id,
            "nodeId": node_id,
            "result": result,
        })

    except Exception as exc:
        await safe_send(send, {
            "type": "node-result",
            "requestId": req_id,
            "nodeId": node_id,
            "error": str(exc),
        })

# ────────────────────────────────────────────────────────────────
# 2. Single-node evaluator  (traversal.js)
# ────────────────────────────────────────────────────────────────
async def handle_evaluate_node(payload, send):
    node_type = payload.get("nodeType")
    node_meta = NODE_REGISTRY.get(node_type)

    if not node_meta:
        await safe_send(
            send,
            {
                "type": "node-result",
                "requestId": payload.get("requestId"),
                "error": f"Unknown nodeType: {node_type}",
            },
        )
        return

    handler = node_meta.get("handler")
    if not callable(handler):
        await safe_send(
            send,
            {
                "type": "node-result",
                "requestId": payload.get("requestId"),
                "error": f"No handler for nodeType: {node_type}",
            },
        )
        return

    await _dispatch_node(
        handler,
        req_id=payload.get("requestId"),
        node_id=payload.get("nodeId"),
        inputs=payload.get("inputs", {}),
        params=payload.get("params", {}),
        send=send,
    )

# ────────────────────────────────────────────────────────────────
# 3. Full-workflow evaluator  (unchanged)
# ────────────────────────────────────────────────────────────────
async def handle_run_workflow(payload, send):
    workflow = payload.get("workflow")
    target_ids = payload.get("targetIds", [])

    if not workflow:
        await safe_send(send, {"type": "error", "message": "No workflow provided."})
        return

    await safe_send(send, {"type": "status", "status": "evaluating"})

    try:
        result = evaluate_workflow(workflow, NODE_REGISTRY, target_ids)
        await safe_send(
            send,
            {
                "type": "workflow-result",
                "nodes": result["nodes"],
                "edges": result["edges"],
            },
        )
    except Exception as exc:
        await safe_send(send, {"type": "error", "message": str(exc)})

# ────────────────────────────────────────────────────────────────
# 4. Legacy single-node call (kept intact)
# ────────────────────────────────────────────────────────────────
async def handle_run_node(payload, send):
    node_name = payload.get("node")
    inputs = payload.get("inputs", {})

    node_meta = NODE_REGISTRY.get(node_name)
    if not node_meta:
        await safe_send(
            send,
            {"type": "error", "message": f"Unknown node: {node_name}"},
        )
        return

    handler = node_meta.get("handler")
    if not callable(handler):
        await safe_send(
            send,
            {"type": "error", "message": f"No handler for node: {node_name}"},
        )
        return

    await _dispatch_node(
        handler,
        req_id=None,
        node_id=node_name,
        inputs=inputs,
        params=node_meta.get("params", {}),
        send=send,
    )

# ────────────────────────────────────────────────────────────────
# 5.  Router – call from your WebSocket endpoint
# ────────────────────────────────────────────────────────────────
MESSAGE_HANDLERS = {
    "evaluate-node": handle_evaluate_node,
    "run-workflow": handle_run_workflow,
    "run-node": handle_run_node,
}

# In the file where you accept websocket connections:
#
#   async for msg in websocket:
#       data = json.loads(msg)
#       handler = MESSAGE_HANDLERS.get(data.get("type"))
#       if handler:
#           await handler(data, websocket.send)
#       else:
#           await safe_send(websocket.send, {
#               "type": "error",
#               "message": f"Unknown WS message type: {data.get('type')}"
#           })
