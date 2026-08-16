"""Fail CI when a Pehredar locale is incomplete or structurally unsafe."""

from pathlib import Path
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "android" / "app" / "src" / "main" / "res"
DEFAULT_FILE = RES / "values" / "strings.xml"
LOCALE_DIRS = [
    "values-as", "values-bn", "values-b+brx", "values-b+doi", "values-gu",
    "values-hi", "values-kn", "values-ks", "values-b+kok", "values-b+mai",
    "values-ml", "values-b+mni", "values-mr", "values-ne", "values-or",
    "values-pa", "values-sa", "values-b+sat", "values-sd", "values-ta",
    "values-te", "values-ur",
]
RTL_DIRS = {"values-ks", "values-sd", "values-ur"}


def strings(path: Path) -> dict[str, str]:
    root = ET.parse(path).getroot()
    return {item.attrib["name"]: "".join(item.itertext()).strip() for item in root.findall("string")}


def main() -> int:
    default_root = ET.parse(DEFAULT_FILE).getroot()
    required = {
        item.attrib["name"]
        for item in default_root.findall("string")
        if item.attrib.get("translatable", "true") != "false"
    }
    english = strings(DEFAULT_FILE)
    failures: list[str] = []

    for directory in LOCALE_DIRS:
        path = RES / directory / "strings.xml"
        localized = strings(path)
        missing = sorted(required - localized.keys())
        blank = sorted(key for key in required if not localized.get(key, "").strip())
        copied = sorted(key for key in required if localized.get(key) == english.get(key))
        non_nfc = sorted(
            key for key in required
            if unicodedata.normalize("NFC", localized.get(key, "")) != localized.get(key, "")
        )
        if missing:
            failures.append(f"{directory}: missing {', '.join(missing)}")
        if blank:
            failures.append(f"{directory}: blank {', '.join(blank)}")
        if copied:
            failures.append(f"{directory}: English fallback {', '.join(copied)}")
        if non_nfc:
            failures.append(f"{directory}: non-NFC Unicode {', '.join(non_nfc)}")
        if directory in RTL_DIRS:
            joined = " ".join(localized.values())
            if not any("ARABIC" in unicodedata.name(char, "") for char in joined):
                failures.append(f"{directory}: no Arabic-script content for RTL locale")
        if directory == "values-b+sat":
            joined = " ".join(localized.values())
            foreign_indic = [
                char for char in joined
                if "\u0900" <= char <= "\u0dff"
            ]
            if foreign_indic:
                failures.append("values-b+sat: non-Ol-Chiki Indic characters detected")

    if failures:
        print("Localization checks failed:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1

    print(f"Localization checks passed: {len(LOCALE_DIRS)} locales, {len(required)} strings each")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
