"""Best-effort extraction of project info from existing manifests (local files only)."""
from __future__ import annotations
import json, os
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    tomllib = None

def detect(directory: str) -> dict:
    info: dict = {}
    pj = os.path.join(directory, "package.json")
    pp = os.path.join(directory, "pyproject.toml")
    try:
        if os.path.isfile(pj):
            with open(pj, encoding="utf-8") as fh: d = json.load(fh)
            info.update({"name": d.get("name"), "description": d.get("description"), "license": d.get("license") if isinstance(d.get("license"), str) else None})
            info["install"] = [f"npm install {d['name']}"] if d.get("name") else []
        elif os.path.isfile(pp) and tomllib:
            with open(pp, "rb") as fh: d = tomllib.load(fh).get("project", {})
            lic = d.get("license"); lic = lic.get("text") if isinstance(lic, dict) else lic
            info.update({"name": d.get("name"), "description": d.get("description"), "license": lic})
            if d.get("name"): info["install"] = [f"pip install {d['name']}"]
            if d.get("requires-python"): info["requirements"] = [f"Python {d['requires-python']}"]
    except (OSError, ValueError, KeyError):
        pass
    if not info.get("name"): info["name"] = os.path.basename(os.path.abspath(directory))
    return {k: v for k, v in info.items() if v}
