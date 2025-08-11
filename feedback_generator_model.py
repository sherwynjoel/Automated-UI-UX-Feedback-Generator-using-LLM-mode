# feedback_generator_model.py
import os
import yaml

def load_config(path="config.yaml"):
    import yaml
    with open(path, "r") as f:
        return yaml.safe_load(f)

# --- Llama.cpp (llama-cpp-python) wrapper ---
def load_llama_cpp(model_path, max_tokens=512):
    try:
        from llama_cpp import Llama
    except Exception as e:
        raise RuntimeError("llama_cpp python package not installed or failed to import.") from e

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    llm = Llama(model_path=model_path, n_ctx=2048)
    class LlamaWrapper:
        def __init__(self, llm, max_tokens):
            self.llm = llm
            self.max_tokens = max_tokens

        def generate(self, prompt):
            resp = self.llm.create(prompt=prompt, max_tokens=self.max_tokens)
            # llama-cpp-python returns choices with 'text'
            return resp["choices"][0].get("text", "").strip()
    return LlamaWrapper(llm, max_tokens)

# --- Mock model used for development/testing ---
class MockModel:
    def __init__(self):
        pass
    def generate(self, prompt):
        # Short mock JSON-style reply to mimic structured output
        sample = {
            "Visibility of system status": {
                "verdict": "Good",
                "why": "Progress indicators are present and clear.",
                "fix": []
            },
            "Match between system and the real world": {
                "verdict": "Needs improvement",
                "why": "Terminology is inconsistent with user expectations.",
                "fix": ["Use simpler language", "Align labels to user mental model"]
            }
        }
        import json
        return json.dumps(sample, indent=2)

# --- Loader that picks backend ---
def load_model_from_config(cfg=None):
    if cfg is None:
        cfg = load_config()
    backend = cfg.get("model_backend", "mock")
    if backend == "llama_cpp":
        return load_llama_cpp(cfg["model_path"], cfg.get("max_tokens", 512))
    elif backend == "pytorch":
        # Placeholder - real BakLLaVA multimodal PyTorch loader is model-specific.
        raise NotImplementedError("PyTorch multimodal loader: implement BakLLaVA-specific loader here.")
    else:
        return MockModel()
