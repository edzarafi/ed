"""בונה את מצגת Jev (בפורמט של ארטיפקט Slides) לתוך deck/out/project/.
לפורמט השקפים אין תמיכה ב-`direction`, ולכן כל קטע טקסט עברי עטוף בתווי
RLI…PDI (U+2067/U+2069), כדי שיוצג מימין לשמאל בתוך הבלוק.

הרצה:  python3 build_deck.py"""
import json, os, re, datetime

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "project")

BG, BG2, INK, MUTED = "#0E1024", "#161937", "#F6F1EA", "#B4B7CF"
PINK, PINKL, LLM, OK, BAD = "#FF4F93", "#FF9BC2", "#8C96FF", "#46D99B", "#FF7A88"
CARD, LINE, DIM = "#1C2046", "#2E3366", "#7E83A6"
HEB = "'Heebo', Arial, sans-serif"
LAT = "'Rubik', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Courier New', monospace"

RLI, PDI = "⁧", "⁩"
def r(t):  # קטע טקסט מימין לשמאל
    return RLI + t + PDI

MARK = ('M49.1185 0.607398C50.5283 -0.206636 52.2665 -0.200104 53.6767 0.61289L53.6822 0.607398L77.1102 14.1282C78.5202 14.9451 79.3892 16.4529 79.3892 18.0823V42.334L100.225 54.3775C101.643 55.1937 102.515 56.7018 102.515 58.3316V112.404C102.514 114.033 101.648 115.542 100.231 116.358L100.225 116.352C100.181 116.378 100.145 116.404 100.115 116.418L100.088 116.429L53.3856 143.388C52.1483 144.099 50.6534 144.193 49.3547 143.657L48.811 143.388L25.4709 129.857L25.4325 129.835C24.0192 129.017 23.1542 127.502 23.1534 125.875V101.651L2.46032 89.6842H2.44934L2.2736 89.5798C1.76769 89.2811 1.30357 88.8832 0.933603 88.3936L0.928112 88.3881C0.665239 88.0347 0.442905 87.6302 0.285573 87.1854L0.291065 87.1799C0.113508 86.6947 0.000423558 86.1747 0 85.6312V31.5646C0.000397288 29.9324 0.880599 28.4203 2.29007 27.605L49.1185 0.607398ZM36.8389 125.886L51.1011 134.151L88.8077 112.393L74.5345 104.144L36.8389 125.886ZM55.9723 61.2697V85.6697C55.9714 87.4832 54.8856 89.1011 53.2483 89.8269L32.2862 101.975V117.967L69.9708 96.2359V53.1638L55.9723 61.2697ZM79.1147 96.2468L93.3823 104.485V60.9676L79.1147 52.7244V96.2468ZM13.7075 85.6367L27.5907 93.6657L41.8419 85.417L27.9916 77.421L13.7075 85.6367ZM9.14382 34.1952V77.734L23.4389 69.5073V45.0854C23.4389 43.4502 24.3038 41.9429 25.7235 41.1258L46.8339 28.956V12.4642L9.14382 34.1952ZM32.5718 69.5183L46.5539 77.5693V61.1104L32.5718 53.032V69.5183ZM37.1355 45.0909L51.0077 53.1199L65.2863 44.8767L51.4031 36.8697L37.1355 45.0909ZM55.9723 28.9615L70.2619 37.1827V20.7183L55.9723 12.4697V28.9615Z')
def logo(w, color=INK, **pos):
    h = round(w * 146 / 103)
    st = f"width:{w}px;height:{h}px" + "".join(f";{k}:{v}" for k, v in pos.items())
    return (f'<svg aria-label="TypeSafe logo" viewBox="0 -1 103 146" width="103" height="146" style="{st}">'
            f'<path fill-rule="evenodd" clip-rule="evenodd" fill="{color}" d="{MARK}"/></svg>')

slides, order, notes_all = {}, [], {}
N = [0]

def section(sid, body, notes, bg=BG, color=INK, footer=True, layout=None, transition="fade"):
    N[0] += 1
    lay = layout or "display:flex;flex-direction:column;gap:48px;padding:128px 128px 160px"
    foot = ""
    if footer:
        foot = (f'<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:{DIM};'
                f'font-family:{LAT};text-align:left">Jev · TypeSafe AI   |   §PAGE§</p>')
    html = (f'<section id="{sid}" data-transition="{transition}" style="background:{bg};color:{color};'
            f'font-family:{HEB};{lay}">\n{body}\n{foot}\n<aside>{notes}</aside>\n</section>\n')
    slides[sid] = html
    order.append(sid)

def eyebrow(t, c=PINKL):
    return f'<p style="font-size:24px;font-weight:500;letter-spacing:4px;color:{c};text-align:right">{r(t)}</p>'
def title(bold, thin="", size=72):
    thin_part = f'<span style="color:{MUTED}">{thin}</span>' if thin else ""
    return (f'<h2 style="font-size:{size}px;font-weight:900;line-height:1.1;text-align:right">'
            f'{r(bold + (" " if thin else ""))}{r(thin_part) if thin else ""}</h2>')
def para(t, size=32, c=INK, w=200, align="right", extra=""):
    return f'<p style="font-size:{size}px;font-weight:{w};line-height:1.45;color:{c};text-align:{align}{extra}">{r(t)}</p>'
def card(inner, bg=CARD, border=LINE, extra=""):
    return (f'<div style="flex:1;display:flex;flex-direction:column;gap:16px;background:{bg};padding:44px;'
            f'border:2px solid {border};border-radius:24px{extra}">{inner}</div>')
def h3(t, c=INK, size=44):
    return f'<h3 style="font-size:{size}px;font-weight:900;line-height:1.2;color:{c};text-align:right">{r(t)}</h3>'
