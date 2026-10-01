"""טסטים שרצים בלי רשת. המימושים של מצב live רצים מול ה-SDK האמיתיים (typesafe-sdk ו-anthropic)
עם HTTP מדומה, כך שנבדקים מבנה הבקשות והפענוח של התשובות בלי מפתחות API ובלי חיבור לאינטרנט."""
import json
import sys
from pathlib import Path

import anthropic
import httpx2
import pytest
from typesafe_sdk import TypeSafeClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pipeline as P  # noqa: E402


def fake_jev_handler(seen):
    def handler(request: httpx2.Request) -> httpx2.Response:
        body = json.loads(request.content)
        seen.append((request.url.path, body))
        answers = {}
        for name, q in body["questions"].items():
            if q["type"] == "choice":
                first = next(iter(q["criteria"]))
                answers[name] = {"type": "choice", "choice": first, "confidence": 0.93,
                                 "probabilities": {k: (0.93 if k == first else 0.07 / (len(q["criteria"]) - 1)) for k in q["criteria"]}}
            elif q["type"] == "score":
                answers[name] = {"type": "score", "score": 1.0, "confidence": 0.8,
                                 "legend": {str(i): c for i, c in enumerate(q["criteria"])},
                                 "probabilities": {str(i): (0.8 if i == 1 else 0.2 / (len(q["criteria"]) - 1)) for i in range(len(q["criteria"]))}}
            else:
                answers[name] = {"type": "noul", "noul": 0.97}
        return httpx2.Response(200, json={"model": body["model"], "usage": {"input_tokens": 500, "output_tokens": 0}, "answers": answers})
    return handler


def fake_claude_handler(seen, extraction: dict):
    def handler(request: httpx2.Request) -> httpx2.Response:
        body = json.loads(request.content)
        seen.append((request.url.path, body))
        return httpx2.Response(200, json={
            "id": "msg_test", "type": "message", "role": "assistant", "model": body["model"],
            "content": [{"type": "text", "text": json.dumps(extraction, ensure_ascii=False)}],
            "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 900, "output_tokens": 300}})
    return handler


@pytest.fixture
def doc():
    return next(d for d in P.load_documents() if d.doc_id == "01_discharge_pneumonia")


@pytest.fixture
def reference():
    gt = P.load_ground_truth()["01_discharge_pneumonia"]["extraction"]
    return {**gt, "evidence": [{"field": "icd10_code", "quote": "ICD-10: J18.1"}]}


def live_backends(jev_seen, claude_seen, extraction):
    ts = TypeSafeClient(api_key="test-key", transport=httpx2.MockTransport(fake_jev_handler(jev_seen)))
    cl = anthropic.Anthropic(api_key="test-key",
                             http_client=anthropic.DefaultHttpxClient(transport=httpx2.MockTransport(fake_claude_handler(claude_seen, extraction))))
    return P.LiveJev(client=ts), P.LiveExtractor(client=cl)


def test_live_pipeline_request_shapes(doc, reference):
    jev_seen, claude_seen = [], []
    jev, ext = live_backends(jev_seen, claude_seen, reference)
    rec = P.run_document(doc, jev, ext)

    # שלב 1 ושלב 3 פונים ל-System One עם שאלות נקיות (בלי מפתחות העזר של הדמו)
    assert [p for p, _ in jev_seen] == ["/v1/systemone", "/v1/systemone"]
    stage1, stage3 = jev_seen[0][1], jev_seen[1][1]
    assert stage1["model"] == "jev-latest"
    assert set(stage1["questions"]) == {"doc_type", "specialty", "urgency", "contains_phi"}
    assert stage1["questions"]["urgency"]["criteria"] == P.PROMPTS["he"]["urgency"]
    assert stage1["questions"]["doc_type"]["instructions"] == "איזה סוג של מסמך רפואי זה?"
    assert all(not k.startswith("_") for q in stage3["questions"].values() for k in q)
    assert stage3["state"]["document"] == doc.text and "evidence" not in stage3["state"]["extracted"]
    assert "icd_consistent" in stage3["questions"] and "extraction_quality" in stage3["questions"]

    # שלב 2 מבקש מ-Claude פלט לפי סכמה
    path, body = claude_seen[0]
    assert path == "/v1/messages" and body["model"] == "claude-opus-5-5"
    assert body["output_config"]["format"]["type"] == "json_schema"
    assert body["output_config"]["effort"] == "low"
    assert "icd10_code" in body["output_config"]["format"]["schema"]["properties"]

    # התשובות מפוענחות לרשומת הניתוב
    assert rec["classification"]["doc_type"]["confidence"] == pytest.approx(0.93)
    assert rec["extraction"]["icd10_code"] == "J18.1"
    assert rec["claude_usage"] == {"input_tokens": 900, "output_tokens": 300}
    assert all(f["confidence"] == pytest.approx(0.97) for f in rec["fields"])
    assert rec["route"] == "auto_accept"
    assert rec["jev_usage"] == [{"input_tokens": 500, "output_tokens": 0}] * 2
    assert P.cost_usd([rec])["jev_input_tokens"] == 1000


def test_demo_run_flags_injected_errors():
    mode, jev, ext = P.make_backends("demo")
    res = P.run_all(P.load_documents(), jev, ext, inject=True)
    ev = P.evaluate(res, P.load_ground_truth())
    assert ev["wrong_fields_missed"] == 0 and ev["wrong_fields_flagged"] == 3
    by_id = {r["doc_id"]: r for r in res}
    assert by_id["09_ct_head_negative"]["route"] == "human_review"
    assert by_id["10_admin_physio_invoice"]["route"] == "archive"


def test_routing_thresholds():
    t = P.Ans("choice", choice="lab_report", confidence=0.95)
    assert P.route(t, {"a": 0.95})[0] == "auto_accept"
    assert P.route(t, {"a": 0.95, "b": 0.7})[0] == "quick_review"
    assert P.route(t, {"a": 0.4})[0] == "human_review"
    assert P.route(P.Ans("choice", choice="lab_report", confidence=0.5), {"a": 0.99})[0] == "human_triage"


def test_english_prompts_option(doc, reference):
    """PROMPT_LANG="en" שולח את אותן שאלות באנגלית, כדי להשוות בין השפות בהרצת live."""
    jev_seen, claude_seen = [], []
    jev, ext = live_backends(jev_seen, claude_seen, reference)
    ext.lang = "en"
    P.run_document(doc, jev, ext, lang="en")
    stage1 = jev_seen[0][1]
    assert stage1["questions"]["doc_type"]["instructions"] == "What kind of medical document is this?"
    assert claude_seen[0][1]["system"].startswith("You extract structured data")
    assert set(stage1["questions"]["doc_type"]["criteria"]) == set(P.PROMPTS["he"]["doc_types"])


def test_hebrew_extraction_prompt(doc, reference):
    jev_seen, claude_seen = [], []
    jev, ext = live_backends(jev_seen, claude_seen, reference)
    P.run_document(doc, jev, ext)
    body = claude_seen[0][1]
    assert body["system"].startswith("אתה מחלץ נתונים מובנים")
    assert "סוג המסמך (לפי המסווג)" in body["messages"][0]["content"]
    assert "קוד ICD-10" in json.dumps(body["output_config"]["format"]["schema"], ensure_ascii=False)
