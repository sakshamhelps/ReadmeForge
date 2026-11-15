"""READMEForge CLI."""
from __future__ import annotations
import argparse, json, os, sys
from . import __version__
from .generator import generate, validate, template_info, ProjectInfoError, STYLES, FIELDS
from .detect import detect

def load_info(path):
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except FileNotFoundError: raise ProjectInfoError(f"file not found: {path}")
    except PermissionError: raise ProjectInfoError(f"permission denied: {path}")
    except IsADirectoryError: raise ProjectInfoError(f"is a directory: {path}")
    except json.JSONDecodeError as e: raise ProjectInfoError(f"invalid JSON in {path}: {e.msg} (line {e.lineno})")
    except UnicodeDecodeError: raise ProjectInfoError(f"not valid UTF-8: {path}")

def write(path, text, force):
    if os.path.exists(path) and not force:
        raise ProjectInfoError(f"{path} already exists; use --force to overwrite")
    try:
        with open(path, "w", encoding="utf-8", newline="\n") as f: f.write(text)
    except OSError as e: raise ProjectInfoError(f"cannot write {path}: {e.strerror}")

def ask(prompt, default=""):
    s = input(f"{prompt}{f' [{default}]' if default else ''}: ").strip()
    return s or default

def interactive(base=None):
    info = dict(base or {})
    info["name"] = ask("Project name", info.get("name", ""))
    info["tagline"] = ask("One-line tagline", info.get("tagline", ""))
    info["description"] = ask("Description", info.get("description", ""))
    for key, label in (("features", "Features"), ("requirements", "Requirements"), ("install", "Install commands"), ("usage", "Usage commands")):
        print(f"{label} (one per line, blank line to finish):")
        items = []
        while (line := input("  > ").strip()): items.append(line)
        if items: info[key] = items
    info["license"] = ask("License (SPDX id)", info.get("license", "MIT"))
    info["license_holder"] = ask("Copyright holder", info.get("license_holder", info.get("author", "")))
    return {k: v for k, v in info.items() if v}

def build_parser():
    p = argparse.ArgumentParser(prog="readmeforge", description="Generate professional README.md files from project information.")
    p.add_argument("--version", action="version", version=f"readmeforge {__version__}")
    sub = p.add_subparsers(dest="command", required=True)
    i = sub.add_parser("init", help="write a starter project-info JSON file")
    i.add_argument("-o", "--output", default="readmeforge.json"); i.add_argument("--force", action="store_true")
    g = sub.add_parser("generate", help="generate README.md")
    g.add_argument("-c", "--config", help="project-info JSON file")
    g.add_argument("--detect", metavar="DIR", help="pre-fill from package.json / pyproject.toml in DIR (config values win)")
    g.add_argument("--interactive", action="store_true", help="answer prompts in the terminal")
    g.add_argument("--style", choices=STYLES, default="standard")
    g.add_argument("--toc", action="store_true", help="force a table of contents")
    g.add_argument("-o", "--output", default="README.md", help="output file, or '-' for stdout (default README.md)")
    g.add_argument("--force", action="store_true", help="overwrite the output file if it exists")
    v = sub.add_parser("validate", help="check a project-info JSON file"); v.add_argument("config")
    sub.add_parser("fields", help="list supported fields")
    return p

def _main(argv=None) -> int:
    a = build_parser().parse_args(argv)
    try:
        if a.command == "fields":
            for k, v in FIELDS.items(): print(f"{k:18}{v}")
            return 0
        if a.command == "init":
            write(a.output, json.dumps(template_info(), indent=2) + "\n", a.force)
            print(f"wrote {a.output}; edit it, then run: readmeforge generate -c {a.output}"); return 0
        if a.command == "validate":
            problems = validate(load_info(a.config))
            for p in problems: print(f"- {p}")
            print("valid" if not problems else f"{len(problems)} problem(s)")
            return 0 if not problems else 1
        info = {}
        if a.detect:
            if not os.path.isdir(a.detect): raise ProjectInfoError(f"not a directory: {a.detect}")
            info.update(detect(a.detect))
        if a.config: info.update(load_info(a.config))
        if a.interactive:
            try: info = interactive(info)
            except EOFError: raise ProjectInfoError("input ended before all answers were given")
        if not info: raise ProjectInfoError("no project information: use --config, --detect or --interactive")
        text = generate(info, a.style, True if a.toc else None)
        if a.output == "-": sys.stdout.write(text)
        else:
            write(a.output, text, a.force); print(f"wrote {a.output}")
        return 0
    except ProjectInfoError as e:
        print(f"readmeforge: error: {e}", file=sys.stderr); return 2
    except KeyboardInterrupt:
        print("\nreadmeforge: cancelled", file=sys.stderr); return 130


def main(argv=None) -> int:
    """Entry point. Exits quietly if the output pipe is closed (e.g. `| head`)."""
    try:
        return _main(argv)
    except BrokenPipeError:
        try:
            sys.stdout = open(os.devnull, "w")
        except OSError:
            pass
        return 0
