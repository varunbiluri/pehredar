"""Generate the extended Android UI copy for every supported Indian locale.

Existing reviewed core-control translations are preserved. Only keys in
EXTENDED_UI_STRINGS are generated or refreshed. Output is deterministic and
then checked by scripts/check_localizations.py in CI.

Usage:
    uv run python scripts/translate_low_resource_strings.py
"""

from pathlib import Path
import re
import xml.etree.ElementTree as ET

import torch
from IndicTransToolkit.processor import IndicProcessor
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "translate" / "en-indic"
RES_DIR = ROOT / "android" / "app" / "src" / "main" / "res"

AI_UI_STRINGS = {
    "ai_lab_button": "Open offline AI Lab",
    "ai_lab_title": "Offline AI Lab",
    "ai_lab_subtitle": "Speak or type what a caller said. Pehredar analyzes it locally and prepares a safe reply.",
    "ai_input_hint": "What did the caller say?",
    "ai_listen_button": "Listen on this device",
    "ai_analyze_button": "Analyze locally",
    "ai_speak_button": "Speak suggested reply",
    "ai_result_placeholder": "The private analysis will appear here.",
    "ai_stt_unavailable": "On-device speech recognition is unavailable. Type the caller's words instead.",
    "ai_permission_denied": "Microphone permission was not granted. You can still type text.",
    "ai_listening": "Listening on this device",
    "ai_risk_high": "High risk",
    "ai_risk_medium": "Caution",
    "ai_risk_low": "No strong risk signal",
    "ai_category_scam": "Possible fraud or credential request",
    "ai_category_delivery": "Delivery",
    "ai_category_appointment": "Appointment",
    "ai_category_business": "Business or sales",
    "ai_category_personal": "Personal",
    "ai_category_unknown": "More information needed",
    "ai_reply_scam": "I never share OTPs, PINs, or passwords. I will contact the organization through its official number.",
    "ai_reply_delivery": "Please state your name, courier company, and whether the delivery needs action today.",
    "ai_reply_appointment": "Please state your name, organization, appointment time, and whether anything is urgent.",
    "ai_reply_business": "Please state your name, company, and the reason for your call.",
    "ai_reply_personal": "Please state your name and what you would like me to pass to the owner.",
    "ai_reply_unknown": "Please state your name and the reason for your call.",
    "ai_result_format": "Risk: %1$s\\nCategory: %2$s\\n\\nSuggested reply: %3$s",
    "ai_scope_note": "Runs without network access. Voice availability depends on downloaded Android language packs. This lab cannot hear or speak inside a cellular call.",
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
    text = re.sub(r"%\s*([123])\s*\$\s*s", r"%\1$s", text)
    return text.replace("PEHREDAR", "Pehredar").replace("'", "\\'")


def sanitize_santali(text: str) -> str:
    """Remove occasional mixed-script model artifacts from Ol Chiki output."""
    foreign_scripts = (
        "ARABIC", "BENGALI", "DEVANAGARI", "GUJARATI", "GURMUKHI",
        "ORIYA", "TAMIL", "TELUGU", "KANNADA", "MALAYALAM", "MEETEI",
    )
    import unicodedata
    return "".join(
        char for char in text
        if not any(script in unicodedata.name(char, "") for script in foreign_scripts)
    )


def indent_xml(root: ET.Element) -> None:
    ET.indent(root, space="    ")


def main() -> None:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model.eval()
    processor = IndicProcessor(inference=True)

    keys = list(AI_UI_STRINGS)
    sentences = list(AI_UI_STRINGS.values())

    for resource_dir, target_language in LANGUAGES:
        batch = processor.preprocess_batch(sentences, src_lang="eng_Latn", tgt_lang=target_language)
        inputs = tokenizer(batch, padding=True, truncation=True, return_tensors="pt")
        with torch.inference_mode():
            outputs = model.generate(**inputs, max_length=160, num_beams=5)
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        translations = processor.postprocess_batch(decoded, lang=target_language)
        if target_language == "sat_Olck":
            translations = [sanitize_santali(text) for text in translations]

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
