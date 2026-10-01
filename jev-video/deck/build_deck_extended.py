"""המצגת המורחבת: 25 השקפים של המצגת הבסיסית, ועוד פרק על מסמכים רפואיים
(Jev מסווג, Claude מחלץ, Jev מאמת). המספרים בשקפי המקרים נלקחים מההרצה השמורה של המחברת,
jev-docs-pipeline/outputs/results_demo.json, ומסומנים כפלט של מצב demo.

הרצה:  python3 build_deck_extended.py   ->  out_extended/project/"""
import json
import os

import build_deck as B
from build_deck import (BAD, BG, BG2, CARD, DIM, HEB, INK, LAT, LINE, LLM, MONO, MUTED, OK, PINK, PINKL,
                        card, eyebrow, h3, para, pill, r, row, section, table, title)

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.normpath(os.path.join(HERE, "..", "..", "jev-docs-pipeline"))
RUN = json.load(open(os.path.join(PIPE, "outputs", "results_demo.json")))
RES = {x["doc_id"]: x for x in RUN["results"]}
GT = json.load(open(os.path.join(PIPE, "documents", "ground_truth.json")))
DOC = lambda d: open(os.path.join(PIPE, "documents", d + ".txt"), encoding="utf-8").read()
DEMO_TAG = "מצב demo: Jev הוחלף בהיוריסטיקה מילולית, ולכן אלה לא תוצאות של המודל. להרצה אמיתית: מצב live במחברת."


def codeblock(lines, size=24):
    body = "".join(f'<p style="font-family:{MONO};font-size:{size}px;line-height:1.45;color:{c};text-align:left">{t or "&#160;"}</p>'
                   for t, c in lines)
    return f'<div style="display:flex;flex-direction:column;background:#090B1A;border:2px solid {LINE};border-radius:24px;padding:32px 40px">{body}</div>'


def ind(n, t):
    return " " * n + t


def demo_note():
    return (f'<p style="position:absolute;right:128px;bottom:110px;width:1664px;font-size:24px;color:{DIM};text-align:right">'
            f'{r(DEMO_TAG)}</p>')


new = []
def add(sid, *a, **k):
    section(sid, *a, **k)
    new.append(sid)

# שקף פתיחת פרק ---------------------------------------------------------------------------------------
add("med-divider", f"""
{eyebrow("חלק 3", "#14102A")}
<p style="font-size:110px;font-weight:900;line-height:1.1;color:#14102A;text-align:right">{r("מסמכים רפואיים")}</p>
<p style="font-size:48px;font-weight:200;line-height:1.3;color:#14102A;text-align:right">{r("Jev מסווג. Claude מחלץ. Jev מאמת.")}</p>
<p style="font-size:30px;font-weight:500;color:#14102A;text-align:right">{r("11 מסמכים סינתטיים · מחברת שאפשר להריץ · jev-docs-pipeline/")}</p>
""", "החלק הזה עוסק בדוגמה מורכבת: תהליך שלם על מסמכים רפואיים. Jev מסווג את המסמך, Claude מחלץ ממנו נתונים, ו-Jev בודק כל נתון שחולץ ונותן לו ציון ביטחון. כל מה שמוצג כאן אפשר להריץ מהמחברת jev_medical_pipeline.ipynb.",
    bg=PINK, color="#14102A", footer=False, layout="display:flex;flex-direction:column;gap:24px;padding:128px;justify-content:center")

# למה זה קשה --------------------------------------------------------------------------------------
def hard(t, d, ex):
    return card(f'{h3(t, size=40)}{para(d, 28, MUTED)}<div style="flex:1"></div>'
                f'<p style="font-size:26px;font-weight:400;color:{INK};background:{BG2};border-radius:12px;padding:14px 18px;text-align:right">{r(ex)}</p>')
