# Learning Partner

A [Claude Code](https://claude.com/claude-code) skill that turns Claude into a tutor whose job is not to explain things well. Its job is to make your own understanding visible to you, so you can steer your learning instead of the tutor steering it.

The enemy is the illusion of competence. A clear explanation *feels* like understanding: you nod, say "makes sense," and two days later can't write the thing from memory. Nearly every move in this skill exists to break that illusion early, while it's cheap to fix.

**Ask before tell.** It finds out what you already believe before teaching, then makes you produce it back: explain it, predict what code does, write it without looking.

**Do before discuss.** Every concept becomes a few lines you write and run yourself, then justify. Your fingers write the concept; the tutor writes the scaffolding.

## What a session looks like

- **New topic** — two anchor questions (what will you build with it, what's your environment), research on the *current* version of the thing, a scope you sign off on: a target level, a small project that grows across sessions, a 3–8 session roadmap ending in a blank-file rebuild.
- **Deep dive** (30–60 min) — retrieval check on last time, then chunks of *predict → teach → do → explain why*, then 3–5 mixed retrieval questions graded blind by an examiner that never sees the transcript.
- **Micro-session** (10–15 min) — one question, one chunk, one log line.
- **Review** — spaced retrieval across whatever's due, interleaved, always one hands-on. No new material.

Every retrieval question asks for a confidence rating first. The examiner compares confidence against results, so you learn not just what you know but where you're overconfident.

The tutor is audited. After each deep dive an auditor grades it against twelve numbered rules (`rules.md`): never wrote your lines, predicted before explaining, one question per message, poker face during evaluation. A rule broken twice produces a proposed rewording. That's how the skill improves: from evidence, not from opinion.

## Install

```sh
git clone https://github.com/Bytevardas/learning-partner-skill ~/.claude/skills/learning-partner
mkdir -p ~/learning
```

Notes go in `~/learning/` by default. To put them elsewhere (an Obsidian vault, a synced folder), set the root in your shell profile:

```sh
export LEARNING_PARTNER_ROOT="$HOME/path/to/notes"
```

Requirements: Claude Code, Python 3 (for `scripts/due.py`), and whatever toolchain the topic needs (Go, Python, Cargo — the tutor sets up a scratch project per topic).

## Use

In Claude Code, just say what you want:

| You say | What happens |
|---|---|
| "teach me Go generics", "I want to really understand the borrow checker" | New topic, or a deep dive if it exists |
| "quick one — remind me how channels block" | Micro-session |
| "what's due", "quiz me", "review" | Review mode across due topics |
| "pick up where we left off" | Continues the roadmap |
| "just explain it, I'm short on time" | You get an explanation; the check moves to next session |

The tutor reads your profile and the topic log first, so every session starts where the last one ended.

## What it writes

```
<learning root>/
  profile.md              how you learn, across topics: what works, calibration, recurring patterns
  tutor-notes.md          the skill's own log: recurring drift and proposed rule edits
  <topic-slug>/
    log.md                scope, roadmap, prior beliefs → corrections, open questions, session history
    research.md           the tutor's teaching prep, verified by running it, under 1,000 words
    workbench.nosync/     runnable exercises, one file per session — yours to keep
```

Everything is plain markdown. Inside an Obsidian vault the notes also get wikilinks, callouts, and queryable frontmatter.

`workbench.nosync/` stays on the machine that created it (the `.nosync` suffix keeps iCloud Drive from syncing build artifacts). Hands-on re-tests need that machine.

## Scripts

```sh
python3 scripts/due.py            # overdue, due today, upcoming
python3 scripts/due.py --all      # every topic, plus roadmap sessions remaining across active ones
python3 scripts/due.py --stats    # retention and first-try rates per topic
python3 scripts/due.py --check    # lint logs and research: unparseable lines, oversize research, missing workbench
python3 scripts/due.py --ics f.ics   # review dates as a calendar file
python3 scripts/due.py --where    # which learning root it's using
```

The tutor runs these itself. `--stats` retention (retrieval passed over asked) is the one number that says whether any of this is working.

## Agents

Four briefs in `agents/`, used when Claude Code can spawn subagents. Without subagents the tutor follows each brief itself.

- **researcher** — reads current docs, changelog, and source for *your* version, verifies claims by running them, drafts the scope. Volatile topics only.
- **critic** — tries to break `research.md` before you learn from it. The researcher, tutor, and examiner are the same model; this is the one pass looking for their shared mistake.
- **examiner** — grades your retrieval answers without the teaching transcript, so it hears only what you said, not what the tutor meant.
- **auditor** — grades the tutor against `rules.md` and proposes rule changes when drift recurs.

## Tuning it

`rules.md` is the contract. Edit it when the auditor shows a rule isn't holding; `tutor-notes.md` in your learning root accumulates the evidence. `references/techniques.md` is the probe catalog; `references/example-new-topic.md` shows what a compact new-topic setup looks like.

## What it is not

- **Not a lecturer.** It explains less than you might want, on purpose. If you want a good explanation and nothing else, ask for one.
- **Not cheap.** A deep dive is an hour of your attention. It only pays off if you do the spaced reviews.
- **Not for your real code.** Building and debugging real work, or weighing design choices, belong to other modes. This one learns; graduation hands off.
