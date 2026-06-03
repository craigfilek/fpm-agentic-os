# CEO Interview — Hermes onboards you as founder

**Purpose:** Hermes interviews you (one question at a time, conversational)
to extract your vision, priorities, working style, decision rights, and success
metrics — then seeds gbrain so every agent starts with ground truth.

**How to run:**
1. Open a fresh Hermes session and paste this file as context.
2. Hermes asks one question, listens, reflects back in one sentence, then moves on.
3. Vague answers get pushed: "Give me a specific example." Don't settle.
4. After all five sections, Hermes writes gbrain pages (see Closing).

---

## 1. Vision

- What is your product *actually* for — in one sentence you'd say to a stranger
  at a coffee shop, not a pitch deck?
- Who is the primary person it serves, and what does their life look like
  *after* it works?
- What has to exist about this that no one else will build?

## 2. Current Priorities

- What are the two or three things that *must* move this month for you to feel
  the company is alive?
- What is currently broken or stuck that is costing you the most time or
  energy?
- What are you deliberately *not* working on right now, and why?

## 3. Working Style

- How do you think best — talking it out, writing, building, or something else?
- What does a great day look like structurally (time, context switches, energy)?
- What do agents or collaborators do that drives you crazy? What do they do
  that makes you trust them immediately?

## 4. Decision Rights

- Which decisions do you make alone, no input needed?
- Which decisions do you want agents to surface but not act on without
  your sign-off?
- Which decisions can agents just handle and tell you after?

## 5. Success Metrics

- Six months from now, what one number or outcome would make you say
  "we're on track"?
- What would make you say the whole thing was a mistake?
- How will you know when gbrain is actually useful vs. just noise?

---

## Closing — storing answers in gbrain

After the interview, Hermes:

1. Calls `put_page` once per section (Vision, Priorities, Working Style,
   Decision Rights, Success Metrics) — title = section name, body =
   your words lightly cleaned, no paraphrase.
2. Calls `extract_facts` on each page to pull durable facts (names,
   numbers, non-negotiables) into the fact store so any agent can query
   them cold.
3. Shows you the five page titles and asks: "Approve, edit, or scrap?"
4. Does NOT finalize until you say approved.
