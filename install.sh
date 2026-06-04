#!/usr/bin/env bash
set -euo pipefail

# install.sh — fpm-ai-os bootstrap
# Target: macOS 13+, invoked via: curl -fsSL .../install.sh | bash
#
# STATUS 2026-06-03: Fleshed out from the original skeleton. Commands marked
# [VERIFIED] were confirmed against the installed tools on the reference machine.
# Commands marked [VERIFY-LIVE] still need one real fresh-machine run to prove
# (Homebrew sudo prompt, Claude Code install method, Telegram flow, CEO handoff).
# It is idempotent: every step checks "already done?" before acting, so a failed
# run can be re-run safely.
#
# SECURITY: no secret is ever hardcoded or passed as argv. API keys are read with
# `read -rs` into env/`.env` files only. This matches gStack's + gbrain's model.

# ── paths ─────────────────────────────────────────────────────────────────────
BUN="$HOME/.bun/bin/bun"
GBRAIN="$HOME/.bun/bin/gbrain"
HERMES="$HOME/hermes-agent/.venv/bin/hermes"
export PATH="$HOME/.bun/bin:$HOME/.local/bin:/opt/homebrew/bin:$PATH"

say() { printf "\n\033[1m== %s\033[0m\n" "$1"; }

# ── 1. Homebrew (the one Mac-password prompt) ─────────────────────────────────
# [VERIFY-LIVE] On a fresh Mac this triggers the single sudo password prompt.
say "Homebrew"
if ! command -v brew &>/dev/null; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Apple Silicon installs brew to /opt/homebrew, Intel to /usr/local — eval whichever exists.
  if [ -x /opt/homebrew/bin/brew ]; then eval "$(/opt/homebrew/bin/brew shellenv)";
  elif [ -x /usr/local/bin/brew ]; then eval "$(/usr/local/bin/brew shellenv)"; fi
else
  echo "brew present: $(brew --version | head -1)"
fi

# ── 2. core CLI tools via brew ────────────────────────────────────────────────
say "core tools (git, gh, ripgrep, ffmpeg)"
for t in git gh ripgrep ffmpeg; do
  brew list "$t" &>/dev/null || brew install "$t"
done

# ── 3. Claude Code ────────────────────────────────────────────────────────────
# [VERIFY-LIVE] Confirm the canonical install channel before shipping. Homebrew
# cask is the current path; npm is the fallback.
say "Claude Code"
if ! command -v claude &>/dev/null; then
  brew install --cask claude-code || npm install -g @anthropic-ai/claude-code
else
  echo "claude present: $(claude --version 2>/dev/null | head -1)"
fi

# ── 4. bun (JavaScript runtime) ───────────────────────────────────────────────
# [VERIFIED] installs to ~/.bun/bin
say "bun"
if ! command -v bun &>/dev/null; then
  curl -fsSL https://bun.sh/install | bash
  export PATH="$HOME/.bun/bin:$PATH"
else
  echo "bun present: $(bun --version)"
fi

# ── 5. uv (Python runtime/venv manager) ───────────────────────────────────────
# [VERIFIED] installs to ~/.local/bin
say "uv"
if ! command -v uv &>/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
else
  echo "uv present: $(uv --version)"
fi

# ── 6. clone the component repos ──────────────────────────────────────────────
# [VERIFIED URLS] your own private product repos are intentionally NOT cloned —
# they are not part of the shareable OS.
say "clone component repos"
clone() { [ -d "$HOME/$2" ] && echo "$2 present" || git clone --depth 1 "$1" "$HOME/$2"; }
clone https://github.com/cgf1812/fpm-ai.git             fpm-ai
clone https://github.com/NousResearch/hermes-agent.git     hermes-agent
clone https://github.com/nickscarabosio/stack-primer.git   stack-primer
clone https://github.com/garrytan/gstack.git               gstack

# ── 7. gbrain (memory) — install globally via bun ─────────────────────────────
# [VERIFIED] bun install -g gbrain  →  ~/.bun/bin/gbrain
say "gbrain"
"$GBRAIN" --version &>/dev/null 2>&1 || bun install -g gbrain
echo "gbrain: $("$GBRAIN" --version 2>/dev/null || echo 'not on PATH yet')"

# ── 8. gbrain init (PGLite, embedded Postgres, no server) ─────────────────────
# [VERIFIED] command shape: gbrain init --pglite  (data lives at ~/.gbrain)
say "gbrain init"
if [ ! -d "$HOME/.gbrain" ]; then
  "$GBRAIN" init --pglite
else
  echo "~/.gbrain already exists — skipping init"
fi

