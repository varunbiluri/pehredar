# Pehredar v1.0.0-beta.1

This is the first public Android beta of Pehredar's private, on-device unknown-caller protection.

## What it does

- Uses Android's official call-screening role.
- Lets saved contacts ring normally.
- Optionally makes non-contact callers ring silently while preserving the call log and voicemail behavior.
- Fails open when caller/contact information cannot be verified.
- Provides localized core controls for English and all 22 scheduled Indian languages.
- Works without an account, ads, internet permission, or backend.

## Important limitation

This beta does not answer calls or hold an AI voice conversation. Android does not provide live cellular-call audio to ordinary third-party screening apps. The repository contains a separate desktop voice-pipeline experiment, but it is not included in the APK.

## Beta testing requested

Please test on a physical Android 10+ device and report the manufacturer, Android version, dual-SIM status, and whether saved and unsaved callers behaved as expected.