def row(*items, gap=32, extra=""):
    return f'<div style="display:flex;flex-direction:row-reverse;gap:{gap}px{extra}">{"".join(items)}</div>'
def pill(t, c=INK, bg=CARD, border=LINE, size=32, w=500):
    return (f'<p style="font-size:{size}px;font-weight:{w};color:{c};background:{bg};border:2px solid {border};'
            f'border-radius:999px;padding:14px 32px;text-align:center;white-space:nowrap">{r(t)}</p>')
def big(t, c=PINK, size=120, align="right"):
    return f'<p style="font-family:{LAT};font-size:{size}px;font-weight:800;line-height:1;color:{c};text-align:{align}">{t}</p>'
def table(head, rows, widths, size=28, first_color=MUTED):
    def cell(tag, t, w, i, extra=""):
        return f'<{tag} style="width:{w}%;text-align:right{extra}">{r(t)}</{tag}>'
    hr = "<tr>" + "".join(cell("th", h, widths[i], i, f";color:{PINKL};font-weight:700") for i, h in enumerate(head)) + "</tr>"
    body = ""
    for k, rw in enumerate(rows):
        bgc = f' style="background:{BG2}"' if k % 2 == 0 else ""
        body += f"<tr{bgc}>" + "".join(cell("td", c, widths[i], i, f";color:{first_color}" if i == 0 else "") for i, c in enumerate(rw)) + "</tr>"
    return (f'<table style="font-size:{size}px;font-family:{HEB};color:{INK};padding:20px 24px;'
            f'border:1px solid {LINE}">{hr}{body}</table>')

# 1 שער --------------------------------------------------------------------
section("cover", f"""
{logo(150, INK, position="absolute", right="128px", top="128px")}
<p style="position:absolute;right:128px;top:420px;width:1200px;font-family:{LAT};font-size:240px;font-weight:800;line-height:1;color:{INK};text-align:right">Jev<span style="color:{PINK}">.</span></p>
<p style="position:absolute;right:128px;top:700px;width:1400px;font-size:56px;font-weight:200;line-height:1.3;color:{INK};text-align:right">{r("מודל ה-<b>System One</b> הראשון, בשפה פשוטה")}</p>
<p style="position:absolute;right:128px;top:800px;width:1400px;font-size:32px;font-weight:400;color:{PINKL};text-align:right">{r("TypeSafe AI · הושק ב-15 בספטמבר 2026")}</p>
""", "מצגת שמסבירה מה זה Jev, המודל של TypeSafe AI, למה הוא שונה ממודלי שפה רגילים, ואיפה הוא שימושי. כל הנתונים מגובים במקורות בשקף האחרון.",
        footer=False, layout="display:flex;flex-direction:column;padding:128px",
        bg="radial-gradient(circle at 15% 10%, #3A1638 0%, #0E1024 55%)")

# 2 פתיחה ---------------------------------------------------------------------
section("hook", f"""
{eyebrow("איך עובדים היום עם AI")}
{title("שואלים שאלה.", "מקבלים פסקה.")}
<div style="display:flex;flex-direction:column;gap:24px">
<p style="align-self:end;font-size:32px;font-weight:500;color:#FFFFFF;background:{PINK};border-radius:28px;padding:24px 36px;text-align:right">{r("לאיזו מחלקה להעביר את הפנייה של הלקוח?")}</p>
<p style="align-self:start;width:1150px;font-size:30px;font-weight:300;line-height:1.5;color:#DCD8E8;background:{CARD};border:2px solid {LINE};border-radius:28px;padding:28px 36px;text-align:right">{r("הפנייה של הלקוח עוסקת ככל הנראה בנושא של חיוב כפול, ולכן כדאי לשקול להעביר אותה למחלקת הכספים. עם זאת, ייתכן שמדובר גם בתקלה טכנית במערכת התשלומים, ובמקרה כזה מומלץ לערב גם את הצוות הטכני, ואולי אף את שירות הלקוחות, כדי לוודא ש…")}</p>
</div>
""", "כולנו מכירים צ'אטבוטים כמו ChatGPT: שואלים שאלה ומקבלים פסקה שלמה של טקסט. לבן אדם זה מצוין. לתוכנה זו בעיה: צריך לפרסר את הטקסט, והתשובה לא תמיד מגיעה בפורמט צפוי.")

# 3 הבעיה ------------------------------------------------------------------
section("problem", f"""
{eyebrow("הבעיה")}
{title("תוכנה צריכה החלטה.", "לא חיבור.")}
{para("כשקוד צריך להחליט מה לעשות עכשיו, הוא צריך תשובה אחת, ברורה, בפורמט קבוע:", 36, MUTED)}
{row(pill("לאיזו מחלקה?", size=40), pill("כמה זה דחוף?", size=40), pill("ספאם או לא?", size=40), pill("מסוכן או בטוח?", size=40), extra=";justify-content:start;flex-wrap:wrap")}
<div style="flex:1"></div>
{para("היום עושים את זה עם מודל שפה גדול: מבקשים JSON, מפרסרים, מקווים שהפורמט תקין, ומשלמים על כל מילה שהמודל כותב.", 32, INK, 300)}
""", "תוכנה לא צריכה חיבור. היא צריכה החלטה: לאיזו מחלקה להעביר, כמה זה דחוף, זה ספאם או לא. היום עושים את זה עם מודלי שפה, ומשלמים בזמן, בכסף ובתשובות שלא תמיד בפורמט הנכון.")

