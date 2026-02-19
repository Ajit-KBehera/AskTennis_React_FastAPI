# TTS Stack: Parakeet, SmolLM3, Kokoro

## What each component is

| Component   | Type        | Role |
|------------|-------------|------|
| **Parakeet** | ASR or TTS toolkit | **NVIDIA NeMo Parakeet** = Automatic Speech Recognition (speech → text). **Paddle Parakeet** = TTS toolkit (archived 2022). So “Parakeet” in a TTS stack usually means **ASR**: user speaks → Parakeet transcribes. |
| **SmolLM3**   | Language model     | **Not TTS.** It’s a 3B-parameter LLM (text in → text out). Use it to **prepare or rewrite text** before TTS (e.g. normalize, shorten, add structure) or as the “brain” in a voice pipeline (user question → SmolLM3 → answer text → TTS). |
| **Kokoro**    | TTS                | **Text → speech.** Lightweight, ONNX-based, multi-voice, multi-language. This is the component that actually produces audio. |

So for “TTS using Parakeet, SmolLM3, Kokoro” you get two natural stacks:

- **TTS-only:** SmolLM3 (optional text prep) → **Kokoro** (speech). No Parakeet.
- **Voice-in, voice-out:** **Parakeet** (ASR) → **SmolLM3** (answer) → **Kokoro** (TTS).

---

## Stack 1: TTS only (e.g. “read AI answer aloud”)

Use **Kokoro** for synthesis. Optionally use **SmolLM3** to clean/summarize the text before speaking.

### Requirements

- **Kokoro**
  - Python 3.9–3.12.
  - `pip install kokoro-tts`
  - Model files in working dir (or configured path):
    - `kokoro-v1.0.onnx`
    - `voices-v1.0.bin`
  - Download: [kokoro-tts releases](https://github.com/nazdridoy/kokoro-tts/releases) (v1.0.0).
- **SmolLM3** (optional)
  - For text preprocessing/summarization: Hugging Face `transformers` + model e.g. `HuggingFaceTB/SmolLM3-3B` (or smaller variant). Needs GPU/CPU and enough RAM.

### Backend (FastAPI) sketch

- **Option A – CLI (simplest)**  
  Call `kokoro-tts` via subprocess: write text to stdin or temp file, get WAV/MP3 back, stream or return file.

```python
# Example: subprocess-based TTS
import subprocess
import tempfile
import os

def text_to_speech_kokoro_cli(text: str, voice: str = "af_sarah", lang: str = "en-us", speed: float = 1.0):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out_path = f.name
    try:
        # kokoro-tts reads from stdin with "-" and writes to file
        proc = subprocess.run(
            ["kokoro-tts", "-", out_path, "--voice", voice, "--lang", lang, "--speed", str(speed)],
            input=text.encode("utf-8"),
            capture_output=True,
            timeout=60,
            cwd=os.getenv("KOKORO_MODEL_DIR", "."),  # dir with .onnx and voices .bin
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode())
        with open(out_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(out_path):
            os.unlink(out_path)
```

- **Option B – Python API**  
  If the `kokoro-tts` package exposes an internal API or you use **PyKokoro** ([PyKokoro docs](https://pykokoro.readthedocs.io/)), call that instead of the CLI for in-process generation.

- **Optional text prep with SmolLM3**  
  Before calling Kokoro, run the text through SmolLM3 (e.g. “Summarize for speaking in 2–3 sentences” or “Normalize abbreviations”). Use the model’s generated text as input to Kokoro.

### Frontend (React)

- Add a “Play” / “Read aloud” control next to the AI answer.
- Call your FastAPI TTS endpoint with the answer text (and optional voice/speed).
- Backend returns WAV or MP3; frontend plays via `<audio src={url}>` or `Audio` object with a blob URL.

### Env / config

- `KOKORO_MODEL_DIR`: directory containing `kokoro-v1.0.onnx` and `voices-v1.0.bin`.
- Optional: `SMOLLM3_MODEL` or Hugging Face token if you use SmolLM3.

---

## Stack 2: Full voice pipeline (Parakeet + SmolLM3 + Kokoro)

Flow: **User speaks → Parakeet (ASR) → SmolLM3 (answer) → Kokoro (TTS) → Play.**

### Requirements

- **Parakeet (ASR)**  
  NVIDIA NeMo Parakeet-TDT or similar: speech → text. Usually requires NeMo + GPU. Alternative: a lighter ASR (e.g. Whisper, faster-whisper) if you want to keep “Parakeet” only as an optional or future swap.
- **SmolLM3**  
  Same as above: takes transcribed text (and optionally context), outputs answer text.
- **Kokoro**  
  Same as above: takes answer text, outputs audio.

### Backend flow

1. Receive audio (e.g. WebM/MP3 from browser).
2. Run Parakeet (or your ASR) → transcript.
3. Run SmolLM3 with transcript (and system prompt / tennis context) → answer text.
4. Run Kokoro on answer text → audio.
5. Return audio (and optionally transcript + answer text) to frontend.

### Frontend

- Record microphone (e.g. `MediaRecorder` or Web Audio).
- POST audio to `/api/voice-query` (or similar).
- Receive audio blob; play in `<audio>` or via `Audio` + blob URL.

---

## Summary: what you need for each stack

| Need | TTS-only (Kokoro ± SmolLM3) | Full pipeline (Parakeet + SmolLM3 + Kokoro) |
|------|----------------------------|---------------------------------------------|
| **Kokoro** (pip + model files) | Yes | Yes |
| **SmolLM3** (optional for TTS-only) | Optional (text prep) | Yes (answer generation) |
| **Parakeet (ASR)** | No | Yes (or another ASR) |
| **FastAPI endpoint** | TTS: text in, audio out | Voice: audio in, audio (+ text) out |
| **Frontend** | “Read aloud” + &lt;audio&gt; | Record + upload + play response |

**Practical order:** Implement **TTS with Kokoro** first (and optionally SmolLM3 for text prep). Add Parakeet (or another ASR) when you’re ready for full voice-in/voice-out.

---

## Kokoro quick reference

- **Install:** `pip install kokoro-tts`
- **Model files:** `kokoro-v1.0.onnx`, `voices-v1.0.bin` in `KOKORO_MODEL_DIR`.
- **CLI:** `echo "Hello" | kokoro-tts - output.wav --voice af_sarah --lang en-us`
- **Voices:** e.g. `af_sarah`, `am_adam`, `bf_emma` (en-gb), etc. List: `kokoro-tts --help-voices`
- **Languages:** `en-us`, `en-gb`, `fr-fr`, `ja`, `it`, `cmn`, etc. List: `kokoro-tts --help-languages`

If you tell me whether you want “read answer aloud” only or the full voice pipeline first, I can outline exact FastAPI routes and React calls (and where to plug in SmolLM3/Parakeet) for your repo.
