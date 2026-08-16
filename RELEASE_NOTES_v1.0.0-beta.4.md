# Pehredar v1.0.0-beta.4

This release strengthens Pehredar's open-source and release-engineering
foundation. The screening behavior is unchanged from beta.3.

## Improvements

- Signed APK and Android App Bundle produced by a reviewable GitHub Actions
  workflow.
- GitHub build-provenance attestations for every published artifact.
- SHA-256 checksums shipped with the release.
- Release-time unit tests, release lint, shrinking, signature verification, and
  Gradle-wrapper validation.
- Production-grade community, security, governance, and contribution files.

## Current beta limitations

- The app has not yet completed the published physical-device test matrix.
- All 22 scheduled-language interfaces exist, but native-speaker review is
  still in progress. Do not interpret localization coverage as certified
  translation quality.
- Pehredar silences unknown callers locally; it cannot answer or converse over
  live carrier-call audio as an ordinary third-party Android app.

Android 10 or later is required. Install the APK for direct testing; the AAB is
provided for store distribution workflows.
