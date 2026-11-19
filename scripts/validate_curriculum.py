#!/usr/bin/env python3
"""Basic regression checks for the Arabic Turkish curriculum."""
import json
from pathlib import Path

source = Path("app.js").read_text(encoding="utf-8")
start = source.index("const L=") + len("const L=")
end = source.index(";\nconst ALPHABET_NAMES=", start)
lessons = json.loads(source[start:end])

alphabet = next(x for x in lessons if x["t"] == "الأبجدية التركية")
expected = ["A a","B b","C c","Ç ç","D d","E e","F f","G g","Ğ ğ","H h","I ı","İ i","J j","K k","L l","M m","N n","O o","Ö ö","P p","R r","S s","Ş ş","T t","U u","Ü ü","V v","Y y","Z z"]
actual = [x[0] for x in alphabet["w"]]
assert actual == expected, f"Turkish alphabet mismatch: {actual}"
assert len(alphabet["q"]) >= 5, "Alphabet quiz is too short"

names_match = __import__("re").search(r"const ALPHABET_NAMES=(\[.*?\]);", source)
assert names_match, "Canonical one-time alphabet pronunciation map is missing"
letter_names = dict(json.loads(names_match.group(1)))
assert set(letter_names) == set(expected), "Alphabet pronunciation map must cover all 29 letters exactly once"
assert letter_names["A a"] == "a" and letter_names["B b"] == "be" and letter_names["Ğ ğ"] == "yumuşak ge", "Alphabet letter names are incorrect"
assert "pronunciationText(l.t,tr)" in source, "Alphabet audio must use its single letter name"
assert "currentAudio.pause()" in source, "Previous audio must stop before a new word is played"

numbers = next(x for x in lessons if x["t"] == "الأرقام 1–20")
expected_numbers = ["Sıfır","Bir","İki","Üç","Dört","Beş","Altı","Yedi","Sekiz","Dokuz","On","On bir","On iki","On üç","On dört","On beş","On altı","On yedi","On sekiz","On dokuz","Yirmi"]
actual_numbers = [x[0] for x in numbers["w"]]
assert actual_numbers == expected_numbers, f"Number sequence mismatch: {actual_numbers}"
assert len(numbers["q"]) >= 5, "Number quiz is too short"

for index, lesson in enumerate(lessons, 1):
    assert lesson.get("t") and lesson.get("d"), f"Lesson {index} missing title or description"
    assert len(lesson.get("w", [])) >= 12, f"Lesson {index} needs at least 12 vocabulary items"
    assert len(lesson.get("q", [])) >= 5, f"Lesson {index} needs at least 5 quiz questions"
    for question in lesson["q"]:
        assert len(question) == 3 and question[2] in range(len(question[1])), f"Bad quiz answer in {lesson['t']}"

assert "https://wa.me/?text=" in source and "encodeURIComponent(message)" in source, "WhatsApp direct share is missing"
assert "navigator.share" not in source and "mailto:" not in source, "Generic share sheet or email target must not be offered"
assert 'const message="حمّل تطبيق تعلم لغات للأندرويد من هنا:\\n"+url' in source and "releases/latest/download/app-debug.apk" in source, "WhatsApp message must contain the direct APK download link"
assert "copyShare" in Path("index.html").read_text(encoding="utf-8"), "Share button is missing"
html = Path("index.html").read_text(encoding="utf-8")
assert "تعلم لغات" in html and "Türkçe Akademi" not in html, "Visible app name was not fully updated"
manifest = json.loads(Path("manifest.webmanifest").read_text(encoding="utf-8"))
assert manifest["name"] == "تعلم لغات" and manifest["short_name"] == "تعلم لغات"
print(f"PASS: {len(lessons)} lessons; all 29 Turkish letters; sequential 0–20; quiz integrity; share-link privacy; app rename.")

assert "voicePicker" in Path("index.html").read_text(encoding="utf-8"), "Voice selector is missing"
assert "getVoices()" in source and "voiceschanged" in source, "Device Turkish voice discovery is missing"
assert 'selectedVoice==="recorded"?humanAudio[audioKey(tr)]:null' in source, "Selected device voice must bypass the default recorded voice"