# 4 שקף הצהרה ----------------------------------------------------------------
section("statement", f"""
{logo(110, "#14102A")}
<p style="font-family:{LAT};font-size:200px;font-weight:800;line-height:1;color:#14102A;text-align:right">Jev</p>
<p style="font-size:72px;font-weight:200;line-height:1.2;color:#14102A;text-align:right">{r("AI שלא כותב טקסט.")}</p>
<p style="font-size:72px;font-weight:900;line-height:1.2;color:#14102A;text-align:right">{r("הוא מחליט.")}</p>
""", "בשביל זה נבנה Jev. הוא לא מודל שפה ולא כותב מילה. נותנים לו מידע ושאלות סגורות, והוא מחזיר החלטות מוכנות עם רמת ביטחון.",
        bg=PINK, color="#14102A", footer=False,
        layout="display:flex;flex-direction:column;gap:24px;padding:128px;justify-content:center")

# 5 החברה ------------------------------------------------------------------
section("company", f"""
{eyebrow("מי עומד מאחוריו")}
{title("TypeSafe AI", "מעבדת AI מסן פרנסיסקו")}
{row(
    card(f'{eyebrow("מייסד ומנכ״ל")}{h3("דיוגו אלמיידה", size=56)}'
         f'{para("חוקר לשעבר ב-OpenAI", 32, MUTED)}{para("ממחברי InstructGPT, המחקר על RLHF שהוביל ל-ChatGPT", 32, MUTED)}'
         f'{para("מייסדים שותפים: Erik Gafni, ‏Sasha Sheng", 28, DIM, 300)}'),
    card(f'{eyebrow("סבב Seed")}{big("$40M")}{para("בהובלת קרן DCVC", 32, MUTED)}'
         f'{para("יצאה מ-stealth אחרי שנתיים, יחד עם השקת Jev", 28, DIM, 300)}'),
    gap=40)}
""", "TypeSafe AI הוקמה על ידי דיוגו אלמיידה, חוקר לשעבר ב-OpenAI ואחד ממחברי מאמר InstructGPT, המחקר על למידה מפידבק אנושי שהוביל ל-ChatGPT. החברה גייסה 40 מיליון דולר בסבב Seed בהובלת DCVC ויצאה מ-stealth ב-15 בספטמבר 2026. השם Jev הוא רפרנס לפרדוקס ג'בונס: כשמשהו נעשה זול ויעיל יותר, משתמשים בו הרבה יותר.")

# 6 System One ---------------------------------------------------------------
section("systemone", f"""
{eyebrow("מאיפה השם")}
{title("למה System One?", "דניאל כהנמן, Thinking, Fast and Slow")}
{row(
    card(f'<p style="font-size:120px;font-weight:900;line-height:1;color:{PINK};text-align:right">1</p>'
         f'{h3("מהירה. אינטואיטיבית.")}{para("לזהות פרצוף מוכר, להבין שמישהו כועס, לעצור ברמזור", 30, MUTED)}'
         f'<p style="font-size:30px;font-weight:700;color:{PINK};text-align:right">{r("← כאן Jev")}</p>', border=PINK),
    card(f'<p style="font-size:120px;font-weight:200;line-height:1;color:{LLM};text-align:right">2</p>'
         f'{h3("איטית. מעמיקה.")}{para("לפתור תרגיל ארוך, לכתוב מכתב, לתכנן טיול", 30, MUTED)}'
         f'<p style="font-size:30px;font-weight:700;color:{LLM};text-align:right">{r("← כאן מודלי שפה")}</p>', border=LLM),
    gap=40)}
""", "הפסיכולוג וזוכה פרס נובל דניאל כהנמן תיאר שתי מערכות חשיבה. מערכת 1 מהירה ואינטואיטיבית, כמו לזהות פרצוף. מערכת 2 איטית ומעמיקה, כמו לפתור תרגיל חשבון. מודלי שפה עובדים כמו מערכת 2: חושבים וכותבים. Jev נבנה להיות מערכת 1: החלטה מהירה בלי מילים.")

# 7 איך זה עובד -------------------------------------------------------------
def q(t, typ):
    return (f'<div style="display:flex;flex-direction:row-reverse;justify-content:space-between;align-items:center;gap:16px;'
            f'border-top:1px solid {LINE};padding:12px 0">{para(t, 28, INK, 400)}'
            f'<p style="font-family:{LAT};font-size:24px;color:{PINKL};border:2px solid #7A3A5C;border-radius:8px;padding:2px 12px">{typ}</p></div>')
def a(t, conf):
    return (f'<div style="display:flex;flex-direction:row-reverse;justify-content:space-between;align-items:center;gap:16px;'
            f'border-top:1px solid {LINE};padding:12px 0">{para(t, 28, INK, 500)}'
            f'<p style="font-family:{LAT};font-size:24px;color:{OK}">{conf}</p></div>')
section("how", f"""
{eyebrow("ככה זה עובד · דוגמה להמחשה")}
{title("מידע + שאלות סגורות", "→ תשובות מוכנות")}
<div style="display:flex;flex-direction:row-reverse;gap:24px;align-items:center">
{card(f'{eyebrow("1 · מידע (STATE)", MUTED)}{para("״חויבתי פעמיים החודש! תטפלו בזה מיד.״", 34, INK, 300)}')}
<x-shape kind="arrow-left" style="background:{LINE};width:56px;height:32px"></x-shape>
{card(f'{eyebrow("2 · שאלות (QUESTIONS)", MUTED)}{q("באיזה נושא?", "Choice")}{q("כמה דחוף? 0–100", "Score")}{q("האם זה ספאם?", "Noul")}', extra=";flex:1.3")}
<x-shape kind="arrow-left" style="background:{LINE};width:56px;height:32px"></x-shape>
<p style="font-family:{LAT};font-size:52px;font-weight:800;color:#FFFFFF;background:{PINK};border-radius:32px;padding:56px 36px">Jev</p>
<x-shape kind="arrow-left" style="background:{LINE};width:56px;height:32px"></x-shape>
{card(f'{eyebrow("3 · תשובות (ANSWERS)", MUTED)}{a("נושא: חיוב", "0.97")}{a("דחיפות: 88", "/100")}{a("ספאם: לא", "0.02")}')}
</div>
{para("כל התשובות מגיעות יחד, בקריאה אחת, כנתונים מוכנים לקוד. בלי טקסט לפרסר.", 30, MUTED, 300)}
""", "נותנים ל-Jev מידע, למשל הודעה של לקוח, ולצדה רשימה של שאלות סגורות. הוא מחזיר תשובה מוכנה לכל שאלה, יחד עם רמת ביטחון. המספרים בשקף להמחשה בלבד, הם לא פלט אמיתי.")