add("med-hard", f"""
{eyebrow("למה זה קשה")}
{title("מסמך רפואי הוא לא טופס")}
{row(hard("עשרות פורמטים", "סיכום אשפוז, מעבדה, פענוח, פתולוגיה, מרשם, פקס סרוק…", "כל סוג צריך שדות אחרים"),
     hard("שלילות", "חלק גדול מהמידע הוא מה שלא נמצא", "״ללא עדות לשבר״ ≠ שבר"),
     hard("מינונים ויחידות", "מ״ג, מק״ג, מ״ג/ק״ג/יום. טעות של פי 2 נראית סבירה", "675 מ״ג פעמיים ביום, לא 1350"),
     hard("מחיר הטעות", "שדה שגוי במערכת רפואית הוא סיכון בטיחותי", "צריך לדעת מתי לא לסמוך"), gap=28, extra=";flex:1")}
""", "למה מסמכים רפואיים קשים לעיבוד אוטומטי: יש המון סוגים, הרבה מהמידע מנוסח כשלילה, יחידות ומינונים קלים לבלבול, ומחיר הטעות גבוה. לכן לא מספיק לחלץ. צריך גם לדעת עד כמה אפשר לסמוך על כל שדה.")

# ארכיטקטורה ----------------------------------------------------------------------------------
def stage(n, who, c, what, why):
    return card(f'<p style="font-family:{LAT};font-size:26px;font-weight:500;color:{c};text-align:right">{n}</p>'
                f'<p style="font-family:{LAT};font-size:44px;font-weight:800;color:{c};text-align:right">{who}</p>'
                f'{para(what, 28, INK, 400)}<div style="flex:1"></div>{para(why, 24, MUTED, 300)}', border=c)
arrow = f'<x-shape kind="arrow-left" style="background:{LINE};width:48px;height:28px;align-self:center"></x-shape>'
add("med-arch", f"""
{eyebrow("הארכיטקטורה")}
{title("שלושה שלבים, שני מודלים")}
<div style="display:flex;flex-direction:row-reverse;gap:16px;flex:1">
{stage("שלב 1", "Jev", PINK, "סיווג: סוג מסמך, תחום, דחיפות, פרטים מזהים", "קריאה אחת, 4 שאלות במקביל")}
{arrow}
{stage("שלב 2", "Claude", LLM, "חילוץ: אבחנה, ICD-10, תרופות, מעבדה, המשך טיפול", "Structured outputs לפי סכמת Pydantic")}
{arrow}
{stage("שלב 3", "Jev", PINK, "אימות: לכל שדה, האם המסמך תומך בו?", "הסתברות לכל שדה + ציון איכות")}
{arrow}
{stage("ניתוב", "קוד", OK, "קבלה, בדיקה מהירה, אדם, ארכיון", "לפי ספים על הביטחון")}
</div>
""", "המבנה: Jev מסווג בקריאה אחת עם ארבע שאלות. Claude מחלץ שדות מובנים לפי סכמה. Jev שוב, הפעם כבודק: לכל שדה שחולץ הוא שואל אם המסמך תומך בו, ומחזיר הסתברות. בסוף, קוד פשוט מנתב לפי ספים.")

# חלוקת עבודה -----------------------------------------------------------------------------
add("med-why", f"""
{eyebrow("למה לשלב")}
{title("כל מודל במה שהוא טוב בו")}
{table(["משימה", "מי", "למה"], [
    ["לאיזה סוג שייך המסמך?", "Jev", "רשימה סגורה, ביטחון מכויל, שבריר מהעלות"],
    ["מה האבחנה, המינון, הקוד?", "Claude", "צריך לקרוא ולכתוב ערכים. Jev לא כותב טקסט"],
    ["האם הערך שחולץ באמת כתוב במסמך?", "Jev", "שאלת כן/לא, ובודק שני ממודל אחר"],
    ["מה עושים עם המסמך?", "קוד", "ספים שקופים שאפשר לכייל ולבקר"],
], [38, 14, 48], size=30)}
{para("אפשר לבנות את הכל עם Claude לבדו. היתרון כאן הוא ביטחון מספרי לכל שדה, מבודק נפרד, כמעט בלי תוספת עלות.", 30, MUTED, 300)}
""", "חלוקת העבודה: מה שאפשר לנסח כשאלה סגורה הולך ל-Jev, ומה שדורש לכתוב ערכים הולך ל-Claude. כדאי להיות כנים: אפשר לבנות את כל התהליך עם Claude בלבד. מה ש-Jev מוסיף הוא ציון ביטחון מכויל לכל שדה, מבודק נפרד, בעלות שולית.")

