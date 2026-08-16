# Architecture

## Product boundary

The shipping product is an Android 10+ call-screening application. It uses the
official `ROLE_CALL_SCREENING` integration, performs a local contacts lookup,
and returns an allow/silence decision. It does not answer cellular calls, access
call audio, use a backend, or include an AI model.

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

## Components

- `MainActivity`: role/permission onboarding and local protection preference.
- `PehredarCallScreeningService`: time-bounded Android Telecom adapter.
- `ScreeningPolicy`: pure decision logic covered by unit tests.
- `Settings`: private local preferences.
- `res/values-*`: complete localized interface resources.
- `scripts/check_localizations.py`: CI localization invariants.

## Privacy and safety invariants

- No Android internet permission.
- No call-audio, microphone, call-log, or phone-state permission.
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