# 8 שלושה סוגי תשובות --------------------------------------------------------------
def tcard(en, he, desc, ex):
    return card(f'<p style="font-family:{LAT};font-size:32px;font-weight:300;color:{PINKL};text-align:right">{en}</p>'
                f'{h3(he, size=56)}{para(desc, 30, MUTED)}<div style="flex:1"></div>'
                f'<p style="font-size:26px;font-weight:400;color:{INK};background:{BG2};border-radius:12px;padding:16px 20px;text-align:right">{r(ex)}</p>')
section("types", f"""
{eyebrow("סוגי התשובות")}
{title("שלושה סוגים בלבד.", "זהו.")}
{row(tcard("Choice", "בחירה", "אפשרות אחת מתוך רשימה שאתם מגדירים, עד 255 אפשרויות", "חיוב / טכני / מכירות / ספאם"),
     tcard("Score", "ציון", "מספר לפי סקאלה או רובריקה שאתם מגדירים", "דחיפות: 88 מתוך 100"),
     tcard("Noul", "כן / לא", "הסתברות מכוילת בין 0 ל-1", "האם זה ספאם? 0.02"), gap=32, extra=";flex:1")}
""", "יש ל-Jev רק שלושה סוגי תשובות. Choice: בחירה של אפשרות אחת מרשימה, עד 255 אפשרויות. Score: ציון מספרי לפי סקאלה. Noul: הסתברות לכן או לא. כל החלטה בתוך תוכנה אפשר לבנות משילוב של השלושה.")

# 9 קוד ---------------------------------------------------------------------
code = [
    ('import { choice, TypeSafeClient } from "@typesafe-ai/sdk";', MUTED),
    ("", INK),
    ("const client = new TypeSafeClient();", INK),
    ("const response = await client.systemOne({", INK),
    ('  state: { document: "I was charged twice. Please fix this ASAP." },', OK),
    ("  questions: {", INK),
    ('    category: choice("What is this ticket about?", {', PINKL),
    ("      billing: null, technical: null, other: null,", PINKL),
    ("    }),", PINKL),
    ("  },", INK),
    ("});", INK),
    ("", INK),
    ("console.log(response.answers.category.choice);  // \"billing\"", MUTED),
]
code_html = "".join(f'<p style="font-family:{MONO};font-size:26px;line-height:1.5;color:{c};text-align:left">{t or "&#160;"}</p>' for t, c in code)
section("code", f"""
{eyebrow("כך זה נראה בקוד")}
{title("קריאה אחת. תשובה מוקלדת.", "מתוך ה-README של ה-SDK הרשמי")}
<div style="display:flex;flex-direction:column;background:#090B1A;border:2px solid {LINE};border-radius:24px;padding:40px 48px">{code_html}</div>
{para("הטיפוס של התשובה נגזר מהשאלה עצמה. אם הגדרתם billing / technical / other, אי אפשר לקבל שום דבר אחר.", 30, MUTED, 300)}
""", "זו הדוגמה מתוך ה-README של ה-SDK הרשמי ל-JavaScript (החבילה @typesafe-ai/sdk). מגדירים state ושאלות, ומקבלים תשובה עם טיפוס שנגזר מהשאלה. יש גם SDK רשמי לפייתון.")

# 10 במקביל ----------------------------------------------------------------
tok = lambda t: f'<p style="font-size:30px;color:{INK};background:#232A5C;border:2px solid #4A52A8;border-radius:12px;padding:10px 18px;white-space:nowrap">{r(t)}</p>'
ans = lambda t: f'<p style="font-size:32px;font-weight:700;color:{INK};background:#3A1638;border:2px solid {PINK};border-radius:14px;padding:14px 26px;white-space:nowrap">{r(t)}</p>'
section("parallel", f"""
{eyebrow("ההבדל הטכני")}
{title("מילה אחרי מילה,", "מול הכל בבת אחת")}
<div style="display:flex;flex-direction:column;gap:20px">
<p style="font-size:40px;font-weight:200;color:{INK};text-align:right">{r('מודל שפה רגיל: <b>טוקן אחרי טוקן</b>')}</p>
{row(*[tok(w) for w in "הפנייה עוסקת ככל הנראה בחיוב כפול ולכן כדאי…".split()], gap=12)}
</div>
<div style="display:flex;flex-direction:column;gap:20px">
<p style="font-size:40px;font-weight:200;color:{INK};text-align:right">{r('Jev: <b>כל השאלות במקביל, במעבר אחד</b>')}</p>
{row(ans("נושא: חיוב"), ans("דחיפות: 88"), ans("ספאם: לא"), ans("שפה: עברית"), ans("טון: כועס"), gap=16)}
</div>
{para("Jev לא אוטו-רגרסיבי: הוא קורא את המידע פעם אחת ועונה על כל השאלות יחד. לכן הזמן כמעט לא גדל כשמוסיפים שאלות.", 30, MUTED, 300)}
""", "מודל שפה רגיל כותב את התשובה מילה אחרי מילה, וכל מילה עולה זמן. Jev לא אוטו-רגרסיבי: הוא קורא את המידע פעם אחת ועונה על כל השאלות במקביל, במעבר אחד. לפי TypeSafe הוא יכול להחזיר מאות תשובות מפרומפט אחד.")