# טבלת המסמכים -------------------------------------------------------------------------------
TYPE_HE = {"discharge_summary": "סיכום אשפוז", "lab_report": "תוצאות מעבדה", "er_visit": "סיכום מיון",
           "imaging_report": "פענוח הדמיה", "pathology_report": "דו״ח פתולוגי", "referral_letter": "מכתב הפניה",
           "prescription": "מרשם", "clinic_visit": "ביקור מרפאה", "administrative": "חשבונית"}
rows_ = []
for did, g in GT.items():
    dx = g["extraction"]["primary_diagnosis"] or "לא רפואי"
    dx = dx if len(dx) <= 46 else dx[:44] + "…"
    rows_.append([did[:2], TYPE_HE[g["doc_type"]], dx, g["extraction"]["icd10_code"] or "—"])
add("med-docs", f"""
{eyebrow("הנתונים")}
{title("11 מסמכים, 10 סוגים, 10 אבחנות")}
{table(["#", "סוג", "אבחנה", "ICD-10"], rows_, [6, 20, 58, 16], size=24)}
<p style="position:absolute;right:128px;bottom:110px;width:1664px;font-size:24px;color:{DIM};text-align:right">{r("כל המסמכים סינתטיים: שמות, מספרי זהות ומוסדות בדויים. jev-docs-pipeline/documents/")}</p>
""", "אחד-עשר מסמכים סינתטיים שכתבתי: סיכום אשפוז על דלקת ריאות, תוצאות מעבדה של סוכרת לא מאוזנת, מיון עם אוטם חריף, צילום עם שבר קולס, פתולוגיה של סרטן שד, הפניה לאנדוקרינולוג בגלל השימוטו, מרשם ליתר לחץ דם, ביקור ילדים עם דלקת אוזן, CT ראש מלא בשלילות, חשבונית פיזיותרפיה, ופקס סרוק עם חשד לפרפור פרוזדורים. קודי ה-ICD-10 נבדקו מול האבחנות.")

# מסמך לדוגמה: מלכודת השלילה ------------------------------------------------------------
ct = DOC("09_ct_head_negative").split("ממצאים:")[1].split("המלצה:")[0].strip().splitlines()
ct_html = "".join(f'<p style="font-size:28px;font-weight:{700 if l.startswith(("ללא", "אין")) else 300};line-height:1.5;color:{PINK if l.startswith(("ללא", "אין")) else "#2A2440"};text-align:right">{r(l)}</p>' for l in ct if l.strip())
add("med-sample", f"""
{eyebrow("מסמך לדוגמה · 09")}
{title("פענוח CT ראש:", "רוב הממצאים הם שלילות")}
<div style="display:flex;flex-direction:row-reverse;gap:40px;flex:1">
<div style="flex:1.3;display:flex;flex-direction:column;gap:4px;background:#F4EFE6;border-radius:20px;padding:40px 48px">
<p style="font-size:24px;font-weight:700;color:#7A6F8F;text-align:right">{r("ממצאים:")}</p>{ct_html}</div>
{card(f'{h3("המלכודת")}{para("מודל שמחלץ בחיפזון רואה את המילה ״שבר״ ורושם אבחנה שלא קיימת.", 30, MUTED)}'
      f'{para("במבחן הכאוס שתלנו בדיוק את הטעות הזו בחילוץ, כדי לבדוק אם שלב 3 תופס אותה.", 30, INK, 400)}')}
</div>
""", "זה המסמך הקשה ביותר בסט: פענוח CT ראש של מטופלת בת 81 אחרי נפילה. כמעט כל שורה היא שלילה: ללא שבר, ללא דימום, אין הזזה. זה בדיוק המקום שבו חילוץ אוטומטי נוטה לטעות.")

