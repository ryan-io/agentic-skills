"""Unit tests for the tech-debt ledger tool (debt.py)."""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import debt

FRONTMATTER = """---
status: living-document
created: 2026-08-15
updated: 2026-08-01
tags: [index, tech-debt]
---

# Registry

| ID | Sev | Category | System | Item | Owning record | Trigger / condition | Status |
|----|-----|----------|--------|------|---------------|---------------------|--------|
"""

LEDGER_ROWS = (
    "| TD-002 | Med | dependency-risk | SaveAccess | Newtonsoft reflection unverified"
    " | [persistence ADR](x.md) | before first trimmed release build | watch |\n"
    "| TD-004 | High | testing | Messaging | no regression test on the fan-in"
    " | [messaging plan](y.md) | none | open |\n"
    # A hand-edited shape: no space before the closing pipe.
    "| TD-009 | Low | docs | docs (systems) | stale synopsis | none | none |resolved (2026-07-09)|\n"
)

ARCHIVE_ROWS = (
    "| TD-015 | Med | testing | Engine | archived row | [wo](z.md) | none | resolved |\n"
)


class DebtLedgerTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.ledger = Path(self.dir.name) / "debt-index.md"
        self.ledger.write_text(FRONTMATTER + LEDGER_ROWS, encoding="utf-8")
        self.archive = Path(self.dir.name) / "tech-debt-archive.md"
        self.archive.write_text(FRONTMATTER + ARCHIVE_ROWS, encoding="utf-8")
        self.base = ["--ledger", str(self.ledger), "--archive", str(self.archive)]

    def tearDown(self):
        self.dir.cleanup()

    def run_cmd(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            debt.main(self.base + list(argv))
        return out.getvalue(), err.getvalue()

    def test_next_id_spans_ledger_and_archive(self):
        out, _ = self.run_cmd("next-id")
        self.assertEqual(out.strip(), "TD-016")

    def test_get_finds_archived_row_and_normalizes_bare_number(self):
        out, _ = self.run_cmd("get", "15")
        self.assertIn("archived row", out)
        out, _ = self.run_cmd("get", "TD-002")
        self.assertIn("SaveAccess", out)

    def test_get_unknown_id_exits(self):
        with self.assertRaises(SystemExit):
            self.run_cmd("get", "TD-999")

    def test_list_status_matches_by_prefix_over_trailing_prose(self):
        out, _ = self.run_cmd("list", "--status", "resolved")
        self.assertIn("TD-009", out)
        self.assertNotIn("TD-002", out)

    def test_list_filters_by_column_substring(self):
        out, _ = self.run_cmd("list", "--filter", "System=Messaging")
        self.assertIn("TD-004", out)
        self.assertNotIn("TD-002", out)

    def test_list_full_prints_the_column_header_raw_rows_and_footer(self):
        out, _ = self.run_cmd("list", "--status", "watch", "--full")
        lines = out.strip().splitlines()
        self.assertEqual(lines[0], " | ".join(debt.COLUMNS))
        self.assertEqual(lines[1], " | ".join([
            "TD-002", "Med", "dependency-risk", "SaveAccess",
            "Newtonsoft reflection unverified", "[persistence ADR](x.md)",
            "before first trimmed release build", "watch"]))
        self.assertEqual(lines[2], "(1 row(s), full)")

    def test_list_full_keeps_a_long_cell_the_compact_form_truncates(self):
        long_item = "L" * 140
        self.ledger.write_text(
            FRONTMATTER + LEDGER_ROWS
            + f"| TD-020 | Low | docs | X | {long_item} | r | none | open |\n",
            encoding="utf-8")
        full, _ = self.run_cmd("list", "--status", "open", "--full")
        compact, _ = self.run_cmd("list", "--status", "open")
        self.assertIn(long_item, full)
        self.assertNotIn(long_item, compact)
        self.assertNotIn(" | ".join(debt.COLUMNS), compact)
        self.assertIn("(2 row(s); `get <id>` for the full row)", compact)

    def test_list_ambiguous_column_exits(self):
        with self.assertRaises(SystemExit):
            self.run_cmd("list", "--filter", "S=x")

    def test_malformed_row_warns_loudly_and_keeps_the_rest(self):
        self.ledger.write_text(
            FRONTMATTER + LEDGER_ROWS + "| TD-011 | Med | broken row missing columns |\n",
            encoding="utf-8")
        out, err = self.run_cmd("list")
        self.assertIn("unparseable table row", err)
        self.assertIn("TD-011", err)
        self.assertIn("TD-002", out)
        self.assertIn("TD-009", out)
        self.assertNotIn("TD-011", out)

    def test_add_appends_row_and_bumps_updated(self):
        import datetime
        out, _ = self.run_cmd("add", "--sev", "Med", "--category", "tooling",
                              "--system", "docs (debt)", "--item", "a  new\nitem | here",
                              "--record", "[plan](p.md)", "--trigger", "none")
        self.assertIn("TD-016", out)
        _, rows, _ = debt.read_table(self.ledger)
        self.assertEqual(rows[-1][0], "TD-016")
        self.assertEqual(rows[-1][4], "a new item / here")
        self.assertEqual(rows[-1][7], "open")
        text = self.ledger.read_text(encoding="utf-8")
        self.assertIn(f"updated: {datetime.date.today().isoformat()}", text)

    def test_add_warns_on_status_outside_the_vocabulary(self):
        _, err = self.run_cmd("add", "--sev", "Med", "--category", "tooling",
                              "--system", "X", "--item", "i", "--record", "r",
                              "--status", "pending")
        self.assertIn("outside", err)

    def test_add_creates_a_missing_ledger_with_its_header(self):
        self.ledger.unlink()
        out, _ = self.run_cmd("add", "--sev", "Low", "--category", "docs", "--system", "X",
                              "--item", "first", "--record", "r")
        self.assertIn("TD-016", out)  # the archive still reserves its ids
        _, rows, _ = debt.read_table(self.ledger)
        self.assertEqual([r[0] for r in rows], ["TD-016"])

    def test_add_preserves_trailing_prose_after_the_table(self):
        self.ledger.write_text(FRONTMATTER + LEDGER_ROWS + "\nTrailing prose.\n",
                               encoding="utf-8")
        self.run_cmd("add", "--sev", "Low", "--category", "docs", "--system", "X",
                     "--item", "i", "--record", "r")
        self.assertIn("Trailing prose.", self.ledger.read_text(encoding="utf-8"))


VERIFY_ROWS = (
    # present identifier + present path; its owning-record link is dead and must
    # stay uncounted (the column is excluded from extraction)
    "| TD-101 | Med | tooling | Hosting | `PresentThing` is still wired in"
    " docs/adr/present.md | [adr](../adr/gone.md) | none | open |\n"
    # missing identifier + missing path: every anchor gone, and a live
    # owning-record link must not rescue the row
    "| TD-102 | Low | tooling | Hosting | `VanishedThing` was deleted with"
    " docs/adr/gone.md | [adr](../adr/present.md) | none | open |\n"
    # prose only: nothing conservative extraction should treat as an anchor
    "| TD-103 | Low | docs | Hosting | the save path and the trigger stay"
    " unpinned; Newtonsoft and AbCdE prove nothing | none | none | watch |\n"
    # one present, one missing
    "| TD-104 | Low | docs | Hosting | `PresentThing` outlived `VanishedThing`"
    " | none | none | accepted |\n"
    # resolved: outside the default scope even though its anchor is gone
    "| TD-105 | Low | docs | Hosting | `VanishedThing` | none | none | resolved |\n"
    # short-name anchor that only exists inside a longer identifier
    "| TD-106 | Low | docs | Hosting | `ConfigAccess` port | none | none | open |\n"
    # binary anchor: the file's name is the only evidence, its content is unread
    "| TD-107 | Low | docs | Hosting | `FixtureReportTemplate.png` is unpinned"
    " | none | none | open |\n"
)


class DebtVerifyTests(unittest.TestCase):
    """Anchor-existence sweep over a fixture repo (ledger at docs/debt, code at tools)."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
        (self.root / "docs" / "debt").mkdir(parents=True)
        (self.root / "docs" / "adr").mkdir()
        (self.root / "tools").mkdir()
        self.ledger = self.root / "docs" / "debt" / "debt-index.md"
        self.ledger.write_text(FRONTMATTER + VERIFY_ROWS, encoding="utf-8")
        self.archive = self.root / "docs" / "debt" / "tech-debt-archive.md"
        self.archive.write_text(FRONTMATTER + ARCHIVE_ROWS, encoding="utf-8")
        (self.root / "docs" / "adr" / "present.md").write_text("# adr\n", encoding="utf-8")
        (self.root / "tools" / "sample.py").write_text(
            "class PresentThing:\n    IConfigAccess = 1\n", encoding="utf-8")
        assets = self.root / "src" / "assets"
        assets.mkdir(parents=True)
        (assets / "FixtureReportTemplate.png").write_text("binary\n", encoding="utf-8")
        self.base = ["--ledger", str(self.ledger), "--archive", str(self.archive)]

    def tearDown(self):
        self.dir.cleanup()

    def verify(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            debt.main(self.base + ["verify", "--root", str(self.root)] + list(argv))
        return out.getvalue(), err.getvalue()

    def row_line(self, out, row_id):
        for line in out.splitlines():
            if line.strip().startswith(row_id):
                return line
        self.fail(f"{row_id} absent from:\n{out}")

    def test_verify_header_disclaims_pertinence_and_states_the_scope(self):
        out, _ = self.verify()
        self.assertIn("existence only, never pertinence", out.splitlines()[0])
        self.assertIn("status != resolved", out)

    def test_verify_finds_a_present_identifier_and_a_present_path(self):
        out, _ = self.verify("--id", "TD-101")
        self.assertIn("2 found / 0 missing", self.row_line(out, "TD-101"))

    def test_verify_reports_a_missing_identifier_and_a_missing_path(self):
        out, _ = self.verify()
        line = self.row_line(out, "TD-102")
        self.assertIn("0 found / 2 missing", line)
        self.assertIn("VanishedThing", line)
        self.assertIn("docs/adr/gone.md", line)
        self.assertIn("all anchors missing (1)", out)

    def test_verify_ignores_the_owning_record_column(self):
        out, _ = self.verify()
        # No link-form path reaches the report: TD-101 stays clean despite its
        # dead link, TD-102 stays all-missing despite its live one.
        self.assertNotIn("../adr/", out)
        self.assertIn("2 found / 0 missing", self.row_line(self.verify("--id", "TD-101")[0],
                                                           "TD-101"))
        self.assertIn("0 found / 2 missing", self.row_line(out, "TD-102"))

    def test_verify_partial_row_lands_in_the_some_missing_section(self):
        out, _ = self.verify()
        self.assertIn("some anchors missing (1)", out)
        line = self.row_line(out, "TD-104")
        self.assertIn("1 found / 1 missing", line)
        self.assertIn("VanishedThing", line)
        self.assertNotIn("PresentThing", line)

    def test_verify_extraction_skips_prose_stopwords_and_short_names(self):
        out, _ = self.verify()
        self.assertIn("no anchors extracted: 1 row(s) (TD-103)", out)
        for word in ("Newtonsoft", "AbCdE", "Hosting", "trigger"):
            self.assertNotIn(word, out)

    def test_verify_matches_an_identifier_inside_a_longer_name(self):
        out, _ = self.verify("--id", "TD-106")
        self.assertIn("1 found / 0 missing", self.row_line(out, "TD-106"))

    def test_verify_matches_a_binary_by_its_filename_not_its_contents(self):
        out, _ = self.verify("--id", "TD-107")
        self.assertIn("1 found / 0 missing", self.row_line(out, "TD-107"))

    def test_verify_default_scope_excludes_resolved_rows(self):
        out, _ = self.verify()
        self.assertIn("of 6 scoped", out)
        self.assertNotIn("TD-105", out)

    def test_verify_status_filter_narrows_the_scope(self):
        out, _ = self.verify("--status", "resolved")
        self.assertIn("status resolved", out)
        self.assertIn("of 1 scoped", out)
        self.assertIn("TD-105", out)

    def test_verify_id_filter_prints_the_clean_row_it_selects(self):
        out, _ = self.verify("--id", "101")
        self.assertIn("of 1 scoped", out)
        self.assertIn("clean:", out)
        self.assertNotIn("TD-102", out)

    def test_verify_unknown_id_exits(self):
        with self.assertRaises(SystemExit):
            self.verify("--id", "TD-999")

    def test_verify_exits_zero_without_strict_and_nonzero_with_it(self):
        self.verify()  # a row with every anchor missing is still exit 0
        with self.assertRaises(SystemExit) as ctx:
            self.verify("--strict")
        self.assertEqual(ctx.exception.code, 1)

    def test_verify_never_counts_the_ledger_under_docs_as_evidence(self):
        # VanishedThing appears in the ledger itself; docs/ is excluded by default.
        out, _ = self.verify("--id", "TD-102")
        self.assertIn("0 found / 2 missing", self.row_line(out, "TD-102"))

    def test_verify_scan_root_override_narrows_the_identifier_scan(self):
        out, _ = self.verify("--id", "TD-101", "--scan-root", "src")
        self.assertIn("1 found / 1 missing", self.row_line(out, "TD-101"))

    def test_verify_strict_stays_zero_when_no_row_lost_every_anchor(self):
        self.verify("--id", "TD-104", "--strict")


if __name__ == "__main__":
    unittest.main()
