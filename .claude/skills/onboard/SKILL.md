---
name: onboard
description: One-time setup. Interviews the owner, fills their operating manual + context folder, and (if installed) seeds gbrain — so the system knows who it works for. Featherweight; works the instant you have Claude Code, no install required. Re-run any time to refresh from aios-intake.md.
---

# /onboard — the system sets itself up

You are standing this agentic OS up for the person in front of you. Goal: in ~15
minutes, with **zero infrastructure**, give them a system that knows who they are
and how they work. This is Tier 0 — markdown only, works before any install.

## How to run

1. **If `aios-intake.md` already has answers** (they edited it), read it and skip
   straight to "Write the files" — no need to re-ask. Otherwise, interview them.
2. **Interview — one question at a time.** Talk like a sharp 11th-grader, no jargon.
   Reflect each answer back in one sentence. Push vague answers: "Give me a specific
   example." Cover these (this is the CEO interview — see `ceo-interview.md` for the
   long form):
   - **Who you are** — name, what you do, how you spend your time.
   - **Voice** — ask them to paste 2–3 samples of how they actually write (pasted
     beats described). If they'd rather not, don't block: capture the *rule* they
     state, write it to `context/voice.md` with a clear "samples pending" note, and
     move on. They can paste samples and re-run any time.
   - **Vision** — what your work is *for*, in one coffee-shop sentence.
   - **Priorities** — the 2–3 things that must move this month.
   - **Decision rights** — what agents decide alone, surface, or just-do-and-tell.
   - **Connections** — what systems they'd want it to reach (Gmail, Drive, Telegram,
     calendar…). Don't wire them yet; just list them.

## Write the files (the Day-1 set)

Create/overwrite, using **their words, lightly cleaned — never paraphrase**:

- `CLAUDE.md` — the operating manual. Top section: who they are, their voice rule,
  their decision rights, their current priorities. Every agent reads this first.
- `context/about-you.md`, `context/voice.md`, `context/vision.md` — the long-form.
- `connections.md` — the registry of systems to reach (status: wired / not yet).
- Append the date + "onboarded" to `decisions/log.md`.

**Bridge to the engine (only if present):** if `~/.bun/bin/gbrain` exists, index each
context file into *their* brain so recall works over the answers — one per file:
`gbrain put context/about-you < context/about-you.md` (and the same for `voice`,
`vision`). If gbrain isn't installed, skip silently — the markdown is the source of
truth either way.

**Safe-by-default:** the files you write (`CLAUDE.md`, `context/*`) are git-ignored by
the kit's `.gitignore`, so they never ship even if they push the repo. Still: never
run `git add .` on their instance, and never push their personal answers anywhere.

## Close — hand off the two verbs

Tell them, plainly:
- **CAPTURE:** drop anything into `context/` or (if installed) run `capture <x>`.
- **RECALL:** just ask me — "what did I say about ___?"
- **In a week, run `/level-up`** — that's how the system grows itself, one workflow
  at a time.

Then ask: **"What do you want to do first?"** Don't assume.

> Re-running `/onboard` is safe: it refreshes from `aios-intake.md` and never
> deletes their work. Boring is beautiful.