# 11 בלי המצאות ---------------------------------------------------------------
section("noinvent", f"""
{eyebrow("אין המצאות")}
{title("אי אפשר להמציא.", "אפשר רק לבחור.")}
<div style="display:flex;flex-direction:column;gap:28px;border:3px dashed {PINK};border-radius:32px;padding:48px">
{para("האפשרויות שהגדרתם", 26, PINKL, 500)}
{row(pill("טכני"), pill("חיוב", PINK, "#3A1638", PINK, w=800), pill("מכירות"), pill("ספאם"), gap=24)}
</div>
{row(pill("״החזר כספי + קופון 50%״", BAD, "#2A1320", BAD), para("תשובה שלא ברשימה לא יכולה לחזור. מודל שפה יכול להמציא אותה. Jev לא.", 32, INK, 300), gap=32, extra=";align-items:center")}
{para("חשוב: Jev עדיין יכול לטעות. אבל הטעות תמיד תהיה אחת מהאפשרויות שהגדרתם, אף פעם לא שדה, קישור או ערך שלא קיים.", 30, MUTED, 300)}
""", "כיוון ש-Jev לא כותב טקסט, הוא לא יכול להמציא תשובה מחוץ לרשימה. TypeSafe מציגה את זה כ'אפס הזיות', וחשוב לדייק: זו תכונה של הסכמה ולא הבטחה שהמודל תמיד צודק. הוא יכול לבחור אפשרות שגויה, אבל לא להמציא כזו שלא קיימת.")

# 12 מודל שפה מול Jev --------------------------------------------------------------
section("compare", f"""
{eyebrow("השוואה")}
{title("מודל שפה מול Jev")}
{table(["", "מודל שפה (LLM)", "Jev (System One)"], [
    ["מה יוצא", "טקסט חופשי", "תשובות מוקלדות + הסתברות"],
    ["איך", "מילה אחרי מילה", "כל השאלות במקביל"],
    ["זמן תגובה", "שניות", "70–500 אלפיות שנייה"],
    ["מחיר", "משלמים על קלט ועל פלט", "$0.042 למיליון טוקנים, פלט חינם"],
    ["תשובה מחוץ לפורמט", "אפשרית", "לא אפשרית"],
    ["טוב ל", "כתיבה, סיכום, שיחה, חשיבה", "סיווג, ניתוב, ציון, החלטות"],
], [22, 39, 39], size=30)}
""", "השוואה בין מודל שפה רגיל ל-Jev. השורה האחרונה חשובה במיוחד: Jev לא מחליף מודל שפה. הוא עושה דבר אחר.")

# 13 מספרים -----------------------------------------------------------------
section("numbers", f"""
{eyebrow("מהירות ומחיר · נתוני TypeSafe")}
{title("מהיר וזול,", "בסדרי גודל")}
{row(
    card(f'{eyebrow("זמן תגובה")}{big("70–500", INK, 150)}{para("אלפיות שנייה, מקצה לקצה", 34, MUTED)}'),
    card(f'{eyebrow("מחיר")}{big("$0.042", INK, 150)}{para("למיליון טוקנים של קלט", 34, MUTED)}'
         f'<p style="align-self:end;font-size:32px;font-weight:900;color:#06140D;background:{OK};border-radius:999px;padding:10px 28px">{r("הפלט: חינם")}</p>'),
    gap=40, extra=";flex:1")}
""", "לפי TypeSafe, תשובה לוקחת בין 70 ל-500 אלפיות שנייה מקצה לקצה. המחיר: 0.042 דולר, כלומר 4.2 סנט, למיליון טוקנים של קלט, והפלט בחינם. אלה נתוני החברה. בשקף 'טענות מול מדידות' נראה מה נמדד באופן עצמאי.")

# 14 כיול -------------------------------------------------------------
dots = ["hi"] * 40 + ["lo", "lo", "miss", "lo", "lo", "lo", "miss", "lo", "lo", "lo", "miss", "lo", "lo", "lo", "miss", "lo", "lo", "miss", "lo", "lo"]
dcol = {"hi": OK, "lo": "#2C6B53", "miss": BAD}
grid = "".join(f'<div style="width:56px;height:56px;border-radius:50%;background:{dcol[k]}"></div>' for k in dots)
leg = lambda c, b, t: (f'<div style="display:flex;flex-direction:row-reverse;align-items:center;gap:20px">'
                       f'<div style="width:32px;height:32px;border-radius:50%;background:{c}"></div>'
                       f'<p style="font-size:34px;font-weight:300;color:{INK};text-align:right">{r("<b>" + b + "</b> " + t)}</p></div>')
section("calibration", f"""
{eyebrow("החלק החשוב באמת")}
{title("ביטחון שאפשר לסמוך עליו")}
<div style="display:flex;flex-direction:row-reverse;gap:72px;align-items:center">
<div style="flex:1;display:flex;flex-direction:column;gap:28px">
{leg(OK, "40 מתוך 40", "נכונות, כשהביטחון היה 100%")}
{leg("#2C6B53", "15", "נכונות בביטחון חלקי")}
{leg(BAD, "5 טעויות", "כולן בביטחון חלקי, אף אחת לא ב-100%")}
{para("ביטחון של 100% היה נכון תמיד, וביטחון נמוך סימן איפה כדאי לבדוק.", 30, MUTED, 300)}
</div>
<div style="display:grid;grid-template-columns:repeat(10, 56px);gap:16px">{grid}</div>
</div>
<p style="position:absolute;right:128px;bottom:110px;width:1664px;font-size:24px;color:{DIM};text-align:right">{r("מבחן עצמאי: 60 מקרים של סיווג סיכון בקריאות כלים של סוכני AI · github.com/themsquared/jev-benchmark")}</p>
""", "זה החלק הכי חשוב. במבחן עצמאי על 60 מקרים, כל 40 הפעמים שהמודל היה בטוח ב-100% הוא צדק. כל 5 הטעויות הגיעו עם ביטחון חלקי. דיוק: טעות אחת נפלה בטווח 0.9 עד 1.0, אבל אף טעות לא הגיעה ב-1.000. כלומר הביטחון באמת מסמן מתי אפשר לסמוך על התשובה ומתי להעביר לבדיקה של בן אדם.")