# קוד שלב 1 ----------------------------------------------------------------------------------
add("med-s1", f"""
{eyebrow("שלב 1 · Jev מסווג")}
{title("ארבע שאלות, קריאה אחת")}
{codeblock([
    ("from typesafe_sdk import TypeSafeClient, Choice, Score, Noul", MUTED),
    ("", INK),
    ("r = TypeSafeClient().system_one(", INK),
    (ind(2, "state=document_text,"), OK),
    (ind(2, "questions={"), INK),
    (ind(4, '"doc_type": Choice(instructions="איזה סוג של מסמך רפואי זה?",'), PINKL),
    (ind(10, 'criteria={"discharge_summary": "סיכום אשפוז...", "lab_report": ..., ...}),'), PINKL),
    (ind(4, '"specialty": Choice(criteria={"cardiology": None, "oncology": None, ...}),'), PINKL),
    (ind(4, '"urgency": Score(criteria=["לא נדרשת פעולה", "שבועות", "ימים", "24-48 שעות", "חירום"]),'), PINKL),
    (ind(4, '"contains_phi": Noul(instructions="האם המסמך מכיל שם או מספר זהות?"),'), PINKL),
    (ind(2, "})"), INK),
    ("", INK),
    ('r.choices["doc_type"].choice, r.choices["doc_type"].confidence   # "imaging_report", 0.97', MUTED),
])}
{para("סיווג בביטחון נמוך מ-0.75 לא ממשיך הלאה. המסמך עובר למיון ידני. ההנחיות למודל בעברית כברירת מחדל; PROMPT_LANG=en מחליף לאנגלית, לצורך השוואה.", 28, MUTED, 300)}
""", "שלב 1: ארבע שאלות בקריאה אחת ל-Jev. Choice לסוג המסמך מתוך 9 סוגים, Choice לתחום הרפואי, Score לדחיפות בסולם 0 עד 4, ו-Noul לשאלה אם יש במסמך פרטים מזהים. זה ה-SDK הרשמי לפייתון, typesafe-sdk.")

# קוד שלב 2 ----------------------------------------------------------------------------------
add("med-s2", f"""
{eyebrow("שלב 2 · Claude מחלץ")}
{title("סכמה קבועה, ציטוט לכל שדה")}
<div style="display:flex;flex-direction:row-reverse;gap:32px">
<div style="flex:1.5">{codeblock([
    ("class MedicalExtraction(BaseModel):", PINKL),
    (ind(2, "primary_diagnosis: str | None"), INK),
    (ind(2, "icd10_code: str | None"), INK),
    (ind(2, "medications: list[Medication]"), INK),
    (ind(2, "lab_values: list[LabValue]"), INK),
    (ind(2, "follow_up: str | None"), INK),
    (ind(2, "evidence: list[Evidence]  # ציטוט מילולי"), MUTED),
    ("", INK),
    ("resp = claude.messages.parse(", INK),
    (ind(2, 'model="claude-opus-5-5",'), OK),
    (ind(2, "system=EXTRACTION_SYSTEM,"), INK),
    (ind(2, 'messages=[{"role": "user", "content": doc}],'), INK),
    (ind(2, "output_format=MedicalExtraction)"), INK),
    ("ex = resp.parsed_output", MUTED),
], size=22)}</div>
{card(f'{h3("ההוראה החשובה")}{para("״לעולם אל תסיק אבחנה שהמסמך שולל. ׳ללא עדות לשבר׳ פירושו שאין שבר.״", 28, INK, 300)}'
      f'{para("Structured outputs מבטיח שהפלט תואם לסכמה. הוא לא מבטיח שהערכים נכונים. בשביל זה יש שלב 3.", 26, MUTED, 300)}')}
</div>
""", "שלב 2: Claude מחלץ לפי סכמת Pydantic. ה-structured outputs מבטיח שהפורמט תקין, אבל לא שהערכים נכונים, ולכן צריך שלב אימות. ביקשנו גם ציטוט מילולי לכל שדה, וההוראה למודל אומרת במפורש לא להסיק אבחנה שהמסמך שולל.")

