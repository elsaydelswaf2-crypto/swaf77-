#!/usr/bin/env python3
"""Generate offline Turkish pronunciation WAV files with the Piper Fahrettin voice."""
import hashlib
import json
import re
import unicodedata
import wave
from pathlib import Path
from piper import PiperVoice

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "audio"
MODEL = ROOT / "models" / "tr_TR-fahrettin-medium.onnx"
AUDIO.mkdir(exist_ok=True)

def norm(value):
    value = unicodedata.normalize("NFKC", value)
    value = value.translate(str.maketrans({"I": "ı", "İ": "i"})).lower().strip()
    value = re.sub(r'^[.,!?;:()\"“”]+|[.,!?;:()\"“”]+$', "", value)
    return re.sub(r" +", " ", value)

def main():
    if not MODEL.exists():
        raise FileNotFoundError(f"Missing Piper model: {MODEL}")
    source = (ROOT / "app.js").read_text(encoding="utf-8")
    start = source.index("const L=") + len("const L=")
    end = source.index(";\nconst K=", start)
    lessons = json.loads(source[start:end])
    names_match = re.search(r"const ALPHABET_NAMES=(\\[.*?\\]);", source)
    if not names_match:
        raise RuntimeError("Missing canonical Turkish alphabet letter names")
    alphabet_names = dict(json.loads(names_match.group(1)))
    wanted = {}
    for lesson in lessons:
        for phrase, _ in lesson.get("w", []):
            key = norm(phrase)
            spoken = alphabet_names.get(phrase, phrase) if lesson.get("t") == "الأبجدية التركية" else phrase
            if key:
                wanted.setdefault(key, spoken)

    voice = PiperVoice.load(str(MODEL))
    manifest = {}
    for key, phrase in wanted.items():
        filename = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16] + ".wav"
        target = AUDIO / filename
        with wave.open(str(target), "wb") as wav_file:
            voice.synthesize_wav(phrase, wav_file)
        manifest[key] = {
            "file": "./audio/" + filename,
            "text": phrase,
            "type": "synthetic",
            "voice": "Fahrettin — Piper Turkish medium"
        }

    (AUDIO / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    credits = [
        "Türkçe Akademi — audio credits",
        "These are pre-generated neural text-to-speech files, NOT recordings of a teacher.",
        "Voice: tr_TR-fahrettin-medium (Piper).",
        "Voice dataset license: CC0, as stated in the model card.",
        "Voice model card: https://huggingface.co/rhasspy/piper-voices/blob/1af0d6b01d3dbe698a426f0c3424650ef77fc131/tr/tr_TR/fahrettin/medium/MODEL_CARD",
        "Piper project: https://github.com/rhasspy/piper",
        "Piper voice model repository: https://huggingface.co/rhasspy/piper-voices",
        ""
    ]
    (AUDIO / "CREDITS.txt").write_text("\n".join(credits), encoding="utf-8")
    print(f"Generated {len(manifest)} offline Turkish WAV pronunciation files.")

if __name__ == "__main__":
    main()
