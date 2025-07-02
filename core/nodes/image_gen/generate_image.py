import io, base64, requests, os
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv
from core.nodes import register_node

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY not found – add it to .env")
client = OpenAI()                       # picks up OPENAI_API_KEY from env

# ── backend handler ───────────────────────────────────────────────
def generate_image_handler(inputs, params=None):
    prompt = (inputs.get("prompt") or "").strip()
    model  = inputs.get("model") or "gpt-image-1"

    if not prompt:
        raise ValueError("Prompt is empty")

    rsp = client.images.generate(
        model   = model,
        prompt  = prompt,
        n       = 1,
        size    = "1024x1024",
        quality = "low",
    )

    data = rsp.data[0]

    # Newer API gives base-64 directly
    if getattr(data, "b64_json", None):
        return {"image": f"data:image/png;base64,{data.b64_json}"}

    # Fallback: download the URL, re-encode
    if getattr(data, "url", None):
        png = Image.open(io.BytesIO(requests.get(data.url).content))
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
        "outputs"    : ["image"],
        "params"     : {},
        "handler"    : generate_image_handler,
        "showOutputOnEdge": False,
        "actions"    : [ { "label": "Delete", "action": "delete" } ],
    },
)
