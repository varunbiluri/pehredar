"""One-off: regenerate the 8 lower-resource-language Android string
resources via IndicTrans2 (a specialized, purpose-built translation model
for exactly these languages) instead of the assistant's own knowledge,
which is less reliable for this set. See README "Language support".

Usage:
    uv run python scripts/translate_low_resource_strings.py
"""

import xml.sax.saxutils as sax
from pathlib import Path

import torch
from IndicTransToolkit.processor import IndicProcessor
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
EN_INDIC_MODEL_PATH = ROOT / "models" / "translate" / "en-indic"
RES_DIR = ROOT / "android" / "app" / "src" / "main" / "res"

STRINGS = {
    "enable_button": "Enable call screening",
    "role_active": "PEHREDAR is your call screening app.",
    "role_inactive": "Call screening is not enabled yet.",
    "role_unavailable": "This device does not support call screening apps.",
    "contacts_button": "Allow contacts access",
    "contacts_granted": "Contacts access granted. Silencing unknown numbers is available.",
    "contacts_not_granted": "Contacts access not granted. Silencing unknown numbers is unavailable.",
    "silence_unknown_switch": "Silently ring calls not in my contacts",
}

# (Android resource dir, IndicTrans2 target code)
LANGUAGES = [
    ("values-b+brx", "brx_Deva"),
    ("values-b+doi", "doi_Deva"),
    ("values-ks", "kas_Arab"),
    ("values-b+kok", "gom_Deva"),
    ("values-b+mai", "mai_Deva"),
    ("values-b+mni", "mni_Beng"),
    ("values-b+sat", "sat_Olck"),
    ("values-sd", "snd_Arab"),
]

BRAND_PLACEHOLDER = "PEHREDAR"


def main() -> None:
    tokenizer = AutoTokenizer.from_pretrained(EN_INDIC_MODEL_PATH, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(EN_INDIC_MODEL_PATH, trust_remote_code=True)
    ip = IndicProcessor(inference=True)

    keys = list(STRINGS.keys())
    sentences = [STRINGS[k] for k in keys]

    for res_dir, tgt_lang in LANGUAGES:
        batch = ip.preprocess_batch(sentences, src_lang="eng_Latn", tgt_lang=tgt_lang)
        inputs = tokenizer(batch, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=80, num_beams=5)
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        translated = ip.postprocess_batch(decoded, lang=tgt_lang)

        lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
        for key, text in zip(keys, translated):
            text = text.replace(BRAND_PLACEHOLDER, "Pehredar")
            lines.append(f'    <string name="{key}">{sax.escape(text)}</string>')
        lines.append("</resources>\n")

        out_path = RES_DIR / res_dir / "strings.xml"
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"{tgt_lang} -> {out_path}")
        for key, text in zip(keys, translated):
            print(f"    {key}: {text!r}")


if __name__ == "__main__":
    main()
