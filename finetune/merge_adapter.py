"""Merges the LoRA adapter into the base Gemma 3 270M weights, producing a
standalone model directory ready for GGUF conversion.

Usage:
    uv run python finetune/merge_adapter.py
"""

import shutil
from pathlib import Path

from peft import PeftModel
from transformers import AutoModelForCausalLM

ROOT = Path(__file__).resolve().parent.parent
BASE_MODEL_PATH = ROOT / "models" / "base" / "gemma-3-270m-it"
ADAPTER_PATH = ROOT / "finetune" / "adapter"
MERGED_OUT = ROOT / "finetune" / "merged"

# Copied verbatim, never re-saved via tokenizer.save_pretrained(): LoRA doesn't
# touch the tokenizer, and re-saving it independently previously produced a
# tokenizer.json inconsistent with base's tokenizer.model/special_tokens_map,
# corrupting chat-template/special-token handling in the exported GGUF.
TOKENIZER_FILES = [
    "tokenizer.model",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "chat_template.jinja",
]


def main() -> None:
    base_model = AutoModelForCausalLM.from_pretrained(BASE_MODEL_PATH)

    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model = model.merge_and_unload()

    MERGED_OUT.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(MERGED_OUT))
    for filename in TOKENIZER_FILES:
        src = BASE_MODEL_PATH / filename
        if src.exists():
            shutil.copy2(src, MERGED_OUT / filename)
    print(f"merged model saved to {MERGED_OUT}")


if __name__ == "__main__":
    main()