# פלט שלב 2 --------------------------------------------------------------------------------
e1 = GT["01_discharge_pneumonia"]["extraction"]
add("med-s2out", f"""
{eyebrow("שלב 2 · פלט לדוגמה (מסמך 01, סיכום אשפוז)")}
{title("מה חוזר מהחילוץ")}
{table(["שדה", "ערך"], [
    ["אבחנה עיקרית", e1["primary_diagnosis"]],
    ["ICD-10", e1["icd10_code"]],
    ["אבחנות משניות", ", ".join(e1["secondary_diagnoses"])],
    ["תרופות", " · ".join(f'{m["name"]} {m["dose"]} {m["frequency"]}' for m in e1["medications"])],
    ["מעבדה", " · ".join(f'{l["test"]} {l["value"]} {l["unit"]}' for l in e1["lab_values"])],
    ["המשך טיפול", e1["follow_up"]],
], [22, 78], size=28)}
<p style="position:absolute;right:128px;bottom:110px;width:1664px;font-size:24px;color:{DIM};text-align:right">{r("הערכים בשקף הם החילוץ הנכון מקובץ הייחוס (ground_truth.json), לא פלט שנמדד מ-Claude.")}</p>
""", "כך נראה חילוץ נכון של סיכום האשפוז: אבחנה, קוד, אבחנות משניות, תרופות בשחרור, ערכי מעבדה חריגים והמשך טיפול. אלה ערכי הייחוס שמולם ההערכה בודקת את Claude במצב live.")

# קוד שלב 3 ----------------------------------------------------------------------------------
add("med-s3", f"""
{eyebrow("שלב 3 · Jev מאמת")}
{title("שאלת כן/לא לכל שדה")}
{codeblock([
    ("questions = {", INK),
    (ind(2, 'f"claim_{field}": Noul(instructions=f"לפי החילוץ, {field} = «{value}». "'), PINKL),
    (ind(26, '"האם הערך הזה כתוב במסמך, או נובע ממנו ישירות?")'), PINKL),
    (ind(2, "for field, value in claims_from(ex)"), INK),
    ("}", INK),
    ('questions["icd_consistent"] = Noul(instructions=f"האם {ex.icd10_code} קוד נכון לאבחנה העיקרית?")', PINKL),
    ('questions["extraction_quality"] = Score(criteria=QUALITY_LEVELS)        # 0-4', PINKL),
    ("", INK),
    ('r = jev.system_one(state={"document": text, "extracted": ex.model_dump()}, questions=questions)', INK),
    ("confidence = {k: a.noul for k, a in r.nouls.items()}", OK),
])}
{row(pill("≥ 0.90 · קבלה", "#06140D", OK, OK, 28, 800), pill("0.60–0.90 · בדיקה מהירה", INK, BG2, PINKL, 28), pill("< 0.60 · נדחה", "#FFFFFF", "#7A2030", BAD, 28, 800), gap=20, extra=";justify-content:start")}
""", "שלב 3: לכל שדה שחולץ, Jev מקבל את המסמך ואת החילוץ, ועונה בהסתברות על השאלה אם המסמך באמת אומר את זה. ההסתברות היא ה-confidence של השדה. מעל 0.9 מתקבל, בין 0.6 ל-0.9 עובר לבדיקה מהירה, ומתחת ל-0.6 נדחה.")

