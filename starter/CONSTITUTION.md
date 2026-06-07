# CLAUDE.md — the Constitution (this folder's root router, laid down FIRST)

*This is the keystone. It defines where everything lives and how it cascades. The installer lays this as the workspace root `CLAUDE.md` before anything else; everything else unpacks inside it.*

## Two domains — never mix them
- **CODE** (runnable software): lives **FLAT at `~/<repo>`**. Owned by `install.sh`. Never reorganized into sub-buckets — moving a repo breaks its wiring (symlinks, venvs, launchd, MCP). Secrets in `.env`/keychain, never committed.
- **THINKING** (markdown knowledge): lives in the **vault / ICM tree** (the brain). This is what folders-over-agents governs.

## ICM layers (the thinking tree)
1. **Map** — a `CLAUDE.md` router in each folder; loads on entry; folder map + routing + naming.
2. **Rooms** — per-workspace `CONTEXT.md`; what's here, the process, what good looks like.
3. **Workspace** — the files, named by convention.
No stationed agents — *you become the agent when you enter the room.* State lives in files, never a running process.

## The brain (gbrain) — ingest broadly, focus by PREFIX
Anything markdown can enter gbrain at any stage. Focus is **not** a gate — it's **folder path = gbrain prefix = recall lens**:
- **Canon / evergreen** (claims, distilled concepts, originals) → prefixes `concepts/ distilled/ originals/` — stay sharp forever. Recall defaults here with `--detail low`.
- **Ephemeral / raw** (dumps, daily, chat, media) → prefixes `daily/ raw/ chat/ media/` — **decay by design**, so noise fades; widen with `--detail`/`--since`/`--salience` only when you want it.
- The folder you file something in decides whether it sticks or fades. Naming is the index.

## The cascade (install order — structure first)
**Structure (this) → Engine (`fpm-ai` + gbrain + bin) → Brain (vault/ICM tree) → Face (`onboard` + GSD + lean skills) → Doctor.** Nothing installs outside this; each junction gets a provable test.

## Replicate at scale (the maintenance rule)
- New area = a folder + its `CLAUDE.md` (Map) + a name under the right prefix. **Two-sided link:** the parent router gets a row pointing at it (no orphans).
- Routers stay ≤ one screen; push detail into a room's `CONTEXT.md`.
- A folder earns the self-evolving triad (`PLAYBOOK.md` + `log.md` + `golden/`) **only** if it's a `kind: stage` (a repeated verb toward a verdict).
- **Every folder carries a `TEST.md`** — a provable check (the `## Check` bash block that `bin/test-all` runs from inside it; exit 0 = pass). `/jvc` drops one from `starter/TEST.template.md` when it builds a folder. Prove each junction; never assume. `bin/test-all` runs them all for the "test it all" pass.
- Grow from use. 15-minute pieces. Collapse anything that doesn't route somewhere *different*. (Anti-sprawl law.)

## JVC is the law
This whole rig is built Jake-Van-Clief style — folders over agents, layers over libraries. The method + voice: `starter/jvc-method-card.md` (and `Wiki/JVC` once the vault exists). Channel Jake or build new folders with the `/jvc` skill.

## The one rule
Strike the structure first; everything else falls in behind it and cascades. If a piece can't say which prefix/room it belongs to, it doesn't get installed until it can.
