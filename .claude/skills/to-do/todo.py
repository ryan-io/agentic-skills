#!/usr/bin/env python3
"""To-do ledger tool: capture, list, complete, and surface small to-dos.

Owns the mechanical edits to docs/todo/todo-ledger.md so sessions need not
hand-edit the table. Stdlib only. Run from the repo root
(`.claude/skills/to-do/` carries an identical copy):

    python .github/skills/to-do/todo.py add "re-run the load test after the cache change" --tags perf
    python .github/skills/to-do/todo.py list [--tag <tag>]
    python .github/skills/to-do/todo.py done TODO-001
    python .github/skills/to-do/todo.py surface

`surface` prints the open rows compactly and prints nothing when the ledger is
empty or missing. `add` creates the ledger when it does not exist yet. Tags are
free text; the tool keeps no vocabulary.
"""

import argparse
import datetime
import re
import sys
from pathlib import Path

LEDGER = Path("docs/todo/todo-ledger.md")
HEADER = "| ID | To-do | Tags | Added |"
SEPARATOR = "|----|-------|------|-------|"
ROW_RE = re.compile(r"^\| (TODO-\d{3}) \| (.*?) \| (.*?) \| (\d{4}-\d{2}-\d{2}) \|$")
HIGH_WATER_RE = re.compile(r"^high-water: (\d+)$")
LEDGER_TEMPLATE = """---
updated: {today}
---

# To-Do Ledger

Row format and lifecycle: the `to-do` skill. Done rows are removed, not archived.

{header}
{separator}
"""


def ensure_ledger(path):
    """Create the ledger with its header row when it does not exist yet."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(LEDGER_TEMPLATE.format(today=datetime.date.today().isoformat(),
                                           header=HEADER, separator=SEPARATOR),
                    encoding="utf-8")


def read_ledger(path):
    """Return (lines-before-rows, rows) where rows are (id, text, tags, added)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        head_end = next(i for i, l in enumerate(lines) if l.strip() == HEADER) + 2
    except StopIteration:
        sys.exit(f"error: {path} has no '{HEADER}' table")
    rows = []
    for line in lines[head_end:]:
        m = ROW_RE.match(line.strip())
        if m:
            rows.append((m.group(1), m.group(2), m.group(3), m.group(4)))
    return lines[:head_end], rows


def write_ledger(path, head, rows):
    today = datetime.date.today().isoformat()
    head = [re.sub(r"^updated: \d{4}-\d{2}-\d{2}$", f"updated: {today}", l) for l in head]
    body = [f"| {i} | {t} | {g} | {a} |" for i, t, g, a in rows]
    path.write_text("\n".join(head + body) + "\n", encoding="utf-8")


def cmd_add(args):
    ensure_ledger(args.ledger)
    head, rows = read_ledger(args.ledger)
    text = re.sub(r"\s+", " ", args.text).strip().replace("|", "/")
    if not text:
        sys.exit("error: empty to-do text")
    tags = sorted(t.strip() for t in args.tags.split(",") if t.strip()) if args.tags else []
    # High-water mark: ids are never recycled even after the highest open row
    # is removed by `done`.
    high_water = max(
        (int(m.group(1)) for l in head if (m := HIGH_WATER_RE.match(l.strip()))),
        default=0,
    )
    next_n = max(high_water, max((int(i.split("-")[1]) for i, *_ in rows), default=0)) + 1
    row_id = f"TODO-{next_n:03d}"
    if any(HIGH_WATER_RE.match(l.strip()) for l in head):
        head = [f"high-water: {next_n}" if HIGH_WATER_RE.match(l.strip()) else l for l in head]
    else:
        # After the frontmatter `updated:` line; a ledger without one gets the
        # mark just above the table.
        at = next((i + 1 for i, l in enumerate(head) if l.startswith("updated: ")),
                  len(head) - 2)
        mark = [f"high-water: {next_n}"] if at != len(head) - 2 else [f"high-water: {next_n}", ""]
        head = head[:at] + mark + head[at:]
    rows.append((row_id, text, ", ".join(tags), datetime.date.today().isoformat()))
    write_ledger(args.ledger, head, rows)
    print(f"{row_id}: {text}")


def cmd_list(args):
    _, rows = read_ledger(args.ledger)
    if not args.tag and args.tag_positional:
        args.tag = args.tag_positional
    elif args.tag and args.tag_positional:
        print(f"note: ignoring extra argument: {args.tag_positional}", file=sys.stderr)
    if args.tag:
        rows = [r for r in rows if args.tag in [t.strip() for t in r[2].split(",")]]
    if not rows:
        print("no open to-dos" + (f" tagged '{args.tag}'" if args.tag else ""))
        return
    for i, t, g, a in rows:
        print(f"{i}  {t}" + (f"  [{g}]" if g else "") + f"  ({a})")


def cmd_done(args):
    if args.extra:
        print(f"note: ignoring extra arguments: {' '.join(args.extra)}", file=sys.stderr)
    head, rows = read_ledger(args.ledger)
    kept = [r for r in rows if r[0] != args.id]
    if len(kept) == len(rows):
        sys.exit(f"error: {args.id} not found")
    write_ledger(args.ledger, head, kept)
    print(f"{args.id} done and removed (git history keeps the account)")


def cmd_surface(args):
    if not args.ledger.exists():
        return
    _, rows = read_ledger(args.ledger)
    if not rows:
        return
    print(f"[to-do] {len(rows)} open ({args.ledger.as_posix()}; `to-do` skill owns lifecycle):")
    # Compact by design: full text stays on `list` / `list --tag`.
    for i, t, g, _ in rows:
        text = t if len(t) <= 100 else t[:97] + "..."
        print(f"  {i}  {text}" + (f"  [{g}]" if g else ""))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ledger", type=Path, default=LEDGER, help="ledger path override (tests)")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="append a to-do row")
    a.add_argument("text")
    a.add_argument("--tags", default="", help="comma-separated free-text tags")
    a.set_defaults(fn=cmd_add)
    l = sub.add_parser("list", help="print open rows")
    l.add_argument("--tag", help="filter by one tag")
    l.add_argument("tag_positional", nargs="?", metavar="tag",
                   help="same as --tag")
    l.set_defaults(fn=cmd_list)
    d = sub.add_parser("done", help="remove a completed row")
    d.add_argument("id")
    d.add_argument("extra", nargs="*",
                   help="tolerated and ignored with a note; a stray token must not fail the removal")
    d.set_defaults(fn=cmd_done)
    s = sub.add_parser("surface", help="compact print of open rows; silent when empty")
    s.set_defaults(fn=cmd_surface)
    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
