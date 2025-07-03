import io, base64, requests, os
from PIL import Image
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
from core.nodes import register_node
from utils.ws import safe_send

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY not found – add it to .env")
# client = OpenAI()
client = AsyncOpenAI()

# ── Progress helper ───────────────────────────────────────────────
async def send_progress(send, request_id, progress, message):
    """Send progress update if send function is available"""
    if send and request_id:
        await safe_send(send, {
            "type": "node-progress",
            "requestId": request_id,
            "progress": progress,
            "message": message
        })

# ── backend handler ───────────────────────────────────────────────
async def generate_image_handler(inputs, params=None, send=None, request_id=None):
    prompt = (inputs.get("prompt") or "").strip()
    model  = inputs.get("model") or "gpt-image-1"

    if not prompt:
        raise ValueError("Prompt is empty")

    # Progress: Starting
    await send_progress(send, request_id, 10, "Initializing image generation...")

    # Progress: Calling OpenAI
    await send_progress(send, request_id, 30, f"Requesting image from {model}...")

    rsp = await client.images.generate(
        model   = model,
        prompt  = prompt,
        n       = 1,
        size    = "1024x1024",
        quality = "low",
    )

    # Progress: Processing response
    await send_progress(send, request_id, 70, "Processing response...")

    data = rsp.data[0]

    # Newer API gives base-64 directly
    if getattr(data, "b64_json", None):
        await send_progress(send, request_id, 90, "Encoding image...")
        return {"image": f"data:image/png;base64,{data.b64_json}"}

    # Fallback: download the URL, re-encode
    if getattr(data, "url", None):
        await send_progress(send, request_id, 80, "Downloading image...")
        png = Image.open(io.BytesIO(requests.get(data.url).content))
        
        await send_progress(send, request_id, 90, "Encoding image...")
        buf = io.BytesIO(); png.save(buf, format="PNG")
        return {"image": f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"}

    raise RuntimeError("OpenAI returned no image data")

# ── node registration ─────────────────────────────────────────────
register_node(
    "generate_image",
    {
        "version"    : "1.0.0",
        "type"       : "image",
        "displayName": "Image Gen",
        "category"   : "AI",
        "clientOnly" : False,               # ← runs on server
        "inputs"     : ["prompt", "model"],
        "outputs"    : [],
        "params"     : {
            "image": {
                "type": "string",
                "ui": "image",
                "default": ""
            }
        },
        "handler"    : generate_image_handler,
        "showOutputOnEdge": False,
        "actions"    : [ { "label": "Delete", "action": "delete" } ],
    },
)