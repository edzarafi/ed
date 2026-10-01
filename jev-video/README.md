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

## בנייה מחדש

```sh
# קול (פעם אחת: python -m venv tts/.venv && pip install israwave nakdimon-onnx soundfile,
# ולהוריד את israwave.onnx, nakdimon.onnx ו-espeak-ng-data מ-github.com/thewh1teagle/israwave/releases/tag/v0.1.0 לתיקייה tts/)
cd tts && .venv/bin/python gen_voice.py ../narration.json ../build/voice && cd ..
tts/.venv/bin/python build_timeline.py      # תזמון, מיקס קול ומוזיקה
npm i && node render.mjs                     # out/jev-explainer.mp4
node render.mjs --stills 30 66 108           # תמונות בדיקה ב-build/stills
```
