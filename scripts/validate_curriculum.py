#!/usr/bin/env python3
"""Regression checks for beginner language curriculum, audio, and share behavior."""
import json, re
from pathlib import Path
source=Path("app.js").read_text(encoding="utf-8")
html=Path("index.html").read_text(encoding="utf-8")
start=source.index("const L=")+len("const L=")
end=source.index(";\nconst ALPHABET_NAMES=",start)
tr=json.loads(source[start:end])
expected=["A a","B b","C c","Ç ç","D d","E e","F f","G g","Ğ ğ","H h","I ı","İ i","J j","K k","L l","M m","N n","O o","Ö ö","P p","R r","S s","Ş ş","T t","U u","Ü ü","V v","Y y","Z z"]
alphabet=next(x for x in tr if x["t"]=="الأبجدية التركية")
assert [x[0] for x in alphabet["w"]]==expected
m=re.search(r"const ALPHABET_NAMES=(\[.*?\]);",source,re.S); assert m
names=dict(json.loads(m.group(1)))
assert set(names)==set(expected) and names["A a"]=="a" and names["Ğ ğ"]=="yumuşak ge"
for lesson in tr: assert len(lesson.get("w",[]))>=12 and len(lesson.get("q",[]))>=5
m=re.search(r"const EN_MORE=(\[.*?\]);",source,re.S); assert m
en_more=json.loads(m.group(1)); assert len(en_more)>=14
for lesson in en_more: assert len(lesson[2])>=12 and len(lesson[3])>=2
m=re.search(r"const AR=makeExtraLessons\((\[.*\]),\"ar\"\);",source,re.S); assert m
ar=json.loads(m.group(1)); assert len(ar)>=18
for lesson in ar: assert len(lesson[2])>=12 and len(lesson[3])>=2
assert "function lessons(){return course===\"tr\"?L:course===\"en\"?EN:AR}" in source
assert "course=direction===\"tr-ar\"?\"tr\":direction===\"en-ar\"?\"en\":\"ar\";" in source
for pair in ["tr-ar","en-ar","ar-en"]: assert pair in html
assert 'option value="ar">العربية' in html and 'id="englishVoicePicker"' in html
assert 'id="previewTarget"' in html and 'id="previewMeaning"' in html
assert 'queueUtterance.rate=rate' in source and 'queueAudio.playbackRate=rate' in source
assert 'rate:0.68' in source and 'rate:0.74' in source
assert 'say(p[0],ll[0],()=>say(p[0],ll[0],()=>say(p[1],ll[1],()=>say(p[1]' in source
assert 'speechSynthesis.cancel()' in source and 'audioKey(clipKey)' in source
assert 'https://wa.me/?text=' in source and 'encodeURIComponent(message)' in source
assert 'releases/latest/download/app-debug.apk' in source
assert 'navigator.share' not in source and 'mailto:' not in source
for id in ["arabicVoicePicker","arabicVoiceHint","englishVoicePicker","englishVoiceHint"]: assert id in html
assert "voiceURI" in source and "selectedSystemVoice" in source and "audioOrderPicker" in source and "pushAudioPair" in source
manifest=json.loads(Path("manifest.webmanifest").read_text(encoding="utf-8"))
assert manifest["name"]=="تعلم لغات"
print(f"PASS: {len(tr)} Turkish, {4+len(en_more)} English, {len(ar)} Arabic lessons; 29 Turkish letters; slower paired audio; three courses.")
