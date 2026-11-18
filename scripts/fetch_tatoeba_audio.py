#!/usr/bin/env python3
"""Fetch reusable, human-recorded Turkish vocabulary clips from Tatoeba."""
import bz2, hashlib, io, json, os, re, tarfile, unicodedata, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "audio"
AUDIO.mkdir(exist_ok=True)
BASE = "https://downloads.tatoeba.org/exports/"
HEADERS = {"User-Agent": "TurkceAkademi/1.0 (educational app; Tatoeba audio attribution)"}

def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()

def rows_from_archive(data):
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:bz2") as archive:
        member = next((m for m in archive.getmembers() if m.isfile()), None)
        if not member:
            return
        stream = archive.extractfile(member)
        for raw in stream:
            try:
                yield raw.decode("utf-8").rstrip("\r\n").split("\t")
            except UnicodeDecodeError:
                continue

def norm(value):
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    value = re.sub(r"^[\W_]+|[\W_]+$", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value)
    return value

def main():
    source = (ROOT / "app.js").read_text(encoding="utf-8")
    start = source.index("const L=") + len("const L=")
    end = source.index(";\nconst K=", start)
    lessons = json.loads(source[start:end])
    wanted = {}
    for lesson in lessons:
        for tr, _ in lesson.get("w", []):
            key = norm(tr)
            if key:
                wanted.setdefault(key, tr)

    sentence_rows = None
    # Prefer the Turkish-only export if it is present; fall back to the official full export.
    for url in (BASE + "per_language/tur/sentences.tar.bz2",
                BASE + "sentences.tar.bz2"):
        try:
            sentence_rows = rows_from_archive(get(url))
            break
        except Exception as exc:
            print("Sentence export unavailable:", url, str(exc)[:180])
    if sentence_rows is None:
        raise RuntimeError("Could not download Tatoeba sentence export")

    matched = {}
    for row in sentence_rows:
        if len(row) < 3:
            continue
        sid, lang, text = row[0], row[1], row[2]
        if lang != "tur":
            continue
        key = norm(text)
        if key in wanted and key not in matched:
            matched[key] = {"sentence_id": sid, "text": text}

    audio_rows = rows_from_archive(get(BASE + "sentences_with_audio.tar.bz2"))
    audio_by_sentence = {}
    for row in audio_rows:
        if len(row) < 5:
            continue
        sid, audio_id, username, license_name, attribution = row[:5]
        lic = license_name.upper().replace("-", " ")
        reusable = ("CC0" in lic or ("CC BY" in lic and "NC" not in lic and "ND" not in lic))
        if reusable:
            audio_by_sentence.setdefault(sid, []).append(
                {"audio_id": audio_id, "username": username, "license": license_name,
                 "attribution": attribution}
            )

    manifest = {}
    credits = [
        "Türkçe Akademi — audio credits",
        "Human-contributed Turkish recordings sourced from Tatoeba.",
        "Each clip is included only when the contributor's audio license permits reuse.",
        "Audio license and contributor attribution are listed per clip below.",
        "Tatoeba downloads and licensing notes: https://tatoeba.org/en/downloads",
        ""
    ]
    for key, item in matched.items():
        choices = audio_by_sentence.get(item["sentence_id"], [])
        if not choices:
            continue
        choice = choices[0]
        filename = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16] + ".mp3"
        try:
            blob = get("https://tatoeba.org/audio/download/" + choice["audio_id"])
            if not blob.startswith(b"ID3") and len(blob) < 1000:
                continue
            (AUDIO / filename).write_bytes(blob)
        except Exception as exc:
            print("Audio skipped:", item["text"], str(exc)[:120])
            continue
        record = {
            "file": "./audio/" + filename,
            "text": item["text"],
            "source": "Tatoeba",
            "username": choice["username"],
            "license": choice["license"],
            "attribution": choice["attribution"],
            "sentence": "https://tatoeba.org/en/sentences/show/" + item["sentence_id"]
        }
        manifest[key] = record
        credits.append(f'{item["text"]} — {choice["username"]} — {choice["license"]} — {choice["attribution"]}')
    (AUDIO / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (AUDIO / "CREDITS.txt").write_text("\n".join(credits) + "\n", encoding="utf-8")
    print(f"Added {len(manifest)} licensed human-recorded Turkish clips for {len(wanted)} vocabulary items.")

if __name__ == "__main__":
    main()
