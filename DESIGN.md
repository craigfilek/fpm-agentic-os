# fpm-agentic-os Design Decisions

This file captures the architectural decisions made while building the integrated agentic OS. Each entry: the decision, the date, the reason. New decisions append to the bottom.

---

## 2026-06-02 — The install target

**Decision:** The full install is a single bootstrap command that asks for the user's Mac password ONCE (the Homebrew sudo prompt). Everything else after that is either automatic OR happens conversationally through the CEO agent.

**Reason:** The 83-year-old-mom test. A non-technical user should never type `git`, edit a config file, or know what `brew` is. The CEO agent handles every decision that needs human input by asking in plain English.

**Implication:** The bootstrap script (`install.sh`) lives at the root of this repo and gets published at the stable raw GitHub URL. The CEO agent collects credentials and preferences post-install as the user's first conversation.

---

## 2026-06-02 — The 6-component integrated build

**Decision:** The agentic OS has six components, each playing a distinct role:

1. **fpm-ai** — opinionated control layer (agents, checker, auditor, trust ceilings, cost-aware tiered models, `--free` mode, dashboard at `:8420`, council pattern, scheduler, agent log, self-mapping vault tagger)
2. **Hermes** — general-purpose agent runtime (TUI, messaging gateways for 6+ platforms, cron, skills, learning loop, 300+ models via Nous Portal)
3. **gbrain** — shared memory and knowledge layer (graph + synthesis with citations + nightly dream cycle, exposes itself as MCP)
4. **Obsidian Vault** — human-facing notes surface
5. **stack-primer** — web-app scaffold for shipping products (Next.js + Tailwind + Supabase + Claude)
6. **fpm-agentic-os** — this repo. The install manual + design log + operator's manual.

**Reason:** fpm-ai and Hermes are different layers (opinionated personal-dev vs general-purpose runtime), not competitors. gbrain serves as shared memory both consume. stack-primer is the only repo covering web-app scaffolding. Obsidian is where the human already lives.

---

## 2026-06-02 — CEO agent lives in fpm-ai (not fpm-agentic-os)

**Decision:** The CEO agent's code, prompt, and config live in fpm-ai:
- `fpm-ai/fpm/prompts/ceo.md` — the prompt
- `fpm-ai/config/agents.yaml` — the agent entry (trust, model, tool set, etc.)

fpm-agentic-os holds the blueprint document `CEO-INTERVIEW.md` describing what the CEO does for a new user (what it asks, what it generates, sample transcript).

**Reason:** fpm-ai is the agent framework. It already has the orchestrator, checker integration, trust system, multi-provider routing, dashboard. Building the CEO in fpm-agentic-os would mean duplicating or importing that infrastructure. The code-vs-manual split keeps fpm-agentic-os a clean install guide and fpm-ai a real code framework.

---

## 2026-06-02 — Kills from fpm-ai

**Decision:** Two pieces of fpm-ai get removed in the integrated build:
- fpm-ai's plain-markdown memory (replaced by gbrain)
- fpm-ai's messaging plugins (replaced by Hermes's production gateways)

**Reason:** gbrain's knowledge graph beats plain markdown folders for search and synthesis. Hermes's messaging gateways are production-ready; fpm-ai's plugins are example-code stubs.

**Implication:** fpm-ai needs a gbrain-backed memory adapter so agents read/write through gbrain instead of local markdown. The messaging plugins can be removed or marked deprecated.

---

## 2026-06-02 — The weekly retro uses fpm-ai's council pattern

**Decision:** The weekly improvement meeting is a new fpm-ai pipeline (`weekly-retro`). Runs on cron each week. Uses fpm-ai's existing council pattern: CEO + reviewer + auditor deliberate on the past week's agent log and auditor reports, propose 3–5 system tweaks, user approves, changes get applied.

**Reason:** The council pattern (`fpm/council.py`) already exists and is built for exactly this kind of multi-agent deliberation. No need to invent a new mechanism.

---

## 2026-06-02 — Self-evolution layer

**Decision:** The system improves itself by combining two existing capabilities:
- **Hermes's learning loop** — autonomously creates skills from experience
- **fpm-ai's agent log** — records every action with verdicts

**Bridge:** Hermes notices it does X often → flags to CEO during the weekly retro → if approved, X becomes either a new fpm-ai pipeline OR a new Hermes skill (depending on which layer the work belongs in).

**Reason:** Both pieces exist independently. The integration is a coordination protocol, not new code.

---

## 2026-06-02 — Adopt the "Four Cs" vocabulary to explain the OS

