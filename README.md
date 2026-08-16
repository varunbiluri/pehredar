# Pehredar

On-device call screening for Android. No server ever sees your calls,
contacts, or audio -- everything runs locally on the phone.

**Status: early alpha, and smaller in scope than earlier plans in this
repo's history.** The original goal was AI that answers and talks to
callers on your behalf, fully on-device. That turned out not to be
legitimately buildable -- see
[Why no live AI conversation](#why-no-live-ai-conversation) below. What
actually ships: calls from unknown numbers ring silently instead of
interrupting you, calls from contacts always ring normally. A validated
on-device voice AI pipeline (speech-to-text, an LLM, translation,
text-to-speech, across five languages) exists in this repo as
[parked research](#parked-research-on-device-voice-pipeline) -- real,
tested code, just not wired into the shipping app, because there's
currently no legitimate way to give it access to live call audio.

## Why no live AI conversation

Answering a call and speaking to the caller requires access to the live
call audio stream (to listen and to inject synthesized speech). On
**Android**, that requires the `CAPTURE_AUDIO_OUTPUT` permission, which
is restricted to privileged system apps (Google's own apps, or apps
pre-loaded by the device manufacturer) -- not available to a regular
third-party app, including one set as the default dialer. `CallScreeningService`,
which a third-party app *can* use, only returns an allow/reject/silence
decision before the call connects; it has no audio access at all. Real
apps that offer "AI answers your calls" (Call Assistant AI, Equal AI, and
similar) work by **forwarding your calls to a phone number they control**,
where their own server-side infrastructure handles the conversation --
architecturally a cloud service, not an on-device one, regardless of how
it's marketed.

On **iOS**, the same outcome for a different reason: Apple provides no
public API for a third-party app to answer or speak during a live
cellular call at all. CallKit covers call blocking/directory lookups
only.

Both platforms reserve this capability to themselves or to
manufacturer-privileged apps. There is no engineering path around this
for an independent app that wants to stay on-device and server-free --
that combination (live call audio + third-party + no server) doesn't
exist as a legitimate option on either platform today.

## What the app actually does

```bash
cd android
./gradlew assembleDebug
```

`PehredarCallScreeningService` requests the `CALL_SCREENING` role and,
for each incoming call:
- If the number is a saved contact -> rings normally.
- If not, and the user has enabled "silence unknown numbers" in the app
  -> rings silently (not blocked -- still reaches voicemail/call log,
  just doesn't interrupt).
- If contacts permission isn't granted, or the setting is off -> rings
  normally, unchanged. Fails open, not closed.

No audio access, no AI model, no network calls anywhere in this path --
it's number/contact-lookup logic only, which is all `CallScreeningService`
legitimately supports.

### Language support

The app's UI (not the parked voice pipeline -- there's no AI involved
here) is localized into English plus all 22 languages of the Indian
Constitution's Eighth Schedule: Assamese, Bengali, Bodo, Dogri, Gujarati,
Hindi, Kannada, Kashmiri, Konkani, Maithili, Malayalam, Manipuri (Meitei),
Marathi, Nepali, Odia, Punjabi, Sanskrit, Santali, Sindhi, Tamil, Telugu,
Urdu -- `android/app/src/main/res/values-*/strings.xml`. Android picks
the right one automatically from the phone's system language.

The 14 higher-resource languages (Hindi, Bengali, Telugu, Marathi, Tamil,
Kannada, Malayalam, Gujarati, Punjabi, Odia, Assamese, Urdu, Nepali,
Sanskrit) were translated directly. For **Bodo, Dogri, Kashmiri, Konkani,
Maithili, Manipuri, Santali, and Sindhi**, translations were regenerated
through IndicTrans2 (`scripts/translate_low_resource_strings.py`) rather
than by direct translation -- a specialized model AI4Bharat built
specifically to cover exactly these underserved languages properly,
rather than relying on weaker general-purpose knowledge of them. That's
a real, substantive quality improvement over the first pass, not just a
caveat -- and it settled the two earlier script uncertainties with the
model's own documented support list: Manipuri in Bengali script (`mni_Beng`)
and Kashmiri/Sindhi in Perso-Arabic script (`kas_Arab`/`snd_Arab`) are
confirmed-valid options; Santali, however, turned out to have **no**
Devanagari option in IndicTrans2 at all -- only Ol Chiki (`sat_Olck`),
so that's what ships now, correcting the earlier Devanagari fallback.

That said, "specialized model" isn't the same as "verified." Machine
translation quality for genuinely low-resource languages is documented
to lag behind high-resource languages even with purpose-built systems,
this is domain-specific app-UI text rather than the general text these
models are typically evaluated on, and the brand name ("Pehredar") had
to be manually corrected in all eight after the model transliterated it
inconsistently (e.g. "PEREDAR"). A native speaker should still review
these eight before shipping to real users -- just from a stronger
starting point than before.

**Untested on a real device or emulator.** This environment has the
Android SDK and build tools but no emulator and no connected device --
confirmed to *compile and package* into a valid APK, not confirmed to
run correctly. Get a real device before trusting it.

**iOS is not supported and will not be**, for the reason above.

## Privacy

The Android app requests only contacts access and Android's user-granted call-screening role. It has no internet permission, account, ads, analytics, call recording, or phone-number logging. See [PRIVACY.md](PRIVACY.md).

## Parked research: on-device voice pipeline

Before the audio-access finding above, a full on-device voice pipeline
was built and validated on desktop (not on a phone) -- kept in this repo
because it's real, tested work, in case a legitimate use for it emerges
(e.g. if voicemail-file-after-the-fact access turns out to be more
permissive than live-call access -- unresearched).

```bash
uv sync
uv run python prototype/pipeline.py --text "Hi, this is Meera from HDFC about a loan offer" --owner-language te
uv run python prototype/pipeline.py --owner-language hindi path/to/caller.wav
```

Call flow: a scripted greeting (not LLM-generated -- see
[Model research](#model-research) for why) asks who's calling and why;
the reply is transcribed and translated to English by Whisper; an LLM
(English-only) generates a brief acknowledgment; that's translated back
into the caller's detected language; Piper speaks it.

Models used (not committed to git -- see `models/` after running, gitignored):
- **STT + translation-to-English**: faster-whisper `tiny` (multilingual, `task="translate"`)
- **LLM**: Llama 3.2 1B Instruct, Q4_K_M GGUF (~770MB), English only
- **Translation back to caller's language**: AI4Bharat IndicTrans2, `en-indic-dist-200M` (~1GB unquantized; covers all 22 scheduled Indian languages textually)
- **TTS**: Piper -- one voice each for English, Hindi, Malayalam, Marathi, Telugu (~60MB each)

### Language coverage

Translation (IndicTrans2) covers all 22 scheduled Indian languages, but
**Piper voice availability is the actual ceiling on end-to-end audio
output**, not translation. Verified directly against the `rhasspy/piper-voices`
repo's real file listing (an earlier claim in this README, based on an
unverified search summary, was wrong and has been corrected):

| Language | Translation (IndicTrans2) | Piper voice | Wired in |
| --- | --- | --- | --- |
| English, Hindi, Malayalam, Marathi, Telugu | Yes | Yes | Yes |
| Bengali, Urdu, Nepali | Yes | Yes (non-India locale: `bn_BD`, `ur_PK`, `ne_NP`) | No, not downloaded yet |
| Tamil, Kannada, Gujarati, Punjabi, Odia, Assamese, and the rest of the 22 | Yes | **No voice exists** | No |

For a caller whose detected language has no Piper voice, the pipeline
falls back to speaking the reply in English rather than silently failing
or mismatching script/voice.

### IndicTrans2 compatibility notes

`ai4bharat/indictrans2-en-indic-dist-200M`'s custom modeling/tokenizer code
(2023, unmaintained) doesn't run on current `transformers` -- it imports
`transformers.onnx` (removed) and its tokenizer `__init__` ordering
conflicts with newer internals. `pyproject.toml` pins `transformers==4.44.2`
project-wide to work around this (see the comment there for why this
conflicts with the newer `transformers` the now-parked Gemma fine-tuning
used). The downloaded local copy of `configuration_indictrans.py` is
patched in place to drop the dead `transformers.onnx` import/class.

The gated `indic-en-dist-200M` (caller-language -> English direction) was
never obtained -- Hugging Face access requests for it weren't approved in
this environment. That's why the caller-to-English leg uses Whisper's
built-in translate mode instead; it turned out to make that model
unnecessary anyway.

### Model research

Gemma 3 270M was tried first to fit a ~500MB total budget, but neither
zero-shot prompting, few-shot prompting, nor three rounds of LoRA
fine-tuning (`finetune/`, 63-example seed dataset in `data/`) made it
reliably ask who's calling and why -- outputs ranged from generic filler
to outright incoherent (leaked chat-template tokens from a tokenizer
mismatch during GGUF conversion, since fixed in `finetune/merge_adapter.py`
but the underlying capacity problem remained). Two attempts at reframing
the task as LLM-based binary classification instead of generation also
failed, collapsing to a fixed output regardless of input.

Llama 3.2 1B fixed the "ask who/why" failure zero-shot, which is why the
budget was revised to ~1GB. It's not fully reliable either -- acknowledgment
quality was inconsistent when it had to handle Hindi directly. That's the
real reason the LLM was moved to English-only reasoning with translation on
both sides rather than just a language scope decision -- it also fixed the
reliability gap, since Llama 3.2 1B only officially supports English and
Hindi among Indian languages anyway, and translation-in/translation-out
sidesteps needing it to be good at any of the rest.

### Latency (measured, desktop, not phone)

Not real-time: 3.7-4.8s end-to-end per turn in testing, dominated by
each pipeline stage reloading its model from disk on every call (a CLI
script, not a persistent service). A phone would likely be slower before
any optimization, not faster.

## Repository layout

```
android/      The actual shipping app (Kotlin/Gradle) -- contact-based silent screening
prototype/    Parked: STT -> LLM -> translate -> TTS pipeline (Python, desktop-only)
data/         Parked: seed call-screening dialogue dataset
finetune/     Parked: LoRA fine-tuning scripts and findings
```

## License

Not yet decided.
