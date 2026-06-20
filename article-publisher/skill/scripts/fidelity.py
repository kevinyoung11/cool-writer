"""Programmatic fidelity check for rewrites.

The rewrite step (LLM) may silently drop or mutate facts. This module extracts
"protected spans" from the source — code/inline-code, URLs, numbers, and
explicitly-listed terms/project names — and verifies they still appear in a
rewritten platform draft. It is deterministic: no model self-grading.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


URL_RE = re.compile(r"https?://[^\s)>\]]+")
# Significant numeric facts: must carry a unit/% OR be >=3 digits (money,
# counts, versions). Bare 1-2 digit numbers (list markers, "3 秒") are noise.
NUM_RE = re.compile(r"\d[\d,\.]*\s*(?:%|万|亿|千|k|K|w|W)|\d{3,}[\d,\.]*")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
# Capture the fence language tag so we can tell real code from prose diagrams.
FENCE_RE = re.compile(r"```([^\n`]*)\n(.*?)```", re.DOTALL)
# Languages whose fenced content is genuine code and must survive verbatim.
CODE_LANGS = {
    "python", "py", "js", "javascript", "ts", "typescript", "bash", "sh",
    "shell", "zsh", "json", "yaml", "yml", "html", "css", "go", "rust",
    "java", "c", "cpp", "sql", "diff", "toml", "ini", "xml", "jsx", "tsx",
}
# Inline code that is just a Chinese/prose phrase (no code-ish chars) is also
# treated as prose, not a protected span.
CODEISH_RE = re.compile(r"[A-Za-z0-9_./\\:@\-]")


@dataclass
class FidelityReport:
    total: int = 0
    preserved: int = 0
    missing: list[dict[str, Any]] = field(default_factory=list)

    @property
    def score(self) -> float:
        return 1.0 if self.total == 0 else self.preserved / self.total

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_protected_spans": self.total,
            "preserved": self.preserved,
            "missing": self.missing,
            "score": round(self.score, 4),
            "passed": self.passed,
        }

    @property
    def passed(self) -> bool:
        # Code and URLs must be 100% preserved; numbers/terms allow none missing
        # either (this is a publishable-fidelity gate, not a fuzzy one).
        return len(self.missing) == 0


def extract_protected_spans(source_md: str, extra_terms: list[str] | None = None
                            ) -> dict[str, list[str]]:
    spans: dict[str, list[str]] = {"code": [], "urls": [], "numbers": [], "terms": []}

    for lang, body in FENCE_RE.findall(source_md):
        lang = lang.strip().lower()
        body = body.strip()
        # Only protect genuine code fences. Prose/diagram fences (```text,
        # untagged) are reflowed by the rewrite and must NOT be required verbatim.
        if body and lang in CODE_LANGS:
            spans["code"].append(body)
    no_fence = FENCE_RE.sub(" ", source_md)

    for m in INLINE_CODE_RE.findall(no_fence):
        m = m.strip()
        # inline code that contains code-ish chars (commands, identifiers, paths)
        if m and CODEISH_RE.search(m):
            spans["code"].append(m)
    for u in URL_RE.findall(no_fence):
        spans["urls"].append(u.rstrip(".,;)"))
    for n in NUM_RE.findall(no_fence):
        n = n.strip()
        if n:
            spans["numbers"].append(n)

    # Only protect user-supplied terms that actually appear in the source —
    # requiring a term the source never had would be a false positive.
    src_norm = _normalize(source_md)
    for t in (extra_terms or []):
        t = t.strip()
        if t and (t in source_md or _normalize(t) in src_norm):
            spans["terms"].append(t)

    # de-dup, keep order
    for k in spans:
        seen, uniq = set(), []
        for v in spans[k]:
            if v not in seen:
                seen.add(v)
                uniq.append(v)
        spans[k] = uniq
    return spans


def _normalize(s: str) -> str:
    return re.sub(r"\s+", "", s)


def check_fidelity(protected: dict[str, list[str]], rewritten_md: str
                   ) -> FidelityReport:
    rep = FidelityReport()
    hay_raw = rewritten_md
    hay_norm = _normalize(rewritten_md)
    for category, items in protected.items():
        for item in items:
            rep.total += 1
            present = item in hay_raw or _normalize(item) in hay_norm
            # code blocks: compare normalized (whitespace-insensitive)
            if not present and category == "code":
                present = _normalize(item) in hay_norm
            if present:
                rep.preserved += 1
            else:
                rep.missing.append({"category": category, "span": item[:120]})
    return rep


def run(source_path: str, rewritten_path: str, terms_path: str | None,
        out_path: str) -> dict[str, Any]:
    src = Path(source_path).read_text(encoding="utf-8")
    rew = Path(rewritten_path).read_text(encoding="utf-8")
    extra: list[str] = []
    if terms_path and Path(terms_path).exists():
        try:
            data = json.loads(Path(terms_path).read_text(encoding="utf-8"))
            if isinstance(data, dict):
                extra = data.get("terms", []) + data.get("project_names", [])
            elif isinstance(data, list):
                extra = data
        except json.JSONDecodeError:
            pass
    protected = extract_protected_spans(src, extra)
    report = check_fidelity(protected, rew)
    payload = {
        "source": source_path,
        "rewritten": rewritten_path,
        "protected_spans": protected,
        "result": report.to_dict(),
    }
    Path(out_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    return payload


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--rewritten", required=True)
    ap.add_argument("--terms")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    r = run(a.source, a.rewritten, a.terms, a.out)
    print(json.dumps(r["result"], ensure_ascii=False, indent=2))
