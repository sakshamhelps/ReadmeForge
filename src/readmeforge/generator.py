"""README generation from a project-information dictionary. Pure functions, no I/O."""
from __future__ import annotations
import re

FIELDS = {
    "name": "Project name (required)", "tagline": "One-line summary", "description": "Longer description (paragraph)",
    "features": "List of feature strings", "requirements": "List of requirements/prerequisites",
    "install": "Installation commands (string or list of lines)", "usage": "Usage instructions/commands (string or list)",
    "examples": "List of {title, code, language} objects", "configuration": "Configuration notes (string)",
    "license": "SPDX licence id, e.g. MIT", "license_holder": "Copyright holder", "year": "Copyright year",
    "author": "Author or organisation", "repo_url": "Repository URL (text link only)", "contact": "Contact or support info",
    "contributing": "Contributing notes (string); section omitted if empty", "acknowledgements": "List of strings",
    "roadmap": "List of planned items", "language": "Primary language for code fences, e.g. bash",
}
STYLES = ("minimal", "standard", "full")

class ProjectInfoError(ValueError):
    pass

def _as_list(v):
    if v is None or v == "": return []
    if isinstance(v, str): return [s for s in v.splitlines() if s.strip()]
    if isinstance(v, (list, tuple)): return [str(x) for x in v if str(x).strip()]
    raise ProjectInfoError(f"expected a string or list, got {type(v).__name__}")

def validate(info: dict) -> list[str]:
    """Return a list of problems (empty if OK). Unknown keys are reported to catch typos."""
    problems = []
    if not isinstance(info, dict): return ["project info must be a JSON object"]
    name = info.get("name")
    if not isinstance(name, str) or not name.strip(): problems.append("'name' is required and must be a non-empty string")
    for k in info:
        if k not in FIELDS: problems.append(f"unknown field '{k}'")
    for k in ("features", "requirements", "acknowledgements", "roadmap", "examples"):
        if k in info and not isinstance(info[k], (list, str)): problems.append(f"'{k}' must be a list")
    for i, ex in enumerate(info.get("examples") or []):
        if not isinstance(ex, dict) or not ex.get("code"): problems.append(f"examples[{i}] needs at least a 'code' value")
    y = info.get("year")
    if y is not None and not re.fullmatch(r"\d{4}(-\d{4})?", str(y)): problems.append("'year' must look like 2026 or 2024-2026")
    return problems

def _fence(code_lines, lang):
    body = "\n".join(code_lines)
    fence = "```" if "```" not in body else "````"
    return f"{fence}{lang}\n{body}\n{fence}"

def _slug(title): return re.sub(r"[^a-z0-9 -]", "", title.lower()).strip().replace(" ", "-")

def generate(info: dict, style: str = "standard", toc: bool | None = None) -> str:
    if style not in STYLES: raise ProjectInfoError(f"unknown style '{style}' (choose from {', '.join(STYLES)})")
    problems = validate(info)
    if problems: raise ProjectInfoError("; ".join(problems))
    lang = info.get("language") or "bash"
    name = info["name"].strip(); sections: list[tuple[str, str]] = []
    def add(title, body):
        if body and body.strip(): sections.append((title, body.strip()))
    feats = _as_list(info.get("features"))
    add("Features", "\n".join(f"- {f}" for f in feats))
    add("Requirements", "\n".join(f"- {r}" for r in _as_list(info.get("requirements"))))
    inst = _as_list(info.get("install")); add("Installation", _fence(inst, lang) if inst else "")
    use = _as_list(info.get("usage")); add("Usage", _fence(use, lang) if use else "")
    if style != "minimal":
        ex_parts = []
        for ex in info.get("examples") or []:
            title = ex.get("title"); code = _fence(_as_list(ex["code"]), ex.get("language") or lang)
            ex_parts.append((f"**{title}**\n\n" if title else "") + code)
        add("Examples", "\n\n".join(ex_parts))
        add("Configuration", str(info.get("configuration") or ""))
    if style == "full":
        add("Roadmap", "\n".join(f"- [ ] {r}" for r in _as_list(info.get("roadmap"))))
    if style != "minimal":
        add("Contributing", str(info.get("contributing") or ""))
    if style == "full":
        add("Acknowledgements", "\n".join(f"- {a}" for a in _as_list(info.get("acknowledgements"))))
        add("Contact", str(info.get("contact") or ""))
    lic = info.get("license")
    if lic:
        holder = info.get("license_holder") or info.get("author")
        yr = info.get("year")
        line = f"Distributed under the {lic} License."
        if holder: line += f" Copyright (c) {yr + ' ' if yr else ''}{holder}."
        line += " See `LICENSE` for details."
        add("License", line)
    out = [f"# {name}", ""]
    if info.get("tagline"): out += [f"> {info['tagline'].strip()}", ""]
    if info.get("description"): out += [str(info["description"]).strip(), ""]
    if info.get("repo_url"): out += [f"Repository: {info['repo_url']}", ""]
    use_toc = (style == "full") if toc is None else toc
    if use_toc and len(sections) > 2:
        out += ["## Table of contents", ""] + [f"- [{t}](#{_slug(t)})" for t, _ in sections] + [""]
    for t, b in sections: out += [f"## {t}", "", b, ""]
    return "\n".join(out).rstrip() + "\n"

def template_info() -> dict:
    return {"name": "my-project", "tagline": "What it does in one line", "description": "A short paragraph explaining the problem it solves.",
            "features": ["Feature one", "Feature two"], "requirements": ["Python 3.10+"],
            "install": ["pip install my-project"], "usage": ["my-project --help"],
            "examples": [{"title": "Basic example", "code": "my-project run input.txt", "language": "bash"}],
            "license": "MIT", "license_holder": "Your Name or Org", "year": "2026", "author": "Your Name or Org"}
