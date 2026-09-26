"""Run gold-set eval against the live graph. Requires OpenAI and ingested Chroma."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests" / "eval" / "cases.json"
HASH_PATH = ROOT / "tests" / "eval" / "profile_hash.txt"
REPORT_PATH = ROOT / "tests" / "eval" / "report.json"
PROFILE_DIR = ROOT / "data" / "profile"

_ABSTAIN_HINTS = ("모른", "모릅", "없", "확인", "기억", "모르", "없어", "모름")


def profile_hash() -> str:
    """SHA-256 of bio.md then projects.md bytes."""
    parts = [
        (PROFILE_DIR / "bio.md").read_bytes(),
        (PROFILE_DIR / "projects.md").read_bytes(),
    ]
    return hashlib.sha256(b"".join(parts)).hexdigest()


def assert_profile_frozen() -> None:
    """Exit 2 when profile files drifted from the frozen hash."""
    if not HASH_PATH.is_file():
        print(f"missing hash file: {HASH_PATH}", file=sys.stderr)
        raise SystemExit(2)
    expected = HASH_PATH.read_text(encoding="utf-8").strip()
    actual = profile_hash()
    if actual != expected:
        print(
            "profile hash mismatch. Update tests/eval/profile_hash.txt and "
            "cases after editing data/profile/, then run scripts/ingest.py.",
            file=sys.stderr,
        )
        print(f"expected: {expected}", file=sys.stderr)
        print(f"actual:   {actual}", file=sys.stderr)
        raise SystemExit(2)


def _contains(haystack: str, needle: str) -> bool:
    return needle.casefold() in haystack.casefold()


def score_case(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Rule-score one case from graph state fields."""
    answer = str(result.get("answer") or "")
    intent = str(result.get("intent") or "")
    context = "\n".join(result.get("context") or [])
    search_query = str(result.get("search_query") or "")

    intent_ok = intent == case["expected_intent"]
    include_ok = all(_contains(answer, item) for item in case.get("must_include") or [])
    exclude_ok = all(
        not _contains(answer, item) for item in case.get("must_not_include") or []
    )

    expect_abstain = bool(case.get("expect_abstain"))
    abstain_ok = True
    if expect_abstain:
        has_hint = any(hint in answer for hint in _ABSTAIN_HINTS)
        abstain_ok = has_hint and exclude_ok

    context_keys = case.get("context_must_include") or []
    followup_ok = True
    if context_keys:
        blob = f"{context}\n{answer}\n{search_query}"
        followup_ok = all(_contains(blob, key) for key in context_keys)

    return {
        "id": case["id"],
        "category": case["category"],
        "intent_ok": intent_ok,
        "include_ok": include_ok,
        "exclude_ok": exclude_ok,
        "abstain_ok": abstain_ok,
        "followup_ok": followup_ok,
        "intent": intent,
        "search_query": search_query,
        "answer": answer,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate pass rates used by the gate."""
    n = len(rows) or 1
    intent_acc = sum(1 for row in rows if row["intent_ok"]) / n
    exclude_fail = sum(1 for row in rows if not row["exclude_ok"])
    include_acc = sum(1 for row in rows if row["include_ok"]) / n

    abstain_rows = [row for row in rows if row["category"] == "unknown"]
    followup_rows = [row for row in rows if row["category"] == "followup"]
    abstain_acc = (
        sum(1 for row in abstain_rows if row["abstain_ok"]) / len(abstain_rows)
        if abstain_rows
        else 1.0
    )
    followup_acc = (
        sum(1 for row in followup_rows if row["followup_ok"]) / len(followup_rows)
        if followup_rows
        else 1.0
    )

    passed = (
        intent_acc >= 0.90
        and exclude_fail == 0
        and abstain_acc >= 0.80
        and followup_acc >= 0.80
    )
    return {
        "intent_accuracy": round(intent_acc, 4),
        "include_accuracy": round(include_acc, 4),
        "exclude_violations": exclude_fail,
        "abstain_accuracy": round(abstain_acc, 4),
        "followup_accuracy": round(followup_acc, 4),
        "passed": passed,
        "n_cases": len(rows),
    }


def main() -> None:
    """Load cases, run the graph, write report, exit 1 on gate fail."""
    assert_profile_frozen()
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    # Import after hash check so drift fails without needing OpenAI.
    from ml.graph.builder import build_graph

    graph = build_graph()
    rows: list[dict[str, Any]] = []
    for case in cases:
        result = graph.invoke(
            {
                "question": case["question"],
                "history": case.get("history") or [],
                "intent": "",
                "search_query": "",
                "context": [],
                "answer": "",
            }
        )
        rows.append(score_case(case, result))
        status = "ok" if rows[-1]["intent_ok"] and rows[-1]["exclude_ok"] else "fail"
        print(f"[{status}] {case['id']} intent={rows[-1]['intent']}")

    summary = summarize(rows)
    report = {"summary": summary, "cases": rows}
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {REPORT_PATH}")
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
