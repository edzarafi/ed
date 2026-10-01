"""Medical document pipeline: Jev classifies, Claude extracts, Jev scores the extraction.

Stage 1  Jev (System One)  -> document type, specialty, urgency, PHI flag      (one call, all questions in parallel)
Stage 2  Claude            -> structured fields + a verbatim evidence quote per field
Stage 3  Jev (System One)  -> per-field "is this supported by the document?" probability,
                              ICD/diagnosis consistency, overall extraction quality
Routing  thresholds on the Stage 1 and Stage 3 confidences decide: auto-accept / review / human.

Two backends per model:
  live  real APIs (typesafe-sdk, anthropic), needs TYPESAFE_API_KEY and ANTHROPIC_API_KEY
  demo  offline stand-ins so the notebook runs anywhere. DemoJev is a lexical heuristic, NOT Jev;
        DemoExtractor replays the reference extraction from documents/ground_truth.json.
        Demo numbers illustrate the flow only; they are not model results.
"""
from __future__ import annotations

import json
import math
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "documents"
CLAUDE_MODEL = "claude-opus-5-5"
JEV_MODEL = "jev-latest"

# ---------------------------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------------------------

@dataclass
class Document:
    doc_id: str
    text: str


def load_documents(docs_dir: Path = DOCS_DIR) -> list[Document]:
    return [Document(p.stem, p.read_text(encoding="utf-8")) for p in sorted(docs_dir.glob("*.txt"))]


