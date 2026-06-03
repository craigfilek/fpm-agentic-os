# Installing Your Agentic OS

> **The 83-year-old-mom test.** This install assumes you don't know what `git` is, you've never opened Terminal before, and you don't want to. Paste one line, type your Mac password when asked, walk away. When you come back, your CEO is waiting to interview you. That's the whole job.

> **STATUS (2026-06-03)** — `install.sh` is now fleshed out with verified commands and a safe secret prompt, but it has not yet been proven end-to-end on a fresh Mac. A few steps (Homebrew sudo, Claude Code install channel, Telegram, the CEO handoff) are marked VERIFY-LIVE in the script and need one real test run before this is mom-test ready.

> **Build status as of 2026-06-02:** gbrain v0.42.10.0 is up (PGLite + zembed-1 embeddings). fpm-ai memory migrated in (11 pages / 30 chunks, semantic search live). Hermes 0.15.1 installed and wired to gbrain as a stdio MCP server (88 tools, connection verified). Remaining before Phase 1 closes: Anthropic API key in `~/.hermes/.env`; Telegram bot token; Obsidian bridge decision. Phase 2 (one-command installer) not yet started.

---

## What you're installing

A coordinated set of AI tools that work together as your second brain plus an always-on assistant fleet:

- **A personal control layer** that runs verified, opinionated AI workflows (fpm-ai)
- **An agent runtime** that talks to you via Telegram, Discord, Slack and schedules work (Hermes)
- **A memory layer** that remembers everything and synthesizes answers with citations (gbrain)
- **A knowledge surface** where you read and write notes (Obsidian)
- **A web-app scaffold** for shipping your own products (stack-primer)
- **A dev/ship skill toolkit** of 58 role-based Claude Code commands — CEO, designer, eng-manager, QA, release (gStack)

**The four jobs of an agentic OS (the "Four Cs").** Borrowed from the *Four Cs of an AIOS™* (a trademark of Nate Herk), the simplest way to think about what all of the above adds up to:

- **Context** — it *knows you* (your memory layer + the CEO interview)
- **Connections** — it *reaches your stuff* (secure links to Gmail, Drive, Telegram, and more)
- **Capabilities** — it *does the work* (verified workflows and skills)
- **Cadence** — it *runs unasked* (scheduled jobs that fire on their own)

You will meet your **CEO** at the end of the install — an AI agent that interviews you, learns who you are, and configures the rest of the system to your specific way of working. After the CEO interview, your agentic OS knows you. Every assistant in the system reads from the same memory of who you are and what you want.

---

## Prerequisites

A Mac running macOS 13 (Ventura) or later. That is it.

---

## The install — one command, one approval

Open the Terminal app (in `Applications > Utilities`). Paste this exactly:

```bash
curl -fsSL https://raw.githubusercontent.com/craigfilek/fpm-ai-os/main/install.sh | bash
```

Press Enter. macOS will ask for your Mac password ONCE — this is the install authorizing itself to add software, the same prompt you see when installing any new app. Type your password, press Enter.

**Then walk away for about 30 minutes.** The script handles everything from here: installs Homebrew, installs the language runtimes (Bun for JavaScript, uv for Python), installs the helper tools (git, gh, ripgrep, ffmpeg), installs Claude Code, clones the component repositories, runs each component's setup, configures the local servers, and wires everything together.

---

## When you come back

A terminal window will be open with the **CEO interview** in progress. You'll see a question. Type your answer in plain English. Press Enter. The CEO walks you through:

1. **Who you are** — name, what you do for work, how you spend your time
2. **Your voice rule** — how you want the assistants to talk to you (formal, casual, terse, detailed)
3. **Your API keys** — the CEO tells you exactly where to sign up for each one. You sign up; you paste each key when the CEO asks
4. **Your features** — which parts to turn on (Telegram bridge, scheduled retros, voice memos, etc.)
5. **Your first project** — what you actually want this system to help you with

When the CEO finishes, your agentic OS is alive. Everything the CEO learned is written into your memory files, and every assistant in the system reads from them on every task. You never have to re-explain who you are.

---

## After install — your first day

_Section in progress — will link to `OPERATING-MANUAL.md` once it exists._

The short version: open Claude Code, type `fpm` to see your available commands, type `hermes` to start a conversation with your runtime agent, or just open Obsidian and start writing — the system is watching.

---

## If something goes wrong

_Section in progress — common errors and the fix for each._

If the install script fails partway through, you can re-run it safely; it picks up where it left off.

---

## What the install actually did, for the curious

_Section in progress — will link to `DESIGN.md` and a future `ARCHITECTURE.md`._

The component repositories on your disk under your home folder, three local language runtimes, one knowledge graph database, one agent runtime, one personal control framework, and a set of MCP servers wiring them all together inside Claude Code.
