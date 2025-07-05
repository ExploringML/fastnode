import base64
from io import BytesIO
import torch
from core.nodes import register_node
from fasthtml.common import FastHTML
from utils.ws import safe_send

# --- The On-Demand Sampler Handler ---
async def sd_sampler_handler(app: FastHTML, inputs, params, send=None, request_id=None):
    # 1. Get the model name from the upstream "Load Model" node
    model_name = inputs.get("model_name")
    if not model_name:
        raise ValueError("A 'model_name' input is required.")

    # 2. Access the global manager and load the model ON-DEMAND
    model_manager = app.state.model_manager
    pipe = await model_manager.load_model(model_name)
    if not pipe:
        raise RuntimeError(f"Failed to load model: {model_name}")

    # 3. Get generation parameters
    prompt = inputs.get("prompt", "")
    negative_prompt = inputs.get("negative_prompt", "")
    steps = int(params.get("steps", 20))
    guidance = float(params.get("guidance", 7.5))
    seed = int(params.get("seed", -1))
    
    generator = torch.Generator("cuda").manual_seed(seed) if seed != -1 else None

    # 4. Define the progress callback to send live updates
    async def progress_callback(step, timestep, latents):
        progress = int((step / steps) * 100)
        if send and request_id:
            await safe_send(send, {
                "type": "node-progress",
                "nodeId": inputs.get("id"),
                "requestId": request_id,
                "progress": progress,
                "message": f"Step {step+1}/{steps}"
            })

    # 5. Run the model
    image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        guidance_scale=guidance,
        generator=generator,
        callback_on_step_end=progress_callback
    ).images[0]
    
    # 6. Convert and return the final image
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return {"image": f"data:image/png;base64,{img_str}"}


# --- Node Registration ---
register_node(
    "sd_sampler",
    {
        "displayName": "SD Sampler",
        "category": "AI",
        "params": {
            "steps": {"ui": "number", "default": 20, "min": 1, "max": 100},
            "guidance": {"ui": "number", "default": 7.5, "min": 1, "max": 20, "step": 0.1},
            "seed": {"ui": "number", "default": -1}
        },
        "inputs": ["model_name", "prompt", "negative_prompt"],
        "outputs": ["image"],
        "handler": sd_sampler_handler,
    },
)