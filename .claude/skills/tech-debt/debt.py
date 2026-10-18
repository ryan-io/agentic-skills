#!/usr/bin/env python3
"""Tech-debt ledger tool: next id, row lookup, filtered lists, and capture.

Owns the mechanical reads and the append to docs/debt/debt-index.md so sessions
never grep the registry for an id or a status slice. Stdlib only. Run from the
repo root (`.claude/skills/tech-debt/` carries an identical copy):

    python .github/skills/tech-debt/debt.py next-id
    python .github/skills/tech-debt/debt.py get TD-005
    python .github/skills/tech-debt/debt.py list [--status open] [--filter System=Save]
    python .github/skills/tech-debt/debt.py verify [--status open] [--id TD-005] [--strict]
    python .github/skills/tech-debt/debt.py add --sev Med --category dependency-risk \
        --system SaveAccess --item "..." --record "..." --trigger "..."

`list` truncates the long cells so a slice costs a few lines; `get` prints one
row in full. `next-id` spans the ledger and the archive, which carry identical
column shapes. `verify` is the deterministic anchor-existence sweep: it reports
existence drift, never pertinence. Archival (moving resolved rows to the
archive) stays with the `tech-debt` skill; this tool never moves a row. `add`
creates the ledger with its header row when it does not exist yet.
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

LEDGER = Path("docs/debt/debt-index.md")
ARCHIVE = Path("docs/debt/tech-debt-archive.md")
COLUMNS = ["ID", "Sev", "Category", "System", "Item",
           "Owning record", "Trigger / condition", "Status"]
HEADER = "| " + " | ".join(COLUMNS) + " |"
ID_RE = re.compile(r"^TD-\d+$")
# Vocabularies are advisory: a cell may carry trailing prose ("resolved (stale
# row: ...)"), so matching is by prefix and a miss only warns.
STATUS_VOCAB = ["open", "accepted", "watch", "resolved"]
SEV_VOCAB = ["High", "Med", "Low"]
LEDGER_TEMPLATE = """---
updated: {today}
---

# Tech Debt Registry

Row format and lifecycle: the `tech-debt` skill. Live rows are `open` and `watch`.

