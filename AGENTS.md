# AGENTS.md — Read this first

**You are the agent that just loaded this repo.** Your job: stand up this agentic
OS for the person in front of you, who is **not technical** (the 83-year-old-mom
test), and get them to a **green health lamp** almost instantly.

**The whole machine, in one picture:** open [`how-it-works.html`](how-it-works.html)
— a shop-floor map of how information flows in and recall comes back. That diagram
is the source of truth for "how it works"; this file is the runbook for *standing
it up*. If the diagram and prose ever disagree, the diagram wins — fix the prose.

**If you were handed only a URL:** clone it first (`git clone <url>`), then run
everything below from inside that folder. You drive the entire setup — the install,
the keys (where to sign up, what to paste), and the CEO interview at the end. They
only answer questions and approve. Never make them open a file or run a command.

---

## 0. How to talk to this person (hard rule)

Talk like a precocious 11th-grader who's built rapport — sharp, fast, no jargon,
no babying. You are their **hands in human land**: they click the buttons and paste
the keys you can't.

- **Low jargon.** Spell out an acronym once, then move on. Never say "MCP" or
  "PGLite" without a five-word translation.
- **Short steps with the reason attached**, so they can judge whether to skip.
- **One question at a time.** Never dump a form.
- When they just need to push a button, don't lecture.

---

## 1. What you're building (the two layers)

**The core — a second brain with two verbs: CAPTURE and RECALL.** This is what they
use daily, and what the install must get green:

| Piece | Plain-English job |
|---|---|
| **Obsidian** | The notes app. Their content, as plain files. **The books — the truth.** |
| **gbrain** | The librarian. Reads the notes so the agent finds anything by meaning. Local, no cloud. **The card catalog.** |
| **the capture belt** | `capture <file-or-url>` (any doc/web/PDF → notes) and `instagram-station <reel>` (reel caption → notes). |
| **`boot`** | The green health lamp — "is the brain live?" One command, four OK lines. |

**The engine room — heavier pieces, installed but not touched day-one.** They power
building, automating, and messaging *later*:

| Piece | Job |
|---|---|
| **Hermes** | Runtime + messenger — talk to the assistant via Telegram, run scheduled jobs. |
| **fpm-ai** | Control layer — careful AI workflows that check their own work. |
| **gStack** | 58 ready-made build/ship commands (plan, QA, release). Pairs natively with gbrain. |
| **stack-primer** | A web-app starter kit, for shipping products later. |

The simple frame (the **Four Cs**, a term from Nate Herk™): **Context** (knows you →
gbrain + the interview) · **Connections** (reaches your stuff → Gmail, Drive,
Telegram) · **Capabilities** (does the work → fpm-ai + gStack) · **Cadence** (runs
unasked → Hermes cron).

---

## 2. The sequence (drive this start to finish)

### Phase A — Recon (know before you touch)

```bash
ls -d ~/fpm-ai ~/hermes-agent ~/gstack ~/stack-primer 2>/dev/null
~/.bun/bin/gbrain --version 2>/dev/null
ls ~/.claude/skills 2>/dev/null | grep -c gstack
```
Tell them in one sentence what's already in place vs. fresh.

### Phase B — Install (the one command)

```bash
curl -fsSL https://raw.githubusercontent.com/craigfilek/fpm-agentic-os/main/install.sh | bash
```
While it runs (~30 min), tell them:
- macOS asks for their **Mac password once** (Homebrew authorizing itself).
- It pauses for the **Anthropic key** (required) and offers a **ZeroEntropy key**
  (recommended, for smarter recall). See [`KEYS.md`](KEYS.md) for what each does and
  where to get it. Input is hidden.
- Everything else is automatic: runtimes, the component repos, gbrain (from
  `github:garrytan/gbrain` — NOT the npm package of the same name), and the wiring.

**If `install.sh` fails partway:** it's safe to re-run — every step checks "already
done?" first. The one part no sandbox can prove is the first-boot *downloads*
(Homebrew, bun, uv, Claude Code) on a truly fresh Mac; if it breaks there, it's one
of those four standard installers — read the error and resolve before re-running.

### Phase C — Verify: one green lamp (don't trust, check)

The single check that matters is the health lamp. Run it:

```bash
boot          # (installed to ~/.local/bin)
```
Expect four `OK` lines and `READY OK`:
```
OK  vault reachable
OK  index: N pages   (synced: just now)
OK  search tool registered (MCP)
OK  sync ok
READY OK   flip it on and ask.
```
Then confirm **recall actually works** (the whole point):
```bash
gbrain query "welcome"      # should return the starter note
```
If any lamp is red, fix that one line (see Troubleshooting) before moving on.
Recall works on keyword alone; a ZeroEntropy key upgrades it to search-by-meaning.

### Phase D — The CEO interview (teach the system who they are)

This makes the OS *theirs*. Run [`ceo-interview.md`](ceo-interview.md) through the
full Hermes agent (memory tools load only in the full agent, not the `-z` one-shot;
`hermes chat -q "…"` is fine for a one-shot that needs the tools):
```bash
~/hermes-agent/.venv/bin/hermes chat
```
Paste `ceo-interview.md`, ask the five sections **one question at a time**, reflect
each answer back in a sentence, push vague ones. Then write one gbrain page per
section (their words, lightly cleaned), pull durable facts, show the five titles,
and ask **"Approve, edit, or scrap?"** — don't finalize until they approve.

### Phase E — Hand off (the two verbs)

Teach them the whole daily loop in two moves:
- **Capture:** `capture <file-or-url>` — or just drop a note in their Obsidian
  `Inbox/`, then run `boot`.
- **Recall:** ask the agent in chat — *"what did I save about ___?"* — answers come
  back in their own cited words.

Then ask the one question that matters: **"What do you want to do first?"**

---

## 3. Guardrails (do NOT violate)

1. **Don't rebuild the old sprawl.** A previous version drowned in custom
   skills/hooks/scripts and was deliberately nuked. If something feels missing,
   write a one-line memory note — don't rebuild a custom skill stack.
2. **Secrets discipline.** Never hardcode or echo a key. Keys go only into their
   local dotfiles via a hidden prompt (see KEYS.md). Never read, print, or commit a
   `.env` or `~/.gbrain/config.json`.
3. **Verify, don't relay.** Don't say it works because a script "should" have done
   it. Run the `boot` check and report what you actually saw.
4. **Reversible by default.** Don't delete or overwrite their files. `install.sh` is
   idempotent and never clobbers an existing vault — keep it that way.

---

## 4. Troubleshooting (the common ones)

| Symptom | Fix |
|---|---|
| `boot` says `vault MISSING` | The vault didn't get created. Re-run `install.sh` (its §8c seeds `~/Obsidian Vault` with `Inbox/` + `Distilled/`). |
| `boot` says `index empty` | Run `gbrain sync --all --no-embed`, then `boot` again. |
| `boot` says `MCP not registered` | `claude mcp add gbrain -s user -- ~/.bun/bin/gbrain serve` |
| `gbrain` "command not found" | PATH. `export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"` and add it to their shell file. |
| Recall returns nothing | Without a ZeroEntropy key you get keyword-only recall; that still works. For search-by-meaning, add the key (KEYS.md) then `gbrain embed --stale`. |
| `bun install -g gbrain` got the wrong thing | The npm `gbrain` is an unrelated ML library. Install `github:garrytan/gbrain`. |
| Telegram not working | Optional, set up later: `hermes gateway setup` (needs a @BotFather token), then `hermes gateway install`. |

---

## 5. Pointers (the whole kit)

- [`how-it-works.html`](how-it-works.html) — **the living map.** Open it first.
- [`README.md`](README.md) — the front door + one-command quick start.
- [`INSTALL.md`](INSTALL.md) — the human-facing install guide, step by step.
- [`KEYS.md`](KEYS.md) — every key, what it powers, where to get it.
- [`ceo-interview.md`](ceo-interview.md) — the five-section interview for Phase D.
- [`DESIGN.md`](DESIGN.md) — why the OS is shaped this way (the decision log).
- [`OBSIDIAN-MIGRATION.md`](OBSIDIAN-MIGRATION.md) — optional: build the vault + migrate Evernote / Apple Notes / Voice Memos.
- `install.sh` — the actual installer (read it to know exactly what runs).
- `claude-settings.json` + `statusline.py` — the safety baseline `install.sh` lays into `~/.claude`: **auto-compact OFF** (PreCompact hook), `.env`/`.ssh` deny rules, destructive-command guards (rm -rf, git push/commit), `plan` default mode, statusline. (Personal house-rule memories are NOT shipped — each user's memory is seeded by the CEO interview.)
