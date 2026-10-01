"""מייצר קריינות בעברית לכל סצנה: ניקוד, תיקון הגייה של שמות לועזיים, סינתזה, חיבור ושמירת תזמונים.

הרצה:  .venv/bin/python gen_voice.py ../narration.json ../build/voice [מזהי סצנות...]"""
import sys, types, json, re
sys.modules['sounddevice'] = types.ModuleType('sounddevice')  # israwave מייבא אותו רק לניגון; אין בו צורך כאן
import numpy as np, soundfile as sf
from israwave import IsraWave
from nakdimon_onnx import Nakdimon

SHEVA, HPATAH, TSERE, SEGOL, PATAH, QAMATS, HOLAM, HIRIQ, DAGESH = (
    "ְ", "ֲ", "ֵ", "ֶ", "ַ", "ָ", "ֹ", "ִ", "ּ")
# מילה בלי ניקוד -> כתיב מנוקד שנהגה נכון (שמות לועזיים שהמנקד טועה בהם)
FIX = {
    "טייפסייף": "ט" + TSERE + "ייפ" + DAGESH + " ס" + TSERE + "ייף",
    "כהנמן": "כ" + DAGESH + QAMATS + "ה" + SHEVA + "נ" + SEGOL + "מ" + PATAH + "ן",
    "דיוגו": "ד" + SHEVA + "יו" + HOLAM + "גו" + DAGESH,
    "אלמיידה": "א" + PATAH + "ל" + SHEVA + "מ" + TSERE + "יד" + QAMATS + "ה",
    "איי": "א" + TSERE + "יי",
    "סונט": "סו" + HOLAM + "נ" + SEGOL + "ט",
    "טוקנים": "טו" + HOLAM + "ק" + TSERE + "נ" + HIRIQ + "ים",
    "וואן": "ו" + QAMATS + "ואן",
    "בינה": "ב" + DAGESH + HIRIQ + "ינ" + QAMATS + "ה",
    "ג'ב": "ג" + SEGOL + "'ב",
    "וג'ב": "ו" + SHEVA + "ג" + SEGOL + "'ב",
}
MARKS = re.compile(r"[֑-ׇ]")

def fix(dotted):
    out = []
    for tok in dotted.split(" "):
        m = re.match(r"^(\W*)(.*?)([^\w֑-ׇ']*)$", tok)
        pre, word, post = m.groups()
        base = MARKS.sub("", word)
        out.append(pre + FIX.get(base, word) + post)
    return " ".join(out)

def main(narration_path, out_dir, only=None):
    nak = Nakdimon("nakdimon.onnx")
    tts = IsraWave("israwave.onnx", "espeak-ng-data")
    sr = tts.sample_rate
    scenes = json.load(open(narration_path))
    timings = {}
    for sc in scenes:
        if only and sc["id"] not in only:
            continue
        parts, lines, t = [], [], 0.0
        for i, line in enumerate(sc["lines"]):
            dotted = fix(nak.compute(line))
            wav = np.asarray(tts.create(dotted, rate=1.0).samples, dtype=np.float32)
            # חיתוך שקט בתחילת ההקלטה ובסופה
            nz = np.where(np.abs(wav) > 0.004)[0]
            if len(nz):
                wav = wav[max(0, nz[0] - int(0.10 * sr)): nz[-1] + int(0.08 * sr)]
            lines.append({"text": line, "dotted": dotted, "start": round(t, 3), "dur": round(len(wav) / sr, 3)})
            parts.append(wav); t += len(wav) / sr
            gap = 0.42 if line.rstrip().endswith((".", "?", ":")) else 0.25
            if i < len(sc["lines"]) - 1:
                parts.append(np.zeros(int(gap * sr), np.float32)); t += gap
        audio = np.concatenate(parts)
        audio = audio / max(1e-6, np.abs(audio).max()) * 0.89
        sf.write(f"{out_dir}/{sc['id']}.wav", audio, sr)
        timings[sc["id"]] = {"dur": round(len(audio) / sr, 3), "lines": lines}
        print(sc["id"], timings[sc["id"]]["dur"], flush=True)
    path = f"{out_dir}/timings.json"
    try:
        old = json.load(open(path))
    except FileNotFoundError:
        old = {}
    old.update(timings)
    json.dump(old, open(path, "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], set(sys.argv[3:]) or None)
