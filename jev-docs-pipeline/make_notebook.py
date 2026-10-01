"""Builds jev_medical_pipeline.ipynb. Run: python make_notebook.py && jupyter nbconvert --execute --inplace jev_medical_pipeline.ipynb"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
RTL = '<div dir="rtl">\n\n{}\n\n</div>'

cells = [
md(RTL.format("""# Jev + Claude: סיווג, חילוץ ואימות של מסמכים רפואיים

התהליך במחברת הזו משלב שני סוגי מודלים, כל אחד במה שהוא טוב בו:

| שלב | מודל | מה הוא עושה | למה הוא |
|---|---|---|---|
| 1. סיווג | **Jev** (System One) | סוג המסמך, תחום רפואי, דחיפות, האם יש פרטים מזהים | החלטה סגורה, מהירה וזולה, עם ביטחון מכויל |
| 2. חילוץ | **Claude** (`claude-opus-5-5`) | שדות מובנים: אבחנה, קוד ICD-10, תרופות, ערכי מעבדה, המשך טיפול | צריך לקרוא ולכתוב ערכים, ו-Jev לא כותב טקסט |
| 3. אימות | **Jev** | לכל שדה שחולץ: האם המסמך באמת תומך בו? ועוד ציון איכות כולל | שאלה סגורה של כן/לא, עם הסתברות |
| ניתוב | קוד | קבלה אוטומטית, בדיקה מהירה או בדיקה אנושית, לפי הספים | |

**שני מצבי הרצה**
- `live`: קריאות אמיתיות ל-Jev ול-Claude. צריך `TYPESAFE_API_KEY` ו-`ANTHROPIC_API_KEY`.
- `demo`: רץ בלי מפתחות ובלי רשת. **ה-Jev בדמו הוא היוריסטיקה מילולית ולא המודל**, וה"חילוץ" משחזר את התשובה הנכונה מקובץ הייחוס. כל המספרים בדמו ממחישים את הזרימה בלבד ואינם תוצאות של מודל.

> ⚠️ כל המסמכים בתיקייה `documents/` סינתטיים ובדויים. זה לא כלי קליני ואין להשתמש בו לקבלת החלטות רפואיות."""
)),
code("""# בהרצה ב-Colab או בסביבה חדשה:
# %pip install -q typesafe-sdk anthropic pydantic pandas
import os, json
import pandas as pd
import pipeline as P

pd.set_option("display.max_colwidth", 80)
MODE = None            # None = live אם שני המפתחות מוגדרים, אחרת demo. אפשר לכפות "live" או "demo"
INJECT_ERRORS = True   # מבחן כאוס: שותל 2 טעויות חילוץ כדי לראות ששלב 3 תופס אותן

mode, jev, extractor = P.make_backends(MODE)
print(f"mode: {mode}\\nstage 1+3: {jev.name}\\nstage 2:   {extractor.name}")"""),
md(RTL.format("""## המסמכים

11 מסמכים סינתטיים מ-10 סוגים, כל אחד עם אבחנה אחרת. שניים מהם קשים במיוחד:
- **`09_ct_head_negative`**: פענוח CT מלא בשלילות ("ללא עדות לשבר", "ללא דימום"). מודל שמחלץ בחיפזון עלול לרשום שבר שלא קיים.
- **`11_mixed_fax`**: פקס סרוק עם שגיאות OCR, שמשלב הפניה ותוצאות מעבדה."""
)),
code("""docs = P.load_documents()
gt = P.load_ground_truth()
pd.DataFrame([{"doc_id": d.doc_id, "סוג (ייחוס)": gt[d.doc_id]["doc_type"],
               "אבחנה (ייחוס)": gt[d.doc_id]["extraction"]["primary_diagnosis"],
               "ICD-10": gt[d.doc_id]["extraction"]["icd10_code"], "מילים": len(d.text.split())} for d in docs])"""),
code("""print(next(d for d in docs if d.doc_id == "09_ct_head_negative").text)"""),
md(RTL.format("""## מעבר מלא על מסמך אחד: `09_ct_head_negative`

### שלב 1: Jev מסווג
ארבע שאלות נשלחות בקריאה אחת, ו-Jev עונה על כולן במקביל:"""
)),
code("""for name, q in P.classification_questions().items():
    crit = q.get("criteria")
    shown = list(crit) if isinstance(crit, dict) else crit
    print(f"{name:13} [{q['type']}] {q['instructions']}\\n{'':16}{shown}\\n")"""),
code("""doc = next(d for d in docs if d.doc_id == "09_ct_head_negative")
q1 = P.classification_questions()
a1, t1, _ = jev.ask(doc.text, q1 if mode == "demo" else P.wire(q1))
for k, a in a1.items():
    if a.type == "choice":
        print(f"{k:13} {a.choice:20} confidence={a.confidence:.2f}")
    elif a.type == "score":
        print(f"{k:13} score={a.score:.2f}/4         confidence={a.confidence:.2f}")
    else:
        print(f"{k:13} p(yes)={a.noul:.2f}")
print(f"latency: {t1*1000:.0f} ms")"""),
md(RTL.format("""### שלב 2: Claude מחלץ שדות לפי סכמה
Claude מקבל את המסמך ואת הסוג שזוהה בשלב 1, ומחזיר אובייקט `MedicalExtraction` (Pydantic) דרך structured outputs. כך הפורמט מובטח. כשמבחן הכאוס פעיל, נשתלת כאן בכוונה טעות: "שבר בגולגולת" במקום "ללא עדות לשבר"."""
)),
code("""ex, t2, usage = extractor.extract(doc, a1["doc_type"].choice)
if INJECT_ERRORS:
    ex, injected = P.inject_error(doc.doc_id, ex)
    print("injected (deliberate) errors in:", injected)
