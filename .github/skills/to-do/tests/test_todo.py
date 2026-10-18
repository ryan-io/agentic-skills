"""Unit tests for the to-do ledger tool (todo.py)."""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import todo

LEDGER_TEMPLATE = """---
status: living-document
created: 2026-08-03
updated: 2026-08-03
tags: [index, process]
---

# To-Do Ledger

| ID | To-do | Tags | Added |
|----|-------|------|-------|
"""

class TodoLedgerTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.ledger = Path(self.dir.name) / "todo-ledger.md"
        self.ledger.write_text(LEDGER_TEMPLATE, encoding="utf-8")
        self.base = ["--ledger", str(self.ledger)]

    def tearDown(self):
        self.dir.cleanup()

    def run_cmd(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            todo.main(self.base + list(argv))
        return out.getvalue()

    def run_cmd_streams(self, *argv):
        """run_cmd for the paths that also write a note to stderr; returns (out, err)."""
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            todo.main(self.base + list(argv))
        return out.getvalue(), err.getvalue()

    def test_add_assigns_sequential_ids(self):
        out1 = self.run_cmd("add", "first thing", "--tags", "docs")
        out2 = self.run_cmd("add", "second thing")
        self.assertIn("TODO-001", out1)
        self.assertIn("TODO-002", out2)
        _, rows = todo.read_ledger(self.ledger)
        self.assertEqual([r[0] for r in rows], ["TODO-001", "TODO-002"])

    def test_add_sanitizes_pipes_and_whitespace(self):
        self.run_cmd("add", "a | b\n  c")
        _, rows = todo.read_ledger(self.ledger)
        self.assertEqual(rows[0][1], "a / b c")

    def test_done_removes_row_and_missing_id_exits(self):
        self.run_cmd("add", "first thing")
        self.run_cmd("add", "second thing")
        self.run_cmd("done", "TODO-001")
        _, rows = todo.read_ledger(self.ledger)
        self.assertEqual([r[0] for r in rows], ["TODO-002"])
        with self.assertRaises(SystemExit):
            self.run_cmd("done", "TODO-099")

    def test_done_extra_tokens_still_removes_the_row_and_notes_them(self):
        self.run_cmd("add", "first thing")
        self.run_cmd("add", "second thing")
        out, err = self.run_cmd_streams("done", "TODO-001", "extra", "tokens")
        self.assertIn("TODO-001 done and removed", out)
        self.assertIn("note: ignoring extra arguments: extra tokens", err)
        _, rows = todo.read_ledger(self.ledger)
        self.assertEqual([r[0] for r in rows], ["TODO-002"])

    def test_list_filters_by_tag(self):
        self.run_cmd("add", "design thing", "--tags", "docs")
        self.run_cmd("add", "process thing", "--tags", "process")
        out = self.run_cmd("list", "--tag", "process")
        self.assertIn("process thing", out)
        self.assertNotIn("design thing", out)

    def test_list_bare_tag_positional_filters_like_the_flag(self):
        self.run_cmd("add", "design thing", "--tags", "docs")
        self.run_cmd("add", "process thing", "--tags", "process")
        bare = self.run_cmd("list", "process")
        self.assertEqual(bare, self.run_cmd("list", "--tag", "process"))
        self.assertIn("process thing", bare)
        self.assertNotIn("design thing", bare)

    def test_list_tag_flag_with_extra_positional_keeps_the_flag_and_notes(self):
        self.run_cmd("add", "design thing", "--tags", "docs")
        self.run_cmd("add", "process thing", "--tags", "process")
        out, err = self.run_cmd_streams("list", "--tag", "process", "docs")
        self.assertIn("process thing", out)
        self.assertNotIn("design thing", out)
        self.assertIn("note: ignoring extra argument: docs", err)

    def test_surface_silent_when_empty_and_prints_rows(self):
        self.assertEqual(self.run_cmd("surface"), "")
        self.run_cmd("add", "re-run the load test after the cache change", "--tags", "docs")
        out = self.run_cmd("surface")
        self.assertIn("[to-do] 1 open", out)
        self.assertIn("TODO-001", out)

    def test_surface_long_row_truncates_at_97_chars_and_leaves_short_rows_whole(self):
        long_text = "x" * 140
        self.run_cmd("add", long_text)
        self.run_cmd("add", "y" * 100)
        self.run_cmd("add", "short thing")
        out = self.run_cmd("surface")
        self.assertIn("x" * 97 + "...", out)
        self.assertNotIn("x" * 98, out)
        self.assertIn("y" * 100, out)
        self.assertIn("short thing", out)
        self.assertIn(long_text, self.run_cmd("list"))

    def test_surface_silent_when_ledger_missing(self):
        self.ledger.unlink()
        self.assertEqual(self.run_cmd("surface"), "")

    def test_add_creates_a_missing_ledger(self):
        self.ledger.unlink()
        self.assertIn("TODO-001", self.run_cmd("add", "first thing"))
        _, rows = todo.read_ledger(self.ledger)
        self.assertEqual([r[0] for r in rows], ["TODO-001"])

    def test_add_without_updated_frontmatter_places_high_water_above_the_table(self):
        self.ledger.write_text(LEDGER_TEMPLATE.replace("updated: 2026-08-03\n", ""),
                               encoding="utf-8")
        self.run_cmd("add", "first thing")
        self.run_cmd("add", "second thing")
        text = self.ledger.read_text(encoding="utf-8")
        self.assertIn("high-water: 2", text)
        _, rows = todo.read_ledger(self.ledger)
        self.assertEqual([r[0] for r in rows], ["TODO-001", "TODO-002"])

    def test_add_does_not_recycle_id_after_done_of_highest_row(self):
        with redirect_stdout(io.StringIO()):
            todo.main(self.base + ["add", "first"])
            todo.main(self.base + ["add", "second"])
            todo.main(self.base + ["done", "TODO-002"])
        out = io.StringIO()
        with redirect_stdout(out):
            todo.main(self.base + ["add", "third"])
        self.assertIn("TODO-003", out.getvalue())
        self.assertIn("high-water: 3", self.ledger.read_text(encoding="utf-8"))

    def test_add_honors_existing_high_water_over_row_max(self):
        text = self.ledger.read_text(encoding="utf-8")
        text = text.replace("updated: 2026-08-03", "updated: 2026-08-03\nhigh-water: 41")
        self.ledger.write_text(text, encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out):
            todo.main(self.base + ["add", "later"])
        self.assertIn("TODO-042", out.getvalue())

    def test_updated_frontmatter_bumps_on_write(self):
        import datetime
        self.run_cmd("add", "first thing")
        text = self.ledger.read_text(encoding="utf-8")
        self.assertIn(f"updated: {datetime.date.today().isoformat()}", text)


if __name__ == "__main__":
    unittest.main()
