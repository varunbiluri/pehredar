# Pehredar v1.0.0-beta.2

This beta improves clarity, presentation, and language-support information while preserving Pehredar's private on-device design.

## Improvements

- Redesigned interface with clear setup, protection, language, and privacy sections.
- Visible active/inactive status for the Android call-screening role and contacts permission.
- In-app list of English plus all 22 scheduled Indian interface languages.
- Clear explanation that screening works for callers speaking any language because this beta checks phone numbers rather than call audio.
- No internet, microphone, call-log, phone-state, advertising, analytics, account, or backend.

## Current behavior

- Saved contacts ring normally.
- Calls from numbers outside contacts ring silently when protection is enabled.
- Calls remain visible in the call log and may reach voicemail.
- Missing or unverifiable caller information fails open and rings normally.

## Important limitation

This beta does not answer calls or conduct an AI voice conversation. Ordinary third-party Android screening apps do not receive live cellular-call audio.
