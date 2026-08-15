"""Quantizes the fine-tuned f16 GGUF to Q4_K_M using llama-cpp-python's
bundled llama.cpp quantize binding (no separate CLI build needed).

Usage:
    uv run python finetune/quantize.py
"""

from pathlib import Path

from llama_cpp import llama_cpp as lcpp

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "finetune" / "pehredar-270m-f16.gguf"
DST = ROOT / "models" / "llm" / "pehredar-270m-finetuned-Q4_K_M.gguf"


def main() -> None:
    params = lcpp.llama_model_quantize_default_params()
    params.ftype = lcpp.LLAMA_FTYPE_MOSTLY_Q4_K_M
    params.nthread = 4

    rc = lcpp.llama_model_quantize(str(SRC).encode(), str(DST).encode(), params)
    if rc != 0:
        raise RuntimeError(f"quantization failed, rc={rc}")
    print(f"quantized model written to {DST}")


if __name__ == "__main__":
    main()