**Decision:** Borrow the **Four Cs of an AIOS™** (a trademark of Nate Herk) from AIS-OS (github.com/nateherkai/AIS-OS, MIT) as the plain-English frame for describing what our OS is. We are NOT adopting AIS-OS as a component and NOT using its plain-markdown memory (we use gbrain) — we are borrowing only the explanatory vocabulary. The mapping to our six components:

- **Context** (knows you) → gbrain + the CEO interview
- **Connections** (reaches your stuff) → MCP servers (Gmail, Drive, Telegram, Supabase)
- **Capabilities** (does the work) → fpm-ai pipelines + Hermes skills
- **Cadence** (runs unasked) → Hermes cron/webhooks + fpm-ai scheduler

**Reason:** A non-technical owner needs one clean sentence per pillar, not an architecture diagram. The Four Cs map cleanly onto what we already built, so the frame costs us nothing and buys instant comprehension.

**Implication:** AIS-OS's build-order dependency graph is independent confirmation of our Phase-1 order: Context first (non-skippable — nothing else works without it) → Connections + Capabilities in parallel → Cadence last. Use the Four Cs as the section spine in user-facing docs. Preserve the ™ and the attribution to Nate Herk wherever the term appears.

---

## 2026-06-02 — Adopt ICM's "folders-as-pipeline" pattern for simple workflows

**Decision:** Adopt the **stage-contract pattern** from ICM — the Interpretable Context Methodology (github.com/RinDig/Interpreted-Context-Methdology, by Jake Van Clief; has an arXiv paper) — as the standard shape for our SIMPLE, sequential, human-reviewed, repeatable pipelines (digests, reports, content, the weekly retro). The pattern: numbered folders = stages, and each stage carries a `CONTEXT.md` that is a contract with an explicit Inputs / Process / Outputs table; one agent reads the right files at the right step.

| Stage contract | Holds |
| --- | --- |
| **Inputs** | what files/data the stage may read |
| **Process** | what the agent does in this stage |
| **Outputs** | what artifacts it writes for the next stage |

**Reason:** For linear, repeatable work, folder structure AS orchestration is simpler and more auditable than spinning up our heavier machinery. ICM is complementary to MCP, not a replacement: MCP = how agents reach tools; ICM = how context is structured across stages. ICM's **"canonical sources" principle** (one home per fact; everything else points there) is the same principle behind making gbrain the single brain — so adopting it is consistent, not a second source of truth.

**Implication:** Draw an explicit boundary. Heavy multi-agent / branching / real-time work stays in fpm-ai (council, checker, trust ceilings) + Hermes; only the simple, sequential, human-reviewed end uses ICM-style numbered folders. The two ICM superpowers we want: **glass-box observability** (system state = the filesystem, so you can see exactly where a run is) and **portability** (a workspace is a zippable folder). Preserve attribution to Jake Van Clief.

---

## 2026-06-02 — The Phase-2 simplicity bar (the mom-test)

**Decision:** Hard design constraint for the Phase-2 installer: hide ALL of the stack's power behind ONE command (`curl … | bash`) plus the CEO interview. AIS-OS proves the UX bar — "clone → run /onboard → done," featherweight. Our stack is far more powerful but far heavier (6 components, language runtimes, API keys), so the install experience must collapse to the same two steps even though the machinery underneath does not.

**Reason:** The mom-test. If any step requires the user to understand git, edit a config file, or know what a runtime is, that step has FAILED the bar and must be moved — either behind the installer (automated) or into the CEO conversation (asked in plain English). Power is allowed to be heavy; the seam the user touches is not.

**Implication:** Every new install step gets checked against this bar before it ships. "The user just has to…" is a red flag: finish that sentence and, if it names git/configs/runtimes, the step goes behind `install.sh` or the CEO interview instead.

---

## Build status — 2026-06-02

### Done
- **gbrain** v0.42.10.0 stood up. PGLite embedded Postgres, embeddings via ZeroEntropy zembed-1 @ 1280 dims.
- **fpm-ai memory + .learnings** migrated into gbrain: 11 pages / 30 chunks, all embedded, cross-folder semantic search verified.
- **Hermes** 0.15.1 installed (uv, CPython 3.11.14, anthropic + mcp extras). Default model: Claude Sonnet 4.6 (`anthropic/claude-sonnet-4-6`).
- **Hermes ↔ gbrain wired**: gbrain exposed as stdio MCP server, 88 tools discovered, connection verified in 675ms.

### Remaining (Phase 1 close-out)
- Drop Anthropic API key into `~/.hermes/.env`.
- Telegram messaging — needs a bot token.
- Obsidian bridge decision (three candidates: through gbrain, through fpm-ai tagger, or direct Obsidian MCP).

