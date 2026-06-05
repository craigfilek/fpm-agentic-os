---
name: level-up
description: The weekly self-evolution ritual. Surfaces one workflow worth building, ships it into the right department, and has that department's manager improve its existing workflows from real run-logs. One run = one shipped workflow + one improvement. This is how the system builds itself over time, one piece at a time — never an org chart drawn up front.
---

# /level-up — the system evolves itself

Run this weekly. One run ships **one** new workflow and improves **one** existing
one. Departments and manager agents are not designed up front — they **accrue**, one
workflow at a time. (Nate Herk's rule, which we keep: *workflows beat agents; boring
is beautiful.*)

## 1. Health check (30 seconds, read-only)

- Glance at the **Four Cs**: Context (does `CLAUDE.md` know them?), Connections
  (`connections.md`), Capabilities (what's in `departments/`), Cadence (anything
  scheduled?). Name the weakest C in one line — that's where leverage hides.
- List the departments that exist and which workflows ran since last time
  (`departments/*/workflows/*/runs/`).

## 2. Find the one workflow (the Method)

Walk them through it, one question at a time:
- **Find the constraint** — what cost the most time/energy this week?
- **EAD** — can we *Eliminate* it, *Automate* it, or *Delegate* it? (Prefer eliminate.)
- **Map the process** — the literal steps they do by hand today.
- **Autonomy level** — does the agent draft-for-approval, or just-do-and-tell?
- **Tie to an outcome** — what does "this worked" look like?

Pick exactly **one**. If nothing clears the bar, ship nothing — that's a valid week.

## 3. Ship it into a department

- **Route it.** Which department owns this? (sales, ops, content, finance, …). If the
  right one doesn't exist, **create it**: copy `departments/_template/` →
  `departments/<name>/`, and fill its `MANAGER.md` charter (what it owns, the outcome
  it's accountable for).
- **Build the workflow** as `departments/<name>/workflows/<workflow>/`:
  - `CONTEXT.md` — the stage-contract (Inputs / Process / Outputs). This is the spec.
  - the actual workflow (a prompt, a checklist, or — if it's code — build it with the
    gStack lane: `autoplan` → `ship`).
  - a `runs/` folder where each execution drops its output + a one-line outcome note.
- **Set autonomy** per step 2. Default: draft-for-approval until it's proven.

## 4. The manager improves its own workflows (self-evolution)

Hand off to the department's manager (the `MANAGER.md` charter is its brief). It does
a **retro** on that department only:
- Read the `runs/` logs of its existing workflows — what produced good outputs, what
  needed correction.
- Propose **one** concrete improvement (tighten a CONTEXT.md step, fix a recurring
  miss, raise an autonomy level that's earned trust).
- Apply it. Log it. Where present, lean on `gstack-retro` + `gstack-learn` and
  fpm-ai's council to do the reasoning — don't reinvent them.

One improvement per run. Compounding beats sweeping.

## 5. Log + (optional) put it on cadence

- Append to `decisions/log.md`: the workflow shipped + the improvement made.
- **Cadence is opt-in, never default.** If they want it to evolve *while they're
  away*, schedule the manager retros (and a `/level-up` nudge) via Hermes cron — one
  line, and only for workflows that already work manually. No daemon runs unasked
  until a human has watched it work. (That guardrail is what keeps this from becoming
  the apparatus that sank the last system.)

> A department is a **folder**. A manager is a **charter + a retro you run** (or
> Hermes fires). Not a swarm of always-on agents. Start with none; grow one at a time.
