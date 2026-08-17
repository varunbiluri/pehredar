# Architecture

## Product boundary

The shipping product is an Android 10+ call-screening application. It uses the
official `ROLE_CALL_SCREENING` integration, performs a local contacts lookup,
and returns an allow/silence decision. A separate Offline AI Lab accepts typed
input or explicitly on-device Android speech recognition, performs compact
local intent/risk analysis, and uses an installed offline TTS voice. It does not
answer cellular calls, access carrier-call audio, or use a backend.

```text
Android Telecom
      │ incoming Call.Details
      ▼
PehredarCallScreeningService
      │
      ├── local setting
      ├── local Contacts PhoneLookup
      ▼
ScreeningPolicy (pure, fail-open)
      │
      ▼
CallResponse: ring normally or silently
```

```text
Microphone (Android on-device STT) or typed text
      ▼
LocalAiEngine (intent + safety signals, no persistence)
      ▼
Localized safe reply → installed offline Android TTS voice
```

## Components

- `MainActivity`: role/permission onboarding and local protection preference.
- `PehredarCallScreeningService`: time-bounded Android Telecom adapter.
- `ScreeningPolicy`: pure decision logic covered by unit tests.
- `Settings`: private local preferences.
- `AiLabActivity`: ephemeral on-device STT, analysis, and offline TTS UI.
- `LocalAiEngine`: compact deterministic intent/risk engine covered by tests.
- `res/values-*`: complete localized interface resources.
- `scripts/check_localizations.py`: CI localization invariants.

## Privacy and safety invariants

- No Android internet permission.
- No carrier-call-audio, call-log, or phone-state permission. Microphone access
  is optional, requested only inside the AI Lab, and is never recorded.
- No phone-number logging, analytics, ads, account, or backend.
- Saved contacts ring normally.
- Missing permission, unavailable caller data, and lookup failure fail open.
- Calls are silenced rather than blocked and remain visible to Android.
- Screening must respond within Android's five-second deadline.

Any pull request changing an invariant requires a design issue, security/privacy
analysis, tests, documentation, and maintainer approval.

## Parked research

`prototype/`, `finetune/`, and `data/` contain desktop research from the earlier
voice-agent investigation. They are not linked into the APK. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before downloading models.
