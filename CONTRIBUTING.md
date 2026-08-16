# Contributing to Pehredar

Thank you for helping build private, accessible call protection for India.
Contributions of code, tests, documentation, translations, design feedback,
and real-device results are welcome.

## Before starting

1. Read the [code of conduct](CODE_OF_CONDUCT.md) and
   [architecture](ARCHITECTURE.md).
2. Search existing issues and discussions.
3. Open an issue before a large change so maintainers and contributors can
   agree on scope. Small fixes may go directly to a pull request.
4. Never include real phone numbers, contacts, call logs, recordings, secrets,
   signing keys, or unlicensed data in an issue or commit.

## Development setup

Requirements: JDK 17+, Android SDK 35, and an Android 10+ test device for
telephony behavior.

```bash
git clone https://github.com/varunbiluri/pehredar.git
cd pehredar/android
./gradlew testDebugUnitTest lintDebug assembleDebug
```

The Python research environment is optional:

```bash
uv sync
```

Model weights are not required to build or test the Android app.

## Pull-request standard

- Keep changes focused and explain the user impact.
- Add or update tests for behavior changes.
- Run localization checks when changing visible copy:
  `python3 scripts/check_localizations.py`.
- Run `./gradlew testDebugUnitTest lintDebug assembleDebug` from `android/`.
- Add physical-device evidence for call-screening changes when possible.
- Update documentation and release notes when behavior changes.
- Confirm new dependencies and assets have compatible licenses.
- Use clear commits; maintainers may squash on merge.

## Translation contributions

Read [TRANSLATIONS.md](TRANSLATIONS.md). Native-speaker corrections are
especially valuable. Include language, region, script, explanation, and a
screenshot when layout is affected. Never regenerate over an approved human
correction without reviewing the diff.

## Contribution license

By submitting a contribution, you agree that it is licensed under Apache-2.0
as described by this repository's [LICENSE](LICENSE). You must have the right
to submit all included material.

## Review expectations

Maintainers aim to acknowledge complete issues and pull requests within seven
days. This is a best-effort community target, not a service-level guarantee.
