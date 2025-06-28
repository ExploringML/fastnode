import json, io, base64, glob, os
import requests
from fasthtml.common import *
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY not found – add it to .env")
client = OpenAI(api_key=openai_api_key)

# Load built asset files
assets_dir = "static/reactflow/assets"
js = os.path.basename(glob.glob(f"{assets_dir}/index-*.js")[0])
css = os.path.basename(glob.glob(f"{assets_dir}/index-*.css")[0])

hdrs = (
    Script(src="https://cdn.tailwindcss.com"),
    Link(rel="stylesheet", href=f"reactflow/assets/{css}", type="text/css"),
    Script(type="module", src=f"reactflow/assets/{js}"),
)
app, rt = fast_app(pico=False, static_path="static", hdrs=hdrs, exts='ws')

@rt
def index():
    return Div("Production", Div(id="root", style="width:100vw; height:100vh;"))

# ✅ JSON-safe WebSocket sender
async def safe_send(send, msg: dict):
    try:
        if not isinstance(msg, dict):
            raise TypeError(f"safe_send expected dict, got {type(msg)}")
        await send(json.dumps(msg))
    except Exception as e:
        print("❌ Failed to send WebSocket message:", e)

@app.ws("/ws")
async def ws(data, send):
    print("✅ WebSocket message received:", data)

    if data.get("type") != "run-workflow":
        return

    prompt = data.get("prompt", "").strip()
    model = data.get("model", "gpt-image-1")

    if not prompt:
        await safe_send(send, {
            "type": "error",
            "message": "Prompt is empty. Please enter a prompt.",
        })
        return

    # 🌀 Notify frontend we're generating
    await safe_send(send, {
        "type": "status",
        "status": "generating"
    })

    try:
        rsp = client.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="low",
        )

        b64 = getattr(rsp.data[0], "b64_json", None)
        if b64:
            await safe_send(send, {
                "type": "image",
                "data": b64,
                "encoding": "base64"
            })
            return

        url = getattr(rsp.data[0], "url", None)
        if url:
            img_bytes = requests.get(url).content
            await safe_send(send, {
                "type": "image",
                "data": base64.b64encode(img_bytes).decode("utf-8"),
                "encoding": "base64"
            })
            return

        raise RuntimeError("No image data in response.")

    except Exception as err:
        msg = str(err)
        print("🧨 Error generating image:", msg)

        # Optional: send error status
        await safe_send(send, {
            "type": "status",
            "status": "error",
            "message": msg
        })

        # Fallback placeholder image
        img = Image.new("RGB", (512, 512), (40, 40, 40))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((20, 200), "Error:", fill=(255, 80, 80), font=font)
        draw.text((20, 220), msg[:200], fill=(200, 200, 200), font=font)
        buf = io.BytesIO(); img.save(buf, format="PNG")

        await safe_send(send, {
            "type": "image",
            "data": base64.b64encode(buf.getvalue()).decode("utf-8"),
            "encoding": "base64"
        })

serve()
