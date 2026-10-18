#!/usr/bin/env python3
"""Refactor ledger tool: next id, row lookup, filtered lists, and capture.

Owns the mechanical reads and the append to docs/refactor/refactor-ledger.md so
sessions never grep the ledger for an id or a status slice. Stdlib only. Run from
the repo root (`.claude/skills/refactor-ledger/` carries an identical copy):

    python .github/skills/refactor-ledger/refactor.py next-id
    python .github/skills/refactor-ledger/refactor.py get RF-008
    python .github/skills/refactor-ledger/refactor.py list [--status open] \
        [--filter Solves=duplication]
    python .github/skills/refactor-ledger/refactor.py add --refactor "..." \
        --solves "..." --evidence "..."

`list` truncates the long cells so a slice costs a few lines; `get` prints one
row in full. `next-id` spans the ledger and the archive, which carry identical
column shapes. Archival (moving resolved rows to the archive) stays with the
`refactor-ledger` skill; this tool never moves a row. `add` creates the ledger
with its header row when it does not exist yet.
"""

import argparse
import datetime
import re
import sys
from pathlib import Path

LEDGER = Path("docs/refactor/refactor-ledger.md")
ARCHIVE = Path("docs/refactor/refactor-ledger-archive.md")
COLUMNS = ["ID", "Refactor", "Solves", "Evidence", "Disposition", "Status"]
HEADER = "| " + " | ".join(COLUMNS) + " |"
ID_RE = re.compile(r"^RF-\d+$")
# Vocabularies are advisory: a cell may carry trailing prose, so matching is by
# prefix and a miss only warns.
STATUS_VOCAB = ["open", "in-flight", "blocked", "resolved"]
DISPOSITION_VOCAB = ["investigated", "needs-review"]
LEDGER_TEMPLATE = """---
updated: {today}
---

# Refactor Ledger

Row format and lifecycle: the `refactor-ledger` skill.

{header}
|{sep}|
"""


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


def normalize_id(raw, prefix="RF"):
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
    print(f"RF-{max(nums, default=0) + 1:03d}")


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
        print("no matching refactor rows")
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
        print(f"{r[0]}  {truncate(r[5], 20):<20}  {truncate(r[4], 13):<13}  "
              f"{truncate(r[1], 100)}")
    print(f"({len(rows)} row(s); `get <id>` for the full row)")


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
    refactor = clean(args.refactor)
    if not refactor:
        sys.exit("error: empty --refactor")
    if not any(args.status.lower().startswith(v) for v in STATUS_VOCAB):
        print(f"warning: status '{args.status}' is outside {STATUS_VOCAB}", file=sys.stderr)
    if args.disposition not in DISPOSITION_VOCAB:
        print(f"warning: disposition '{args.disposition}' is outside "
              f"{DISPOSITION_VOCAB}", file=sys.stderr)
    next_n = max((int(r[0].split("-")[1]) for r in all_rows(args)), default=0) + 1
    row_id = f"RF-{next_n:03d}"
    rows.append([row_id, refactor, clean(args.solves), clean(args.evidence),
                 clean(args.disposition), clean(args.status)])
    write_table(args.ledger, head, rows, tail)
    print(f"{row_id}: {truncate(refactor, 100)}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ledger", type=Path, default=LEDGER, help="ledger path override (tests)")
    p.add_argument("--archive", type=Path, default=ARCHIVE, help="archive path override (tests)")
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("next-id", help="print the next free RF id (ledger + archive)")
    n.set_defaults(fn=cmd_next_id)
    g = sub.add_parser("get", help="print one row in full")
    g.add_argument("id")
    g.set_defaults(fn=cmd_get)
    l = sub.add_parser("list", help="print compact rows, optionally filtered")
    l.add_argument("--status", help="status prefix match (open/in-flight/blocked/resolved)")
    l.add_argument("--filter", action="append", help="<column>=<substring>, repeatable")
    l.add_argument("--full", action="store_true",
                   help="every column of each matching row; the triage pass, instead of a full Read")
    l.set_defaults(fn=cmd_list)
    a = sub.add_parser("add", help="append a refactor row")
    a.add_argument("--refactor", required=True, help="what moves, merges, splits, or renames")
    a.add_argument("--solves", required=True, help="the concrete problem removed")
    a.add_argument("--evidence", required=True, help="file, symbol, refs count")
    a.add_argument("--disposition", default="investigated",
                   help="investigated / needs-review")
    a.add_argument("--status", default="open")
    a.set_defaults(fn=cmd_add)
    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
