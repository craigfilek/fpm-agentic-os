# fpm-agentic-os

Your own AI second brain + assistant fleet, set up by one command. **Capture** anything;
**recall** it later in your own cited words. Built for a non-technical owner — paste one
line, answer a few plain-English questions, done.

> ## ⚡ Start here
>
> Open the **Terminal** app (in `Applications ▸ Utilities`), paste this line, press Enter:
>
> ```bash
> curl -fsSL https://raw.githubusercontent.com/craigfilek/fpm-agentic-os/main/install.sh | bash
> ```
>
> macOS asks for your password once (the installer authorizing itself). Near the end it
> asks for an **Anthropic API key** — make a free one at
> [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys). Then
> walk away ~30 min. When you're back, an AI **CEO** interviews you and your assistant is alive.
>
> **Already have Claude Code?** You can instead paste this to the agent and let it drive:
> *"Clone https://github.com/craigfilek/fpm-agentic-os, read its AGENTS.md, and set up my
> whole agentic OS step by step. I'm not technical — do everything and ask me in plain English."*

---

## How it works

A **capture → recall** production line. Picture a shop floor: raw notes enter on the left,
get converted to Markdown, land in your Obsidian vault (the source of truth), get indexed
by gbrain (the searchable catalog), and an AI agent picks them back out on request — in your
own cited words.

> **See the floor plan:** open [`how-it-works.html`](how-it-works.html) in a browser for the
> full graphical map (intake → process → store → retrieve, with the health "andon" board).

The one idea that unlocks it: **Obsidian = the books (your content, the truth); gbrain = the
card catalog (an index that points at the books).** Delete the catalog and your brain is
untouched — you just re-scan the books.

## What gets installed

Homebrew · git/gh/ripgrep/ffmpeg · Claude Code · Bun + uv runtimes · markitdown + yt-dlp
(the capture front door) · **gbrain** (your local brain index) · the component repos
(fpm-ai, Hermes, stack-primer, gStack) · and the `bin/` tools (`boot`, `capture`,
`instagram-station`). Full detail: **[INSTALL.md](INSTALL.md)**.

## The keys you'll need

| Key | Needed? | Powers |
|---|---|---|
| Anthropic | **Required** | the agent itself |
| ZeroEntropy | Recommended | semantic recall (keyword works without it) |
| Telegram bot | Optional | talk to it from your phone |

Where to get each + how it's stored: **[KEYS.md](KEYS.md)**.

## Day one

```
boot         # the green health lamp — is the brain live?
capture <file-or-url>     # file anything into the brain
```
Then just ask your agent: *"what did I save about ___?"*

## More

- **[INSTALL.md](INSTALL.md)** — what the installer does, step by step
- **[KEYS.md](KEYS.md)** — every key, where to get it, where it's stored
- **[AGENTS.md](AGENTS.md)** — the runbook an AI agent follows to set you up
- **[DESIGN.md](DESIGN.md)** — why it's built this way
- **[OBSIDIAN-MIGRATION.md](OBSIDIAN-MIGRATION.md)** — build your vault + migrate Evernote / Apple Notes / Voice Memos

## Credits

Built with Claude (Anthropic). Borrows the "Four Cs" vocabulary (Nate Herk), gStack
(Garry Tan), ICM (Jake Van Clief), and PARA (Tiago Forte) — see DESIGN.md.
