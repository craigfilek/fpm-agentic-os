# Installing Your Agentic OS

> **The 83-year-old-mom test.** This install assumes you don't know what `git` is, you've never opened Terminal before, and you don't want to. Paste one line, type your Mac password when asked, walk away. When you come back, your CEO is waiting to interview you. That's the whole job.

---

## How it works (one picture)

Open **[how-it-works.html](how-it-works.html)** in a browser — a shop-floor map of
the whole thing: notes come in on the left, get filed in your Obsidian vault (the
truth), get indexed by gbrain (the catalog), and an AI agent hands them back on
request. That diagram is the living map; everything below is just how to install it.

## What you're installing

**The core — a second brain with two verbs, CAPTURE and RECALL.** This is what you
use every day:

- **Obsidian** — your notes, as plain files on your disk. The source of truth.
- **gbrain** — a local memory that reads your notes so the agent can find anything by
  meaning (no cloud, runs on your Mac).
- **the capture belt** — `capture <file-or-url>` files anything (docs, web pages,
  PDFs, YouTube) into your notes; `instagram-station` files reel captions.
- **`boot`** — a one-line green health lamp that tells you the brain is live.

**The engine room — installed, but not what you touch day-one.** For building,
automating, and messaging later: **Hermes** (runtime + Telegram messenger + scheduled
jobs), **fpm-ai** (careful AI workflows), **gStack** (58 build/ship commands), and
**stack-primer** (a web-app starter kit).

**The four jobs of an agentic OS (the "Four Cs", a trademark of Nate Herk):**
**Context** (it knows you → gbrain + the interview) · **Connections** (it reaches
your stuff → Gmail, Drive, Telegram) · **Capabilities** (it does the work → fpm-ai +
gStack) · **Cadence** (it runs unasked → Hermes).

You meet your **CEO** at the end of the install — an AI agent that interviews you,
learns who you are, and seeds the memory every assistant reads from. After that, the
OS knows you and you never re-explain yourself.

---

## Prerequisites

A Mac running macOS 13 (Ventura) or later. That is it.

---

## The install — one command, one approval

Open the Terminal app (in `Applications > Utilities`). Paste this exactly:

```bash
curl -fsSL https://raw.githubusercontent.com/craigfilek/fpm-agentic-os/main/install.sh | bash
```

Press Enter. macOS will ask for your Mac password ONCE — this is the install authorizing itself to add software, the same prompt you see when installing any new app. Type your password, press Enter.

**Then walk away for about 30 minutes.** The script handles everything from here: installs Homebrew, installs the language runtimes (Bun for JavaScript, uv for Python), installs the helper tools (git, gh, ripgrep, ffmpeg), installs Claude Code, clones the component repositories, runs each component's setup, configures the local servers, and wires everything together.

---

## When you come back

A terminal window will be open with the **CEO interview** in progress. You'll see a question. Type your answer in plain English. Press Enter. The CEO walks you through:

1. **Who you are** — name, what you do for work, how you spend your time
2. **Your voice rule** — how you want the assistants to talk to you (formal, casual, terse, detailed)
3. **Any keys you skipped** — the install already asked for your Anthropic key (required) and offered a ZeroEntropy key (recommended). If you skipped one, the CEO points you to where to get it (see [KEYS.md](KEYS.md))
4. **Your features** — which parts to turn on (Telegram bridge, scheduled retros, voice memos, etc.)
5. **Your first project** — what you actually want this system to help you with

When the CEO finishes, your agentic OS is alive. Everything the CEO learned is written into your memory files, and every assistant in the system reads from them on every task. You never have to re-explain who you are.

---

## After install — your first day

Everything runs off two verbs. That's it:

1. **CAPTURE** — file anything into your brain:
   ```bash
   capture <file-or-url>          # a doc, a web page, a PDF, a YouTube link
   ```
   Or just drop a note into your Obsidian `Inbox/` folder.
2. **Check the lamp** — confirm the brain is live:
   ```bash
   boot          # four OK lines + "READY OK" = good to go
   ```
3. **RECALL** — open Claude Code and ask in plain English: *"What did I save about
   ___?"* Your own words come back, cited to the source.

The engine room is there when you want it: type `hermes` to talk to your assistant,
or open Obsidian and just start writing.

---

## If something goes wrong

Re-running `install.sh` is always safe — every step checks "already done?" first.
For specific symptoms, the fix table lives in [AGENTS.md](AGENTS.md#4-troubleshooting-the-common-ones).
The quick ones:

- **`boot` shows a red line** — fix that one line; the lamp tells you the command.
- **Recall comes back empty** — without a ZeroEntropy key you get keyword-only recall
  (still works); add the key (see [KEYS.md](KEYS.md)) for search-by-meaning.
- **`gbrain: command not found`** — run `export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"`.

---

## What the install actually did, for the curious

On your disk under your home folder: the component repos (`~/fpm-ai`,
`~/hermes-agent`, `~/stack-primer`, `~/gstack`), two language runtimes (Bun, uv),
**gbrain** (your local memory, installed from `github:garrytan/gbrain`), and an
`~/Obsidian Vault` seeded with `Inbox/` + `Distilled/`. It registered gbrain as a
read-only search tool inside both Claude Code and Hermes, and laid a safety baseline
into `~/.claude` (auto-compact off, destructive-command guards). The full map is
[how-it-works.html](how-it-works.html); the *why* is in [DESIGN.md](DESIGN.md).
