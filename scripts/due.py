#!/usr/bin/env python3
"""Learning-partner log tools: what's due, retention stats, calendar export.

Scans <root>/*/log.md. Relies on two line shapes the tutor writes:

    **Next review:** 2026-09-01 — re-test: reopen session-02-send.py and add a reset command
    Retrieval: 2/3          (any retrieval check: session-start or review mode)
    First-try: 2/3          (exercises that passed on the first run — the difficulty dial)

Also reads the log's frontmatter `status:` (researching | active | paused | done) and
counts roadmap checkboxes (`- [ ] S3 ...` / `- [x] S1 ...`) so --all can sum the
sessions still to run across active topics — the capacity check at scope time.

Usage:
    python due.py                 # overdue, due today, upcoming within 3 days
    python due.py --all           # every topic, plus roadmap sessions remaining across active ones
    python due.py --stats         # retention and first-try rates per topic
    python due.py --check         # lint log.md and research.md files: unparseable lines, oversize
                                  #   research, workbench paths named but missing on disk
    python due.py --ics out.ics   # write an all-day calendar event per review date
    python due.py --where            # print the learning root this script will use
    python due.py --root ~/notes/learning

The learning root is --root, else $LEARNING_PARTNER_ROOT, else ~/learning.

Parsing is tolerant of bold/colon/dash variations, but run --check after
editing logs — a line that drifts too far is silently invisible to --stats.
"""
import argparse
import datetime
import os
import pathlib
import re
import sys

REVIEW_RE = re.compile(r"\*{0,2}Next review\*{0,2}:?\*{0,2}\s*(\d{4}-\d{2}-\d{2})\s*(?:[—–-]+\s*(.*))?", re.I)
RETRIEVAL_RE = re.compile(r"^\*{0,2}Retrieval\*{0,2}:?\s*(\d+)\s*/\s*(\d+)", re.M | re.I)
FIRSTTRY_RE = re.compile(r"^\*{0,2}First[-\s]?try\*{0,2}:?\s*(\d+)\s*/\s*(\d+)", re.M | re.I)
STATUS_RE = re.compile(r"^status:\s*(\w+)", re.M)
ROADMAP_DONE_RE = re.compile(r"^- \[x\] S\d+", re.M | re.I)
ROADMAP_LEFT_RE = re.compile(r"^- \[ \] S\d+", re.M)
WORKBENCH_PATH_RE = re.compile(r"workbench\.nosync/([\w./{},*-]*)")

RESEARCH_WORD_CAP = 1000
ACTIVE_STATUSES = ("active", "researching")


def load(root):
    topics = []
    for log in sorted(root.glob("*/log.md")):
        text = log.read_text(errors="replace")
        m = REVIEW_RE.search(text)
        due, note = None, ""
        if m:
            try:
                due = datetime.date.fromisoformat(m.group(1))
                note = (m.group(2) or "").strip()
            except ValueError:
                note = f"unparseable date: {m.group(1)}"
        status = STATUS_RE.search(text[:500])
        topics.append({
            "topic": log.parent.name,
            "due": due,
            "note": note,
            "status": status.group(1).lower() if status else "active",
            "sessions_done": len(ROADMAP_DONE_RE.findall(text)),
            "sessions_left": len(ROADMAP_LEFT_RE.findall(text)),
            "retrieval": [(int(a), int(b)) for a, b in RETRIEVAL_RE.findall(text)],
            "firsttry": [(int(a), int(b)) for a, b in FIRSTTRY_RE.findall(text)],
        })
    return topics


def when(days):
    if days < 0:
        return f"{-days}d overdue"
    if days == 0:
        return "today"
    return f"in {days}d"


