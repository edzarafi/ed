# Jev: סרטון, מצגות ותהליך עבודה עם מסמכים רפואיים

המאגר מסביר את **Jev**, מודל ה-System One של TypeSafe AI, בשלוש דרכים:

| תוצר | איפה | מה יש בו |
|---|---|---|
| סרטון הסבר | `jev-video/out/jev-explainer.mp4` | סרטון מושן גרפיק בעברית (2:54), עם קריינות, מוזיקה וכתוביות |
| מצגת בסיסית | `jev-video/deck/` | 25 שקפים: מה זה Jev, איך הוא עובד, דוגמאות, מגבלות |
| מצגת מורחבת | `jev-video/deck/` | 41 שקפים: הבסיסית, ועוד פרק על מסמכים רפואיים |
| מחברת | `jev-docs-pipeline/jev_medical_pipeline.ipynb` | Jev מסווג מסמכים רפואיים, Claude מחלץ נתונים, Jev נותן ציון ביטחון לכל נתון |

> ⚠️ כל המסמכים הרפואיים במאגר סינתטיים ובדויים. זה לא כלי קליני ואין להשתמש בו לקבלת החלטות רפואיות.

---

## 1. צפייה בסרטון

הקובץ המלא: `jev-video/out/jev-explainer.mp4` (35MB, איכות גבוהה).
עותק קטן יותר לצפייה מהירה: `jev-video/out/jev-explainer-preview.mp4` (12MB).

---

## 2. הרצת המחברת

### מה צריך
- Python 3.10 ומעלה
- למצב **live** (קריאות אמיתיות למודלים): שני מפתחות API
  - `TYPESAFE_API_KEY`: מפתח של TypeSafe AI, בשביל Jev
  - `ANTHROPIC_API_KEY`: מפתח של Anthropic, בשביל Claude
- בלי מפתחות, המחברת רצה אוטומטית במצב **demo**.

### הרצה על המחשב
```sh
cd jev-docs-pipeline
python -m venv .venv
source .venv/bin/activate          # ב-Windows:  .venv\Scripts\activate
pip install -r requirements.txt

# רק למצב live:
export TYPESAFE_API_KEY=...
export ANTHROPIC_API_KEY=...

jupyter notebook jev_medical_pipeline.ipynb
```

### הגדרות (בתא השני של המחברת, או במשתני סביבה)
| הגדרה | ערכים | מה היא עושה |
|---|---|---|
| `MODE` | ריק (אוטומטי) / `live` / `demo` | אוטומטי = live אם שני המפתחות מוגדרים, אחרת demo |
| `PROMPT_LANG` | `he` (ברירת מחדל) / `en` | שפת ההנחיות שנשלחות ל-Jev ול-Claude |
| `INJECT_ERRORS` | `True` / `False` | מבחן כאוס: שותל 2 טעויות חילוץ כדי לבדוק ששלב האימות תופס אותן |

### ב-Google Colab
1. מעלים את התיקייה `jev-docs-pipeline` ל-Colab (או משכפלים את המאגר).
2. מריצים בתא הראשון: `%pip install -q typesafe-sdk anthropic pydantic pandas`
3. שומרים את המפתחות ב-Secrets של Colab (סמל המפתח בסרגל הצד), וטוענים אותם:
   ```python
   from google.colab import userdata
   import os
   os.environ["TYPESAFE_API_KEY"] = userdata.get("TYPESAFE_API_KEY")
   os.environ["ANTHROPIC_API_KEY"] = userdata.get("ANTHROPIC_API_KEY")
   ```
4. מריצים את המחברת מההתחלה.

### חשוב לדעת על מצב demo
במצב demo, **Jev מוחלף בהיוריסטיקה מילולית פשוטה**, וה"חילוץ" משחזר את התשובה הנכונה מקובץ הייחוס. התוצאות ממחישות את הזרימה בלבד. הן לא אומרות דבר על הביצועים של Jev או של Claude. כדי לקבל תוצאות אמיתיות צריך מצב live.

---

## 3. הרצה אוטומטית ב-GitHub Actions

הקובץ `.github/workflows/jev-pipeline.yml` מריץ את הטסטים ואת המחברת.

**אוטומטית:** בכל push שנוגע בתיקייה `jev-docs-pipeline/`, במצב demo.

**הרצה ידנית במצב live:**
1. במאגר ב-GitHub: **Settings** ← **Secrets and variables** ← **Actions** ← **New repository secret**.
2. מוסיפים שני secrets: `TYPESAFE_API_KEY` ו-`ANTHROPIC_API_KEY`.
3. עוברים ללשונית **Actions**, בוחרים **jev-medical-pipeline** ולוחצים **Run workflow**.
4. בוחרים `mode: live` ואת שפת ההנחיות (`he` או `en`), ומריצים.
5. בסיום, בדף ההרצה, מורידים את **pipeline-results**: המחברת אחרי הרצה ותיקיית `outputs/`.

**המלצה:** להריץ live פעמיים, פעם עם `he` ופעם עם `en`, ולהשוות את טבלת ההערכה בסוף המחברת. לא מצאנו תיעוד שמאשר ש-Jev עובד בעברית טוב כמו באנגלית.

---

## 4. בנייה מחדש של הסרטון

ההוראות המלאות נמצאות ב-`jev-video/README.md`. בקצרה:
1. **קריינות:** `tts/gen_voice.py` מייצר קריינות בעברית מתוך `narration.json`.
2. **תזמון ומיקס:** `build_timeline.py` מסנכרן את הסצנות לקריינות ומוסיף מוזיקה.
3. **רינדור:** `render.mjs` מרנדר את האנימציה לקובץ MP4.

כדי לשנות את הטקסט: עורכים את `narration.json`, ומריצים מחדש את שלושת השלבים.

---

## 5. בנייה מחדש של המצגות

```sh
cd jev-video/deck
python3 build_deck.py            # המצגת הבסיסית  -> out/project/
python3 build_deck_extended.py   # המצגת המורחבת -> out_extended/project/
```
המצגת המורחבת קוראת את התוצאות מ-`jev-docs-pipeline/outputs/results_demo.json`. לכן אם מריצים את המחברת מחדש, צריך לבנות גם את המצגת מחדש.

---

## 6. מקורות ומגבלות

- המקורות לכל נתון בסרטון ובמצגות: `jev-video/SOURCES.md`.
- **ביצועי Jev:** הנתונים של TypeSafe (פי 193.6 מהיר, פי 444.6 זול) הם מבחנים פנימיים של החברה. מבחן עצמאי מצא אותו דיוק כמו Claude Sonnet 5, מהירות גבוהה פי 3.5 בערך ועלות נמוכה פי 40 בערך. הסרטון והמצגות מציגים את שני הצדדים.
- **אימות:** שלב האימות במחברת בודק שהערך שחולץ כתוב במסמך. הוא לא בודק נכונות קלינית.
- **פרטיות:** מסמכים רפואיים אמיתיים הם מידע מזהה. לפני ששולחים אותם ל-API חיצוני צריך לוודא שזה תואם את מדיניות הארגון והרגולציה.
