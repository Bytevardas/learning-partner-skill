# Probe and retrieval techniques

A catalog of moves for making the user's understanding visible. Each one tests something slightly different; rotating between them keeps sessions from getting predictable and catches gaps that any single technique would miss.

## Prediction probes (before teaching)

**Predict-the-output.** Show 3–10 lines of code, ask what it prints/returns/throws. The default move for language features. Keep snippets small enough that the answer hinges on the one concept being taught — if it also depends on three other things, a wrong answer tells you nothing.

**Predict-the-failure.** Show code that *doesn't* work and ask what goes wrong and where. Good for concepts that are mostly about constraints (borrow checker, type systems, concurrency rules). Forces the user to run the rule-checker in their head.

**Predict-the-diff.** Show two nearly-identical snippets, ask how their behavior differs. Isolates a single variable. Excellent for "what does this keyword actually change" questions (`async` vs not, `const` vs `let`, `defer` placement).

**What-would-you-guess.** For users who say they know nothing: "If you had to guess how X is implemented, what would you say?" Almost always surfaces an adjacent mental model you can build on or correct.

**Sketch-the-mechanism.** For non-code topics (protocols, tool workflows, system architecture): "Draw me the sequence — what talks to what, in what order?" Text diagrams are fine. The gaps in the sketch are the gaps in the model.

## Production probes (after teaching)

**Teach-it-back.** "Explain that to me as if I'm the one learning it." Listen for hedging ("it sort of..."), skipped steps, and places where they reach for the example instead of the principle. Those are the soft spots.

**Write-from-memory.** "Without scrolling up, write the version that does X." The closest thing to a real retention test. Works for anything with a concrete artifact — code, config, a command, a query.

**Fill-the-gap.** Give a snippet with one critical part removed and ask them to fill it in. Lower stakes than write-from-memory; good for micro-sessions or when confidence is low and you want a win before pushing harder.

**Spot-the-bug.** Give working-looking code with one subtle misuse of the concept just taught. This is the level-4 test. If they can find it, they understand the concept well enough to recognize its violation — which is stronger than being able to use it correctly.

**Transfer.** "How would this change if [one constraint is different]?" Change the input type, the scale, the language, the failure mode. A concept that only works in the original example isn't a concept yet; it's a memorized example.

**Explain-the-why.** Not "what does it do" but "why is it designed this way — what problem does it solve?" People who can answer this retain the *what* almost for free, because it stops being arbitrary.

## Calibration moves

**Confidence-before-answer.** Ask for a 1–5 confidence rating *before* they attempt a retrieval question, not after. Post-hoc ratings are contaminated by having just seen the answer.

**Bet-on-it.** "Would you bet on that?" Informal, but it snaps people out of casual agreement and makes them actually check.

**Explain-your-confidence.** When someone is highly confident and wrong, ask what made them confident before correcting. The faulty reasoning is the real target; the wrong answer is a symptom.

## Structuring moves

**Interleave.** In a deep dive with several chunks, mix retrieval questions from earlier chunks into later ones rather than testing each chunk in isolation. Interleaved practice feels harder and produces better retention — the difficulty is the point.

**Contrast cases.** When a concept is often confused with a neighbor (`==` vs `is`, `Mutex` vs `RwLock`, `map` vs `flatMap`), teach them side by side and probe the boundary. Confusable pairs need the boundary made explicit or they merge in memory.

**Worked example → faded example → problem.** For procedural skills (writing a recursive function, setting up a build pipeline): show a full worked example, then one with steps removed, then a bare problem. Fade the scaffolding across chunks.

## When a topic isn't code-snippet-shaped

Protocols, tool workflows, mental models, and architectural concepts don't always have a 5-line snippet to predict. Substitute:

- **Sketch-the-mechanism** for predict-the-output
- **Walk-me-through** ("narrate what happens when I run `git rebase -i`") for write-from-memory
- **What-breaks-if** ("what fails if the client skips the handshake step?") for spot-the-bug
- **Compare-to-known** ("how is this like/unlike HTTP keep-alive?") for transfer

The metacognitive logic is identical — commit to a model, test it, notice the gap — only the artifact changes.

## When feedback is slow

Languages and libraries give feedback in seconds: run it, see it. Distributed systems, performance, security, and operations don't — the failure shows up under load, at 3am, or never in the toy. The workbench principle still holds; what changes is that you have to *build the fast feedback loop* before you can practice inside it.

**Build a harness that makes it fast.** A local cluster in containers with a fault injector (kill a node, partition the network, add latency) turns "what happens when the leader dies" from a thought experiment into a ten-second experiment. A replay harness that feeds recorded traffic turns "how does this behave under a burst" into something you can run twenty times. A benchmark with a profiler attached turns "is this the slow part" into a number. Spend the first session building the harness — it's the workbench for the topic, and building it teaches half the topic anyway.

**Postmortem as prediction probe.** Public incident reports are the best predict-before-reveal material there is. Give the learner the setup and the symptoms, stop before the root cause, and ask what they think happened and what they'd check first. Then read the finding. The gap between their guess and the real cause is exactly the mental model that needs work, and it comes with a real story attached, which is what makes it stick.

**Design-review probe.** Show a design — a schema, an API, a deployment topology — and ask what a senior reviewer would flag. Then compare against a real review, or against what actually went wrong later. This is the level-4 "spot the bug" for judgment-heavy topics.

**What-breaks-first.** "This system is at 10x load. What fails first, and how would you know?" Forces them to hold the whole system in their head and reason about bottlenecks, which is most of what expertise in these areas *is*.

**Bring the real thing in.** For these topics more than any other, the learner's actual systems are the best material. A real trace, a real slow query, a real alert that fired last week — used as the exercise — beats any constructed example, and it's the bridge to graduation.
