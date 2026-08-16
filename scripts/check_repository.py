"""Fast, dependency-free repository policy checks for local use and CI."""

from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = {
    "README.md", "LICENSE", "NOTICE", "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md", "SECURITY.md", "SUPPORT.md", "GOVERNANCE.md",
    "ARCHITECTURE.md", "ROADMAP.md", "CHANGELOG.md", "RELEASING.md",
    "TRANSLATIONS.md", "THIRD_PARTY_NOTICES.md", "DATASET.md",
    ".github/CODEOWNERS", ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/dependabot.yml",
    ".github/workflows/release.yml",
}
LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
ACTION = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)
PINNED_ACTION = re.compile(r"^[^@]+@[0-9a-f]{40}$")


def tracked_files() -> list[str]:
    output = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return output.splitlines()


def main() -> int:
    failures: list[str] = []
    for name in sorted(REQUIRED):
        if not (ROOT / name).is_file():
            failures.append(f"missing required file: {name}")

    for markdown in ROOT.rglob("*.md"):
        if any(part in {".git", ".venv", "build", "models"} for part in markdown.parts):
            continue
        text = markdown.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            target = target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (markdown.parent / target).resolve().exists():
                failures.append(f"broken local link in {markdown.relative_to(ROOT)}: {target}")

    for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
        for action in ACTION.findall(workflow.read_text(encoding="utf-8")):
            if not action.startswith("./") and not PINNED_ACTION.match(action):
                failures.append(f"unpinned action in {workflow.name}: {action}")

    forbidden_suffixes = {".apk", ".aab", ".jks", ".keystore", ".gguf", ".onnx", ".safetensors"}
    for name in tracked_files():
        if Path(name).suffix.lower() in forbidden_suffixes:
            failures.append(f"forbidden binary or secret tracked by Git: {name}")
        if name in {"android/keystore.properties", ".env"}:
            failures.append(f"secret-bearing file tracked by Git: {name}")

    if failures:
        print("Repository checks failed:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Repository policy checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