# מקרה: מלכודת השלילה ---------------------------------------------------------------------------
def field_rows(doc_id):
    out = []
    for f in RES[doc_id]["fields"]:
        st = {"accept": "קבלה", "review": "בדיקה", "reject": "נדחה"}[f["status"]]
        out.append([f["field"], f["value"], f'{f["confidence"]:.2f}', st])
    return out
r9 = RES["09_ct_head_negative"]
add("med-case-ct", f"""
{eyebrow("מקרה 1 · מבחן כאוס על מסמך 09")}
{title("״שבר בגולגולת״ שלא קיים", "נתפס")}
{table(["שדה", "ערך שחולץ", "ביטחון", "החלטה"], field_rows("09_ct_head_negative"), [24, 46, 12, 18], size=28)}
<div style="display:flex;flex-direction:row-reverse;align-items:center;gap:24px">
{pill("ניתוב: בדיקה אנושית", "#FFFFFF", "#7A2030", BAD, 32, 800)}
{para("שני השדות השתולים קיבלו ביטחון נמוך, והשדות הנכונים התקבלו. המסמך לא נכנס למערכת בלי עין אנושית.", 28, INK, 300)}
</div>
{demo_note()}
""", "מבחן כאוס: שתלנו בחילוץ של ה-CT את האבחנה 'שבר בעצמות הגולגולת' עם קוד S02.0. שלב 3 נתן לשני השדות האלה ביטחון נמוך מאוד, קיבל את הגיל ואת המשך הטיפול, והמסמך נותב לבדיקה אנושית. חשוב: בדמו את Jev מחליפה היוריסטיקה, ולכן המספרים ממחישים את הזרימה. את ההתנהגות של Jev עצמו בודקים במצב live.")

# מקרה: מינון ------------------------------------------------------------------------------------
add("med-case-dose", f"""
{eyebrow("מקרה 2 · מבחן כאוס על מסמך 08")}
{title("מינון כפול לילד בן 3")}
<div style="display:flex;flex-direction:row-reverse;gap:40px">
{card(f'{eyebrow("מה כתוב במסמך", MUTED)}{para("Amoxicillin 90 מ״ג/ק״ג/יום, כלומר <b>675 מ״ג פעמיים ביום</b>", 32, INK, 300)}'
      f'{para("15 ק״ג × 90 = 1,350 מ״ג ליום = 675 מ״ג × 2", 28, MUTED, 300)}')}
{card(f'{eyebrow("מה ״חולץ״", MUTED)}{para("Amoxicillin <b>1350 מ״ג</b> פעמיים ביום", 32, BAD, 300)}'
      f'{para("המינון היומי נרשם כמינון לפעם אחת: כפול מהנכון", 28, MUTED, 300)}', border=BAD)}
</div>
{table(["שדה", "ערך שחולץ", "ביטחון", "החלטה"], [x for x in field_rows("08_pediatric_otitis") if x[0].startswith("medications")], [24, 46, 12, 18], size=28)}
{demo_note()}
""", "מקרה שני: טעות מינון קלאסית. במסמך כתוב 90 מ״ג לק״ג ליום, כלומר 675 מ״ג פעמיים ביום לילד של 15 ק״ג. בחילוץ השתול נרשם 1350 מ״ג לפעם, פי שניים. שלב 3 דחה את השדה הזה וקיבל את הפרצטמול הנכון.")

# תוצאות הניתוב -------------------------------------------------------------------------------
from collections import Counter
cnt = Counter(x["route"] for x in RUN["results"])
RHE = {"auto_accept": ("קבלה אוטומטית", OK), "quick_review": ("בדיקה מהירה", PINKL), "human_review": ("בדיקה אנושית", BAD),
       "human_triage": ("מיון ידני", BAD), "archive": ("ארכיון", MUTED)}
