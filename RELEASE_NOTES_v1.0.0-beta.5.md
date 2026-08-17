# Pehredar v1.0.0-beta.5

This release improves the safety, test depth, and accessibility of the Android
call-screening application. Its deliberately narrow behavior is unchanged:
saved contacts ring normally and unknown numbers can ring silently.

## Improvements

- Contacts-provider errors and permission races now fail open explicitly, so a
  number is never classified as unknown when Pehredar cannot verify it.
- Automated policy coverage now exercises every protection/contact-state
  combination, missing numbers, permission denial, saved and unsaved contacts,
  and simulated provider failures.
- Screen sections are exposed as accessibility headings, status changes are
  announced as polite live regions, and the smallest informational copy is
  easier to read.
- Unsupported devices now show the correct status immediately and cannot start
  an unavailable role-request flow.
- Signed APK and AAB artifacts include checksums and GitHub build provenance.

## Beta validation still required

- Physical-device and dual-SIM testing across common Android manufacturers.
- TalkBack, large-text, contrast, and switch-access testing on real hardware.
- Two independent native-speaker reviews for each localized interface.

Android 10 or later is required. Pehredar has no internet permission and does
not listen to, record, transcribe, or answer calls.
