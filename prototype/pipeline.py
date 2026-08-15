"""Prototype: scripted greeting -> STT -> LLM acknowledgment -> TTS, on-device.

Call flow (matches how a real screener actually behaves): Pehredar answers
and speaks a FIXED greeting first, asking who's calling and why -- this is
never LLM-generated, since it's not a response to anything, just the app's
opening line. Only once the caller replies does the LLM run, and only to
generate a brief acknowledgment.

This split exists because "ask who's calling and why" turned out to be an
unreliable generative task at this model size across every approach tried
(zero-shot, few-shot, three rounds of LoRA fine-tuning on Gemma 3 270M --
see finetune/ -- and two attempts at an LLM-based yes/no classifier, which
collapsed to a fixed output regardless of input). Scripting it removes the
failure mode entirely; "acknowledge what the caller just said" is the
generative task the LLM was actually consistently decent at across testing.

Usage:
    uv run python prototype/pipeline.py path/to/caller_utterance.wav
    uv run python prototype/pipeline.py --text "This is Meera from HDFC about a loan offer"
    uv run python prototype/pipeline.py --text "..." --owner-language hindi
"""

from __future__ import annotations

import argparse
import time
import wave
from pathlib import Path

from faster_whisper import WhisperModel
from llama_cpp import Llama
from piper import PiperVoice

ROOT = Path(__file__).resolve().parent.parent
LLM_PATH = ROOT / "models" / "llm" / "Llama-3.2-1B-Instruct-Q4_K_M.gguf"
TTS_MODEL_PATH = ROOT / "models" / "tts" / "hi" / "hi_IN" / "priyamvada" / "medium" / "hi_IN-priyamvada-medium.onnx"
GREETING_WAV = ROOT / "prototype" / "greeting.wav"
REPLY_WAV = ROOT / "prototype" / "output.wav"

# Fixed opening line, spoken the instant Pehredar answers -- before the
# caller has said anything, so there's nothing to detect or generate from.
# Language is the owner's configured preference, not inferred from speech.
GREETINGS = {
    "english": "Hi, this is Pehredar, the owner's AI assistant. Who's calling, and what's it regarding?",
    "hindi": "नमस्ते, मैं पहरेदार हूँ, मालिक का AI सहायक। आप कौन हैं और किस बारे में कॉल कर रहे हैं?",
    "hinglish": "Namaste, main Pehredar hoon, malik ka AI assistant. Aap kaun hain aur kis baare mein call kar rahe hain?",
}

SYSTEM_PROMPT = (
    "You are Pehredar, an AI call screener. You've already asked the caller "
    "who they are and why they're calling; this is their reply. Acknowledge "
    "briefly and helpfully in under 20 words, in the same language (Hindi, "
    "English, or a Hindi-English mix) they used. Never claim to be human."
)

# Below this avg_logprob, faster-whisper's output is unreliable enough
# (garbled/hallucinated words) that it shouldn't be forwarded to the LLM.
STT_CONFIDENCE_THRESHOLD = -0.8


def transcribe(audio_path: Path) -> tuple[str, float | None]:
    model = WhisperModel("tiny", device="cpu", compute_type="int8", download_root=str(ROOT / "models" / "stt"))
    segments, _info = model.transcribe(str(audio_path), language=None)
    segments = list(segments)
    if not segments:
        return "", None
    text = " ".join(segment.text.strip() for segment in segments)
    avg_logprob = sum(s.avg_logprob for s in segments) / len(segments)
    return text, avg_logprob


def generate_reply(caller_text: str) -> str:
    llm = Llama(model_path=str(LLM_PATH), n_ctx=1024, n_threads=4, verbose=False)
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": caller_text},
        ],
        max_tokens=40,
        temperature=0.4,
    )
    return response["choices"][0]["message"]["content"].strip()


def synthesize(text: str, out_path: Path) -> None:
    voice = PiperVoice.load(str(TTS_MODEL_PATH))
    with wave.open(str(out_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(voice.config.sample_rate)
        for chunk in voice.synthesize(text):
            wav_file.writeframes(chunk.audio_int16_bytes)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", nargs="?", type=Path, help="Path to a caller utterance WAV file")
    parser.add_argument("--text", help="Skip STT and use this text as the caller utterance directly")
    parser.add_argument("--owner-language", choices=sorted(GREETINGS), default="hinglish")
    args = parser.parse_args()

    greeting_text = GREETINGS[args.owner_language]
    t0 = time.perf_counter()
    synthesize(greeting_text, GREETING_WAV)
    greeting_tts_seconds = time.perf_counter() - t0
    print(f"[pehredar greets] {greeting_text!r}  (TTS: {greeting_tts_seconds:.2f}s, -> {GREETING_WAV})")

    avg_logprob = None
    if args.text:
        caller_text = args.text
        stt_seconds = 0.0
    elif args.audio:
        t0 = time.perf_counter()
        caller_text, avg_logprob = transcribe(args.audio)
        stt_seconds = time.perf_counter() - t0
    else:
        parser.error("Provide either an audio file or --text")
        return

    confidence_note = f", avg_logprob={avg_logprob:.2f}" if avg_logprob is not None else ""
    print(f"[caller said] {caller_text!r}  (STT: {stt_seconds:.2f}s{confidence_note})")

    t0 = time.perf_counter()
    if avg_logprob is not None and avg_logprob < STT_CONFIDENCE_THRESHOLD:
        reply_text = "Sorry, I didn't catch that clearly — could you say that again?"
        print("[stt confidence below threshold, skipping LLM]")
    else:
        reply_text = generate_reply(caller_text)
    llm_seconds = time.perf_counter() - t0
    print(f"[pehredar acknowledges] {reply_text!r}  (LLM: {llm_seconds:.2f}s)")

    t0 = time.perf_counter()
    synthesize(reply_text, REPLY_WAV)
    tts_seconds = time.perf_counter() - t0
    print(f"[audio written] {REPLY_WAV}  (TTS: {tts_seconds:.2f}s)")

    total = greeting_tts_seconds + stt_seconds + llm_seconds + tts_seconds
    print(f"[total pipeline latency] {total:.2f}s")


if __name__ == "__main__":
    main()
