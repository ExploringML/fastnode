"""
WebSocket message routing for FastNode
──────────────────────────────────────
• evaluate-node   → execute a single node handler (used by traversal.js)
• run-workflow    → execute a whole DAG  (your existing logic)
• run-node        → legacy single-node call (kept for completeness)
"""

from core.nodes import NODE_REGISTRY
from utils.ws import safe_send
import inspect

# ────────────────────────────────────────────────────────────────
# 1. Helper – call handler safely and emit node-result frame
# ────────────────────────────────────────────────────────────────
async def _dispatch_node(app, handler, *, req_id, node_id, inputs, params, send):
    print(f"🟡 Dispatching {handler.__name__}, async={inspect.iscoroutinefunction(handler)}")

    try:
        sig = inspect.signature(handler)
        kwargs = {}
        # Prepare arguments that the handler might optionally accept
        if 'send' in sig.parameters: kwargs['send'] = send
        if 'request_id' in sig.parameters: kwargs['request_id'] = req_id

        # Prepare the main arguments, including the 'app' context if needed
        main_args = {"inputs": inputs, "params": params}
        if 'app' in sig.parameters:
            main_args['app'] = app

        # Call the handler with the correct set of arguments
        if inspect.iscoroutinefunction(handler):
            result = await handler(**main_args, **kwargs)
        else:
            result = handler(**main_args, **kwargs)

        await safe_send(send, {
            "type": "node-result",
            "requestId": req_id,
            "nodeId": node_id,
            "result": result,
        })

    except Exception as exc:
        import traceback
        traceback.print_exc()
        await safe_send(send, {
            "type": "node-result",
            "requestId": req_id,
            "nodeId": node_id,
            "error": str(exc),
        })

# ────────────────────────────────────────────────────────────────
# 2. Single-node evaluator  (traversal.js)
# ────────────────────────────────────────────────────────────────
async def handle_evaluate_node(app, payload, send):
    node_type = payload.get("nodeType")
    node_meta = NODE_REGISTRY.get(node_type)

    if not node_meta:
        # ... (error handling for unknown node is the same)
        return

    handler = node_meta.get("handler")
    if not callable(handler):
        # ... (error handling for missing handler is the same)
        return

    # Pass 'app' down to the dispatcher
    await _dispatch_node(
        app,
        handler,
        req_id=payload.get("requestId"),
        node_id=payload.get("nodeId"),
        inputs=payload.get("inputs", {}),
        params=payload.get("params", {}),
        send=send,
    )

# ────────────────────────────────────────────────────────────────
# 3. Full-workflow evaluator (needs 'app' for its nodes)
# ────────────────────────────────────────────────────────────────
async def handle_run_workflow(app, payload, send):
    # This handler is not fully implemented in the provided code,
    # but it will also need the 'app' object to pass to its nodes.
    # For now, we'll just acknowledge it.
    await safe_send(send, {"type": "error", "message": "'run-workflow' not fully implemented yet."})


# ────────────────────────────────────────────────────────────────
# 4. Legacy single-node call (kept intact but now needs 'app')
# ────────────────────────────────────────────────────────────────
async def handle_run_node(app, payload, send):
    node_name = payload.get("node")
    # ... (code to find node_meta and handler is the same) ...

    # Pass 'app' down to the dispatcher
    await _dispatch_node(
        app,
        handler,
        req_id=None,
        node_id=node_name,
        inputs=payload.get("inputs", {}),
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