"""Prototype: scripted greeting -> STT(-> English) -> LLM -> translate-back
-> TTS, on-device, across multiple Indian languages.

Call flow: Pehredar answers and speaks a FIXED greeting first, asking who's
calling and why -- never LLM-generated, since it's not a response to
anything, just the app's opening line (see "Model research" in README for
why this is scripted rather than generated).

Once the caller replies, faster-whisper both detects their language AND
translates their speech directly to English in one pass (Whisper's built-in
translate task). The LLM -- which is only reliable in English, see README
-- generates a brief English acknowledgment. That's translated back into
the caller's language with IndicTrans2 (covers all 22 scheduled Indian
languages), then spoken with a Piper voice in that language if one exists.

This sidesteps needing one small LLM to be fluent in many Indian languages
(it never has to be: it only ever reasons in English) at the cost of two
extra model hops. Piper voice availability, not translation, is the actual
ceiling on language coverage right now -- see LANGUAGES below.

Usage:
    uv run python prototype/pipeline.py path/to/caller_utterance.wav
    uv run python prototype/pipeline.py --text "This is Meera from HDFC about a loan offer"
    uv run python prototype/pipeline.py --text "..." --owner-language hindi
"""

from __future__ import annotations

import argparse
import time
import wave
from dataclasses import dataclass
from pathlib import Path

import torch
from faster_whisper import WhisperModel
from IndicTransToolkit.processor import IndicProcessor
from llama_cpp import Llama
from piper import PiperVoice
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
LLM_PATH = ROOT / "models" / "llm" / "Llama-3.2-1B-Instruct-Q4_K_M.gguf"
EN_INDIC_MODEL_PATH = ROOT / "models" / "translate" / "en-indic"
GREETING_WAV = ROOT / "prototype" / "greeting.wav"
REPLY_WAV = ROOT / "prototype" / "output.wav"

# Piper voice availability -- not translation -- is what actually limits
# language coverage. IndicTrans2 covers all 22 scheduled Indian languages
# for the text translation leg, but rhasspy/piper-voices (verified against
# the repo's real file listing, not assumed) currently only has voices for
# these Indian languages: Hindi, Malayalam, Marathi, Telugu, Bengali (bn_BD,
# Bangladesh locale), Urdu (ur_PK, Pakistan locale), Nepali. Only the ones
# with a downloaded voice are wired in below; Tamil, Kannada, Gujarati,
# Punjabi, Odia, Assamese, and others have no on-device voice yet.
TTS_FALLBACK_LANG = "en"


@dataclass(frozen=True)
class Language:
    name: str
    indictrans_code: str  # FLORES-200 style code IndicTrans2 expects
    piper_model_path: Path


LANGUAGES: dict[str, Language] = {
    "en": Language("english", "eng_Latn", ROOT / "models/tts/en/en_US/lessac/medium/en_US-lessac-medium.onnx"),
    "hi": Language("hindi", "hin_Deva", ROOT / "models/tts/hi/hi_IN/priyamvada/medium/hi_IN-priyamvada-medium.onnx"),
    "ml": Language("malayalam", "mal_Mlym", ROOT / "models/tts/ml/ml_IN/meera/medium/ml_IN-meera-medium.onnx"),
    "mr": Language("marathi", "mar_Deva", ROOT / "models/tts/mr/mr_IN/google/medium/mr_IN-google-medium.onnx"),
    "te": Language("telugu", "tel_Telu", ROOT / "models/tts/te/te_IN/padmavathi/medium/te_IN-padmavathi-medium.onnx"),
}

# Owner's opening-greeting language choice. "hinglish" is a literal style
# choice (code-switched, not a caller-detected language) layered on top of
# the codes above; everything else is translated from English at runtime.
GREETING_EN = "Hi, this is Pehredar, the owner's AI assistant. Who's calling, and what's it regarding?"
HINGLISH_GREETING = "Namaste, main Pehredar hoon, malik ka AI assistant. Aap kaun hain aur kis baare mein call kar rahe hain?"

SYSTEM_PROMPT = (
    "You are Pehredar, an AI call screener. You've already asked the caller "
    "who they are and why they're calling; this is their reply, translated "
    "to English. Acknowledge briefly and helpfully in English, under 20 "
    "words. Never claim to be human."
)

# Below this avg_logprob, faster-whisper's output is unreliable enough
# (garbled/hallucinated words) that it shouldn't be forwarded to the LLM.
STT_CONFIDENCE_THRESHOLD = -0.8


def transcribe_to_english(audio_path: Path) -> tuple[str, str, float | None]:
    """Returns (english_text, detected_language_code, avg_logprob)."""
    model = WhisperModel("tiny", device="cpu", compute_type="int8", download_root=str(ROOT / "models" / "stt"))
    segments, info = model.transcribe(str(audio_path), task="translate", language=None)
    segments = list(segments)
    if not segments:
        return "", info.language, None
    text = " ".join(segment.text.strip() for segment in segments)
    avg_logprob = sum(s.avg_logprob for s in segments) / len(segments)
    return text, info.language, avg_logprob