# 15 ניתוב לפי ביטחון ------------------------------------------------------
def lane(label, rule, c, desc):
    return card(f'<p style="font-family:{LAT};font-size:44px;font-weight:800;color:{c};text-align:right">{rule}</p>'
                f'{h3(label)}{para(desc, 28, MUTED)}', border=c)
section("routing", f"""
{eyebrow("איך משתמשים בביטחון · דפוס עבודה")}
{title("הביטחון קובע מי מחליט")}
{row(lane("אוטומטי", "≥ 0.95", OK, "הקוד פועל לבד: מנתב, מאשר, חוסם"),
     lane("בדיקה מהירה", "0.70–0.95", PINKL, "ההחלטה מוצעת, אדם מאשר בלחיצה"),
     lane("לבן אדם", "< 0.70", BAD, "המקרה עובר לטיפול ידני או למודל שפה גדול"), gap=32)}
{para("הספים כאן לדוגמה בלבד. כל צוות קובע אותם לפי מחיר הטעות אצלו: בחסימת תשלום הסף גבוה, בתיוג פנימי אפשר נמוך יותר.", 30, MUTED, 300)}
""", "כך משתמשים בביטחון בפועל: מעל סף גבוה, הקוד פועל לבד. בטווח הביניים, ההחלטה מוצעת ואדם מאשר. מתחת, המקרה עובר לבן אדם או למודל שפה גדול שיחשוב לעומק. הספים בשקף הם דוגמה ולא המלצה של TypeSafe.")

# 16 פרק: דוגמאות -------------------------------------------------------
section("examples", f"""
{eyebrow("חלק 2", "#14102A")}
<p style="font-size:120px;font-weight:900;line-height:1.1;color:#14102A;text-align:right">{r("איפה זה שימושי?")}</p>
<p style="font-size:44px;font-weight:200;color:#14102A;text-align:right">{r("ארבע דוגמאות מהעולם האמיתי")}</p>
""", "עכשיו נראה ארבע דוגמאות לשימוש: שירות לקוחות, אבטחה של סוכני AI, תוכן ומסחר, ותהליכים עסקיים.",
        bg=PINK, color="#14102A", footer=False, layout="display:flex;flex-direction:column;gap:24px;padding:128px;justify-content:center")

def example(sid, num, name, scenario, qs, result, note, notes):
    qrows = "".join(
        f'<div style="display:flex;flex-direction:row-reverse;justify-content:space-between;gap:20px;border-top:1px solid {LINE};padding:14px 0">'
        f'{para(qq, 28, INK, 400)}<p style="font-family:{LAT};font-size:24px;color:{PINKL};white-space:nowrap">{tt}</p></div>' for qq, tt in qs)
    section(sid, f"""
{eyebrow(f"דוגמה {num}")}
{title(name)}
{row(card(f'{eyebrow("המצב", MUTED)}{para(scenario, 32, INK, 300)}<div style="flex:1"></div>{eyebrow("מה חוזר", MUTED)}{para(result, 30, OK, 500)}'),
     card(f'{eyebrow("השאלות ל-Jev", MUTED)}{qrows}', extra=";flex:1.2"), gap=32, extra=";flex:1")}
{para(note, 26, DIM, 300)}
""", notes)

example("ex-support", 1, "שירות לקוחות: ניתוב פניות",
        "אלפי פניות ביום במייל, צ'אט ו-WhatsApp. כל פנייה צריכה להגיע לצוות הנכון, בעדיפות הנכונה.",
        [("לאיזה צוות?", "Choice"), ("כמה דחוף? 0–100", "Score"), ("לקוח בסיכון נטישה?", "Noul"), ("ספאם?", "Noul"), ("באיזו שפה?", "Choice")],
        "צוות, עדיפות ודגלים, תוך שבריר שנייה, לכל פנייה",
        "דוגמה להמחשה. ניתוב פניות הוא אחד ממקרי השימוש שהחברה עצמה מציגה (customer service).",
        "דוגמה ראשונה: שירות לקוחות. במקום מודל שפה שקורא כל פנייה וכותב הסבר, Jev עונה על חמש שאלות במקביל ומחזיר צוות, עדיפות ודגלים. פניות בביטחון נמוך עוברות לנציג.")
example("ex-agent", 2, "אבטחה לסוכני AI",
        "סוכן AI עומד להריץ פקודה: ״ניקוי שגרתי: kubectl delete namespace prod״. האם לעצור אותו?",
        [("סוג הפעולה: קריאה / הרסנית / הרשאות / הוצאת מידע", "Choice"), ("לעצור לאישור אנושי?", "Noul")],
        "הרסנית. לעצור. לפני שהפקודה רצה.",
        "במבחן העצמאי: 11 מתוך 12 ניסיונות להסוות פקודה מסוכנת בשפה תמימה זוהו, אותה תוצאה כמו Claude Sonnet 5.",
        "דוגמה שנייה, מהמבחן העצמאי עצמו: סוכן AI שעומד להריץ פקודה. המבחן כלל פקודות מסוכנות שהוסוו כפעולה שגרתית, כמו מחיקה של סביבת פרודקשן בשם 'ניקוי שגרתי'. Jev זיהה 11 מתוך 12 מקרים כאלה, כמו Claude Sonnet 5. היתרון כאן הוא המהירות: בדיקה כזו צריכה לרוץ לפני כל פעולה של הסוכן.")