# ── 8a. gbrain settings (enable embeddings, schema pack, skill publishing) ─────
# [VERIFIED — deltas from default] A fresh `gbrain init` ships with
# embeddings OFF; flip embedding_disabled→false. Also pin the schema pack
# (if unset) and enable MCP skill publishing, matching his ~/.gbrain/config.json.
# Idempotent JSON merge; preserves every other field.
say "gbrain settings"
_GB_CFG="$HOME/.gbrain/config.json"
if [ -f "$_GB_CFG" ]; then
  python3 -c '
import json, sys
p = sys.argv[1]
with open(p) as f:
    c = json.load(f)
c["embedding_disabled"] = False
c.setdefault("schema_pack", "gbrain-base-v2")
mcp = c.get("mcp") if isinstance(c.get("mcp"), dict) else {}
mcp["publish_skills"] = True
c["mcp"] = mcp
with open(p, "w") as f:
    json.dump(c, f, indent=2)
' "$_GB_CFG"
  echo "gbrain settings applied (embeddings on, schema_pack, publish_skills)"
else
  echo "# ~/.gbrain/config.json not found — settings apply on next run"
fi

# ── 8b. embedding-provider key → ~/.gbrain/config.json ────────────────────────
# [VERIFIED] gbrain reads the embedding key from the FILE plane of
# ~/.gbrain/config.json. Confirmed against gbrain/src/cli.ts:1799 — at runtime it
# maps the config's `zeroentropy_api_key` field → ZEROENTROPY_API_KEY env var,
# which the zeroentropyai recipe consumes. (`gbrain config set zeroentropy_api_key`
# writes the DB plane, which the gateway IGNORES — per gbrain/src/core/config.ts:37
# — so we write the JSON field directly.) The reference setup uses ZeroEntropy, so
# we default to it. Without an embedding key, pages import structurally but
# semantic search degrades.
# SECURITY: key read with `read -rs` (hidden), never argv, never echoed. The
# python3 -c JSON edit reads the key from an env var (not argv, so it never shows
# in `ps`) and rewrites the file in place, preserving every other field. chmod 0600.
say "embedding-provider key (gbrain semantic search)"
_GB_CFG="$HOME/.gbrain/config.json"
# Idempotent: skip if a non-empty embedding key is already present.
_GB_HAS_KEY=""
if [ -f "$_GB_CFG" ]; then
  _GB_HAS_KEY=$(python3 -c '
import json, sys
try:
    c = json.load(open(sys.argv[1]))
except Exception:
    print(""); sys.exit(0)
for k in ("zeroentropy_api_key", "voyage_api_key", "openai_api_key"):
    if str(c.get(k, "")).strip():
        print(k); break
' "$_GB_CFG" 2>/dev/null || echo "")
fi
if [ -n "$_GB_HAS_KEY" ]; then
  echo "embedding key already set ($_GB_HAS_KEY) — skipping"
elif [ ! -f "$_GB_CFG" ]; then
  echo "# ~/.gbrain/config.json not found (gbrain init may have been skipped) — set the embedding key later"
elif [ -t 0 ]; then
  read -rsp "Paste your ZeroEntropy embedding key (input hidden; Enter to skip): " _EK; echo
  if [ -n "${_EK:-}" ]; then
    # Pass the key via env (EK), NOT argv, so it never shows in `ps`.
    EK="$_EK" python3 -c '
import json, os, sys
p = sys.argv[1]
with open(p) as f:
    c = json.load(f)
c["zeroentropy_api_key"] = os.environ["EK"]
with open(p, "w") as f:
    json.dump(c, f, indent=2)
' "$_GB_CFG"
    chmod 600 "$_GB_CFG"
    unset _EK EK
    echo "ZeroEntropy embedding key written to ~/.gbrain/config.json (mode 0600)"
  else
    echo "# no embedding key entered — semantic search will degrade until one is set"
  fi
else
  echo "# non-interactive shell — set an embedding key before first search:"
  echo "#   add \"zeroentropy_api_key\": \"ze-…\" to ~/.gbrain/config.json (chmod 600), then re-run import"
fi

# ── 9. import memory sources + embed ──────────────────────────────────────────
# [VERIFIED] command shape: gbrain import <dir>. Embeddings need a provider key
# (ZeroEntropy preferred, set in step 8b; else VOYAGE_API_KEY/OPENAI_API_KEY env)
# — without one, pages import structurally but semantic search degrades. Import
# fpm-ai's markdown memory.
say "import memory into gbrain"
if [ -d "$HOME/fpm-ai/memory" ]; then
  "$GBRAIN" import "$HOME/fpm-ai/memory" || echo "import returned non-zero (often = nothing new)"
fi
# Obsidian vault import is OPTIONAL and can be large/slow — left to the CEO step.
echo "# (Obsidian vault import deferred to the CEO interview — it's large)"

# ── 10. install hermes (Python agent runtime) ─────────────────────────────────
# [VERIFIED] uv sync --python 3.11 --extra anthropic --extra mcp  →  .venv, hermes 0.15.1
say "hermes"
if [ ! -x "$HERMES" ]; then
  (cd "$HOME/hermes-agent" && uv sync --python 3.11 --extra anthropic --extra mcp)
else
  echo "hermes present: $("$HERMES" --version 2>/dev/null | head -1)"
fi

# ── 11. wire gbrain as a stdio MCP server inside hermes ───────────────────────
# [VERIFIED] yields ~88 tools. `yes` auto-confirms the enable-tools prompt.
# NOTE: `yes |` is an infinite writer; when hermes closes the pipe, yes gets
# SIGPIPE (exit 141), which under `set -o pipefail` would abort the whole
# installer. Scope-disable pipefail here and read hermes's REAL exit via
# PIPESTATUS so a benign SIGPIPE on yes can't kill the run.
say "wire gbrain → hermes (MCP)"
if ! "$HERMES" mcp list 2>/dev/null | grep -q gbrain; then
  set +o pipefail
  yes | "$HERMES" mcp add gbrain \
    --command "$GBRAIN" --args serve \
    --env "PATH=$HOME/.bun/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin" \
    --env "HOME=$HOME"
  _rc=${PIPESTATUS[1]}
  set -o pipefail
  [ "${_rc:-0}" -eq 0 ] || echo "gbrain MCP add returned $_rc — check 'hermes mcp list'"
else
  echo "gbrain already registered in hermes"
fi

# ── 12. wire gbrain as an MCP server inside Claude Code ───────────────────────
# [VERIFIED command shape from gStack docs] gives gbrain tools to Claude Code too.
say "wire gbrain → Claude Code (MCP)"
if command -v claude &>/dev/null; then
  claude mcp list 2>/dev/null | grep -q gbrain || claude mcp add gbrain -s user -- "$GBRAIN" serve
else
  echo "claude not on PATH — skipping (re-run after Claude Code is installed)"
fi

# ── 13. gStack (58 dev/ship skills) — build + install skills ──────────────────
# [VERIFIED command shape] gStack's ./setup builds its binary and symlinks its
# skills into ~/.claude/skills/. Needs bun install first (per gstack/CLAUDE.md).
say "gStack setup"
if [ -d "$HOME/gstack" ]; then
  (cd "$HOME/gstack" && bun install && ./setup --prefix) || echo "gStack setup returned non-zero — re-run install.sh or gStack/setup manually"
  # apply gStack preferences (6 deltas from default)
  _GSC="$HOME/.claude/skills/gstack/bin/gstack-config"
  if [ -x "$_GSC" ]; then
    "$_GSC" set skill_prefix true            >/dev/null 2>&1 || true
    "$_GSC" set proactive false              >/dev/null 2>&1 || true
    "$_GSC" set telemetry off                >/dev/null 2>&1 || true
    "$_GSC" set checkpoint_mode explicit     >/dev/null 2>&1 || true
    "$_GSC" set cross_project_learnings false >/dev/null 2>&1 || true
    "$_GSC" set routing_declined true        >/dev/null 2>&1 || true
    echo "gStack preferences applied (prefix, explicit-only, telemetry off, ...)"
  fi
  # gbrain↔gStack wiring is handled by gStack's own /setup-gbrain skill on first
  # use; the gbrain MCP registered in step 12 already gives it a tool surface.
fi

# ── 14. set hermes default model ──────────────────────────────────────────────
# [VERIFIED] normalizes to claude-sonnet-4-6 for the native anthropic provider.
say "hermes model"
"$HERMES" config set model anthropic/claude-sonnet-4.6 || true

# ── 15. Anthropic API key → ~/.hermes/.env (and ~/.env.anthropic) ─────────────
# [VERIFIED pattern] read -rs, never argv, never echoed.
say "Anthropic API key"
mkdir -p "$HOME/.hermes"
if ! grep -q "ANTHROPIC_API_KEY=" "$HOME/.hermes/.env" 2>/dev/null; then
  if [ -t 0 ]; then
    read -rsp "Paste your Anthropic API key (input hidden): " _AK; echo
    if [ -n "${_AK:-}" ]; then
      printf 'ANTHROPIC_API_KEY=%s\n' "$_AK" >> "$HOME/.hermes/.env"
      printf 'ANTHROPIC_API_KEY=%s\n' "$_AK" >  "$HOME/.env.anthropic"
      chmod 600 "$HOME/.hermes/.env" "$HOME/.env.anthropic"
      unset _AK
    fi
  else
    echo "# non-interactive shell — set ANTHROPIC_API_KEY in ~/.hermes/.env before first run"
  fi
else
  echo "Anthropic key already present in ~/.hermes/.env"
fi

# ── 16. Telegram gateway (optional) ───────────────────────────────────────────
# [VERIFIED] `hermes gateway setup` configures messaging platforms interactively
# (needs a @BotFather bot token); `hermes gateway install` runs it as a background
# service. OPTIONAL and never blocks the install. Interactive: offer to run setup
# now. Non-interactive (curl|bash): just print the two-command instructions.
# Idempotent: if a gateway is already configured, `hermes gateway status` reports
# it and we skip the offer.
say "Telegram gateway (optional)"
if [ -x "$HERMES" ] && "$HERMES" gateway status 2>/dev/null | grep -qiE "running|installed|configured|active"; then
  echo "hermes gateway already configured — skipping"
elif [ -x "$HERMES" ] && [ -t 0 ]; then
  read -rp "Set up the Telegram gateway now? (needs a @BotFather bot token) [y/N]: " _TG
  case "${_TG:-}" in
    [yY]|[yY][eE][sS])
      # setup is interactive; never let a non-zero exit abort the whole installer.
      "$HERMES" gateway setup || echo "gateway setup returned non-zero — re-run 'hermes gateway setup' later"
      echo "# To run it as a background service:  hermes gateway install"
      ;;
    *)
      echo "# Skipped. To enable later:  hermes gateway setup  then  hermes gateway install"
      ;;
  esac
  unset _TG
