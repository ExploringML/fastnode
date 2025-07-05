import torch
from diffusers import DiffusionPipeline
from collections import OrderedDict

class ModelCacheManager:
    def __init__(self, cache_size=3):
        """
        Initializes the model cache.
        cache_size: The maximum number of models to keep in VRAM at once.
        """
        self.cache = OrderedDict()
        self.cache_size = cache_size
        print(f"ModelCacheManager initialized with cache size: {self.cache_size}")

    async def load_model(self, model_id: str):
        """
        Loads a model on demand. If the model is already in the cache,
        it's returned instantly. Otherwise, it's loaded from disk.
        """
        # If model is already cached, move it to the end (most recently used)
        if model_id in self.cache:
            self.cache.move_to_end(model_id)
            print(f"✅'{model_id}' found in cache.")
            return self.cache[model_id]

        # If cache is full, remove the least recently used model
        if len(self.cache) >= self.cache_size:
            # popitem(last=False) removes the first item (oldest)
            lru_model_id, lru_pipe = self.cache.popitem(last=False)
            print(f"Cache full. Removing least recently used model: '{lru_model_id}'")
            # Optional: explicitly clear memory
            del lru_pipe
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        # Load the new model from disk
        print(f"🚀 Loading '{model_id}' from disk...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pipe = DiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16"
        )
        pipe.to(device)
        pipe.enable_xformers_memory_efficient_attention()

        # Add the new model to the cache
        self.cache[model_id] = pipe
        print(f"✅ Model '{model_id}' loaded and cached.")
        return pipe