### Remaining (Phase 2)
- One-command installer (`install.sh`): exact ordering, error handling, and chicken-and-egg fix if user lacks Claude Code.

---

## 2026-06-03 — Add gStack as the dev/ship skill layer (component #7)

**Decision:** Adopt **gStack** (github.com/garrytan/gstack, MIT, ~106k stars) — Garry Tan's 58-skill Claude Code toolkit — as a first-class component. Cloned to `~/gstack`. It supplies the role-based dev workflow skills (CEO / Designer / Eng-Manager / Release-Manager / Doc-Engineer / QA): `office-hours`, `autoplan` + the `plan-*-review` set, `qa`/`qa-only`, `review`, `ship`, `land-and-deploy`, `canary`, `cso`, `investigate`, `benchmark`, `careful`/`guard`/`freeze`, `retro`, `learn`, `context-save`/`context-restore`, plus iOS and browser skills.

**Reason:** This is the same toolkit Nick's `stack-primer` only *documented* (its 23-command reference is a subset of gStack). gStack ships the actual skill code. Critically, gStack is built to pair with **gbrain** — it ships `setup-gbrain/`, `sync-gbrain/`, `USING_GBRAIN_WITH_GSTACK.md`, and an `openclaw/` integration — so it slots onto our existing memory layer with no glue. It also refills the part of a past over-built setup that got used most (the `/dev` + plan/ship/qa lane) with a maintained, externally-supported toolkit instead of custom skills.

**Implication:**
- `stack-primer` is now largely redundant as a skill source — keep it only for its `CLAUDE.md` standards file + the Next.js `starter/` scaffold; gStack is the real command layer.
- `install.sh` gets a step: `git clone https://github.com/garrytan/gstack ~/gstack`, then its Bun-based `setup`, then `setup-gbrain` to wire it to the existing brain.
- Preserve attribution to Garry Tan. Stay lean: adopt gStack's skills as-is; do NOT fork-and-customize (that was the Build A failure mode).

**Component count is now 7:** fpm-ai · Hermes · gbrain · Obsidian · stack-primer (standards + scaffold only) · **gStack (dev/ship skills)** · fpm-agentic-os (manual).

---

## 2026-06-05 — Where it landed (the reconciliation)

After the build settled and a real fresh-machine install test, the design is best
understood as **two layers**, and earlier docs that listed "7 equal components"
were corrected to match:

- **The core (what the user touches): CAPTURE → RECALL.** Obsidian (the books / the
  truth) + gbrain (the catalog) + the `capture`/`instagram-station` belt + `boot`
  (the green health lamp). This is the Apple-IIe experience: one command installs it,
  one lamp says it's live, two verbs run it. The day this lamp is reliably green, the
  brain is DONE.
- **The engine room (installed, not daily): Hermes, fpm-ai, gStack, stack-primer.**
  For messaging, automation, and building products later. Real, but secondary to the
  core — they should never be what a new user is asked to think about first.

**The living map.** `how-it-works.html` is the single source of truth for "how it
works." All other docs link to it rather than re-describing the architecture in prose
(prose drifts; the diagram is updated in one place and every link stays current).

**Corrections baked in (each was a real fresh-machine bug or drift):**
- gbrain installs from `github:garrytan/gbrain`, **not** the npm package `gbrain`
  (an unrelated GPU/ML library) — that wrong source aborted every fresh install.
- `install.sh` clones **itself** alongside the other repos, or its `bin/` tools and
  Claude settings never land when run via `curl | bash`.
- The brain is **one vault source** (`Inbox/` + `Distilled/` as subfolders), not
  several top-level sources — 3+ federated sources trip a gbrain cross-source-search
  quirk that silently breaks recall.
- Recall works on **keyword alone**; the ZeroEntropy embedding key upgrades it to
  search-by-meaning. So the key is *recommended*, not *required* (see `KEYS.md`).
- `boot` is source-agnostic (`sync --all`, total page count) and imports with
  `--no-embed` so a keyless brain is still searchable; embeddings are a bonus layer.
- The repo is **public** (verified leak-clean: allow-list `.gitignore` + neutral
  authorship + full-history scan), so the `curl | bash` URL actually resolves for
  strangers. Personal data lives only in separate private repos.

**Still open (the last mile):** one real fresh-Mac/VM run by a first user — only the
OS-level downloads (Homebrew, bun, uv, Claude Code) remain unexercised; all custom
logic is proven end-to-end in a sandbox.
