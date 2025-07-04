import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from core.nodes import register_node
from utils.ws import safe_send

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY not found – add it to .env")

client = AsyncOpenAI()

# ── Progress helper ─────────────────────────────
async def send_progress(send, request_id, progress, message):
    if send and request_id:
        await safe_send(send, {
            "type": "node-progress",
            "requestId": request_id,
            "progress": progress,
            "message": message
        })

# ── Handler ─────────────────────────────────────
async def generate_llm_response_handler(inputs, params=None, send=None, request_id=None):
    system_prompt = (inputs.get("system_prompt") or "").strip()
    user_prompt   = (inputs.get("user_prompt") or "").strip()
    model         = inputs.get("model") or "gpt-4o-mini"

    print(f"inputs: {inputs}")
    print(f"system_prompt: {system_prompt}")
    print(f"user_prompt: {user_prompt}")
    print(f"model: {model}")

    if not user_prompt:
        raise ValueError("User prompt is empty")

    await send_progress(send, request_id, 10, "Preparing LLM request...")

    messages = []
    if system_prompt:
        messages.append({ "role": "system", "content": system_prompt })
    messages.append({ "role": "user", "content": user_prompt })

    await send_progress(send, request_id, 30, f"Calling {model}...")

    rsp = await client.chat.completions.create(
        model=model,
        messages=messages
    )

    await send_progress(send, request_id, 80, "Processing response...")
    
    content = rsp.choices[0].message.content.strip()

    return {"response": content}

# ── Node registration ───────────────────────────
register_node(
    "generate_llm_response",
    {
        "version"    : "1.0.0",
        "type"       : "text",
        "displayName": "LLM Response",
        "showOutputOnEdge"  : False,
        "category"   : "AI",
        "clientOnly" : False,
        "inputs"     : ["system_prompt", "user_prompt", "model"],
        "outputs"    : ["response"],
        # "params"     : {
        #     "response": {
        #         "type": "string",
        #         "ui": "text_readonly",
        #         "default": ""
        #     }
        # },
        "handler"    : generate_llm_response_handler,
        "actions"    : [{ "label": "Delete", "action": "delete" }],
    },
)
