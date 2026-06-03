# AGENTS.md — Read this first

**You are the agent that just loaded this repo.** Your job: stand up a complete
7-component agentic OS for the person in front of you, who is **not technical**
(assume the 83-year-old-mom test), and get them to "it works" almost instantly.

Follow the phases below in order. Do not improvise architecture. When you need a
human action you cannot take (a click, a password, an API-key signup), ask for it
in plain English and wait.

**If you were handed only a URL:** clone it first (`git clone <url>`), then run everything below from inside that folder. You drive the entire setup yourself — the install, walking them through the two API keys (where to sign up, what to paste), and conducting the CEO interview at the end. They should only ever answer questions and approve. Never make them open a file or run a command themselves.

---

## 0. How to talk to this person (hard rule)

Talk like a precocious 11th-grader who's built rapport with them — sharp, fast,
no jargon, no babying. You are their **hands in human land**: they click the
buttons and paste the keys you can't. So:

- **Low jargon.** Spell out an acronym once, then move on. Never say "MCP" or
  "PGLite" without a five-word translation.
- **Short steps with the reason attached**, so they can judge whether to skip.
- **One question at a time.** Never dump a form.
- **Yes/no clear** when a choice is binary.
- When they just need to push a button, don't lecture. Read the room.

---

## 1. What you're building (say this in plain English if asked)

Seven pieces that work together as a second brain plus an always-on assistant:

| # | Piece | Plain-English job |
|---|---|---|
| 1 | **fpm-ai** | The control layer. Runs careful AI workflows and double-checks its own work before you see it. (Python, `fpm` command.) |
| 2 | **Hermes** | The runtime + messenger. Talks to you via Telegram and runs scheduled jobs. (Python.) |
| 3 | **gbrain** | The memory. Remembers everything and answers with citations. (Runs locally, no cloud needed.) |
| 4 | **Obsidian** | The notes app where the human reads and writes. |
| 5 | **stack-primer** | A web-app starter kit (for building products later). |
| 6 | **gStack** | 58 ready-made commands for planning, building, QA, and shipping. Pairs natively with gbrain. |
| 7 | **fpm-ai-os** | This repo — the install manual + design log. |

The simple frame (the **Four Cs**, a term from Nate Herk™):
**Context** (it knows you → gbrain + the interview) ·
**Connections** (it reaches your stuff → Gmail, Drive, Telegram) ·
**Capabilities** (it does the work → fpm-ai + gStack) ·
**Cadence** (it runs unasked → Hermes cron).

---

## 2. The sequence (drive this start to finish)

### Phase A — Recon (know before you touch)

Check what already exists so you don't redo finished work:

```bash
ls -d ~/fpm-ai ~/hermes-agent ~/gstack ~/stack-primer 2>/dev/null
~/.bun/bin/gbrain --version 2>/dev/null
~/hermes-agent/.venv/bin/hermes --version 2>/dev/null
ls ~/.claude/skills 2>/dev/null | grep -c gstack
```

Tell the human in one sentence what's already in place vs. fresh.

### Phase B — Install (the one command)

The whole stack installs from `install.sh` in this repo. On a fresh Mac:

```bash
curl -fsSL https://raw.githubusercontent.com/craigfilek/fpm-ai-os/main/install.sh | bash
```

What to tell the human while it runs (~30 min):
- macOS will ask for their **Mac password once** (Homebrew authorizing itself — the
  same prompt as installing any app). They type it, press Enter.
- Near the end the script asks them to **paste their Anthropic API key** (input is
  hidden). If they don't have one, send them to
  `https://console.anthropic.com/settings/keys`, have them create one, paste it.
- Everything else is automatic: it installs the runtimes, clones the repos,
  stands up the memory, and wires the pieces together.

**If `install.sh` fails partway:** it's safe to re-run — every step checks
"already done?" first. A few steps are marked `[VERIFY-LIVE]` in the script
(Homebrew sudo, the Claude Code install channel, Telegram); if one of those is
the failure, read that block and resolve it before re-running.

### Phase C — Verify each piece (don't trust, check)

Run these and confirm each is green before moving on. Report results plainly.

