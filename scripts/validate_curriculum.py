#!/usr/bin/env python3
"""Basic regression checks for the Arabic Turkish curriculum."""
import json
from pathlib import Path

source = Path("app.js").read_text(encoding="utf-8")
start = source.index("const L=") + len("const L=")
end = source.index(";\nconst K=", start)
lessons = json.loads(source[start:end])

alphabet = next(x for x in lessons if x["t"] == "الأبجدية التركية")
expected = ["A a","B b","C c","Ç ç","D d","E e","F f","G g","Ğ ğ","H h","I ı","İ i","J j","K k","L l","M m","N n","O o","Ö ö","P p","R r","S s","Ş ş","T t","U u","Ü ü","V v","Y y","Z z"]
actual = [x[0] for x in alphabet["w"]]
assert actual == expected, f"Turkish alphabet mismatch: {actual}"
assert len(alphabet["q"]) >= 5, "Alphabet quiz is too short"

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

assert "navigator.share" not in source, "Generic Android share sheet can expose email/account targets"
assert "mailto:" not in source, "Email share target must not be offered"
assert "https://wa.me/?text=" in source, "WhatsApp direct share link missing"
html = Path("index.html").read_text(encoding="utf-8")
assert "تعلم لغات" in html and "Türkçe Akademi" not in html, "Visible app name was not fully updated"
manifest = json.loads(Path("manifest.webmanifest").read_text(encoding="utf-8"))
assert manifest["name"] == "تعلم لغات" and manifest["short_name"] == "تعلم لغات"
print(f"PASS: {len(lessons)} lessons; all 29 Turkish letters; sequential 0–20; quiz integrity; WhatsApp-only sharing; app rename.")
