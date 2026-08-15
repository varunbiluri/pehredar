"""LoRA fine-tune Gemma 3 270M on the call-screening seed dataset.

Trains a small adapter on top of the frozen base model -- cheap enough to
run on a laptop CPU/MPS in minutes given the dataset size (63 examples).
Output: finetune/adapter/ (LoRA weights only, merged separately for GGUF
conversion).

Usage:
    uv run python finetune/train_lora.py
"""

from pathlib import Path

from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer

ROOT = Path(__file__).resolve().parent.parent
BASE_MODEL_PATH = ROOT / "models" / "base" / "gemma-3-270m-it"
DATASET_PATH = ROOT / "data" / "call_screening_seed.jsonl"
ADAPTER_OUT = ROOT / "finetune" / "adapter"

LORA_CONFIG = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    task_type="CAUSAL_LM",
)


def main() -> None:
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL_PATH)

    model = get_peft_model(model, LORA_CONFIG)
    model.print_trainable_parameters()

    dataset = load_dataset("json", data_files=str(DATASET_PATH), split="train")

    config = SFTConfig(
        output_dir=str(ROOT / "finetune" / "checkpoints"),
        num_train_epochs=5,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=2,
        learning_rate=1e-4,
        logging_steps=5,
        save_strategy="no",
        report_to="none",
        max_length=512,
        packing=False,
    )

    trainer = SFTTrainer(
        model=model,
        args=config,
        train_dataset=dataset,
        processing_class=tokenizer,
    )
    trainer.train()

    ADAPTER_OUT.mkdir(parents=True, exist_ok=True)
    trainer.model.save_pretrained(str(ADAPTER_OUT))
    tokenizer.save_pretrained(str(ADAPTER_OUT))
    print(f"adapter saved to {ADAPTER_OUT}")


if __name__ == "__main__":
    main()
