import torch
from collections import OrderedDict
from diffusers import StableDiffusionPipeline, EulerAncestralDiscreteScheduler

class ModelCacheManager:
    def __init__(self, cache_size=2):
        self.cache = OrderedDict()
        self.cache_size = cache_size
        print(f"ModelCacheManager initialized with cache size: {self.cache_size}")

    async def load_model(self, model_id: str):
        # Use the model_id as the cache key
        if model_id in self.cache:
            self.cache.move_to_end(model_id)
            print(f"✅ Model '{model_id}' found in in-memory cache.")
            return self.cache[model_id]

        if len(self.cache) >= self.cache_size:
            lru_key, lru_pipe = self.cache.popitem(last=False)
            print(f"🔥 Cache full. Evicting model: '{lru_key}'")
            del lru_pipe
            if torch.cuda.is_available(): torch.cuda.empty_cache()
        
        print(f"🚀 Loading '{model_id}' using its Hub ID...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # ✅ Create the specific scheduler, just like in your script
        scheduler = EulerAncestralDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
        
        # ✅ Call from_pretrained with the Hub ID. Diffusers will use the local cache if available.
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            scheduler=scheduler,
            torch_dtype=torch.float16,
            use_safetensors=True
        )
        pipe.to(device)
        
        # ✅ Apply the same optimizations
        print("Applying optimizations...")
        pipe.enable_vae_slicing()
        pipe.enable_attention_slicing()

        self.cache[model_id] = pipe
        print(f"✅ Model '{model_id}' loaded and cached.")
        return pipe