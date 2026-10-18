"""Unit tests for the refactor ledger tool (refactor.py)."""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import refactor

FRONTMATTER = """---
status: living-document
created: 2026-08-15
updated: 2026-08-01
tags: [index, refactoring]
---

# Refactor Ledger

| ID | Refactor | Solves | Evidence | Disposition | Status |
|----|----------|--------|----------|-------------|--------|
"""

LEDGER_ROWS = (
    "| RF-008 | Extract the dedicated-writer idiom | Two autosave writers diverge"
    " | SnapshotAutosaveService.cs | investigated | open |\n"
    "| RF-041 | Rebuild the lookup index only on key changes | Per-frame rebuild"
    " | ReportCacheRenderer.cs | investigated | blocked |\n"
    # A hand-edited shape: no space before the closing pipe.
    "| RF-050 | Extract shared pure-tier test support | Thrice-duplicated stub"
    " | OrderPricingTests.cs | needs-review |resolved (2026-08-12)|\n"
)

ARCHIVE_ROWS = (
    "| RF-031 | Archived refactor | Solved problem | evidence.cs | investigated | resolved |\n"
)


class RefactorLedgerTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.ledger = Path(self.dir.name) / "refactor-ledger.md"
        self.ledger.write_text(FRONTMATTER + LEDGER_ROWS, encoding="utf-8")
        self.archive = Path(self.dir.name) / "refactor-ledger-archive.md"
        self.archive.write_text(FRONTMATTER + ARCHIVE_ROWS, encoding="utf-8")
        self.base = ["--ledger", str(self.ledger), "--archive", str(self.archive)]

    def tearDown(self):
        self.dir.cleanup()

    def run_cmd(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            refactor.main(self.base + list(argv))
        return out.getvalue(), err.getvalue()

    def test_next_id_spans_ledger_and_archive(self):
        out, _ = self.run_cmd("next-id")
        self.assertEqual(out.strip(), "RF-051")

    def test_get_finds_archived_row_and_normalizes_bare_number(self):
        out, _ = self.run_cmd("get", "31")
        self.assertIn("Archived refactor", out)
        out, _ = self.run_cmd("get", "RF-008")
        self.assertIn("dedicated-writer", out)

    def test_get_unknown_id_exits(self):
        with self.assertRaises(SystemExit):
            self.run_cmd("get", "RF-999")

    def test_list_status_blocked_is_a_first_class_value(self):
        out, _ = self.run_cmd("list", "--status", "blocked")
        self.assertIn("RF-041", out)
        self.assertNotIn("RF-008", out)

    def test_list_status_matches_by_prefix_over_trailing_prose(self):
        out, _ = self.run_cmd("list", "--status", "resolved")
        self.assertIn("RF-050", out)
        self.assertNotIn("RF-041", out)

    def test_list_filters_by_column_substring(self):
        out, _ = self.run_cmd("list", "--filter", "Solves=Per-frame")
        self.assertIn("RF-041", out)
        self.assertNotIn("RF-008", out)

    def test_list_full_prints_the_column_header_raw_rows_and_footer(self):
        out, _ = self.run_cmd("list", "--status", "blocked", "--full")
        lines = out.strip().splitlines()
        self.assertEqual(lines[0], " | ".join(refactor.COLUMNS))
        self.assertEqual(lines[1], " | ".join([
            "RF-041", "Rebuild the lookup index only on key changes",
            "Per-frame rebuild", "ReportCacheRenderer.cs",
            "investigated", "blocked"]))
        self.assertEqual(lines[2], "(1 row(s), full)")

    def test_list_full_keeps_a_long_cell_the_compact_form_truncates(self):
        long_refactor = "L" * 140
        self.ledger.write_text(
            FRONTMATTER + LEDGER_ROWS
            + f"| RF-060 | {long_refactor} | s | e | investigated | open |\n",
            encoding="utf-8")
        full, _ = self.run_cmd("list", "--status", "open", "--full")
        compact, _ = self.run_cmd("list", "--status", "open")
        self.assertIn(long_refactor, full)
        self.assertNotIn(long_refactor, compact)
        self.assertNotIn(" | ".join(refactor.COLUMNS), compact)
        self.assertIn("(2 row(s); `get <id>` for the full row)", compact)

    def test_malformed_row_warns_loudly_and_keeps_the_rest(self):
        self.ledger.write_text(
            FRONTMATTER + LEDGER_ROWS + "| RF-060 | broken row |\n", encoding="utf-8")
        out, err = self.run_cmd("list")
        self.assertIn("unparseable table row", err)
        self.assertIn("RF-060", err)
        self.assertIn("RF-008", out)
        self.assertNotIn("RF-060", out)

    def test_add_appends_row_and_bumps_updated(self):
        import datetime
        out, _ = self.run_cmd("add", "--refactor", "Merge  the two\nhelpers | now",
                              "--solves", "duplication", "--evidence", "a.cs:1")
        self.assertIn("RF-051", out)
        _, rows, _ = refactor.read_table(self.ledger)
        self.assertEqual(rows[-1][0], "RF-051")
        self.assertEqual(rows[-1][1], "Merge the two helpers / now")
        self.assertEqual(rows[-1][4], "investigated")
        self.assertEqual(rows[-1][5], "open")
        text = self.ledger.read_text(encoding="utf-8")
        self.assertIn(f"updated: {datetime.date.today().isoformat()}", text)

    def test_add_warns_on_disposition_outside_the_vocabulary(self):
        _, err = self.run_cmd("add", "--refactor", "r", "--solves", "s",
                              "--evidence", "e", "--disposition", "guessed")
        self.assertIn("outside", err)

    def test_add_creates_a_missing_ledger_with_its_header(self):
        self.ledger.unlink()
        out, _ = self.run_cmd("add", "--refactor", "r", "--solves", "s", "--evidence", "e")
        self.assertIn("RF-032", out)  # the archive still reserves its ids
        _, rows, _ = refactor.read_table(self.ledger)
        self.assertEqual([r[0] for r in rows], ["RF-032"])

    def test_add_preserves_trailing_prose_after_the_table(self):
        self.ledger.write_text(FRONTMATTER + LEDGER_ROWS + "\nTrailing prose.\n",
                               encoding="utf-8")
        self.run_cmd("add", "--refactor", "r", "--solves", "s", "--evidence", "e")
        self.assertIn("Trailing prose.", self.ledger.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
