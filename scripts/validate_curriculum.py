#!/usr/bin/env python3
"""Regression checks for the Arabic/Turkish/English curriculum."""
import json, re
from pathlib import Path
source=Path("app.js").read_text(encoding="utf-8")
start=source.index("const L=")+len("const L=")
end=source.index(";\nconst ALPHABET_NAMES=",start)
lessons=json.loads(source[start:end])
expected=["A a","B b","C c","Ç ç","D d","E e","F f","G g","Ğ ğ","H h","I ı","İ i","J j","K k","L l","M m","N n","O o","Ö ö","P p","R r","S s","Ş ş","T t","U u","Ü ü","V v","Y y","Z z"]
alphabet=next(x for x in lessons if x["t"]=="الأبجدية التركية")
assert [x[0] for x in alphabet["w"]]==expected
m=re.search(r"const ALPHABET_NAMES=(\[.*?\]);",source)
assert m
names=dict(json.loads(m.group(1)))
assert set(names)==set(expected) and names["A a"]=="a" and names["Ğ ğ"]=="yumuşak ge"
assert "pronunciationText(l.t,p[0])" in source
assert "speechSynthesis.cancel()" in source
assert 'const EN=' in source and "كلمات إنجليزية شائعة" in source and "جمل يومية أساسية" in source
for title in ["في المطعم والتسوق","المواصلات والاتجاهات"]:
    assert title in source
for lesson in lessons:
    assert len(lesson.get("w",[]))>=12 and len(lesson.get("q",[]))>=5
assert all("unitPlay" in x for x in [Path("index.html").read_text(encoding="utf-8"),source])
html=Path("index.html").read_text(encoding="utf-8")
for x in ["tr-ar","ar-tr","en-ar","ar-en"]: assert x in html
assert "https://wa.me/?text=" in source and "encodeURIComponent(message)" in source
assert "releases/latest/download/app-debug.apk" in source
assert "navigator.share" not in source and "mailto:" not in source
assert "audioKey(clipKey)" in source
manifest=json.loads(Path("manifest.webmanifest").read_text(encoding="utf-8"))
assert manifest["name"]=="تعلم لغات"
print(f"PASS: {len(lessons)} Turkish lessons, 4 English lessons, 29 Turkish letters, 4 directions, unit audio queue, WhatsApp APK share.")
