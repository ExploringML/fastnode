import base64
from io import BytesIO
import torch
from core.nodes import register_node
from fasthtml.common import FastHTML
from utils.ws import safe_send
from anyio import from_thread, to_thread
from functools import partial
from diffusers import EulerAncestralDiscreteScheduler

async def sd_sampler_handler(app: FastHTML, inputs, params, send=None, request_id=None):
    # Get model name from the upstream loader node
    model_name = inputs.get("model")
    if not model_name:
        raise ValueError("An input for 'model' is required.")

    # Access the global manager and load the model on-demand
    model_manager = app.state.model_manager
    pipe = await model_manager.load_model(model_name)
    if not pipe:
        raise RuntimeError(f"Failed to load model: {model_name}")

    # Dynamically apply the selected scheduler
    scheduler_name = params.get("scheduler", "Default")
    if scheduler_name == "Euler A":
        print("Applying EulerAncestralDiscreteScheduler...")
        model_path_or_id = app.state.model_manager.models_base_dir / model_name if \
                           (app.state.model_manager.models_base_dir / model_name).is_dir() else model_name
        pipe.scheduler = EulerAncestralDiscreteScheduler.from_pretrained(model_path_or_id, subfolder="scheduler")

    # Get other generation parameters
    prompt = inputs.get("prompt", "")
    negative_prompt = inputs.get("negative_prompt", "")
    steps = int(params.get("steps", 20))
    guidance = float(params.get("guidance", 7.5))
    seed = int(params.get("seed", -1))
    
    generator = torch.Generator("cuda").manual_seed(seed) if seed != -1 else None

    # Define the synchronous progress callback
    def progress_callback(pipe, step, timestep, callback_kwargs):
        progress = int(((step + 1) / steps) * 100)
        if send and request_id:
            from_thread.run(
                safe_send, send,
                {
                    "type": "node-progress",
                    "nodeId": inputs.get("id"), "requestId": request_id,
                    "progress": progress, "message": f"Step {step + 1}/{steps}",
                },
            )
        # ✅ 2. Return the arguments to the pipeline
        return callback_kwargs

    # Define a wrapper for the blocking call to use with torch.inference_mode
    def generate_in_inference_mode():
        with torch.inference_mode():
            return pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=steps,
                guidance_scale=guidance,
                generator=generator,
                callback_on_step_end=progress_callback
            )

    # Run the generation in a worker thread to avoid blocking the server
    pipe_output = await to_thread.run_sync(
        generate_in_inference_mode,
        cancellable=True
    )
    image = pipe_output.images[0]
    
    # Convert and return the final image
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return {"image": f"data:image/png;base64,{img_str}"}

# --- Node Registration ---
register_node("sd_sampler", {
    "displayName": "SD Sampler",
    "category": "AI",
    "params": {
        "scheduler": {
            "type": "string",
            "ui": "select",
            "options": [["euler-a", "Euler A"]],
            "default": "euler-a"
        },
        "steps": {"ui": "number", "default": 20, "min": 1, "max": 100},
        "guidance": {"ui": "number", "default": 7.5, "min": 1, "max": 20, "step": 0.1},
        "seed": {"ui": "number", "default": -1}
    },
    "inputs": ["model", "prompt", "negative_prompt"],
    "outputs": ["image"],
    "handler": sd_sampler_handler,
    "actions": [
        {"label": "Reset", "action": "reset"},
        {"label": "Delete", "action": "delete"},
    ]
})