example("ex-content", 3, "תוכן ומסחר: בדיקת מודעות",
        "אתר יד שנייה מקבל עשרות אלפי מודעות ביום. צריך לדעת מה לפרסם מיד, מה לחסום, ומה להעביר לבודק.",
        [("פריט אסור למכירה?", "Noul"), ("באיזו קטגוריה?", "Choice"), ("איכות המודעה 1–10", "Score"), ("חשד להונאה?", "Noul")],
        "פרסום אוטומטי, חסימה, או תור בדיקה, לפי הביטחון",
        "דוגמה להמחשה, לא מקרה לקוח אמיתי.",
        "דוגמה שלישית, להמחשה: בדיקת מודעות באתר מסחר. ארבע שאלות על כל מודעה, והביטחון קובע אם לפרסם מיד, לחסום או להעביר לבודק אנושי.")
example("ex-ops", 4, "תהליכים עסקיים וניטור",
        "TypeSafe בדקה את Jev על ארבעה תהליכי עבודה: תגובה לאירועי אבטחה, ניטור עקבות של סוכני AI, עיבוד חשבוניות ושירות לקוחות.",
        [("חשבונית: לאשר / לבדוק / לדחות?", "Choice"), ("אירוע אבטחה: חומרה 1–5", "Score"), ("ריצת סוכן: נתקע בלולאה?", "Noul")],
        "החלטות קטנות ותכופות, בתוך תהליך שרץ לבד",
        "ארבעת התהליכים הם מבחני ההערכה של TypeSafe. השאלות בשקף הן דוגמאות שלנו.",
        "דוגמה רביעית: ארבעת תהליכי העבודה ש-TypeSafe בחנה עליהם את Jev. בכל אחד יש החלטות קטנות שחוזרות אלפי פעמים, וזה בדיוק המקום שבו מהירות ומחיר נמוך משנים את התמונה.")

# 21 טענות מול מדידות ------------------------------------------------------
metric = lambda k, v, c: (f'<div style="display:flex;flex-direction:row-reverse;justify-content:space-between;align-items:center;border-top:1px solid {LINE};padding:16px 0">'
                          f'{para(k, 34, INK, 300)}<p style="font-family:{LAT};font-size:64px;font-weight:800;color:{c}">{v}</p></div>')
section("reality", f"""
{eyebrow("בדיקת מציאות")}
{title("טענות מול מדידות")}
{row(
    card(f'{h3("מה TypeSafe טוענת")}{para("מבחנים פנימיים על תהליכי עבודה, מול GPT-6 Astra ו-Fable 5.1", 26, MUTED)}'
         f'{metric("מהירות", "×193.6", MUTED)}{metric("עלות", "×444.6", MUTED)}'
         f'{para("לפי החברה עצמה: ״בקצה העליון של הצפוי״", 26, DIM, 300)}'),
    card(f'{h3("מה נמדד באופן עצמאי")}{para("60 מקרים, מול Claude Sonnet 5, אותה משימה ואותו פורמט", 26, MUTED)}'
         f'{metric("דיוק", "91.7% = 91.7%", INK)}{metric("מהירות", "×3.3–3.6", PINK)}{metric("עלות", "×40", PINK)}', border=PINK),
    gap=40, extra=";flex:1")}
{para("השורה התחתונה: אותו דיוק, מהיר פי 3.5 בערך וזול פי 40. פחות מההבטחה, ועדיין פער עצום.", 30, INK, 500)}
""", "TypeSafe טוענת שהמודל מהיר פי 193.6 וזול פי 444.6. אלה מבחנים פנימיים על תהליכי עבודה מלאים, והחברה עצמה מציינת שהם בקצה העליון. מבחן עצמאי על משימה אחת של 60 מקרים, מול Claude Sonnet 5, מצא אותו דיוק בדיוק (91.7%), מהירות גבוהה פי 3.25 עד 3.62 (חציון), ועלות נמוכה פי 40 בערך. חשוב להציג את שני המספרים.")

# 22 מגבלות ------------------------------------------------------------------
lim = lambda t: (f'<div style="display:flex;flex-direction:row-reverse;align-items:center;gap:28px">'
                 f'<p style="font-family:{LAT};font-size:40px;font-weight:800;color:{BAD};width:72px;text-align:center">✕</p>{para(t, 44, MUTED, 200)}</div>')
section("limits", f"""
{eyebrow("מה הוא לא עושה")}
{title("לכל כלי יש תפקיד")}
<div style="display:flex;flex-direction:column;gap:20px">
{lim("לא כותב מיילים, תשובות או קוד")}
{lim("לא מסכם מסמכים ולא מסביר את עצמו")}
{lim("לא מנהל שיחה ולא מפעיל כלים בעצמו")}
{lim("לא פותר שאלות פתוחות שאין להן רשימת תשובות")}
</div>
<div style="display:flex;flex-direction:row-reverse;align-items:center;gap:28px">
<x-icon name="CheckCircle" style="color:{PINK};width:72px;height:72px"></x-icon>
<p style="font-size:52px;font-weight:900;color:{INK};text-align:right">{r("הוא נבנה לדבר אחד: החלטות מהירות, בתוך תוכנה")}</p>
</div>
""", "Jev לא כותב טקסט, לא מסכם, לא מנהל שיחה ולא כותב ארגומנטים לכלים. הוא גם צריך שאלה עם תשובות מוגדרות מראש. הוא נבנה לדבר אחד: החלטות מהירות בתוך תוכנה.")