def show_due(topics, today, horizon, show_all):
    dated = sorted((t for t in topics if t["due"]), key=lambda t: t["due"])
    width = max((len(t["topic"]) for t in topics), default=10)

    def section(title, rows):
        if not rows:
            return
        print(title)
        for t in rows:
            d = (t["due"] - today).days
            line = f"  {t['topic']:<{width}}  {when(d):<12}"
            if t["note"]:
                line += f"  {t['note']}"
            print(line)
        print()

    section("OVERDUE", [t for t in dated if (t["due"] - today).days < 0])
    section("DUE TODAY", [t for t in dated if (t["due"] - today).days == 0])
    section("UPCOMING", [t for t in dated if 0 < (t["due"] - today).days <= horizon])
    if show_all:
        section("LATER", [t for t in dated if (t["due"] - today).days > horizon])
        undated = [t for t in topics if not t["due"]]
        if undated:
            print("NO REVIEW DATE")
            for t in undated:
                print(f"  {t['topic']}" + (f"  ({t['note']})" if t["note"] else ""))
            print()
        show_capacity(topics)
    if not topics:
        print("no topics found")
    elif dated and not any((t["due"] - today).days <= horizon for t in dated):
        nxt = dated[0]
        print(f"nothing due in the next {horizon} days — next is {nxt['topic']} {when((nxt['due'] - today).days)}")


def show_capacity(topics):
    """Roadmap sessions still unchecked, summed over active topics. Each topic is scoped
    alone; this is the number that says whether they fit together before a deadline."""
    active = [t for t in topics if t["status"] in ACTIVE_STATUSES]
    if not active:
        return
    total_left = sum(t["sessions_left"] for t in active)
    per_topic = ", ".join(
        f"{t['topic']} {t['sessions_done']}/{t['sessions_done'] + t['sessions_left']} done"
        for t in active
    )
    print(f"roadmap sessions remaining across {len(active)} active topic(s): {total_left}  ({per_topic})")


def rate(pairs):
    asked = sum(b for _, b in pairs)
    passed = sum(a for a, _ in pairs)
    return (passed, asked, (passed / asked) if asked else None)


def show_stats(topics):
    """Retention = retrieval checks passed / asked, across the whole log. This is the
    one number that says whether learning stuck. Trend = same over the last three checks."""
    width = max((len(t["topic"]) for t in topics), default=10)
    print(f"  {'topic':<{width}}  retention   last3   first-try   checks")
    for t in topics:
        p, a, r = rate(t["retrieval"])
        p3, a3, r3 = rate(t["retrieval"][-3:])
        fp, fa, fr = rate(t["firsttry"])
        def fmt(r, p, a):
            return f"{r*100:3.0f}% ({p}/{a})" if r is not None else "   —      "
        print(f"  {t['topic']:<{width}}  {fmt(r,p,a):<11} {fmt(r3,p3,a3):<11} {fmt(fr,fp,fa):<11} {len(t['retrieval'])}")
    print()
    print("retention below ~80% on last3 → repeat the interval; first-try above ~80% → turn the dial up")


def check(root):
    """Lint every log.md for shapes this script relies on. Returns problem count.

    Catches the failure mode that matters: a line a human reads as a review date
    or a score, but the regexes above silently skip."""
    problems = 0

    def flag(log, msg):
        nonlocal problems
        problems += 1
        print(f"  {log.parent.name}: {msg}")

    logs = sorted(root.glob("*/log.md"))
    for log in logs:
        text = log.read_text(errors="replace")
        m = REVIEW_RE.search(text)
        if m:
            try:
                datetime.date.fromisoformat(m.group(1))
            except ValueError:
                flag(log, f"unparseable review date: {m.group(1)!r}")
        else:
            for line in text.splitlines():
                if re.search(r"next\s*review", line, re.I):
                    flag(log, f"looks like a review line but doesn't parse: {line.strip()!r}")
                    break
            else:
                flag(log, "no 'Next review:' line — topic is invisible to due dates")
        if ROADMAP_DONE_RE.search(text) and not RETRIEVAL_RE.search(text):
            flag(log, "sessions marked done but no parseable 'Retrieval: n/m' line — topic is invisible to --stats")
        for line in text.splitlines():
            if re.search(r"\d+\s*/\s*\d+", line) and re.search(r"retrieval|first[-\s]?try", line, re.I):
                if not (RETRIEVAL_RE.match(line) or FIRSTTRY_RE.match(line)):
                    flag(log, f"score line doesn't parse (not at line start?): {line.strip()!r}")
    for folder in sorted(root.iterdir()):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        if not (folder / "log.md").exists():
            flag(folder / "log.md", "topic folder has no log.md — create it before research, not after")
        check_research(folder, flag)
    if problems:
        print(f"{problems} problem(s) in {root}")
    else:
        print(f"all {len(logs)} log(s) parse cleanly")
    return problems


