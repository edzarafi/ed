# מקורות

| נתון בסרטון | מקור |
|---|---|
| Jev הוא מודל ה-System One הראשון של TypeSafe AI, הושק ב-15.9.2026 בגישה מוקדמת. מחזיר תשובות מוגדרות מראש (typed) עם הסתברויות, ולא טקסט | [TypeSafe blog: Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev), [docs: System One](https://docs.typesafe.ai/concepts/system-one) |
| שלושה סוגי שאלות: Choice (עד 255 אפשרויות), Score, Noul (כן/לא, 0–1). כל השאלות נבדקות במקביל במעבר אחד | [TrueFoundry](https://www.truefoundry.com/blog/typesafe-ai-jev), [Width.ai](https://www.width.ai/post/what-is-jev-ai-typesafe), TypeSafe SDK README (`@typesafe-ai/sdk`) |
| 70–500ms, ‏$0.042 למיליון טוקנים של קלט, פלט בחינם | TypeSafe, מצוטט ב-[DataCamp](https://www.datacamp.com/blog/system-one-models-jev) ו-[DigitalOcean](https://www.digitalocean.com/resources/articles/what-is-jev) |
| סבב Seed של 40 מיליון דולר בהובלת DCVC. המייסד והמנכ״ל דיוגו אלמיידה, לשעבר חוקר ב-OpenAI | [Dealroom](https://dealroom.co/news/151032-typesafe-exits-stealth-with-40m-seed-to-build-ai-for-software-not-people/) |
| אלמיידה הוא ממחברי InstructGPT (מחקר ה-RLHF של OpenAI) | [arXiv 2203.02155](https://arxiv.org/abs/2203.02155) |
| הטענה של TypeSafe: פי 193.6 מהיר ופי 444.6 זול מ-GPT-6 Astra ו-Fable 5.1, על מבחני תהליכי עבודה פנימיים, ״בקצה העליון של הרווחים הצפויים״ | TypeSafe launch post, וניתוח ב-[DEV](https://dev.to/arifulislamat/typesafes-jev-model-is-it-really-193x-faster-and-444x-cheaper-56oa) |
| מבחן עצמאי (60 מקרים): דיוק 91.7% זהה ל-Claude Sonnet 5, מהיר פי 3.25–3.62 (חציון), זול פי ~40.6. 40 תשובות בביטחון 1.000, כולן נכונות. 5 טעויות, אף אחת בביטחון 1.000 | [themsquared/jev-benchmark](https://github.com/themsquared/jev-benchmark) |
| מגבלות: לא מייצר טקסט, לא מסכם, לא מנהל שיחה | [DEV: Jev can't talk](https://dev.to/lukeocodes/jev-the-chatgpt-co-creators-system-one-model-cant-talk-3774), [Ginger Labs](https://gingerlabs.ai/blog/jev-ai-capabilities-limitations-and-how-to-use) |
| System 1 ו-System 2 | Daniel Kahneman, *Thinking, Fast and Slow* (2011) |

**הערות**
- הדוגמה בסצנת ״ככה זה עובד״ (פנייה על חיוב כפול, ציון 88, ביטחון 0.97) היא להמחשה בלבד. היא לא פלט אמיתי של Jev.
- בסרטון כתוב ״מהיר פי 3.5״. זה עיגול של הטווח 3.25–3.62 שנמדד במבחן העצמאי.
- הסמל של TypeSafe נלקח מחבילות קהילה ב-npm (`@itsmeyaw/n8n-nodes-typesafe`, ותואם לשרטוט עצמאי ב-`n8n-nodes-typesafe`), כי האתר typesafe.ai חסום בסביבה שבה הסרטון נבנה. כדאי לוודא מול ערכת המותג הרשמית.
- המאמר של גלעד שוהם בלינקדאין לא היה נגיש מהסביבה (linkedin.com חסום), ולכן התוכן לא מבוסס עליו ישירות.