def load_ground_truth(docs_dir: Path = DOCS_DIR) -> dict:
    return json.loads((docs_dir / "ground_truth.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------------------------------------
# Stage 1: classification questions (Jev)
# ---------------------------------------------------------------------------------------------

DOC_TYPES = {
    "discharge_summary": "Hospital discharge summary: admission course, diagnoses and discharge instructions",
    "lab_report": "Laboratory results report: tests, values, units and reference ranges",
    "er_visit": "Emergency department visit summary",
    "imaging_report": "Radiology / imaging report (X-ray, CT, MRI, ultrasound) with findings and impression",
    "pathology_report": "Pathology report on a tissue sample or biopsy",
    "referral_letter": "Letter from one clinician referring the patient to another clinic or specialist",
    "prescription": "Prescription listing medications to dispense",
    "clinic_visit": "Outpatient clinic visit summary (complaint, exam, diagnosis, treatment)",
    "administrative": "Non-clinical document: invoice, receipt, insurance or billing paperwork",
}
SPECIALTIES = {
    "internal_medicine": None, "family_medicine": None, "cardiology": None, "endocrinology": None,
    "orthopedics": None, "oncology": None, "pediatrics": None, "emergency_medicine": None,
    "neurology": None, "none": "No clinical specialty applies (e.g. billing paperwork)",
}
URGENCY_LEVELS = [
    "No clinical action needed",
    "Routine follow-up within weeks",
    "Needs attention within days",
    "Needs attention within 24-48 hours (e.g. new cancer diagnosis needing referral)",
    "Life-threatening emergency, immediate action",
]


def classification_questions() -> dict:
    """Plain-dict questions: the wire format both the SDK and DemoJev accept."""
    return {
        "doc_type": {"type": "choice", "instructions": "What kind of medical document is this?", "criteria": DOC_TYPES},
        "specialty": {"type": "choice", "instructions": "Which clinical specialty should own this document?", "criteria": SPECIALTIES},
        "urgency": {"type": "score", "instructions": "How urgently does this document require clinical action?", "criteria": URGENCY_LEVELS},
        "contains_phi": {"type": "noul", "instructions": "Does the document contain personally identifying details (name, ID number)?",
                         "criteria": {"true": "A patient name or ID number appears", "false": "No identifying details"}},
    }

# ---------------------------------------------------------------------------------------------
# Stage 2: extraction schema (Claude)
# ---------------------------------------------------------------------------------------------

class Medication(BaseModel):
    name: str
    dose: str | None = None
    frequency: str | None = None


class LabValue(BaseModel):
    test: str
    value: str
    unit: str | None = None
    flag: Literal["high", "low", "normal", "unknown"] = "unknown"


class Evidence(BaseModel):
    field: str = Field(description="Name of the extracted field, e.g. icd10_code or medications[0]")
    quote: str = Field(description="Verbatim span copied from the document that supports the value")


class MedicalExtraction(BaseModel):
    patient_name: str | None
    patient_age: int | None
    patient_sex: Literal["male", "female", "unknown"]
    document_date: str | None = Field(description="ISO date YYYY-MM-DD of the document")
    facility: str | None
    primary_diagnosis: str | None = Field(description="Main diagnosis, in the document's language")
    icd10_code: str | None
    secondary_diagnoses: list[str]
    medications: list[Medication]
    lab_values: list[LabValue]
    follow_up: str | None
    evidence: list[Evidence]


EXTRACTION_SYSTEM = (
    "You extract structured data from clinical documents. Copy values exactly as written in the document "
    "(keep Hebrew text in Hebrew). Use null when a field is not stated; never infer a diagnosis the document "
    "rules out (for example 'ללא עדות לשבר' means there is NO fracture). For every non-null field add an "
    "evidence item quoting the exact supporting span."
)

# ---------------------------------------------------------------------------------------------
# Answers (backend-neutral)
# ---------------------------------------------------------------------------------------------

@dataclass
class Ans:
    type: str
    choice: str | None = None
    confidence: float | None = None
    probabilities: dict = field(default_factory=dict)
    noul: float | None = None
    score: float | None = None

# ---------------------------------------------------------------------------------------------
# Jev backends
# ---------------------------------------------------------------------------------------------

class LiveJev:
    name = "Jev (live)"

    def __init__(self, client=None, model: str = JEV_MODEL):
        from typesafe_sdk import TypeSafeClient
        self.client = client or TypeSafeClient()
        self.model = model

    def ask(self, state, questions: dict) -> tuple[dict[str, Ans], float, dict]:
        t0 = time.perf_counter()
        r = self.client.system_one(state=state, questions=questions, model=self.model)
        dt = time.perf_counter() - t0
        usage = {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}
        out = {}
        for k, a in r.answers.items():
            if a.type == "choice":
                out[k] = Ans("choice", choice=a.choice, confidence=a.confidence, probabilities=dict(a.probabilities))
            elif a.type == "score":
                out[k] = Ans("score", score=a.score, confidence=a.confidence, probabilities=dict(a.probabilities))
            else:
                out[k] = Ans("noul", noul=a.noul)
        return out, dt, usage


_NEG = re.compile(r"(ללא|אין|לא נמצא|שלילי)\s+(עדות\s+ל|סימני\s+)?\S*\s*$")
_KEYWORDS = {
    "doc_type": {
        "discharge_summary": ["סיכום אשפוז", "שחרור", "מהלך האשפוז"],
        "lab_report": ["תוצאות בדיקות", "טווח תקין", "תאריך דגימה", "מעבדות"],
        "er_visit": ["מיון", "רפואה דחופה"],
        "imaging_report": ["פענוח", "רנטגן", "CT", "דימות", "רושם"],
        "pathology_report": ["פתולוג", "ביופסיה", "דגימה", "מיקרוסקופי"],
        "referral_letter": ["הפניה", "מפנה", "בקשה לתור", "אל:", "לכב'"],
        "prescription": ["מרשם", "90 יום"],
        "clinic_visit": ["סיכום ביקור", "מרפאת ילדים", "תלונות"],
        "administrative": ["חשבונית", "קבלה", "מע\"מ", "לתשלום"],
    },
    "specialty": {
        "internal_medicine": ["פנימית", "דלקת ריאות"],
        "family_medicine": ["רפואת המשפחה", "יתר לחץ דם", "מרשם"],
        "cardiology": ["קרדיולוג", "אוטם", "STEMI", "פרפור", "אק\"ג"],
        "endocrinology": ["אנדוקרינ", "סוכרת", "TSH", "HbA1c", "תריס"],
        "orthopedics": ["שבר", "אורתופד", "רדיוס"],
        "oncology": ["קרצינומה", "אונקולוג", "גידול"],
        "pediatrics": ["ילד", "ילדים"],
        "emergency_medicine": ["מיון", "נפילה", "חבלת ראש"],
        "neurology": ["תוך-גולגולתי", "נוירולוג"],
        "none": ["חשבונית", "לתשלום"],
    },
    "urgency": [["חשבונית"], ["ביקורת", "מעקב", "בעוד שבוע"], ["48", "השגחה", "תוך 48"], ["אונקולוג", "קרצינומה"], ["בדחיפות", "STEMI", "צנתור"]],
}


def _softmax(scores: dict[str, float], temp: float = 1.2) -> dict[str, float]:
    m = max(scores.values())
    ex = {k: math.exp((v - m) / temp) for k, v in scores.items()}
    z = sum(ex.values())
    return {k: v / z for k, v in ex.items()}


def _norm(s: str) -> str:
    return re.sub(r"[\s\"'״׳.,:;()\-–/]+", "", s or "").lower()


class DemoJev:
    """Offline lexical stand-in for Jev. Keyword votes for Stage 1, substring/negation checks for Stage 3.
    It exists so the notebook runs without API keys. It is NOT Jev and its numbers are not model output."""

    name = "DemoJev (heuristic stand-in)"

    def ask(self, state, questions: dict) -> tuple[dict[str, Ans], float, dict]:
        t0 = time.perf_counter()
        text = state if isinstance(state, str) else state.get("document", "")
        out = {}
        for k, q in questions.items():
            if k in ("doc_type", "specialty"):
                kw = _KEYWORDS[k]
                votes = {c: float(sum(text.count(w) for w in kw.get(c, []))) for c in q["criteria"]}
                probs = _softmax(votes, temp=0.45)
                best = max(probs, key=probs.get)
                out[k] = Ans("choice", choice=best, confidence=probs[best], probabilities=probs)
            elif k == "urgency":
                votes = {i: sum(text.count(w) for w in ws) for i, ws in enumerate(_KEYWORDS["urgency"])}
                top = max(i for i, v in votes.items() if v) if any(votes.values()) else 1
                probs = {i: (0.8 if i == top else 0.2 / (len(votes) - 1)) for i in votes}
                out[k] = Ans("score", score=sum(i * p for i, p in probs.items()), confidence=0.8, probabilities=probs)
            elif k == "contains_phi":
                out[k] = Ans("noul", noul=0.97 if re.search(r"(שם|מטופל|ת\.ז|לכבוד)", text) else 0.1)
            elif k.startswith("claim_"):
                out[k] = Ans("noul", noul=self._support(text, q["_value"]))
            elif k == "icd_consistent":
                out[k] = Ans("noul", noul=0.9 if q["_value"] and q["_value"] in text else 0.15)
            elif k == "extraction_quality":
                vals = q["_values"]
                hit = sum(1 for v in vals if self._support(text, v) > 0.5) / max(1, len(vals))
                lvl = round(hit * (len(q["criteria"]) - 1))
                out[k] = Ans("score", score=float(lvl), confidence=0.75, probabilities={lvl: 0.75})
        return out, time.perf_counter() - t0, {}

    @staticmethod
    def _support(text: str, value: str) -> float:
        nv, nt = _norm(value), _norm(text)
        if not nv:
            return 0.5
        if nv in nt:
            # found verbatim: still reject when the document negates it ("ללא עדות לשבר")
            i = text.find(value.split()[0]) if value.split() else -1
            line_start = text.rfind("\n", 0, i) + 1 if i > 0 else 0
            if i > 0 and _NEG.search(text[max(line_start, i - 25):i]):
                return 0.06
            return 0.96
        toks = [t for t in re.split(r"[\s,;()]+", value) if len(t) > 1]
        if not toks:
            return 0.3
        frac = sum(1 for t in toks if _norm(t) in nt) / len(toks)
        if frac == 1:
            return 0.91  # every token present, not contiguous: likely a light paraphrase
        # some tokens missing (e.g. a changed dose) -> uncertain-to-low
        return round(0.08 + 0.6 * frac ** 2, 3)

# ---------------------------------------------------------------------------------------------
# Extraction backends
# ---------------------------------------------------------------------------------------------

class LiveExtractor:
    name = f"Claude ({CLAUDE_MODEL})"

    def __init__(self, client=None, model: str = CLAUDE_MODEL):
        import anthropic
        self.client = client or anthropic.Anthropic()
        self.model = model

    def extract(self, doc: Document, doc_type: str) -> tuple[MedicalExtraction, float, dict]:
        t0 = time.perf_counter()
        resp = self.client.messages.parse(
            model=self.model,
            max_tokens=16000,
            output_config={"effort": "low"},
            system=EXTRACTION_SYSTEM,
            messages=[{"role": "user", "content":
                       f"Document type (from the classifier): {doc_type}\n\n<document>\n{doc.text}\n</document>"}],
            output_format=MedicalExtraction,
        )
        dt = time.perf_counter() - t0
        if resp.stop_reason == "refusal" or resp.parsed_output is None:
            raise RuntimeError(f"{doc.doc_id}: extraction stopped ({resp.stop_reason})")
        usage = {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
        return resp.parsed_output, dt, usage


class DemoExtractor:
    """Replays the reference extraction from ground_truth.json (what a correct extraction looks like)."""
    name = "DemoExtractor (reference replay)"

    def __init__(self, ground_truth: dict):
        self.gt = ground_truth

    def extract(self, doc: Document, doc_type: str) -> tuple[MedicalExtraction, float, dict]:
        data = dict(self.gt[doc.doc_id]["extraction"])
        data.setdefault("evidence", [])
        return MedicalExtraction.model_validate(data), 0.0, {}


# Deliberate errors for a "chaos test": shows that Stage 3 catches wrong extractions.
INJECTED_ERRORS = {
    "09_ct_head_negative": {"primary_diagnosis": "שבר בעצמות הגולגולת", "icd10_code": "S02.0XXA"},
    "08_pediatric_otitis": {"medications": [{"name": "Amoxicillin", "dose": "1350 מ\"ג", "frequency": "פעמיים ביום, 10 ימים"},
                                            {"name": "Paracetamol", "dose": "15 מ\"ג/ק\"ג", "frequency": "לפי הצורך, עד 4 פעמים ביום"}]},
}


def inject_error(doc_id: str, ex: MedicalExtraction) -> tuple[MedicalExtraction, list[str]]:
    patch = INJECTED_ERRORS.get(doc_id)
    if not patch:
        return ex, []
    return MedicalExtraction.model_validate({**ex.model_dump(), **patch}), list(patch)

# ---------------------------------------------------------------------------------------------
# Stage 3: verification questions (Jev)
# ---------------------------------------------------------------------------------------------

QUALITY_LEVELS = [
    "Mostly wrong or empty",
    "Several important fields wrong or missing",
    "Mostly right, one important error or omission",
    "Right, minor omissions only",
    "Complete and fully supported by the document",
]


def claims_from(ex: MedicalExtraction) -> list[tuple[str, str, str]]:
    """(claim_key, field_label, value) for every value worth checking against the document."""
    c = []
    add = lambda k, label, v: v not in (None, "", []) and c.append((k, label, str(v)))
    add("claim_patient_age", "patient_age", ex.patient_age)
    add("claim_primary_diagnosis", "primary_diagnosis", ex.primary_diagnosis)
    add("claim_icd10_code", "icd10_code", ex.icd10_code)
    for i, m in enumerate(ex.medications):
        add(f"claim_med_{i}", f"medications[{i}]", " ".join(x for x in (m.name, m.dose) if x))
    for i, lv in enumerate(ex.lab_values):
        add(f"claim_lab_{i}", f"lab_values[{i}]", f"{lv.test} {lv.value}")
    add("claim_follow_up", "follow_up", ex.follow_up)
    return c


def verification_questions(ex: MedicalExtraction) -> dict:
    qs = {}
    for key, label, value in claims_from(ex):
        qs[key] = {"type": "noul",
                   "instructions": f"The extractor says {label} = «{value}». Is this value stated in, or directly entailed by, the document?",
                   "criteria": {"true": "The document states this value (wording may differ slightly)",
                                "false": "The document does not state it, states a different value, or rules it out"},
                   "_value": value}
    if ex.icd10_code:
        qs["icd_consistent"] = {"type": "noul",
                                "instructions": f"Is ICD-10 code {ex.icd10_code} a correct code for the main diagnosis described in the document?",
                                "_value": ex.icd10_code}
    qs["extraction_quality"] = {"type": "score",
                                "instructions": "Rate how complete and correct the extracted record (state.extracted) is against the document (state.document).",
                                "criteria": QUALITY_LEVELS, "_values": [v for _, _, v in claims_from(ex)]}
    return qs


def wire(questions: dict) -> dict:
    """Strip the demo-only helper keys before a question goes to the real API."""
    return {k: {kk: vv for kk, vv in q.items() if not kk.startswith("_")} for k, q in questions.items()}

# ---------------------------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------------------------

ACCEPT, REVIEW = 0.90, 0.60          # field confidence thresholds
CLASSIFY_MIN = 0.75                  # doc_type confidence below this goes to a human for triage


def field_status(p: float) -> str:
    return "accept" if p >= ACCEPT else ("review" if p >= REVIEW else "reject")


def route(doc_type: Ans, field_conf: dict[str, float]) -> tuple[str, str]:
    if doc_type.confidence is not None and doc_type.confidence < CLASSIFY_MIN:
        return "human_triage", f"classification confidence {doc_type.confidence:.2f} < {CLASSIFY_MIN}"
    if doc_type.choice == "administrative":
        return "archive", "non-clinical document, no extraction"
    worst = min(field_conf.values()) if field_conf else 1.0
    if worst < REVIEW:
        bad = [k for k, v in field_conf.items() if v < REVIEW]
        return "human_review", "rejected fields: " + ", ".join(bad)
    if worst < ACCEPT:
        return "quick_review", f"lowest field confidence {worst:.2f}"
    return "auto_accept", f"all fields >= {ACCEPT}"

# ---------------------------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------------------------

def run_document(doc: Document, jev, extractor, inject: bool = False) -> dict:
    is_demo = isinstance(jev, DemoJev)
    q1 = classification_questions()
    a1, t1, u1 = jev.ask(doc.text, q1 if is_demo else wire(q1))
    rec = {"doc_id": doc.doc_id, "classification": {k: vars(v) for k, v in a1.items()},
           "latency_s": {"classify": t1}, "jev_usage": [u1]}
    if a1["doc_type"].choice == "administrative":
        rec["route"], rec["route_reason"] = route(a1["doc_type"], {})
        return rec

    ex, t2, usage = extractor.extract(doc, a1["doc_type"].choice)
    injected = []
    if inject:
        ex, injected = inject_error(doc.doc_id, ex)
    rec.update(extraction=ex.model_dump(), injected_fields=injected, claude_usage=usage)
    rec["latency_s"]["extract"] = t2

    q3 = verification_questions(ex)
    state = {"document": doc.text, "extracted": ex.model_dump(exclude={"evidence"})}
    a3, t3, u3 = jev.ask(state, q3 if is_demo else wire(q3))
    rec["latency_s"]["verify"] = t3
    rec["jev_usage"].append(u3)
    labels = {k: label for k, label, _ in claims_from(ex)}
    values = {k: v for k, _, v in claims_from(ex)}
    rec["fields"] = [{"field": labels[k], "value": values[k], "confidence": round(a3[k].noul, 3),
                      "status": field_status(a3[k].noul)} for k in labels if k in a3]
    if "icd_consistent" in a3:
        rec["icd_consistent"] = round(a3["icd_consistent"].noul, 3)
    rec["extraction_quality"] = vars(a3["extraction_quality"])
    conf = {f["field"]: f["confidence"] for f in rec["fields"]}
    rec["route"], rec["route_reason"] = route(a1["doc_type"], conf)
    return rec


def run_all(docs: list[Document], jev, extractor, inject: bool = False) -> list[dict]:
    return [run_document(d, jev, extractor, inject) for d in docs]


def make_backends(mode: str | None = None):
    """mode: 'live', 'demo', or None = live when both API keys are present, else demo."""
    if mode is None:
        mode = "live" if os.environ.get("TYPESAFE_API_KEY") and os.environ.get("ANTHROPIC_API_KEY") else "demo"
    if mode == "live":
        return mode, LiveJev(), LiveExtractor()
    return mode, DemoJev(), DemoExtractor(load_ground_truth())

# ---------------------------------------------------------------------------------------------
# Cost (published list prices; check current pricing before relying on them)
# ---------------------------------------------------------------------------------------------

PRICE_PER_MTOK = {"claude_in": 4.00, "claude_out": 20.00,   # Claude Opus 5.5
                  "jev_in": 0.042, "jev_out": 0.0}           # Jev: input only, output free (TypeSafe)


def cost_usd(results: list[dict]) -> dict:
    ci = sum(r.get("claude_usage", {}).get("input_tokens", 0) for r in results)
    co = sum(r.get("claude_usage", {}).get("output_tokens", 0) for r in results)
    ji = sum((u or {}).get("input_tokens") or 0 for r in results for u in r.get("jev_usage", []))
    jev = ji * PRICE_PER_MTOK["jev_in"] / 1e6
    claude = (ci * PRICE_PER_MTOK["claude_in"] + co * PRICE_PER_MTOK["claude_out"]) / 1e6
    return {"claude_input_tokens": ci, "claude_output_tokens": co, "jev_input_tokens": ji,
            "claude_usd": round(claude, 5), "jev_usd": round(jev, 6)}

# ---------------------------------------------------------------------------------------------
# Evaluation against ground truth
# ---------------------------------------------------------------------------------------------

def evaluate(results: list[dict], gt: dict) -> dict:
    """Classification accuracy, plus how well Stage 3 separates wrong fields from right ones.
    A field counts as wrong when its value differs from the reference extraction's value for the same claim."""
    n = len(results)
    type_ok = sum(r["classification"]["doc_type"]["choice"] == gt[r["doc_id"]]["doc_type"] for r in results)
    spec_ok = sum(r["classification"]["specialty"]["choice"] == gt[r["doc_id"]]["specialty"] for r in results)
    urg_err = [abs(r["classification"]["urgency"]["score"] - gt[r["doc_id"]]["urgency"]) for r in results]
    caught = missed = false_alarm = right_ok = 0
    wrong_fields = []
    for r in results:
        ref = {label: _norm(v) for _, label, v in claims_from(MedicalExtraction.model_validate(
            {**gt[r["doc_id"]]["extraction"], "evidence": []}))}
        for f in r.get("fields", []):
            wrong = ref.get(f["field"]) != _norm(f["value"])
            flagged = f["status"] != "accept"
            if wrong:
                wrong_fields.append((r["doc_id"], f["field"], f["value"], f["confidence"]))
            caught += wrong and flagged
            missed += wrong and not flagged
            false_alarm += (not wrong) and flagged
            right_ok += (not wrong) and not flagged
    return {"documents": n, "doc_type_accuracy": round(type_ok / n, 3), "specialty_accuracy": round(spec_ok / n, 3),
            "urgency_mean_abs_error": round(sum(urg_err) / n, 2),
            "wrong_fields_flagged": caught, "wrong_fields_missed": missed,
            "correct_fields_flagged": false_alarm, "correct_fields_accepted": right_ok,
            "wrong_fields": wrong_fields}
