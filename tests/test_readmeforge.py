import io, json, os, sys, tempfile, unittest, contextlib
import _path  # noqa
from readmeforge.cli import main
from readmeforge.generator import generate, validate, template_info, ProjectInfoError
from readmeforge.detect import detect

def run(argv, stdin=None):
    o, e = io.StringIO(), io.StringIO(); old = sys.stdin
    if stdin is not None: sys.stdin = io.StringIO(stdin)
    try:
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
            try: c = main(argv)
            except SystemExit as x: c = x.code
    finally: sys.stdin = old
    return c, o.getvalue(), e.getvalue()

class T(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup); self.d = t.name
    def p(self, n): return os.path.join(self.d, n)

    def test_generate_standard(self):
        md = generate(template_info())
        for s in ("# my-project", "> What it does", "## Features", "- Feature one", "## Installation", "```bash\npip install my-project\n```",
                  "## Examples", "**Basic example**", "## License", "Distributed under the MIT License. Copyright (c) 2026 Your Name or Org."):
            self.assertIn(s, md)
        self.assertNotIn("## Roadmap", md)
    def test_styles(self):
        i = {**template_info(), "roadmap": ["x"], "contact": "me@x"}
        mini, full = generate(i, "minimal"), generate(i, "full")
        self.assertNotIn("## Examples", mini); self.assertNotIn("## Contributing", mini)
        self.assertIn("## Roadmap", full); self.assertIn("## Table of contents", full); self.assertIn("- [ ] x", full)
        with self.assertRaises(ProjectInfoError): generate(i, "fancy")
    def test_minimum_input_and_validation(self):
        self.assertEqual(generate({"name": "x"}), "# x\n")
        for bad in ({}, {"name": " "}, {"name": 5}, {"name": "x", "bogus": 1}, {"name": "x", "year": "26"}, {"name": "x", "examples": [{"title": "t"}]}, []):
            self.assertTrue(validate(bad), bad)
            with self.assertRaises(ProjectInfoError): generate(bad)
    def test_code_fence_escaping_and_multiline_strings(self):
        md = generate({"name": "x", "usage": "```nested```\nline2"}); self.assertIn("````", md)
    def test_unicode(self): self.assertIn("日本語 ☕", generate({"name": "日本語 ☕"}))
    def test_init_generate_roundtrip_and_overwrite_protection(self):
        cfg, out = self.p("c.json"), self.p("README.md")
        self.assertEqual(run(["init", "-o", cfg])[0], 0); self.assertEqual(run(["init", "-o", cfg])[0], 2); self.assertEqual(run(["init", "-o", cfg, "--force"])[0], 0)
        self.assertEqual(run(["generate", "-c", cfg, "-o", out])[0], 0)
        original = open(out).read()
        c, _, e = run(["generate", "-c", cfg, "-o", out, "--style", "minimal"]); self.assertEqual(c, 2); self.assertIn("already exists", e)
        self.assertEqual(open(out).read(), original)
        self.assertEqual(run(["generate", "-c", cfg, "-o", out, "--force", "--style", "minimal"])[0], 0)
    def test_stdout_output(self):
        cfg = self.p("c.json"); open(cfg, "w").write('{"name":"z"}'); self.assertEqual(run(["generate", "-c", cfg, "-o", "-"])[1], "# z\n")
    def test_bad_config_files(self):
        self.assertEqual(run(["generate", "-c", self.p("nope.json")])[0], 2)
        bad = self.p("b.json"); open(bad, "w").write("{oops"); c, _, e = run(["generate", "-c", bad]); self.assertEqual(c, 2); self.assertIn("invalid JSON", e)
        empty = self.p("e.json"); open(empty, "w").write(""); self.assertEqual(run(["generate", "-c", empty])[0], 2)
        self.assertEqual(run(["generate", "-c", self.d])[0], 2)
        self.assertEqual(run(["generate"])[0], 2)
    def test_validate_command(self):
        ok, bad = self.p("o.json"), self.p("b.json"); open(ok, "w").write('{"name":"x"}'); open(bad, "w").write('{"nme":"x"}')
        self.assertEqual(run(["validate", ok])[0], 0); c, o, _ = run(["validate", bad]); self.assertEqual(c, 1); self.assertIn("unknown field 'nme'", o)
    def test_detect_package_json_and_pyproject(self):
        open(self.p("package.json"), "w").write('{"name":"pkg","description":"d","license":"MIT"}')
        self.assertEqual(detect(self.d)["name"], "pkg")
        with tempfile.TemporaryDirectory() as e:
            self.assertEqual(detect(e)["name"], os.path.basename(e))
            open(os.path.join(e, "package.json"), "w").write("{broken"); self.assertEqual(detect(e)["name"], os.path.basename(e))
        out = self.p("R.md"); self.assertEqual(run(["generate", "--detect", self.d, "-o", out])[0], 0); self.assertIn("npm install pkg", open(out).read())
        self.assertEqual(run(["generate", "--detect", self.p("none")])[0], 2)
    def test_detect_without_tomllib_falls_back_to_folder_name(self):
        """Simulates Python 3.10 (no tomllib)."""
        import readmeforge.detect as dm
        with open(self.p("pyproject.toml"), "w") as f: f.write('[project]\nname="fromtoml"\n')
        old = dm.tomllib; dm.tomllib = None
        try: info = dm.detect(self.d)
        finally: dm.tomllib = old
        self.assertEqual(info["name"], os.path.basename(self.d))

    def test_interactive(self):
        answers = "proj\ntag\ndesc\nf1\n\n\ni1\n\n\nMIT\nBYREX\n"
        out = self.p("R.md"); c, _, _ = run(["generate", "--interactive", "-o", out], stdin=answers); self.assertEqual(c, 0)
        t = open(out).read(); self.assertIn("# proj", t); self.assertIn("- f1", t); self.assertIn("Copyright (c) BYREX", t)
        self.assertEqual(run(["generate", "--interactive", "-o", self.p("x.md")], stdin="only-name\n")[0], 2)
    def test_unwritable_output_dir(self):
        cfg = self.p("c.json"); open(cfg, "w").write('{"name":"z"}'); self.assertEqual(run(["generate", "-c", cfg, "-o", self.p("no/such/R.md")])[0], 2)
    def test_fields(self): self.assertIn("license_holder", run(["fields"])[1])

if __name__ == "__main__": unittest.main()