def check_research(folder, flag):
    """research.md is reread every session, so it has a size cap. Workbench paths it names
    are checked on this machine only: .nosync folders don't sync, so a topic set up on
    another Mac has its workbench there — a fact the tutor needs before promising hands-on."""
    research = folder / "research.md"
    if not research.exists():
        return
    text = research.read_text(errors="replace")
    words = len(text.split())
    if words > RESEARCH_WORD_CAP:
        flag(research, f"research.md is {words} words (cap {RESEARCH_WORD_CAP}) — it's reread every session; move detail to research-<focus>.md")
    mentions = WORKBENCH_PATH_RE.findall(text)
    if not mentions:
        return
    workbench = folder / "workbench.nosync"
    if not workbench.is_dir():
        flag(research, "workbench.nosync/ is not on this machine (.nosync never syncs) — hands-on work needs the Mac it was built on, or a rebuild here")
        return
    for rel in sorted(set(mentions)):
        rel = rel.rstrip(".,;:/")
        if not rel or any(c in rel for c in "{}*") or "NN" in rel:
            continue
        if not (workbench / rel).exists():
            flag(research, f"names workbench.nosync/{rel} which isn't in this machine's workbench")


def write_ics(topics, path):
    def esc(s):
        return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//learning-partner//due.py//EN"]
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for t in topics:
        if not t["due"]:
            continue
        d = t["due"].strftime("%Y%m%d")
        nxt = (t["due"] + datetime.timedelta(days=1)).strftime("%Y%m%d")
        lines += [
            "BEGIN:VEVENT",
            f"UID:learning-{t['topic']}-{d}@learning-partner",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{d}",
            f"DTEND;VALUE=DATE:{nxt}",
            f"SUMMARY:{esc('Review: ' + t['topic'])}",
            f"DESCRIPTION:{esc(t['note'] or 'Run review mode in learning-partner')}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    pathlib.Path(path).write_text("\r\n".join(lines) + "\r\n")
    n = sum(1 for t in topics if t["due"])
    print(f"wrote {n} review event(s) to {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.environ.get("LEARNING_PARTNER_ROOT", "~/learning"),
                    help="learning root (default: $LEARNING_PARTNER_ROOT, else ~/learning)")
    ap.add_argument("--where", action="store_true", help="print the resolved learning root and exit")
    ap.add_argument("--all", action="store_true", help="show every topic, not just those due soon")
    ap.add_argument("--horizon", type=int, default=3, help="days ahead that count as upcoming")
    ap.add_argument("--stats", action="store_true", help="retention and first-try rates per topic")
    ap.add_argument("--check", action="store_true", help="lint log.md files for unparseable lines")
    ap.add_argument("--ics", metavar="PATH", help="write review dates as an .ics calendar file")
    args = ap.parse_args()

    root = pathlib.Path(args.root).expanduser()
    if args.where:
        print(root)
        return 0 if root.is_dir() else 1
    if not root.is_dir():
        print(f"no learning folder at {root} — create it, or set LEARNING_PARTNER_ROOT", file=sys.stderr)
        return 1
    if args.check:
        return 1 if check(root) else 0
    topics = load(root)
    if args.ics:
        write_ics(topics, args.ics)
        return 0
    if args.stats:
        show_stats(topics)
        return 0
    show_due(topics, datetime.date.today(), args.horizon, args.all)
    return 0


if __name__ == "__main__":
    sys.exit(main())
