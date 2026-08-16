# Pehredar

On-device AI call screening. No server ever sees your calls, your audio, or
your transcripts -- everything runs locally on the phone. Starting with
Indian languages: English, Hindi, Hindi-English (Hinglish) code-switching,
Malayalam, Marathi, and Telugu, with more to follow as on-device voices
become available (see [Language coverage](#language-coverage)).

**Status: early alpha.** The desktop pipeline is validated end-to-end with
known quality gaps; the Android app is a compiled, installable skeleton
that requests the call-screening role but does not yet run the AI pipeline
during a real call. See [Current limitations](#current-limitations) before
assuming this does more than it does.

## How it works

A real call screener speaks first -- Pehredar answers with a fixed,
scripted greeting asking who's calling and why (not LLM-generated: it's
not a response to anything yet, so there's nothing to generate). Only
once the caller replies does the AI pipeline run:

```
caller rings -> Pehredar answers with scripted greeting (no AI, owner's chosen language)
             -> caller replies (any supported language)
             -> speech-to-text, translated straight to English + language detected
             -> LLM acknowledges, in English
             -> translated back into the caller's detected language
             -> text-to-speech, in that language (if a voice exists -- see below)
```

Two design choices worth explaining:

1. **The greeting is scripted, not generated.** "Ask who's calling and why"
   turned out to be an unreliable *generative* task at small on-device
   model sizes, no matter how it was prompted (see
   [Model research](#model-research)) -- scripting it removes the failure
   mode entirely, leaving the LLM only the narrower job it was actually
   consistently decent at: acknowledging what the caller just said.
2. **The LLM only ever reasons in English**, regardless of what language
   the caller speaks. Rather than needing one small model to be reliably
   fluent in many Indian languages (which testing showed was a real
   problem -- see below), the caller's speech is translated to English
   by Whisper's built-in translate mode, and the English reply is
   translated back to the caller's language by a dedicated translation
   model (IndicTrans2). Translation, not generation, carries the
   multilingual burden.

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
uv run python prototype/pipeline.py --text "Hi, this is Meera from HDFC about a loan offer" --owner-language te
uv run python prototype/pipeline.py --owner-language hindi path/to/caller.wav
```

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
currently falls back to speaking the reply in English rather than silently
failing or mismatching script/voice.

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
quality was inconsistent when it had to handle Hindi directly. That's the
real reason the LLM was moved to English-only reasoning with translation on
both sides (see [How it works](#how-it-works)) rather than just a language
scope decision -- it also fixed the reliability gap, since Llama 3.2 1B
only officially supports English and Hindi among Indian languages anyway,
and translation-in/translation-out sidesteps needing it to be good at any
of the rest.

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
- **Audio output works end-to-end for English, Hindi, Malayalam, Marathi,
  and Telugu.** Translation text covers all 22 scheduled Indian languages,
  but Tamil, Kannada, Gujarati, Punjabi, Odia, Assamese, and the rest have
  no Piper voice available (see [Language coverage](#language-coverage)) --
  those callers currently get an English-language reply, not silence, but
  not their own language either.
- **STT quality is a known weak point.** faster-whisper `tiny` has
  hallucinated words in testing (e.g. mistranslating "ज़रूरी"/urgent as
  "village"); the confidence gate catches the worst cases and falls back
  to "could you repeat that?" rather than acting on garbled input, but
  doesn't fix the underlying transcription/translation quality.
- **Quality is validated on roughly a dozen hand-picked utterances per
  language**, not a real evaluation set.

## License

Not yet decided.