{header}
|{sep}|
"""

# --- verify: anchor existence sweep -----------------------------------------
# Only the prose-bearing cells carry anchors; ID/Sev/Category are vocabulary.
# "Owning record" is excluded on purpose: its link almost always resolves, and
# counting it would keep the all-missing bucket unreachable.
VERIFY_COLUMNS = ["System", "Item", "Trigger / condition", "Status"]
# Default identifier roots: every top-level entry of the repo except these, so
# the ledger and the records citing an identifier never count as evidence of it.
# Override with --scan-root.
EXCLUDED_TOP_DIRS = {"docs"}
# Content is read for these; every other file counts by name alone, so a binary
# or generated asset anchor resolves without parsing its contents.
SCAN_EXTS = {".cs", ".py", ".json", ".md", ".ps1", ".sh", ".yml", ".yaml", ".csproj",
             ".props", ".targets", ".xaml", ".ts", ".tsx", ".js", ".go", ".rs", ".java",
             ".kt", ".toml", ".sql"}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "obj", "bin",
             "dist", "build", "out", "target", ".vs", ".idea", ".mypy_cache",
             ".pytest_cache"}
BACKTICK_RE = re.compile(r"`([^`]+)`")
PATH_RE = re.compile(r"[A-Za-z0-9_.\-/]*/[A-Za-z0-9_.\-]+\.[A-Za-z0-9]{1,6}")
IDENT_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# Two or more case humps, so a single capitalized prose word is never an anchor.
PASCAL_RE = re.compile(r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+\b")
CODEY_RE = re.compile(r"^(?=.*[A-Z_])[A-Za-z_][A-Za-z0-9_]*$")
MIN_ANCHOR_LEN = 6
# Capitalized registry and prose vocabulary that reads as an identifier but names
# no symbol; extraction stays conservative by dropping these outright.
ANCHOR_STOPWORDS = {
    "github", "gitignore", "javascript", "typescript", "readme", "changelog",
    "definitionofdone", "questionmark", "newtonsoft", "dotnet",
}


def read_table(path, columns=COLUMNS, id_re=ID_RE, header=HEADER):
    """Return (head, rows, tail) for a ledger, warning loudly on any unparseable row."""
    if not path.exists():
        sys.exit(f"error: {path} not found (run from the repo root)")
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        head_end = next(i for i, l in enumerate(lines) if l.strip() == header) + 2
    except StopIteration:
        sys.exit(f"error: {path} has no '{header}' table")
    rows, tail = [], []
    for offset, line in enumerate(lines[head_end:]):
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith("|"):
            tail = lines[head_end + offset:]
            break
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) != len(columns):
            warn(path, head_end + offset + 1,
                 f"{len(cells)} columns, expected {len(columns)}", stripped)
        elif not id_re.match(cells[0]):
            warn(path, head_end + offset + 1, f"unrecognized id '{cells[0]}'", stripped)
        else:
            rows.append(cells)
    return lines[:head_end], rows, tail


def warn(path, lineno, reason, text):
    print(f"warning: {path}:{lineno} unparseable table row ({reason}): "
          f"{text[:120]}", file=sys.stderr)


def write_table(path, head, rows, tail):
    today = datetime.date.today().isoformat()
    head = [re.sub(r"^updated: \d{4}-\d{2}-\d{2}$", f"updated: {today}", l) for l in head]
    body = ["| " + " | ".join(r) + " |" for r in rows]
    out = head + body + tail
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def normalize_id(raw, prefix="TD"):
    raw = raw.strip().upper()
    if raw.isdigit():
        return f"{prefix}-{int(raw):03d}"
    return raw


def clean(text):
    """Collapse whitespace and strip pipes so a cell cannot break the table."""
    return re.sub(r"\s+", " ", text or "").strip().replace("|", "/")


def truncate(text, width):
    return text if len(text) <= width else text[:width - 3] + "..."


def all_rows(args):
    _, ledger_rows, _ = read_table(args.ledger)
    archive_rows = []
    if args.archive.exists():
        _, archive_rows, _ = read_table(args.archive)
    return ledger_rows + archive_rows


def cmd_next_id(args):
    rows = all_rows(args)
    nums = [int(r[0].split("-")[1]) for r in rows]
    print(f"TD-{max(nums, default=0) + 1:03d}")


def cmd_get(args):
    target = normalize_id(args.id)
    for row in all_rows(args):
        if row[0] == target:
            width = max(len(c) for c in COLUMNS)
            for col, cell in zip(COLUMNS, row):
                print(f"{col:<{width}}  {cell}")
            return
    sys.exit(f"error: {target} not found in {args.ledger} or {args.archive}")


def cmd_list(args):
    _, rows, _ = read_table(args.ledger)
    if args.status:
        want = args.status.lower()
        rows = [r for r in rows if r[-1].lower().startswith(want)]
    for spec in args.filter or []:
        if "=" not in spec:
            sys.exit(f"error: --filter expects <column>=<substring>, got '{spec}'")
        col, _, sub = spec.partition("=")
        matches = [c for c in COLUMNS if c.lower().startswith(col.strip().lower())]
        if len(matches) != 1:
            sys.exit(f"error: '{col.strip()}' matches {len(matches)} columns "
                     f"of {COLUMNS}")
        idx = COLUMNS.index(matches[0])
        rows = [r for r in rows if sub.strip().lower() in r[idx].lower()]
    if not rows:
        print("no matching debt rows")
        return
    if args.full:
        # Full-fidelity subset: header once, raw cells, one row per line. Meant
        # for a filtered scope; unfiltered it approximates the file (a full read).
        print(" | ".join(COLUMNS))
        for r in rows:
            print(" | ".join(r))
        print(f"({len(rows)} row(s), full)")
        return
    for r in rows:
        print(f"{r[0]}  {r[1]:<4}  {truncate(r[7], 24):<24}  {truncate(r[3], 22):<22}  "
              f"{truncate(r[4], 100)}")
    print(f"({len(rows)} row(s); `get <id>` for the full row)")


def identifier_anchor(token):
    """Return the token if it reads as a code identifier, else None."""
    if len(token) < MIN_ANCHOR_LEN or token.lower() in ANCHOR_STOPWORDS:
        return None
    return token if CODEY_RE.match(token) else None


def path_anchor(raw):
    """Strip link, fragment, and line-number decoration from a path-like token.

    Leading dots survive the strip so a relative link (`../adr/x.md`) keeps its
    parent hop.
    """
    raw = raw.strip().lstrip("([").rstrip(")],;:'\"").rstrip(".")
    raw = raw.split("#")[0].split(":")[0]
    return raw if "/" in raw and "." in raw.rsplit("/", 1)[1] else None


def extract_anchors(cells):
    """Return the ordered, de-duplicated anchors a row's prose cells reference.

    Three shapes are recognized: path-like tokens, backticked identifiers, and
    bare PascalCase names of at least MIN_ANCHOR_LEN characters.
    """
    anchors, seen = [], set()

    def add(value, kind):
        if value and value not in seen:
            seen.add(value)
            anchors.append((value, kind))

    for cell in cells:
        for raw in PATH_RE.findall(cell):
            if "//" in raw:  # a URL, not a repo path
                continue
            add(path_anchor(raw), "path")
        bare = cell
        for quoted in BACKTICK_RE.findall(cell):
            bare = bare.replace(f"`{quoted}`", " ")
            if PATH_RE.fullmatch(quoted.strip()):
                continue
            for token in IDENT_TOKEN_RE.findall(quoted):
                add(identifier_anchor(token), "identifier")
        for token in PASCAL_RE.findall(PATH_RE.sub(" ", bare)):
            add(identifier_anchor(token), "identifier")
    return anchors


def scan_bases(root, scan_roots):
    """Return the directories (and loose top-level files) the identifier scan walks."""
    if scan_roots:
        return [root / r for r in scan_roots]
    return [p for p in sorted(root.iterdir())
            if p.name not in EXCLUDED_TOP_DIRS and p.name not in SKIP_DIRS]


def scan_identifiers(wanted, root, scan_roots=None):
    """Return the subset of `wanted` present in the scanned trees, in one pass.

    One walk builds the tree's token set, from every file's name and from the
    text of the scannable ones; an anchor missing an exact token then falls back
    to a substring test, so `ConfigAccess` counts as present via `IConfigAccess`
    and `ReportExporter` via an asset named after it.
    """
    if not wanted:
        return set()
    tokens = set()
    for base in scan_bases(root, scan_roots):
        if base.is_file():
            walk = [(str(base.parent), [], [base.name])]
        elif base.is_dir():
            walk = os.walk(base)
        else:
            continue
        for dirpath, dirs, files in walk:
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                stem, ext = os.path.splitext(name)
                tokens.update((name, stem))
                if ext.lower() not in SCAN_EXTS:
                    continue
                try:
                    text = Path(dirpath, name).read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                tokens.update(IDENT_TOKEN_RE.findall(text))
    found = wanted & tokens
    rest = wanted - found
    if rest:
        blob = "\n".join(tokens)
        found |= {w for w in rest if w in blob}
    return found


def path_exists(rel, root, ledger_dir):
    """Test a path anchor against the repo root and the ledger's own directory."""
    return any((base / rel).exists() for base in (root, ledger_dir))