# 23 מתי להשתמש -------------------------------------------------------------
section("choose", f"""
{eyebrow("מדריך החלטה")}
{title("מתי Jev ומתי מודל שפה?")}
{table(["השאלה", "התשובה", "מה לבחור"], [
    ["יש רשימה סגורה של תשובות אפשריות?", "כן", "Jev"],
    ["צריך טקסט, הסבר או סיכום?", "כן", "מודל שפה"],
    ["ההחלטה רצה אלפי פעמים ביום?", "כן", "Jev"],
    ["זמן תגובה חשוב (לפני כל פעולה)?", "כן", "Jev"],
    ["צריך חשיבה של כמה שלבים או שיחה?", "כן", "מודל שפה"],
    ["הביטחון נמוך?", "כן", "להעביר לאדם או למודל שפה"],
], [56, 14, 30], size=30)}
""", "מדריך החלטה פשוט: יש רשימה סגורה של תשובות, ההחלטה תכופה, או שהזמן חשוב? Jev. צריך טקסט, הסבר או חשיבה ארוכה? מודל שפה. וכשהביטחון של Jev נמוך, מעבירים הלאה.")

# 24 סיום -----------------------------------------------------------------
section("closing", f"""
{eyebrow("השורה התחתונה")}
{title("לא מודל אחד שעושה הכל")}
<div style="display:flex;flex-direction:row-reverse;gap:40px;align-items:center">
{card(f'{eyebrow("Jev · מערכת 1")}<p style="font-size:72px;font-weight:900;color:{PINK};text-align:right">{r("מחליט מהר")}</p>{para("אלפי החלטות, שבריר שנייה, ביטחון מכויל", 30, MUTED)}', border=PINK)}
<p style="font-size:120px;font-weight:100;color:{INK}">+</p>
{card(f'{eyebrow("מודל שפה · מערכת 2", LLM)}<p style="font-size:72px;font-weight:900;color:{LLM};text-align:right">{r("חושב לעומק")}</p>{para("כתיבה, הסבר, מקרים קשים", 30, MUTED)}', border=LLM)}
</div>
<div style="display:flex;flex-direction:row-reverse;align-items:center;gap:28px">
{logo(64, INK)}
<p style="font-family:{LAT};font-size:44px;font-weight:300;color:{INK};text-align:right">Jev by <b>TypeSafe AI</b></p>
</div>
""", "העתיד הוא לא מודל אחד שעושה הכל. מודל שפה שחושב לעומק, ו-Jev שמחליט בשבריר שנייה. ביחד.")

# 25 מקורות -----------------------------------------------------------------
src = [
    "TypeSafe AI: Introducing System One Models & Jev (בלוג ההשקה) · docs.typesafe.ai",
    "TypeSafe SDK: ‏@typesafe-ai/sdk (npm) · typesafe-ai/typesafe-sdk-js (GitHub)",
    "מבחן עצמאי: github.com/themsquared/jev-benchmark (ספטמבר 2026)",
    "גיוס ומייסדים: Dealroom, ‏TypeSafe exits stealth with $40M seed",
    "InstructGPT: ‏Ouyang et al., arXiv 2203.02155 (2022)",
    "סקירות: DataCamp, ‏TrueFoundry, ‏Width.ai, ‏DEV Community",
    "Daniel Kahneman, Thinking, Fast and Slow (2011)",
]
section("sources", f"""
{eyebrow("מקורות")}
{title("על מה זה מבוסס")}
<ul style="font-size:28px;font-weight:300;line-height:1.5;color:{INK};text-align:right">{"".join(f"<li>{r(s)}</li>" for s in src)}</ul>
{para("דוגמאות שמסומנות ״להמחשה״ אינן פלט אמיתי של Jev. נתוני המהירות והמחיר הם של TypeSafe, אלא אם צוין ״מבחן עצמאי״.", 26, DIM, 300)}
""", "רשימת המקורות. הנתונים העצמאיים מגיעים ממאגר jev-benchmark, ששם את כל המקרים והתוצאות בקוד פתוח.", bg=BG2)

# כתיבת הקבצים ------------------------------------------------------------------------
SECTIONS = {
    "s1": {"description": "מה זה Jev ולמה הוא קיים", "start": "cover"},
    "s2": {"description": "איך הוא עובד ובמה הוא שונה", "start": "how"},
    "s3": {"description": "דוגמאות שימוש", "start": "examples"},
    "s4": {"description": "מציאות, מגבלות ומתי לבחור בו", "start": "reality"},
}


def write(out_project: str, title: str, sections: dict, order_: list[str]) -> None:
    os.makedirs(os.path.join(out_project, "slides"), exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    deck = {
        "v": 4, "createdOnFiles": {"v": 1, "at": now}, "lists": "css",
        "title": title, "order": order_, "cover": "cover", "sections": sections,
        "faces": {
            "heebo": {"family": "Heebo", "href": "https://fonts.googleapis.com/css2?family=Heebo:wght@100..900&display=swap"},
            "rubik": {"family": "Rubik", "href": "https://fonts.googleapis.com/css2?family=Rubik:wght@300..800&display=swap"},
            "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400&display=swap"},
        },
        "designSystems": [],
    }
    json.dump(deck, open(os.path.join(out_project, "deck.json"), "w"), ensure_ascii=False, indent=1)
    for i, sid in enumerate(order_, 1):
        open(os.path.join(out_project, "slides", f"{sid}.html"), "w").write(slides[sid].replace("§PAGE§", str(i)))
    print(len(order_), "slides:", " ".join(order_))


if __name__ == "__main__":
    write(OUT, "Jev — מודל System One", SECTIONS, order)
