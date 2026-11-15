# READMEForge

Generate professional `README.md` files from project information you provide: a JSON file, interactive prompts, or details auto-detected from `package.json` / `pyproject.toml`. Fully offline, standard library only.

## Install

Python 3.10+ (auto-detecting from `pyproject.toml` needs Python 3.11+; everything else works on 3.10).

```
pip install .
# or: PYTHONPATH=src python -m readmeforge --help
```

## Usage

```
readmeforge init [-o readmeforge.json]            # write a starter project-info file
readmeforge generate -c readmeforge.json          # create README.md
readmeforge generate --interactive                # answer prompts in the terminal
readmeforge generate --detect . -c extra.json     # pre-fill from manifests; config values win
readmeforge validate readmeforge.json             # check a project-info file
readmeforge fields                                # list supported fields
```

Options for `generate`: `--style minimal|standard|full`, `--toc`, `-o FILE` (`-` for stdout), `--force`.

- **minimal**: title, summary, features, requirements, install, usage, licence.
- **standard** (default): adds examples, configuration and (if you supply text) contributing.
- **full**: adds a table of contents, roadmap, acknowledgements and contact.

Sections with no information are **omitted**, never filled with placeholder text, so the README only says what you told it. An existing README is never overwritten unless you pass `--force`.

See `examples/project.json` for a complete input and `examples/README.generated.md` for its output.

Exit codes: `0` success, `1` validation problems (`validate`), `2` error.

## Project-info fields

Run `readmeforge fields`. Only `name` is required. Unknown fields are rejected so typos are caught.

## Limitations

- It writes the README structure and your text; it cannot know whether your install commands work. Review before publishing.
- No badges are generated (they would link to external services).
- English section headings only.

## Tests

```
python -m unittest discover -s tests -v
```

## Licence

MIT, Copyright (c) 2026 BYREX. No third-party dependencies.

The MIT licence covers the code only. The BYREX name and branding are not licensed for use by forks: see [TRADEMARK.md](TRADEMARK.md).
