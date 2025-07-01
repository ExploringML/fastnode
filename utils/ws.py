# utils/ws.py
import json

async def safe_send(send, msg: dict):
    try:
        if not isinstance(msg, dict):
            raise TypeError(f"safe_send expected dict, got {type(msg)}")
        await send(json.dumps(msg))
    except Exception as e:
        print("❌ Failed to send WebSocket message:", e)
