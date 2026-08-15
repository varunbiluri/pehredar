# Pehredar

On-device AI call screening. No server ever sees your calls, your audio, or
your transcripts -- everything runs locally on the phone. Starting with
English, Hindi, and Hindi-English (Hinglish) code-switching; more Indian
languages later.

**Status: early alpha.** The desktop pipeline is validated end-to-end with
known quality gaps; the Android app is a compiled, installable skeleton
that requests the call-screening role but does not yet run the AI pipeline
during a real call. See [Current limitations](#current-limitations) before
assuming this does more than it does.

## How it works

A real call screener speaks first -- Pehredar answers with a fixed,
scripted greeting asking who's calling and why (not LLM-generated: it's
not a response to anything yet, so there's nothing to generate). Only
once the caller replies does the AI pipeline run, and only to produce a
brief acknowledgment:

```
caller rings -> Pehredar answers with scripted greeting (no AI)
             -> caller replies -> speech-to-text -> LLM acknowledgment -> text-to-speech
```

This split exists because "ask who's calling and why" turned out to be an
unreliable *generative* task at small on-device model sizes, no matter how
it was prompted (see [Model research](#model-research) below) -- scripting
it removes the failure mode entirely, and leaves the LLM only the
narrower job it was actually consistently decent at.

## Repository layout

```
prototype/    Working STT -> LLM -> TTS pipeline (Python, desktop-validated)
data/         Seed call-screening dialogue dataset (63 examples, 3 languages)
finetune/     LoRA fine-tuning scripts (train/merge/quantize) -- see notes below
android/      Android app (Kotlin/Gradle) -- compiles; AI pipeline not wired in yet
```

## Desktop prototype

```bash
uv sync
uv run python prototype/pipeline.py --text "Hi, main tumhare loan EMI ke bare mein baat karna chahta hoon"
uv run python prototype/pipeline.py --owner-language hindi path/to/caller.wav
```

Models used (not committed to git -- see `models/` after running, gitignored):
- **STT**: faster-whisper `tiny` (multilingual)
- **LLM**: Llama 3.2 1B Instruct, Q4_K_M GGUF (~770MB)
- **TTS**: Piper, Hindi voice (`hi_IN-priyamvada-medium`, ~61MB)

## Model research

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
quality is solid in English/Hinglish, weaker in pure Hindi (Devanagari)
output -- but the scripted-greeting restructuring above means that gap no
longer breaks the core screening function.

## Android app

```bash
cd android
./gradlew assembleDebug
```

Requests the `CALL_SCREENING` role via `RoleManager` and registers a
`CallScreeningService`. Currently applies a stub allow-all policy --
see [Current limitations](#current-limitations).

## Current limitations

- **The Android app does not run the AI pipeline yet.** `PehredarCallScreeningService`
  allows every call through unchanged. Wiring in the validated STT/LLM/TTS
  pipeline requires native (NDK) Android builds of llama.cpp, whisper.cpp,
  and onnxruntime, plus handling live in-call audio access -- none of that
  is done.
- **Untested on a real device or emulator.** This environment has the
  Android SDK and build tools but no NDK, no emulator, and no connected
  device -- the app is confirmed to *compile and package* into a valid
  APK, not confirmed to run correctly.
- **iOS is not supported and will not be.** Apple provides no public API
  for a third-party app to answer or speak during a live cellular call --
  CallKit covers call blocking/directory lookups only. There is no way to
  build this specific product on iOS through the App Store.
- **Only English and Hindi (incl. Hinglish) are implemented.** The LLM
  (Llama 3.2 1B) officially supports only Hindi among Indian languages;
  Tamil, Telugu, Bengali, Marathi, Kannada, Malayalam, Gujarati, Punjabi,
  Urdu, and others are unbuilt and untested, not just unpolished.
- **Quality is validated on roughly a dozen hand-picked utterances**, not
  a real evaluation set.

## License

Not yet decided.