print(json.dumps(ex.model_dump(exclude={"evidence"}), ensure_ascii=False, indent=1))"""),
md(RTL.format("""### שלב 3: Jev מאמת כל שדה
לכל ערך שחולץ נשאלת שאלת כן/לא: "האם המסמך אומר את זה?". ההסתברות שחוזרת היא ה-confidence של השדה. בנוסף נבדק אם קוד ה-ICD מתאים לאבחנה, ומתקבל ציון איכות כולל לחילוץ (Score, ‏0–4)."""
)),
code("""q3 = P.verification_questions(ex)
for k, q in q3.items():
    print(f"{k:24} [{q['type']}] {q['instructions'][:110]}")"""),
code("""state = {"document": doc.text, "extracted": ex.model_dump(exclude={"evidence"})}
a3, t3, _ = jev.ask(state, q3 if mode == "demo" else P.wire(q3))
rows = [{"field": label, "value": value, "confidence": round(a3[k].noul, 3), "status": P.field_status(a3[k].noul)}
        for k, label, value in P.claims_from(ex)]
print(f"icd_consistent p={a3['icd_consistent'].noul:.2f}   extraction_quality={a3['extraction_quality'].score:.1f}/4")
pd.DataFrame(rows)"""),
code("""route, reason = P.route(a1["doc_type"], {r["field"]: r["confidence"] for r in rows})
print(f"route: {route}  ({reason})")"""),
md(RTL.format("""## הרצה על כל המסמכים

ספי הניתוב (ב-`pipeline.py`):
- **סיווג:** ביטחון מתחת ל-0.75 עובר למיון ידני (`human_triage`).
- **שדה:** מעל 0.90 מתקבל אוטומטית; בין 0.60 ל-0.90 עובר לבדיקה מהירה; מתחת ל-0.60 נדחה.
- **מסמך מנהלי:** עובר לארכיון בלי חילוץ."""
)),
code("""results = P.run_all(docs, jev, extractor, inject=INJECT_ERRORS)
pd.DataFrame([{
    "doc_id": r["doc_id"],
    "type": r["classification"]["doc_type"]["choice"],
    "type_conf": round(r["classification"]["doc_type"]["confidence"], 2),
    "specialty": r["classification"]["specialty"]["choice"],
    "urgency": round(r["classification"]["urgency"]["score"], 1),
    "min_field_conf": min((f["confidence"] for f in r.get("fields", [])), default=None),
    "route": r["route"], "reason": r["route_reason"]} for r in results])"""),
md(RTL.format("""## הערכה מול הייחוס
- **שדה שגוי:** שדה שהערך שלו שונה מהערך בקובץ הייחוס. במצב live זה מודד גם טעויות אמיתיות של Claude, לא רק את השתולות.
- **השאלה החשובה:** האם הביטחון של שלב 3 מפריד בין שדות שגויים לשדות נכונים?"""
)),
code("""ev = P.evaluate(results, gt)
wrong = ev.pop("wrong_fields")
display(pd.Series(ev).to_frame("value"))
pd.DataFrame(wrong, columns=["doc_id", "field", "value", "confidence"])"""),
md(RTL.format("""## עלות וזמן
המחירים לפי מחירוני הספקים: Claude Opus 5.5 עולה ‎$4 למיליון טוקנים של קלט ו-‎$20 למיליון של פלט; Jev עולה ‎$0.042 למיליון טוקנים של קלט, והפלט חינם. במצב demo אין קריאות אמיתיות, ולכן אין טוקנים ואין זמנים אמיתיים."""
)),
code("""lat = pd.DataFrame([r["latency_s"] for r in results]).describe().loc[["mean", "50%", "max"]]
display((lat * 1000).round(0).rename(index={"50%": "p50"}).add_suffix(" (ms)"))
P.cost_usd(results)"""),
code("""os.makedirs("outputs", exist_ok=True)
out = f"outputs/results_{mode}.json"
json.dump({"mode": mode, "inject_errors": INJECT_ERRORS, "results": results, "evaluation": {**ev, "wrong_fields": wrong},
           "cost": P.cost_usd(results)}, open(out, "w"), ensure_ascii=False, indent=1, default=str)
print("saved", out)"""),
md(RTL.format("""## הערות ומגבלות
- **עברית:** לא מצאתי תיעוד שמאשר שהביצועים של Jev בעברית זהים לאנגלית. לפני שימוש אמיתי צריך להריץ במצב live ולבדוק את ההערכה למעלה.
- **הספים:** 0.90, 0.60 ו-0.75 הם נקודת התחלה. כדאי לכייל אותם על נתונים אמיתיים, לפי מחיר הטעות בכל שדה. למשל, מינון תרופה מצדיק סף מחמיר יותר מתאריך.
- **שאלות האימות:** שלב 3 בודק *עקביות עם המסמך*, לא נכונות קלינית. אם המסמך עצמו שגוי, האימות לא יתפוס את זה.
- **פרטיות:** מסמכים אמיתיים מכילים מידע רפואי מזהה. צריך לוודא שהשימוש ב-API תואם את מדיניות הפרטיות והרגולציה של הארגון."""
)),
]
nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
                  "language_info": {"name": "python"}}
nbf.write(nb, "jev_medical_pipeline.ipynb")
print("wrote jev_medical_pipeline.ipynb with", len(cells), "cells")