tiles = "".join(card(f'<p style="font-family:{LAT};font-size:120px;font-weight:800;line-height:1;color:{c};text-align:right">{cnt.get(k, 0)}</p>{h3(lbl, size=36)}', border=c)
                for k, (lbl, c) in RHE.items() if k in ("auto_accept", "quick_review", "human_review", "archive"))
ev = RUN["evaluation"]
add("med-routing", f"""
{eyebrow("הרצה על כל 11 המסמכים")}
{title("לאן הלך כל מסמך")}
{row(tiles, gap=24)}
{table(["מדד", "בדמו", "מה זה בודק במצב live"], [
    ["שדות שגויים שסומנו", f'{ev["wrong_fields_flagged"]} מתוך {ev["wrong_fields_flagged"] + ev["wrong_fields_missed"]}', "האם Jev תופס טעויות, כולל טעויות אמיתיות של Claude"],
    ["שדות נכונים שסומנו בטעות", str(ev["correct_fields_flagged"]), "כמה עבודה מיותרת נוצרת לבודקים"],
    ["דיוק סיווג סוג המסמך", f'{ev["doc_type_accuracy"]:.0%}', "בדמו זו היוריסטיקה, ו-100% לא אומר כלום על Jev"],
], [30, 14, 56], size=26)}
{demo_note()}
""", "על כל אחד-עשר המסמכים: שמונה התקבלו אוטומטית, שניים עם הטעויות השתולות הלכו לבדיקה אנושית, והחשבונית לארכיון. הטבלה מסבירה מה כל מדד בודק כשמריצים במצב live. בדמו המספרים מושלמים כי ההיוריסטיקה פשוטה והמסמכים נכתבו יחד איתה. אל תסיקו מהם דבר על Jev.")

# עלות ------------------------------------------------------------------------------------------
add("med-cost", f"""
{eyebrow("עלות לכל מסמך · הערכה לפי מחירון")}
{title("האימות כמעט חינם")}
{table(["שלב", "טוקנים (הערכה)", "מחיר", "עלות למסמך"], [
    ["Jev סיווג", "~1,500 קלט", "$0.042 / 1M", "≈ $0.00006"],
    ["Claude חילוץ", "~2,000 קלט + ~600 פלט", "$4 / $20 ל-1M", "≈ $0.02"],
    ["Jev אימות", "~3,500 קלט", "$0.042 / 1M", "≈ $0.00015"],
], [22, 30, 22, 26], size=30)}
{para("שני שלבי Jev יחד מוסיפים כ-1% לעלות של החילוץ. אלפי מסמכים ביום מקבלים ציון ביטחון לכל שדה כמעט בלי תוספת.", 32, INK, 400)}
<p style="position:absolute;right:128px;bottom:110px;width:1664px;font-size:24px;color:{DIM};text-align:right">{r("מספרי הטוקנים הם הערכה למסמך של עמוד אחד. המחברת מחשבת את העלות בפועל מה-usage במצב live.")}</p>
""", "חישוב גס לפי המחירונים: חילוץ עם Claude Opus 5.5 עולה בערך שני סנט למסמך של עמוד, ושני הסבבים של Jev יחד עולים בערך שתי מאיות הסנט, כלומר כאחוז מהחילוץ. אלה הערכות; המחברת מחשבת את העלות האמיתית מה-usage כשמריצים live.")

