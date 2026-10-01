# Jev: סרטון הסבר בעברית (מושן גרפיק)

סרטון באורך כשלוש דקות (1080p, 30fps) שמסביר מה זה **Jev**, מודל ה-System One של TypeSafe AI, עם קריינות בעברית, מוזיקת רקע וכתוביות.

**הקובץ המוגמר:** `out/jev-explainer.mp4`

## מבנה

| קובץ | תפקיד |
|---|---|
| `narration.json` | טקסט הקריינות לפי סצנות (14 סצנות) |
| `tts/gen_voice.py` | קריינות עברית: ניקוד אוטומטי (Nakdimon), תיקוני הגייה לשמות לועזיים, סינתזה (israwave) |
| `music/gen_music.py` | מוזיקת רקע מקורית שנוצרת בקוד (לה מינור, 100 BPM), בלי בעיות זכויות |
| `build_timeline.py` | מסנכרן את הסצנות לאורכי הקריינות, מחבר את רצועת הקול ומנמיך את המוזיקה כשיש דיבור |
| `web/index.html`, `web/scenes.js` | האנימציה (HTML + GSAP), פונטים Heebo ו-Rubik במשקלים דקים ועבים |
| `render.mjs` | רינדור פריים אחרי פריים ב-Chromium וקידוד ב-ffmpeg |
| `assets/typesafe-mark.svg` | סמל TypeSafe |
| `SOURCES.md` | מקורות לכל נתון בסרטון |

## בנייה מחדש, שלב אחרי שלב

### מה צריך
- Python 3.10 ומעלה, Node.js 20 ומעלה, ו-ffmpeg
- Chromium (או Chrome). ‏`render.mjs` מחפש אותו ב-`/opt/pw-browsers`; אפשר להגדיר נתיב אחר במשתנה הסביבה `CHROMIUM`.

### שלב 1: הכנת הקריינות (פעם אחת)
```sh
cd jev-video/tts
python -m venv .venv
.venv/bin/pip install israwave nakdimon-onnx soundfile numpy

# מודל הקול, מודל הניקוד ונתוני ההגייה
for f in israwave.onnx nakdimon.onnx espeak-ng-data.tar.gz; do
  curl -LO https://github.com/thewh1teagle/israwave/releases/download/v0.1.0/$f
done
tar xzf espeak-ng-data.tar.gz
```

### שלב 2: יצירת הקריינות
```sh
cd jev-video/tts
.venv/bin/python gen_voice.py ../narration.json ../build/voice
# אפשר לייצר מחדש רק סצנות מסוימות:
.venv/bin/python gen_voice.py ../narration.json ../build/voice intro outro
```
כדי לשנות את מה שנאמר, עורכים את `narration.json`. שמות לועזיים שנהגים לא נכון מתקנים במילון `FIX` שבתוך `gen_voice.py`.

### שלב 3 (לא חובה): בדיקה שהקריינות מובנת
```sh
curl -L https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2 | tar xj
.venv/bin/pip install sherpa-onnx
.venv/bin/python asr.py ../build/voice/*.wav     # מדפיס תמלול של כל סצנה
```

### שלב 4: תזמון ומיקס
```sh
cd jev-video
tts/.venv/bin/python build_timeline.py
```
הסקריפט מסנכרן את הסצנות לאורך הקריינות, מייצר מוזיקה באורך המדויק, מנמיך אותה כשיש דיבור, ושומר את `build/mix.wav` ואת `build/timeline.js`.

### שלב 5: רינדור
```sh
cd jev-video
npm install
node render.mjs --stills 30 66 108     # כמה תמונות לבדיקה, ב-build/stills/
node render.mjs                        # הסרטון המלא -> out/jev-explainer.mp4 (כ-7 דקות)
```

### שינוי העיצוב
- **הסצנות:** כל הטקסט והמבנה ב-`web/index.html`, והאנימציה ב-`web/scenes.js`. התזמון של כל אנימציה צמוד לשורת הקריינות שלה, כך ששינוי בקריינות מזיז את האנימציה אוטומטית.
- **צבעים:** משתני ה-CSS בראש `web/index.html` (`--pink`, `--bg` וכו').
- **הלוגו:** `assets/typesafe-mark.svg`. הוא נלקח מחבילות קהילה ב-npm, כי האתר הרשמי היה חסום בסביבה שבה הסרטון נבנה. כדאי לוודא אותו מול ערכת המותג הרשמית.

## המצגות
```sh
cd jev-video/deck
python3 build_deck.py            # המצגת הבסיסית  -> out/project/
python3 build_deck_extended.py   # המצגת המורחבת -> out_extended/project/
```
התוכן של כל שקף, כולל הערות הדובר, נמצא בקבצים האלה. הטקסט העברי נעטף בתווי כיווניות (RLI/PDI), כי לפורמט השקפים אין הגדרת כיוון.
