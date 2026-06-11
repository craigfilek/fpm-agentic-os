# Decisions log

Append-only. What was decided and why. `/onboard` and `/level-up` add to this; you
can too. Never delete — move old context to memory, not the trash.

---

## 2026-06-05 — Cron Central: GitHub Actions over Railway/DigitalOcean
Craig wants ONE home for all scheduled jobs (no crons in 10 places) + a dashboard. Decision: GitHub Actions (free, centralized, native run history) for scheduled/one-way jobs (incl. the 3am Integrator heartbeat → Telegram). Caveat noted: Actions cannot host the always-on TWO-WAY Telegram listener (that still needs Hermes on a server) — deferred. Nick runs Hermes on Railway; we revisit two-way later.

## 2026-06-05 — Company-heartbeats model does NOT break JVC (council-vetted)
Q (Craig): does the seats + Integrator + heartbeats model contradict JVC's "folders over agents / no stationed agents"? 5-member Claude council, UNANIMOUS: **no conflict** — the model is JVC-coherent as built. Confirmed by the Integrator's own `job.md` ("whoever reads this folder *becomes* the Integrator — you become the agent when you enter the room") and by the heartbeat being an external scheduler (GitHub Actions / cron) firing a cold run, not a daemon.
**The one load-bearing rule that keeps it coherent — state lives in FILES, never in a process:**
- Seat = folder + `job.md` (a Room you *become*).
- Heartbeat = a scheduler firing a COLD, ephemeral run that reads the `job.md`, proposes, and exits. Nothing persists between beats except files.
- Integrator = a SKILL you invoke (like `/converge`), holding ZERO memory between runs — it reconciles by reading/writing files.
**Litmus (same as gbrain's "delete it, lose nothing"):** kill every heartbeat + the Integrator → you lose nothing, just re-read the `job.md`s. The moment the Integrator caches cross-run state to "be smart," it has become a stationed agent — cut it.
**Vocabulary watch:** "heartbeat" / "conductor" pull toward a daemon; keep them honest with the litmus. Proposed (pending Craig's yes — Canon gate): add one line under "No stationed agents" in the router → *"Seats and the Integrator are files you become, never processes that run. Kill every heartbeat and lose nothing."* [APPROVED + added 2026-06-05.]

## 2026-06-05 — /jvc is the rig-wide constructor (council-vetted, APPROVED, wired)
6-voice council (5 lenses + Jake/ICM channeled from the method-card). Strategy for /jvc as the rig's daemon-free, always-on-call folder/project builder. Craig approved via GSD (option a):
- **Trigger:** on-entry gap (a router names a folder that doesn't exist = the work order) + explicit `/jvc --build`. **NO scanner/cron** — all six called it "a daemon in a costume." Continuity = a router rule re-read every entry, not a process.
- **Approval boundary:** auto-build reversible scaffolding + **announce** (`built <path> · revert: git restore <path>`) = recognition, not permission. Even new top-level projects (empty scaffold = blast-radius zero). **Canon is the only hard gate:** mission/identity/voice, a router principle, the gbrain index, `Distilled/` — show + wait for go. /jvc never ships.
- **Scope:** rig-wide. /jvc is `mkdir` for the rig; one front door keeps routers/naming consistent.
- **Self-evolving triad** (PLAYBOOK+log+golden) only on `kind: stage` rooms (chunk/frame/fix); lean by default everywhere else.
- **Orphan-proof:** two-sided-link invariant — never create a folder without writing the parent router's row pointing at it, same move (or abort).
- **One real split** (top-level: announce-and-build vs show-then-go) → took announce-and-build + the visible git-revert line (Red-teamer's amendment), honoring Projector recognition without a queue.
Wired: `/jvc` SKILL.md constructor section + "Structure reflex" rule in `~/Obsidian Vault/CLAUDE.md`. Next: use 3× by hand; only add the cold-run root-scan backstop if "a folder I needed but never visited" actually bites.

## 2026-06-06 — Session wrap: SIFT lap + autopoiesis + disk (council-vetted → SUBTRACT before Build C)
5-member Claude council on "did this session finish strong or over-build again." Verdict: BOTH — proved the core, over-built around it. Stage-2 peer-review skipped on purpose: the council's own unanimous finding is that running more council to bless a wrap IS the over-build, and the load-bearing claims are verified against code + git, not opinion.

**BEDROCK (carry into Build C):** the 4-bucket sift (`sift_core.py`; only `claim` ships to gbrain); `loopback()` = the ONE claim-writer (no second writer, ever); the `build-ship`/`score_build` earning-lane; the storage-tier law (text+pointers local, heavy media→cold, transcription=size valve); `reclaim` (a standalone tool, not rig-coupled).

**PARK / cut (reversible → _attic):** Modal GPU chunker (undeployed, `modal` not even installed); 2 of the 3 HTML explainers; demote the "Autopoiesis reflex"/wiki to a one-line pointer at `loopback()` — don't name rig behaviors after grand theories (the Build-A tell). Self-evolving/autopoiesis-as-framework DEFERRED until the manual loop earns a real dollar.

**OPEN — must resolve before "lap closed" is a TRUE statement:**
1. CONTRADICTION: `sift-ship` on disk is now a dry-run "Door-5" that REFUSES to ship; `build-ship` ships. The two lanes disagree, and the "6 claims @0.83" proof came from an EARLIER sift-ship that's been overwritten. → Decide ONE ship semantic (auto-ship-via-`loopback` vs Craig's-gate) and apply to BOTH lanes; re-verify on a real source.
2. `sift_core.py` has THREE concurrent editors → name ONE owner, others read-only. The collision already detonated (the sift-ship overwrite).
3. LEAK unmitigated: engine = Claude Haiku/OpenRouter, no local path; private text egresses. Apply `deploy/sift-private.patch.md` (the `--private` guard) before any private/voice chunk.
4. Tracking: `decisions/log.md` + `web/` uncommitted; confirm whether `bin/` is tracked under the allow-list `.gitignore` or the "rebuild from repo" won't include the tools.

**STANDING GUARD:** over-build recurred under the minimal-rebuild north star. Rule — a session that adds reflexes/primitives/canon/theory before producing cashflow gets cut back to its one falsifiable output before wrap. The council is not summoned to bless wraps.