def generate_reply(english_text: str) -> str:
    llm = Llama(model_path=str(LLM_PATH), n_ctx=1024, n_threads=4, verbose=False)
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": english_text},
        ],
        max_tokens=40,
        temperature=0.4,
    )
    return response["choices"][0]["message"]["content"].strip()


def translate_from_english(text: str, target_indictrans_code: str) -> str:
    tokenizer = AutoTokenizer.from_pretrained(EN_INDIC_MODEL_PATH, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(EN_INDIC_MODEL_PATH, trust_remote_code=True)
    ip = IndicProcessor(inference=True)
    batch = ip.preprocess_batch([text], src_lang="eng_Latn", tgt_lang=target_indictrans_code)
    inputs = tokenizer(batch, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=60, num_beams=5)
    decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    return ip.postprocess_batch(decoded, lang=target_indictrans_code)[0]


def synthesize(text: str, voice_path: Path, out_path: Path) -> None:
    voice = PiperVoice.load(str(voice_path))
    with wave.open(str(out_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(voice.config.sample_rate)
        for chunk in voice.synthesize(text):
            wav_file.writeframes(chunk.audio_int16_bytes)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", nargs="?", type=Path, help="Path to a caller utterance WAV file")
    parser.add_argument("--text", help="Skip STT and use this English text as the caller utterance directly")
    parser.add_argument(
        "--owner-language",
        choices=[*sorted(LANGUAGES), "hinglish"],
        default="hinglish",
    )
    args = parser.parse_args()

    t0 = time.perf_counter()
    if args.owner_language == "hinglish":
        greeting_text, greeting_voice = HINGLISH_GREETING, LANGUAGES["hi"].piper_model_path
    elif args.owner_language == "en":
        greeting_text, greeting_voice = GREETING_EN, LANGUAGES["en"].piper_model_path
    else:
        lang = LANGUAGES[args.owner_language]
        greeting_text, greeting_voice = translate_from_english(GREETING_EN, lang.indictrans_code), lang.piper_model_path
    synthesize(greeting_text, greeting_voice, GREETING_WAV)
    greeting_seconds = time.perf_counter() - t0
    print(f"[pehredar greets, {args.owner_language}] {greeting_text!r}  ({greeting_seconds:.2f}s, -> {GREETING_WAV})")

    detected_lang, avg_logprob = "en", None
    if args.text:
        english_text = args.text
        stt_seconds = 0.0
    elif args.audio:
        t0 = time.perf_counter()
        english_text, detected_lang, avg_logprob = transcribe_to_english(args.audio)
        stt_seconds = time.perf_counter() - t0
    else:
        parser.error("Provide either an audio file or --text")
        return

    confidence_note = f", avg_logprob={avg_logprob:.2f}" if avg_logprob is not None else ""
    print(f"[caller said, detected={detected_lang}] {english_text!r}  (STT: {stt_seconds:.2f}s{confidence_note})")

    t0 = time.perf_counter()
    if avg_logprob is not None and avg_logprob < STT_CONFIDENCE_THRESHOLD:
        reply_en = "Sorry, I didn't catch that clearly — could you say that again?"
        print("[stt confidence below threshold, skipping LLM]")
    else:
        reply_en = generate_reply(english_text)
    llm_seconds = time.perf_counter() - t0
    print(f"[pehredar acknowledges, english] {reply_en!r}  (LLM: {llm_seconds:.2f}s)")

    reply_lang = LANGUAGES.get(detected_lang)
    if reply_lang is None:
        print(f"[no piper voice for {detected_lang!r}, falling back to {TTS_FALLBACK_LANG}]")
        reply_lang = LANGUAGES[TTS_FALLBACK_LANG]

    t0 = time.perf_counter()
    if reply_lang.indictrans_code == "eng_Latn":
        reply_text = reply_en
        translate_seconds = 0.0
    else:
        reply_text = translate_from_english(reply_en, reply_lang.indictrans_code)
        translate_seconds = time.perf_counter() - t0
    print(f"[translated to {reply_lang.name}] {reply_text!r}  (translate: {translate_seconds:.2f}s)")

    t0 = time.perf_counter()
    synthesize(reply_text, reply_lang.piper_model_path, REPLY_WAV)
    tts_seconds = time.perf_counter() - t0
    print(f"[audio written] {REPLY_WAV}  (TTS: {tts_seconds:.2f}s)")

    total = greeting_seconds + stt_seconds + llm_seconds + translate_seconds + tts_seconds
    print(f"[total pipeline latency] {total:.2f}s")


if __name__ == "__main__":
    main()
