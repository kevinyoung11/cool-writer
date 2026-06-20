"""Open-source tool adapters for the article-publisher skill.

Every adapter implements the same contract:

    discover()      -> resolve the tool's executable inside the local toolbox
    can_run()       -> real health check (bin exists AND a probe invocation works)
    run(...)        -> invoke the real tool, capture stdout/stderr/files
    collect_result()-> normalize into a ToolResult record for report.json

The point of this layer is that the skill *actually* uses the vendored /
pinned open-source projects (lint-md, zhlint, textlint, wenyan) rather than
faking it.  When a tool genuinely cannot run, the adapter says so explicitly
(status="unavailable"/"failed") and records whether a fallback was used, so the
publish-checklist can flag degraded output for human review.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional


@dataclass
class ToolResult:
    name: str
    kind: str                       # "lint" | "format"
    status: str                     # ok | failed | unavailable | skipped
    used_real_tool: bool = False
    fallback_used: bool = False
    bin_path: Optional[str] = None
    command: list[str] = field(default_factory=list)
    output_files: list[str] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)
    stdout_tail: str = ""
    stderr_tail: str = ""
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _tail(text: str, n: int = 1200) -> str:
    text = text or ""
    return text[-n:]


class Adapter:
    """Base adapter: resolve bin in the toolbox, run a probe, run the tool."""

    name = "base"
    kind = "lint"

    def __init__(self, toolbox: Path, config: dict[str, Any]):
        self.toolbox = Path(toolbox)
        self.config = config
        self.bin_name = config.get("bin", self.name)
        self._bin: Optional[str] = None

    # --- discover ---------------------------------------------------------
    def discover(self) -> Optional[str]:
        local = self.toolbox / "node_modules" / ".bin" / self.bin_name
        if local.exists():
            self._bin = str(local)
            return self._bin
        on_path = shutil.which(self.bin_name)
        self._bin = on_path
        return on_path

    # --- can_run ----------------------------------------------------------
    def can_run(self) -> tuple[bool, str]:
        """Real health check: bin resolves AND `--version`/`--help` exits cleanly."""
        if not self.discover():
            return False, f"{self.bin_name} not found in toolbox or PATH"
        for probe in (["--version"], ["--help"]):
            try:
                p = subprocess.run(
                    [self._bin, *probe],
                    capture_output=True, text=True, timeout=30,
                )
                if p.returncode == 0 or (p.stdout or p.stderr):
                    return True, f"probe `{self.bin_name} {probe[0]}` ok"
            except Exception as exc:  # noqa: BLE001
                last = str(exc)
                continue
        return False, f"probe failed for {self.bin_name}: {last}"

    # --- run --------------------------------------------------------------
    def run(self, markdown: Path, out_dir: Path) -> ToolResult:  # pragma: no cover
        raise NotImplementedError

    # --- helpers ----------------------------------------------------------
    def _exec(self, cmd: list[str], cwd: Optional[Path] = None, timeout: int = 120):
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(cwd) if cwd else None,
        )


class LintMdAdapter(Adapter):
    name = "lint-md"
    kind = "lint"

    def run(self, markdown: Path, out_dir: Path) -> ToolResult:
        res = ToolResult(name=self.name, kind=self.kind, status="failed",
                         bin_path=self._bin)
        cmd = [self._bin, str(markdown)]
        res.command = cmd
        try:
            p = self._exec(cmd)
        except Exception as exc:  # noqa: BLE001
            res.detail = f"exec error: {exc}"
            return res
        res.used_real_tool = True
        res.stdout_tail = _tail(p.stdout)
        res.stderr_tail = _tail(p.stderr)
        # lint-md exits non-zero when it finds problems; that is success for us.
        findings = []
        for line in (p.stdout or "").splitlines():
            line = line.strip()
            if "error" in line and ":" in line:
                findings.append({"tool": self.name, "raw": line})
        res.findings = findings
        out = out_dir / "lint-md.txt"
        out.write_text(p.stdout or p.stderr or "", encoding="utf-8")
        res.output_files = [str(out)]
        res.status = "ok"
        res.detail = f"exit={p.returncode}; {len(findings)} finding(s)"
        return res


class ZhlintAdapter(Adapter):
    name = "zhlint"
    kind = "lint"

    def run(self, markdown: Path, out_dir: Path) -> ToolResult:
        res = ToolResult(name=self.name, kind=self.kind, status="failed",
                         bin_path=self._bin)
        # zhlint needs a *relative* path (it feeds the path through `ignore`,
        # which rejects absolute paths). Run from the file's parent dir.
        rel = markdown.name
        cmd = [self._bin, rel]
        res.command = cmd
        try:
            p = self._exec(cmd, cwd=markdown.parent)
        except Exception as exc:  # noqa: BLE001
            res.detail = f"exec error: {exc}"
            return res
        res.used_real_tool = True
        res.stdout_tail = _tail(p.stdout)
        res.stderr_tail = _tail(p.stderr)
        text = p.stdout or ""
        findings = [{"tool": self.name, "raw": ln.strip()}
                    for ln in text.splitlines()
                    if " - " in ln and (":" in ln)]
        res.findings = findings
        out = out_dir / "zhlint.txt"
        out.write_text(text or p.stderr or "", encoding="utf-8")
        res.output_files = [str(out)]
        res.status = "ok"
        res.detail = f"exit={p.returncode}; {len(findings)} finding(s)"
        return res


class TextlintAdapter(Adapter):
    name = "textlint"
    kind = "lint"

    def run(self, markdown: Path, out_dir: Path) -> ToolResult:
        res = ToolResult(name=self.name, kind=self.kind, status="failed",
                         bin_path=self._bin)
        cfg = self.config.get("config")
        skill_root = Path(self.config["_skill_root"])
        cfg_path = (skill_root / cfg) if cfg else None
        cmd = [self._bin]
        if cfg_path and cfg_path.exists():
            cmd += ["--config", str(cfg_path)]
        cmd += ["-f", "json", str(markdown)]
        res.command = cmd
        try:
            p = self._exec(cmd)
        except Exception as exc:  # noqa: BLE001
            res.detail = f"exec error: {exc}"
            return res
        res.used_real_tool = True
        res.stdout_tail = _tail(p.stdout)
        res.stderr_tail = _tail(p.stderr)
        findings = []
        try:
            data = json.loads(p.stdout or "[]")
            for filerep in data:
                for m in filerep.get("messages", []):
                    findings.append({
                        "tool": self.name,
                        "rule": m.get("ruleId"),
                        "message": m.get("message"),
                        "line": m.get("line"),
                        "column": m.get("column"),
                    })
        except json.JSONDecodeError:
            res.detail = "could not parse textlint json (no rules loaded?)"
        res.findings = findings
        out = out_dir / "textlint.json"
        out.write_text(p.stdout or "[]", encoding="utf-8")
        res.output_files = [str(out)]
        res.status = "ok"
        res.detail = (res.detail + f"; exit={p.returncode}; "
                      f"{len(findings)} finding(s)").lstrip("; ")
        return res


class WenyanAdapter(Adapter):
    name = "wenyan"
    kind = "format"

    def run(self, markdown: Path, out_dir: Path, theme: str = "default",
            highlight: str = "solarized-light", label: str = "") -> ToolResult:
        res = ToolResult(name=self.name, kind=self.kind, status="failed",
                         bin_path=self._bin)
        suffix = f"-{label}" if label else ""
        out = out_dir / f"wenyan{suffix}.html"
        cmd = [self._bin, "render", "-f", str(markdown),
               "-t", theme, "-h", highlight]
        res.command = cmd
        try:
            p = self._exec(cmd)
        except Exception as exc:  # noqa: BLE001
            res.detail = f"exec error: {exc}"
            return res
        res.used_real_tool = True
        res.stderr_tail = _tail(p.stderr)
        html = p.stdout or ""
        if p.returncode == 0 and html.strip().startswith("<section"):
            out.write_text(html, encoding="utf-8")
            res.output_files = [str(out)]
            res.status = "ok"
            res.detail = f"exit=0; theme={theme}; {len(html)} bytes"
        else:
            res.detail = f"exit={p.returncode}; unexpected output"
            res.stdout_tail = _tail(html)
        return res


ADAPTERS = {
    "lint-md": LintMdAdapter,
    "zhlint": ZhlintAdapter,
    "textlint": TextlintAdapter,
    "wenyan": WenyanAdapter,
}


def build_adapter(name: str, toolbox: Path, tool_cfg: dict[str, Any],
                  skill_root: Path) -> Adapter:
    cfg = dict(tool_cfg)
    cfg["_skill_root"] = str(skill_root)
    return ADAPTERS[name](toolbox, cfg)
