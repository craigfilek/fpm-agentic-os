---
name: router
description: The board router — "where is each project, and what's the single best next move?" Reads your project folders + BUILD-QUEUE.md, marks each on its lifecycle, stars ONE move (EROS-weighted), and on "go" routes that move into the gstack build chain (office-hours → autoplan → review → ship). Points; never an engine. Replaces /gsd (eradicated 2026-06-11). Trigger on "/router", "what's next", "what should I work on", "project board", "the one thing".
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Edit
  - Write
---

# /router — what's next (the thin face on the gstack engine)

One job: **where is each project, and what's the single best next move?** The router points; gstack builds. It never becomes an engine itself.

## Steps
1. **Read your project folders** (the rooms under your map). Infer each one's stage from what's actually in the folder — the work IS the status. Don't demand a `stage:` field.
   Also skim **`01 Projects/BUILD-QUEUE.md`** (top-ROI rows only — it's ROI-sorted; the belt parks
   build-bucket chunks there). Its best rows COMPETE for the star like any project's next step.
   Skip rows with `near` below 1.0 when starring — they're third-party inspiration (someone
   else's business in a video), not Craig's build; they stay on the board as reference only.
   Why: the queue is where dumped build ideas land; without this read it's a parking lot with no
   exit ramp (wired 2026-06-11 on Craig's go).
2. **Show one box** per project (or the whole board): the stage, then three options with one starred (★) and a one-line why it beats the runner-up. If a queue row out-pulls every project move, star the queue row — say which feature it nests under.
3. **On "go"** (or you pick a move): route the ONE starred move into the gstack chain —
   a. `/gstack-office-hours` shapes it (pushback + narrowest wedge),
   b. `/gstack-autoplan` plans it with auto-reviews,
   c. `/gstack-ship` lands it (tests, review, commit, PR).
   Small moves (a file edit, a tidy) skip the chain — just hand ready-to-run instructions to Claude Code. Then stop.

## Build-project lifecycle (the 9 steps, off the folder)
For a `kind: build` project, read the lifecycle straight from the files — **a step is done when its file exists.** The folder is the database; no `stage:` field, no DB.

| Step | Done when… |
|------|-----------|
| RECON | the folder + `CLAUDE.md`/`CONTEXT.md` exist |
| DISCUSS | `PRD.md` has a `## Structural Tension` with a DO |
| RESEARCH | `reference/` holds ≥1 source |
| PRD | `PRD.md` exists |
| PLAN | `CONTEXT.md` (or the PRD) has a build loop + next action |
| EXECUTE | `lab.md` has ≥1 run, or real work files exist |
| VERIFY | `lab.md` has a run with `Verdict: keep` (kill-line passed) |
| WTD | that run's result was checked against the real artifact |
| COMMIT | `git log` references the project path |

Grid: **Discovery** (RECON·DISCUSS·RESEARCH) · **Build** (PRD·PLAN·EXECUTE) · **Ship** (VERIFY·WTD·COMMIT). Mark `●` done · `◐` current · `○` pending. **Star the first pending step** — weight by **EROS**.

## EROS — star by the forward pull (not just by order)
Decay (the board) prunes what's dead; **EROS is the router's selection bias** — it stars the move that's *pulling*, not just the next in line. Weight the star by:
a. **Alive** — is it in a humming constellation / recently reinforced? Dead-quiet work waits.
b. **Cashflow-near** — does it pull toward money (the Hormozi lens)? That earns the gravity bonus.
c. **Drawn-to** — does Craig recognize it / want it? (Projector-fit: follow the yes, not the should.)
Then **lower activation energy**: present the starred move as already-decided and attractive — one yes to start, not a push. The lifecycle says what's *next*; EROS says what's *alive and worth it*. When they disagree, surface both and let the pull win.

## The one-thing lock (optional)
Keep ONE target locked until it's done. New tasks that fall out get parked *under* it — they never displace the one thing. Only you swap the target.

## Rules
- Point, don't run. No auto-chaining past the chain hand-off, no looping. Your next "go" restarts it.
- Undo-able tidying (refresh the board, archive a dead project) → just do it + log one line. Anything that costs (ship, delete, merge) → wait for "go".
- One starred move at a time. **Never hand someone a queue to clear.**
- No new store, no database — your folders + files are the truth.
