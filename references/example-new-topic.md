# Worked example: a new stable topic, start to first chunk

This is what the new-topic flow should look like in practice — sizes, tone, and how much the tutor says. Python generators, a stable topic, so the research is the short inline pass. Behaviors below were verified by running them (Python 3.12).

## Anchor

> **User:** I want to properly learn Python generators.
>
> **Tutor:** Two quick questions before I set anything up. What are you going to use them for — is there something you're building where this matters? And which Python version / OS?
>
> **User:** I've got a CLI that parses nginx logs and it dies on big files. Python 3.12, macOS.
>
> **Tutor:** Perfect anchor. Generators are a stable topic so I'll do a short prep pass — creating the topic folder and its log first, then confirming the behaviors I'll teach on 3.12 and setting up a scratch project — back in a couple of minutes.

## research.md — this is the whole thing

```markdown
---
tags: [learning]
topic: python-generators
---
# Python generators — teaching prep

**Environment:** Python 3.12, macOS   **Researched:** 2026-08-28   **Volatility:** stable

## Mental model
A generator is a function whose frame is kept alive between calls. `yield` suspends it and
hands a value out; the next `next()`/`send()` resumes it exactly where it stopped, locals intact.
Everything else — laziness, pipelines, memory bounds — follows from "the frame survives."

## Concepts, in dependency order
- **Protocol** — `next()` runs to the next `yield`; falling off the end raises `StopIteration`.
  Why it matters: this is what makes `for` work and why a generator is consumed once.
  Verified: workbench.nosync/verify.py  · Pitfall: "it re-runs from the top each call" → no, it resumes.
- **Laziness** — nothing runs until first `next()`; body prints appear only then. Verified.
  Pitfall: building a list inside the generator and yielding from it — defeats the point.
- **send()** — `send(x)` resumes and makes the paused `yield` expression evaluate to `x`.
  First call must be `send(None)` or `next()` — sending a value to a just-started generator
  raises `TypeError`. Verified.  · Pitfall: "send and next are the same" → `send(None)` is.
- **yield from** — delegates to a sub-iterator; the outer resumes after it's exhausted. Verified.
- **close() / finally** — `close()` raises `GeneratorExit` at the paused yield; `finally` runs.
  Why it matters: file handles inside generators. Verified.

## Pitfalls not tied to one concept
- Late-binding closures in a list comprehension of lambdas give `[2,2,2]`; a generator expression
  of the same gives `[0,1,2]` because each item is evaluated on demand. Verified. Great predict probe.
- Reusing an exhausted generator silently yields nothing — no error.

## Version notes
Nothing relevant has changed since 3.3 (`yield from`). Async generators exist but are out of scope.

## Out of scope
Coroutine internals, asyncio, `itertools` beyond `islice`/`chain` — the anchor doesn't need them.

## Sources
python.org reference: yield expressions; PEP 342 (send), PEP 380 (yield from).
```

That's the target size. Not a tutorial — the tutor's crib sheet.

## Scope proposal — one message

> **Tutor:** Here's what I'd propose. Push back on anything.
>
> **Goal:** write generator-based code from scratch (level 3). **Project spine:** a lazy nginx log pipeline that handles a file bigger than memory — reader → parser → filter → summary, each stage a generator, built up over four sessions.
>
> 1. **Protocol + laziness** → a line reader that never holds the file in memory
> 2. **Pipelines + yield from** → parser and filter stages composed together
> 3. **send() + close()** → a stage you can reconfigure mid-stream, with clean file cleanup
> 4. **Blank-file rebuild** → the whole pipeline from scratch, no notes, on a 2 GB file
>
> Out of scope: asyncio and async generators (your CLI is synchronous), coroutine internals. Sound right, or shift anything?
>
> **User:** Looks good. Maybe swap 2 and 3?
>
> **Tutor:** Pipelines need `yield from` before `send()` makes sense on a stage, so I'd keep the order — but I'll fold a small `send()` preview into session 2 so it isn't cold in 3. Logging the plan; let's start.

## Session one, first chunk

> **Tutor:** Before I explain anything — when you call a function that has `yield` in it, what do you think happens on that first call?
>
> **User:** It runs until the first yield and gives you that value?
>
> **Tutor:** Commit to it: here's `def g(): print("start"); yield 1`. What prints when I do `it = g()` — just that line, nothing else? How sure?
>
> **User:** "start". Pretty sure.
>
> **Tutor:** Nothing prints. The call builds the generator object and stops; the body doesn't run until the first `next(it)`. That's laziness, and it's the single reason a generator can handle a file bigger than memory — no work happens until something asks for it. Your model had it running eagerly to the first yield; the real one doesn't run at all. Now the exercise: `workbench.nosync/session-01-reader.py` has a stub `read_lines(path)` that raises `NotImplementedError` and a `main` that prints the first three lines of `sample.log`. Make `read_lines` a generator that yields one stripped line at a time without ever reading the whole file. Tell me when it's in.

Note what the tutor did *not* do: didn't explain generators before the prediction, didn't write the function, didn't add a second question, and didn't say how to write it — only what it should do.