else
  echo "# To enable Telegram later: run  hermes gateway setup  (needs a @BotFather bot token),"
  echo "#   then  hermes gateway install  to run it as a background service."
fi

# ── 17. Obsidian bridge (optional) ────────────────────────────────────────────
# [VERIFY-LIVE] Obsidian MCP serves on localhost:22360 when the app is open.
say "Obsidian bridge (optional)"
echo "# To enable: open Obsidian (with its MCP plugin), then  claude mcp add obsidian ..."

# ── 18. Claude Code customizations (settings, statusline, house-rule memory) ───
# [VERIFIED — files ship in this repo] Safety/behavior baseline: auto-compact OFF
# (PreCompact hook + env override), .env/.ssh deny rules, destructive-command
# guards (rm -rf, git push/commit, gh ...), plan default mode, statusline, and
# the starter house-rule memories. Idempotent; skips gracefully if files absent.
say "Claude Code customizations"
PKG="$HOME/fpm-ai-os"
[ -f "./claude-settings.json" ] && PKG="$(pwd)"
if [ -f "$PKG/claude-settings.json" ]; then
  mkdir -p "$HOME/.claude"
  [ -f "$HOME/.claude/settings.json" ] && cp "$HOME/.claude/settings.json" "$HOME/.claude/settings.json.bak.$(date +%Y%m%d-%H%M%S)"
  sed "s#__HOME__#$HOME#g" "$PKG/claude-settings.json" > "$HOME/.claude/settings.json"
  [ -f "$PKG/statusline.py" ] && cp "$PKG/statusline.py" "$HOME/.claude/statusline.py" && chmod +x "$HOME/.claude/statusline.py"
  MEMDIR="$HOME/.claude/projects/-$(printf '%s' "${HOME#/}" | tr '/' '-')/memory"
  mkdir -p "$MEMDIR"
  for f in "$PKG"/claude-memory/*.md; do
    [ -e "$f" ] || continue
    base=$(basename "$f")
    [ -e "$MEMDIR/$base" ] || cp "$f" "$MEMDIR/$base"
  done
  echo "settings + statusline + house-rule memory in place"
else
  echo "# fpm-ai-os package files not found on disk — apply claude-settings.json + claude-memory/ from the repo manually"
fi

# ── 19. wire the bus: fpm-ai → gbrain + Obsidian bridge ───────────────────────
# Plug the last two cards onto the gbrain bus so a fresh machine boots integrated.
say "wire fpm-ai + Obsidian to the brain"
for rc in "$HOME/.zshrc" "$HOME/.bash_profile"; do
  [ -f "$rc" ] || touch "$rc"
  grep -q "FPM_MEMORY_BACKEND=gbrain" "$rc" 2>/dev/null || echo 'export FPM_MEMORY_BACKEND=gbrain' >> "$rc"
done
echo "fpm-ai now reads/writes gbrain (FPM_MEMORY_BACKEND=gbrain)"
PKG="$HOME/fpm-ai-os"; [ -f "./bin/obsidian-to-gbrain" ] && PKG="$(pwd)"
if [ -f "$PKG/bin/obsidian-to-gbrain" ]; then
  mkdir -p "$HOME/.local/bin"
  cp "$PKG/bin/obsidian-to-gbrain" "$HOME/.local/bin/obsidian-to-gbrain"
  chmod +x "$HOME/.local/bin/obsidian-to-gbrain"
  echo "Obsidian→gbrain bridge installed (run: obsidian-to-gbrain)"
fi

say "install.sh complete"
echo "Next: open Claude Code and meet your CEO (the interview collects remaining keys + preferences)."
