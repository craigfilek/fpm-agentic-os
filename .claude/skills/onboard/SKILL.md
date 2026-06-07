---
name: onboard
description: One-time setup. Interviews the owner, fills their operating manual + context folder, and (if installed) seeds gbrain — so the system knows who it works for. Featherweight; works the instant you have Claude Code, no install required. Re-run any time to refresh from aios-intake.md.
---

# /onboard — the system sets itself up

You are standing this agentic OS up for the person in front of you. Goal: in ~15
minutes, with **zero infrastructure**, give them a system that knows who they are
and how they work. This is Tier 0 — markdown only, works before any install.

## Step 0 — lay the JVC structure FIRST (before you ask anything)
Structure precedes content. Run JVC right away:
1. Copy `starter/CONSTITUTION.md` → the workspace root `CLAUDE.md` — the folder standard that governs everything (code flat · thinking in the vault · gbrain prefix = recall lens). Every later file cascades inside it.
2. Read `starter/jvc-method-card.md` **if present** to channel Jake Van Clief's voice + the folders-over-agents pattern. (It's held from the public ship — Jake's paid course; the Constitution carries the high-level pattern either way, so don't block if it's absent.) If a vault exists, also read `Wiki/JVC`.
3. Use the `/jvc` skill to lay the folder skeleton — each project folder gets its own `CLAUDE.md`.
THEN do the interview below.

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

## Write the files (the Day-1 set — the FOUR core files)

**First — archive-recon (if a prior build exists):** if there's an archive — a frozen
build (`~/Obsidian Vault/98 Build*/`), an old `CLAUDE.md`/`SOUL.md`, or memory at
`~/.claude/.../memory/` — **READ it to inform the files, but write FRESH (never copy
stale).** A returning owner gets richer files from their archive than from re-interviewing.
A brand-new owner: skip this, use the interview answers.

Create/overwrite, **their words lightly cleaned — never paraphrase**:

- **`CLAUDE.md`** — the operating manual (the Step-0 root router + their identity, voice
  rule, decision rights, current priorities). Every agent reads this first.
- **`SOUL.md`** — who they are at the core: essence, values, voice, what the work is *for*.
  Built from Vision + Voice + "what's this all for" (+ the archive if present). The deeper
  layer beneath CLAUDE.md.
- **`FOCUS.md`** — the north star (what the system should *produce*) + the 2–3 priorities
  this month + the first thing they'll build. The "where we're pointed" file.
- **Seed the memory** — create `memory/MEMORY.md` (the index) + one short memory file per
  durable preference they gave (voice, KPI, decision-rights, work-style, what-to-avoid…).
  This is the starting brain; it grows from use.
- `context/about-you.md`, `context/voice.md`, `context/vision.md` — the long-form.
- `connections.md` — systems to reach (wired / not yet).
- Append the date + "onboarded" to `decisions/log.md`.

**Then prove it:** run `bin/test-onboard` (or `bin/test-all`) — it confirms all four core
files exist + are non-empty + carry their expected anchors. Green = the owner is set up.

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