```bash
# 1. API key works (expect output containing PING!)
set -a; source ~/.env.anthropic; set +a
python3 -c "from anthropic import Anthropic; print(Anthropic().messages.create(model='claude-opus-4-7', max_tokens=10, messages=[{'role':'user','content':'PONG'}]).content[0].text)"

# 2. memory is alive
~/.bun/bin/gbrain doctor --json

# 3. runtime sees the memory (expect a line containing gbrain)
~/hermes-agent/.venv/bin/hermes mcp list | grep gbrain

# 4. Claude Code sees the memory too
claude mcp list 2>/dev/null | grep gbrain

# 5. the 58 build/ship commands are installed
ls ~/.claude/skills | grep -c gstack
```

If a check fails, fix that one piece before continuing — see Troubleshooting.

### Phase D — The CEO interview (teach the system who they are)

This is what makes the OS *theirs*. Open the file `ceo-interview.md` in this repo
and run it through Hermes:

1. Start a Hermes session that can reach the memory tools. **Use the full agent,
   not the fast one-shot:**
   ```bash
   ~/hermes-agent/.venv/bin/hermes chat
   ```
   (The `hermes -z` one-shot does NOT load memory tools — don't use it here.)
2. Paste `ceo-interview.md` as context.
3. Ask the five sections **one question at a time** (Vision, Priorities, Working
   Style, Decision Rights, Success Metrics). Reflect each answer back in one
   sentence. Push vague answers: "Give me a specific example."
4. When done, write one gbrain page per section (their words, lightly cleaned —
   no paraphrase), then pull durable facts into the fact store.
5. Show them the five page titles and ask: **"Approve, edit, or scrap?"** Do not
   finalize until they say approved.

### Phase E — Hand off

Tell them, plainly, what they now have and the three ways to use it day-1:
- Type `fpm` in the terminal to see their workflows.
- Type `hermes` to talk to their assistant.
- Open Obsidian and just start writing — the system is watching.

Then ask the one question that matters: **"What do you want to do first?"** Don't
assume.

---

## 3. Guardrails (do NOT violate)

1. **Don't rebuild the old sprawl.** A previous version of this rig drowned in
   custom skills/hooks/scripts and got deliberately nuked. If something feels
   missing, write a one-line memory note — **do not** rebuild a custom skill
   stack.
2. **Secrets discipline.** Never hardcode or echo an API key. Keys go only into
   `~/.hermes/.env` / `~/.env.anthropic` via a hidden prompt. Never read, print,
   or commit a `.env` file.
3. **Never touch your own private product repos.** Those are live products, not
   part of this OS. They are intentionally excluded from `install.sh`.
4. **Verify, don't relay.** Don't tell the human something works because a script
   "should" have done it. Run the Phase-C check and report what you actually saw.
5. **Reversible by default.** Don't delete or overwrite their existing files.
   `install.sh` is built to be idempotent; keep it that way.

---

## 4. Troubleshooting (the common ones)

| Symptom | Fix |
|---|---|
| API check returns `401` | The key is bad. Have them make a new one at console.anthropic.com/settings/keys and re-paste. |
| `gbrain` "command not found" | PATH issue. Run `export PATH="$HOME/.bun/bin:$PATH"` and retry, then add it to their shell file. |
| `hermes mcp list` shows no gbrain | Re-run the wiring step: `hermes mcp add gbrain --command ~/.bun/bin/gbrain --args serve`. |
| Hermes can't see memory in a one-shot | You used `hermes -z`. Use `hermes chat` (full agent) — only it loads memory tools. |
| `gbrain search` returns nothing useful | Embeddings need a provider key (Voyage or OpenAI) set before sync. Without one, search degrades. |
| Telegram not working | It's optional and set up later: `hermes gateway setup` (needs a bot token from @BotFather), then `hermes gateway install`. |
| Obsidian memory bridge | Open the Obsidian app first (its local server only runs while it's open), then wire it. |

---

## 5. Pointers

- `install.sh` — the actual installer (read it to know exactly what runs).
- `INSTALL.md` — the human-facing one-page install guide.
- `DESIGN.md` — why the OS is shaped this way (the decision log).
- `ceo-interview.md` — the five-section interview script for Phase D.
- `README.md` — the Obsidian second-brain setup (notes layer), plus the quick start.
- `claude-settings.json` + `statusline.py` + `claude-memory/` — the safety + behavior baseline `install.sh` (step 18) lays into `~/.claude`: **auto-compact OFF** (PreCompact hook + env override), `.env`/`.ssh` deny rules, destructive-command guards (rm -rf, git push/commit, gh), `plan` default mode, statusline, and the starter house-rule memories (verify-don't-relay, minimal-over-complex, Elon's 5 steps, voice, …). Existing settings are backed up, memories never clobbered.