def cmd_verify(args):
    _, rows, _ = read_table(args.ledger)
    if args.id:
        target = normalize_id(args.id)
        rows = [r for r in rows if r[0] == target]
        if not rows:
            sys.exit(f"error: {target} not found in {args.ledger}")
        scope = target
    elif args.status:
        want = args.status.lower()
        rows = [r for r in rows if r[-1].lower().startswith(want)]
        scope = f"status {want}"
    else:
        rows = [r for r in rows if not r[-1].lower().startswith("resolved")]
        scope = "status != resolved"

    idx = [COLUMNS.index(c) for c in VERIFY_COLUMNS]
    per_row = [(r[0], extract_anchors([r[i] for i in idx])) for r in rows]
    wanted = {a for _, anchors in per_row for a, kind in anchors if kind == "identifier"}
    root = args.root.resolve()
    present = scan_identifiers(wanted, root, args.scan_root)
    ledger_dir = args.ledger.resolve().parent

    clean, partial, gone, empty, total, missed = [], [], [], [], 0, 0
    for row_id, anchors in per_row:
        missing = [a for a, kind in anchors
                   if not (a in present if kind == "identifier"
                           else path_exists(a, root, ledger_dir))]
        total += len(anchors)
        missed += len(missing)
        entry = (row_id, len(anchors) - len(missing), missing)
        if not anchors:
            empty.append(entry)
        elif not missing:
            clean.append(entry)
        elif len(missing) == len(anchors):
            gone.append(entry)
        else:
            partial.append(entry)

    def show(entries):
        for row_id, found, missing in entries:
            print(f"  {row_id}  {found} found / {len(missing)} missing"
                  f"{'  missing: ' + ', '.join(missing) if missing else ''}")

    print("verify: anchor existence only, never pertinence (every anchor can "
          "exist and the row still be stale); prose files (README, SKILL.md) "
          "under the scan roots count as existence sources, so a type surviving "
          "only in prose reads present")
    roots = args.scan_root or [f"repo root minus {', '.join(sorted(EXCLUDED_TOP_DIRS))}/"]
    print(f"scope: {len(rows)} row(s) ({scope}); identifier roots: {', '.join(roots)}")
    if gone:
        print(f"\nall anchors missing ({len(gone)}) -- candidate stale or "
              f"resolved-in-code, needs human triage:")
        show(gone)
    if partial:
        print(f"\nsome anchors missing ({len(partial)}):")
        show(partial)
    if args.id:
        for label, entries in (("clean", clean), ("no anchors extracted", empty)):
            if entries:
                print(f"\n{label}:")
                show(entries)
    print(f"\nclean: {len(clean)} row(s), every anchor present")
    if empty and not args.id:
        print(f"no anchors extracted: {len(empty)} row(s) "
              f"({', '.join(e[0] for e in empty)})")
    print(f"summary: {len(clean)} clean, {len(partial)} partial, {len(gone)} "
          f"all-missing, {len(empty)} no-anchors of {len(rows)} scoped "
          f"({total} anchors, {missed} missing)")
    if args.strict and gone:
        sys.exit(1)