# איך מריצים ------------------------------------------------------------------------------------
add("med-run", f"""
{eyebrow("להריץ בעצמכם")}
{title("הכל במחברת אחת")}
{codeblock([
    ("cd jev-docs-pipeline", INK),
    ("pip install -r requirements.txt", INK),
    ("export TYPESAFE_API_KEY=...  ANTHROPIC_API_KEY=...   # בלי מפתחות: מצב demo", MUTED),
    ("export PROMPT_LANG=he        # או en, להשוואה", MUTED),
    ("jupyter notebook jev_medical_pipeline.ipynb", OK),
], size=26)}
{table(["קובץ", "מה יש בו"], [
    ["jev_medical_pipeline.ipynb", "מעבר על מסמך אחד, הרצה על כולם, הערכה ועלות"],
    ["pipeline.py", "השאלות ל-Jev, סכמת החילוץ, הספים והניתוב"],
    ["documents/", "11 מסמכים + ground_truth.json"],
    ["tests/", "בודקים את קוד ה-live מול שני ה-SDK עם HTTP מדומה"],
    [".github/workflows/jev-pipeline.yml", "טסטים + הרצת המחברת בכל push; live בהפעלה ידנית"],
], [40, 60], size=26)}
""", "כדי להריץ: מתקינים את התלויות, מגדירים שני מפתחות API ופותחים את המחברת. בלי מפתחות היא רצה במצב demo. ב-GitHub Actions יש workflow שמריץ את הטסטים ואת המחברת בכל push, ובהפעלה ידנית אפשר לבחור live עם המפתחות ששמורים כ-secrets.")

# הסתייגויות ---------------------------------------------------------------------------------------
lim = lambda t: (f'<div style="display:flex;flex-direction:row-reverse;align-items:start;gap:24px">'
                 f'<x-icon name="Warning" style="color:{PINKL};width:44px;height:44px"></x-icon>{para(t, 32, INK, 300)}</div>')
add("med-caveats", f"""
{eyebrow("לפני שמשתמשים באמת")}
{title("מה הדוגמה הזו לא מוכיחה")}
<div style="display:flex;flex-direction:column;gap:22px">
{lim("<b>עברית:</b> לא מצאתי תיעוד שמאשר ש-Jev עובד בעברית כמו באנגלית. צריך להריץ live ולבדוק.")}
{lim("<b>עקביות ≠ נכונות קלינית:</b> שלב 3 בודק שהערך כתוב במסמך. אם המסמך שגוי, האימות לא יתפוס.")}
{lim("<b>ספים:</b> 0.90 / 0.60 / 0.75 הם נקודת התחלה. מינון תרופה מצדיק סף מחמיר מתאריך.")}
{lim("<b>פרטיות ורגולציה:</b> מסמכים אמיתיים הם מידע רפואי מזהה. נדרש אישור לשימוש ב-API חיצוני.")}
{lim("<b>אדם בלולאה:</b> המטרה היא לצמצם בדיקה ידנית, לא לבטל אותה.")}
</div>
""", "מה הדוגמה לא מוכיחה: לא נבדק שהביצועים של Jev בעברית טובים כמו באנגלית. האימות בודק עקביות עם המסמך ולא נכונות קלינית. הספים צריכים כיול. ובמסמכים אמיתיים יש שאלות של פרטיות ורגולציה. זה כלי שמצמצם עבודה ידנית, לא מחליף אותה.")

# הרכבת המצגת ----------------------------------------------------------------------------------------
base = [s for s in B.order if s not in new]
i = base.index("ex-ops") + 1
order = base[:i] + new + base[i:]
B.slides["sources"] = B.slides["sources"].replace(
    "</ul>", f"<li>{r('המחברת והמסמכים: jev-docs-pipeline/ (typesafe-sdk 0.7.2, anthropic 1.11)')}</li>"
             f"<li>{r('ICD-10-CM: מערכת הקודים לסיווג אבחנות')}</li></ul>")
sections = dict(B.SECTIONS)
sections["s3b"] = {"description": "מסמכים רפואיים: Jev מסווג, Claude מחלץ, Jev מאמת", "start": "med-divider"}
out = os.path.join(HERE, "out_extended", "project")
B.write(out, "Jev — גרסה מורחבת: מסמכים רפואיים", sections, order)
