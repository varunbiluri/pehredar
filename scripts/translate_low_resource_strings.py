"""Generate the extended Android UI copy for every supported Indian locale.

Existing reviewed core-control translations are preserved. Only keys in
EXTENDED_UI_STRINGS are generated or refreshed. Output is deterministic and
then checked by scripts/check_localizations.py in CI.

Usage:
    uv run python scripts/translate_low_resource_strings.py
"""

from pathlib import Path
import xml.etree.ElementTree as ET

import torch
from IndicTransToolkit.processor import IndicProcessor
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "translate" / "en-indic"
RES_DIR = ROOT / "android" / "app" / "src" / "main" / "res"

EXTENDED_UI_STRINGS = {
    "screen_title": "Private call protection",
    "screen_subtitle": "Unknown numbers ring silently. Your contacts stay on this phone.",
    "setup_title": "Complete these two steps",
    "protection_title": "Protection",
    "privacy_note": "On-device only. No account. No ads. No network access.",
    "safety_note": "Saved contacts ring normally. If a number cannot be checked, it also rings normally.",
    "languages_title": "Language support",
    "languages_summary": "Core controls are available in English and 22 Indian languages.",
    "languages_scope_note": "This beta checks phone numbers. It does not listen to calls. It works with callers speaking any language.",
}

LANGUAGES = [
    ("values-as", "asm_Beng"),
    ("values-bn", "ben_Beng"),
    ("values-b+brx", "brx_Deva"),
    ("values-b+doi", "doi_Deva"),
    ("values-gu", "guj_Gujr"),
    ("values-hi", "hin_Deva"),
    ("values-kn", "kan_Knda"),
    ("values-ks", "kas_Arab"),
    ("values-b+kok", "gom_Deva"),
    ("values-b+mai", "mai_Deva"),
    ("values-ml", "mal_Mlym"),
    ("values-b+mni", "mni_Beng"),
    ("values-mr", "mar_Deva"),
    ("values-ne", "npi_Deva"),
    ("values-or", "ory_Orya"),
    ("values-pa", "pan_Guru"),
    ("values-sa", "san_Deva"),
    ("values-b+sat", "sat_Olck"),
    ("values-sd", "snd_Arab"),
    ("values-ta", "tam_Taml"),
    ("values-te", "tel_Telu"),
    ("values-ur", "urd_Arab"),
]


def android_escape(text: str) -> str:
    return text.replace("PEHREDAR", "Pehredar").replace("'", "\\'")


def indent_xml(root: ET.Element) -> None:
    ET.indent(root, space="    ")


def main() -> None:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model.eval()
    processor = IndicProcessor(inference=True)

    keys = list(EXTENDED_UI_STRINGS)
    sentences = list(EXTENDED_UI_STRINGS.values())

    for resource_dir, target_language in LANGUAGES:
        batch = processor.preprocess_batch(sentences, src_lang="eng_Latn", tgt_lang=target_language)
        inputs = tokenizer(batch, padding=True, truncation=True, return_tensors="pt")
        with torch.inference_mode():
            outputs = model.generate(**inputs, max_length=160, num_beams=5)
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        translations = processor.postprocess_batch(decoded, lang=target_language)

        output_path = RES_DIR / resource_dir / "strings.xml"
        tree = ET.parse(output_path)
        root = tree.getroot()
        by_name = {element.attrib["name"]: element for element in root.findall("string")}
        for key, translation in zip(keys, translations):
            element = by_name.get(key)
            if element is None:
                element = ET.SubElement(root, "string", {"name": key})
            element.text = android_escape(translation)

        indent_xml(root)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"{target_language}: {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
