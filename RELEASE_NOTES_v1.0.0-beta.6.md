# Pehredar v1.0.0-beta.6

Beta.6 adds the first real on-device AI capability while keeping Pehredar
server-free and explicit about Android's carrier-call boundary.

## Offline AI Lab

- Speak on Android 12+ phones that expose an on-device speech recognizer, or
  type on any supported Android version.
- Classify credential/OTP danger, delivery, appointment, business, and personal
  caller intent using a compact local engine.
- Produce a safety-focused suggested reply and speak it with an installed
  offline Android voice.
- Complete AI Lab interface resources for English and all 22 scheduled Indian
  languages.
- No transcript, recording, result, phone number, or model input is saved or
  transmitted. The app still has no internet permission.

## Call protection

The existing cellular flow is unchanged: Pehredar checks the incoming number
against contacts and can silence unknown numbers. Android does not expose live
carrier-call audio to third-party call-screening apps, so the AI Lab uses the
phone microphone or typed input and cannot answer a cellular call.

## Compatibility

- Android 10 or later for call screening and typed AI analysis.
- Android 12 or later plus an installed on-device recognition service for voice
  input.
- Spoken output requires an installed offline TTS voice for the phone language.

This is a public beta. Native-language review and physical-device validation
remain required before a stable release.
