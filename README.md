# learning-partner

A Claude Code skill for learning technical topics and actually retaining them.

It doesn't lecture. It asks what you think first, makes you write the code, grades you blind, and schedules spaced reviews. Your notes and exercises stay on disk.

## Install

```sh
git clone https://github.com/Bytevardas/learning-partner-skill ~/.claude/skills/learning-partner
mkdir -p ~/learning
```

Optional: keep notes somewhere else, e.g. an Obsidian vault.

```sh
export LEARNING_PARTNER_ROOT="$HOME/vault/learning"
```

Needs Python 3 for the scripts, plus the toolchain of whatever you're learning.

## Usage

Start a topic:

```
> teach me Go slices properly

Two quick questions. What are you going to use them for, and which Go version / OS?

> a transaction ledger for a side project, Go 1.25, macOS

Setting up a scratch project and checking the behaviours I'll teach on 1.25. Back in a minute.
```

It comes back with a scope: target level, a small project that grows session by session, 3–8 sessions, out of scope. You adjust, it starts.

A chunk in a session:

```
Before I explain anything: a := make([]int, 3, 8); b := append(a, 9); b[0] = 42.
What does a[0] print, and how sure are you?

> 0, pretty sure. append makes a new array

42. There was spare capacity, so append wrote into the same array and handed
back a longer header. Your model had append copying every time; it only
copies when cap runs out.

Exercise: workbench.nosync/session-02-ledger/report.go has a stub
RecentHistory(n). Make it return the last n entries without exposing the
ledger's backing array. Tell me when it's in.
```

You write the lines. It runs them. If it fails, it asks what you think went wrong instead of fixing it.

Other things to say:

```
> what's due                 spaced reviews across topics, 10–15 min
> quiz me on rust lifetimes  review one topic
> quick one: how do Go channels block   micro-session
> just explain it            you get the explanation; the check moves to next session
```

Sessions end with retrieval questions. You rate confidence 1–5 before each answer, then an examiner that never saw the session grades them. You get verdicts, a calibration table, and the next review date.

## Files

```
~/learning/
  profile.md            how you learn: what works, where you're overconfident
  tutor-notes.md        rule changes the auditor has proposed
  go-slices/
    log.md              scope, roadmap, misconceptions caught, session history
    research.md         the tutor's prep, verified by running it
    workbench.nosync/   your exercises, one file per session
```

Plain markdown. In an Obsidian vault you also get wikilinks and backlinks.

## Scripts

```sh
python3 scripts/due.py          # what's due
python3 scripts/due.py --stats  # retention per topic
python3 scripts/due.py --check  # lint logs and research
python3 scripts/due.py --all    # every topic + sessions remaining
```

## How it stays honest

`rules.md` has twelve rules the tutor is graded against after every deep dive: never write the learner's lines, predict before teach, one question per message, poker face while collecting answers. A rule broken twice gets a proposed rewording in `tutor-notes.md`. Edit `rules.md` when the evidence says to.

`agents/` holds the briefs for the researcher, critic, examiner, and auditor. Without subagents the tutor follows them itself.

## Not for

Building or debugging real code, or design decisions. This skill learns; when a topic is done it hands off to real work.
