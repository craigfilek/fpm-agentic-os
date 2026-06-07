# CEO Interview — the JVC setup (answer these, your OS builds itself)

**Purpose:** these are the questions Jake Van Clief's course makes you answer to stand up a
"folders over agents" system. Answer them once and the installer builds your folder
structure, routing, and the four core files the right way — **no videos required.**

**How to run:** one question at a time, conversational. Talk like a sharp 11th-grader, no
jargon. Reflect each answer back in one sentence. Push vague answers: "Give me a specific
example." If `aios-intake.md` already holds an answer, confirm it instead of re-asking. If a
prior build/archive exists, read it to *inform* the answers — but write fresh.

---

## The big picture
1. What do you ultimately want this system to **produce** for you?

## Who & voice
2. Who are you, and what is this project/work?
3. What role should the AI play for you?
4. How do you actually write/talk? (paste 2–3 real samples — pasted beats described)

## What "good" looks like
5. What does a great result look like — and what should it always **avoid**?
6. What background should it **know** but never act on directly? (references)

## System vs. one-off
7. Are you doing one-off tasks, or building a repeatable system? What's specific to **you**
   that's worth building around (your data, relationships, knowledge)?

## Your workspaces (the heart)
8. What are your **2–4 modes of work**? (the test: would you want the AI to forget what it's
   doing and switch focus? → that's a separate workspace)
9. For each mode: what's it for, the process, what good looks like, what to avoid?

## Routing & naming
10. For a given task — where does it go, and what should it **read vs. skip**? (the routing table)
11. How should files be **named** so it finds and files them with no database?
12. Which tools/skills belong to which workspace?

## Day-to-day & first build
13. How will you use it day-to-day — building vs. thinking?
14. What's the **first real thing** you'll build with it?

## Sorting / opt-in (basic setup)
- **Connections** — what systems should it reach? (Gmail, Drive, Telegram, calendar…) List, don't wire yet.
- **Decision rights** — what do agents decide alone · surface for your yes · just-do-and-tell?
- **Keys check** — the install collected the required key(s). If `bin/doctor` is green, skip.
  If one was skipped, see `KEYS.md` for where to get it and drop it in, then continue.

---

## Closing — write the four core files + seed the brain
After the interview, write (their words, lightly cleaned — never paraphrase):
1. **`CLAUDE.md`** — operating manual (the Step-0 root router + identity, voice, decision rights, priorities).
2. **`SOUL.md`** — who they are at the core: essence, values, what the work is *for* (from Q1–7 + archive).
3. **`FOCUS.md`** — north star (Q1) + this-month priorities + first build (Q14).
4. **Seed `memory/MEMORY.md`** + one short memory per durable preference.
Plus `context/*` long-form and `connections.md`. If `gbrain` is installed, index each context file.
Show the titles, ask **"Approve, edit, or scrap?"** — don't finalize until they say approved.
Then **prove it:** run `bin/test-onboard` — green = they're set up.
