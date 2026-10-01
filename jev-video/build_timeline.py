"""פורש את הסצנות על ציר זמן אחד לפי אורך הקריינות, בונה את רצועת הקול המלאה,
את המוזיקה (שיורדת בווליום בזמן דיבור), ואת build/timeline.js לדף האנימציה.

הרצה:  tts/.venv/bin/python build_timeline.py"""
import json, subprocess, sys
import numpy as np, soundfile as sf

ROOT = __file__.rsplit("/", 1)[0] or "."
B = f"{ROOT}/build"
narr = json.load(open(f"{ROOT}/narration.json"))
tim = json.load(open(f"{B}/voice/timings.json"))

# זמן נוסף לסצנות שיש בהן רגע ויזואלי לפני הקריינות או אחריה
LEAD = {"hook": 1.2, "intro": 1.6, "outro": 0.8}
TAIL = {"outro": 5.5, "reality": 1.4, "calibration": 1.2, "how": 1.0}

# טקסט הכתוביות: מה שנאמר, עם שמות ומספרים בכתיב הרגיל
SUBS = [
    ("צ'אט ג'י פי טי", "ChatGPT"), ("צ'אטבוטים", "צ'אטבוטים"),
    ("טייפסייף", "TypeSafe"), ("אופן איי איי", "OpenAI"), ("סיסטם וואן", "System One"),
    ("קלוד סונט חמש", "Claude Sonnet 5"), ("ג'ב", "Jev"),
    ("אלפיים עשרים ושש", "2026"), ("ארבעים מיליון", "40 מיליון"),
    ("שבעים עד חמש מאות", "70 עד 500"), ("ארבעה סנט וקצת", "4.2 סנט"),
    ("ארבעים הפעמים", "40 הפעמים"), ("במאה אחוז", "ב-100%"),
    ("פי מאה תשעים ושלוש", "פי 193"), ("פי ארבע מאות ארבעים וארבע", "פי 444"),
    ("פי שלוש וחצי", "פי 3.5"), ("פי ארבעים", "פי 40"),
]
def sub(text):
    for a, b in SUBS:
        text = text.replace(a, b)
    return text

SR = 44100
scenes, t = [], 0.0
for sc in narr:
    v = tim[sc["id"]]
    lead, tail = LEAD.get(sc["id"], 0.5), TAIL.get(sc["id"], 0.75)
    start, vstart = t, t + lead
    dur = lead + v["dur"] + tail
    scenes.append({
        "id": sc["id"], "start": round(start, 3), "dur": round(dur, 3), "voice": round(vstart, 3),
        "lines": [{"t": round(vstart + l["start"], 3), "d": l["dur"], "sub": sub(l["text"])} for l in v["lines"]],
    })
    t += dur
total = round(t, 3)

# רצועת הקול
voice = np.zeros(int(total * SR) + SR, np.float32)
for s in scenes:
    a, sr = sf.read(f"{B}/voice/{s['id']}.wav", dtype="float32")
    if sr != SR:
        a = np.interp(np.linspace(0, len(a) - 1, int(len(a) * SR / sr)), np.arange(len(a)), a).astype(np.float32)
    i = int(s["voice"] * SR)
    voice[i:i + len(a)] += a
voice = voice[: int(total * SR)]
sf.write(f"{B}/voice_full.wav", voice, SR)

# המוזיקה, מונמכת מתחת לקריינות
subprocess.run([sys.executable, f"{ROOT}/music/gen_music.py", str(total), f"{B}/music.wav"], check=True)
music, _ = sf.read(f"{B}/music.wav", dtype="float32")
music = music[: len(voice)]
env = np.abs(voice)
win = int(0.25 * SR)
env = np.convolve(env, np.ones(win) / win, mode="same")
speaking = (env > 0.01).astype(np.float32)
# החלקת שינויי הווליום (כניסה ~0.15 שניות, יציאה ~0.6 שניות) בעזרת ממוצע נע
speaking = np.convolve(speaking, np.ones(int(0.5 * SR)) / int(0.5 * SR), mode="same")
gain = 0.42 - 0.26 * np.clip(speaking * 1.6, 0, 1)
mix = music * gain[:, None] + voice[:, None] * 0.95
mix = mix / np.abs(mix).max() * 0.92
sf.write(f"{B}/mix.wav", mix, SR)

json.dump({"total": total, "scenes": scenes}, open(f"{B}/timeline.json", "w"), ensure_ascii=False, indent=1)
open(f"{B}/timeline.js", "w").write("window.TL = " + json.dumps({"total": total, "scenes": scenes}, ensure_ascii=False) + ";\n")
print("total", total, "s;", len(scenes), "scenes")
