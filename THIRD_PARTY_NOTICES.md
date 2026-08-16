# Third-party notices

The Apache-2.0 project license covers original Pehredar source code,
documentation, configuration, seed data, and translations committed to this
repository. It does not relicense third-party dependencies or optional model
weights.

## Android application

The Android application uses AndroidX and Material Components. Their license
metadata is resolved by Gradle from the versions declared in
`android/app/build.gradle.kts`.

## Parked voice research

Model weights are downloaded separately and excluded from Git. Anyone using
the research prototype must review and comply with each upstream model's
license and acceptable-use terms:

- Meta Llama 3.2 1B Instruct: Meta Llama license.
- AI4Bharat IndicTrans2: license distributed with the downloaded model.
- faster-whisper and the selected Whisper model: their upstream licenses.
- Piper runtime and individual Piper voices: the runtime and each voice may
  have separate license metadata.

The research prototype is not distributed in the Android APK. Pehredar does
not grant rights to third-party weights merely because scripts can load them.

## Contributor responsibility

Do not commit a model, dataset, font, voice, image, or other asset unless its
license permits redistribution and the pull request records its provenance,
license, and required attribution.