def ensure_ledger(path):
    """Create the ledger with its header row when it does not exist yet."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    sep = "|".join("-" * (len(c) + 2) for c in COLUMNS)
    path.write_text(LEDGER_TEMPLATE.format(today=datetime.date.today().isoformat(),
                                           header=HEADER, sep=sep), encoding="utf-8")


def cmd_add(args):
    ensure_ledger(args.ledger)
    head, rows, tail = read_table(args.ledger)
    item = clean(args.item)
    if not item:
        sys.exit("error: empty --item")
    if not any(args.status.lower().startswith(v) for v in STATUS_VOCAB):
        print(f"warning: status '{args.status}' is outside {STATUS_VOCAB}", file=sys.stderr)
    if args.sev not in SEV_VOCAB:
        print(f"warning: severity '{args.sev}' is outside {SEV_VOCAB}", file=sys.stderr)
    next_n = max((int(r[0].split("-")[1]) for r in all_rows(args)), default=0) + 1
    row_id = f"TD-{next_n:03d}"
    rows.append([row_id, clean(args.sev), clean(args.category), clean(args.system),
                 item, clean(args.record), clean(args.trigger), clean(args.status)])
    write_table(args.ledger, head, rows, tail)
    print(f"{row_id}: {truncate(item, 100)}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ledger", type=Path, default=LEDGER, help="ledger path override (tests)")
    p.add_argument("--archive", type=Path, default=ARCHIVE, help="archive path override (tests)")
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("next-id", help="print the next free TD id (ledger + archive)")
    n.set_defaults(fn=cmd_next_id)
    g = sub.add_parser("get", help="print one row in full")
    g.add_argument("id")
    g.set_defaults(fn=cmd_get)
    l = sub.add_parser("list", help="print compact rows, optionally filtered")
    l.add_argument("--status", help="status prefix match (open/accepted/watch/resolved)")
    l.add_argument("--filter", action="append", help="<column>=<substring>, repeatable")
    l.add_argument("--full", action="store_true",
                   help="every column of each matching row; the triage pass, instead of a full Read")
    l.set_defaults(fn=cmd_list)
    v = sub.add_parser("verify", help="anchor-existence sweep over the non-closed rows")
    v.add_argument("--status", help="status prefix match; default is every non-resolved row")
    v.add_argument("--id", help="verify one row (prints the clean and no-anchor rows too)")
    v.add_argument("--strict", action="store_true",
                   help="exit 1 when a row has every anchor missing")
    v.add_argument("--root", type=Path, default=Path("."), help="repo root override (tests)")
    v.add_argument("--scan-root", action="append",
                   help="identifier scan root relative to --root, repeatable; "
                        "default is every top-level entry except docs/")
    v.set_defaults(fn=cmd_verify)
    a = sub.add_parser("add", help="append a debt row")
    a.add_argument("--sev", required=True, help="High / Med / Low")
    a.add_argument("--category", required=True)
    a.add_argument("--system", required=True)
    a.add_argument("--item", required=True)
    a.add_argument("--record", required=True, help="owning record link or name")
    a.add_argument("--trigger", default="none")
    a.add_argument("--status", default="open")
    a.set_defaults(fn=cmd_add)
    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
