<!-- Moved out of README.md so the front page is just the OS install. This is the vault setup + notes-migration guide. -->

# Obsidian Second Brain Setup
### From zero to fully migrated, agent-assisted, agentic OS ready

> **Who this is for:** Anyone setting up their own Obsidian second brain.  
> **How to use it:** Hand this document to an AI agent (Claude in Cowork, Claude Code, or similar) and say *"Run this setup guide for me."* The agent handles 90% of the work. The remaining 10% is clicks only you can authorize.

---

## Quick start — the whole agentic OS in one command

> **New here? Start with this.** The fastest path is to hand this repo to an AI
> agent and say *"Read AGENTS.md and set me up."* The agent drives everything
> below for you.

If you'd rather paste one line yourself, open the **Terminal** app and paste:

```bash
curl -fsSL https://raw.githubusercontent.com/craigfilek/fpm-agentic-os/main/install.sh | bash
```

Press Enter. macOS asks for your Mac password **once** (that's the installer
authorizing itself, like installing any app). Near the end it asks you to paste
an **Anthropic API key** — if you don't have one, make a free one at
[console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys).
Then walk away for ~30 minutes. When you come back, an AI **CEO** interviews you
about how you work, and your assistant is alive.

- **What gets installed:** see [INSTALL.md](INSTALL.md).
- **The agent's runbook (what it follows to set you up):** see [AGENTS.md](AGENTS.md).
- **Why it's built this way:** see [DESIGN.md](DESIGN.md).

The rest of this document is the **Obsidian notes layer** — how your second-brain
vault gets created and your old notes migrated in. The one-command installer above
handles the agentic OS; the phases below handle Obsidian.

---

## Prerequisites

Before the agent starts, you need three things:

1. **A Mac** running macOS 13 Ventura or later (tested on macOS 26)
2. **Obsidian** installed — [obsidian.md](https://obsidian.md) — free download
3. **An AI agent** with computer-use and shell access (Claude in Cowork mode recommended)

---

## Phase 1 — Create Your Vault

### 1.1 Choose your vault location

**Critical:** Do NOT put your vault inside `~/Documents` or `~/Desktop` if iCloud Drive is enabled. iCloud will evict files to the cloud and make them disappear in Obsidian.

**Correct location:** `~/Obsidian Vault` (your home folder, outside iCloud reach)

**Agent instructions:**
```bash
# Create the vault folder
mkdir -p ~/Obsidian\ Vault

# Verify it's not inside iCloud
ls ~/Obsidian\ Vault && echo "Good — vault folder created at home level"
```

### 1.2 Open Obsidian and point it at the vault

1. Launch Obsidian
2. Click **Open folder as vault**
3. Navigate to your home folder (`/Users/yourname/`)
4. Select `Obsidian Vault` → **Open**
5. Trust the vault when prompted

---

## Phase 2 — Install Plugins

Open Obsidian Settings (gear icon bottom-left) → **Community plugins** → turn off Restricted mode → **Browse**

Install each plugin below by searching its name and clicking Install, then Enable.

### Essential plugins

| Plugin | ID | Purpose |
|---|---|---|
| **Importer** | `obsidian-importer` | Migrate Evernote, Apple Notes, Notion, etc. |
| **Dataview** | `dataview` | Query your notes like a database |
| **Templater** | `templater-obsidian` | Powerful note templates with variables |
| **Calendar** | `calendar` | Daily notes calendar view |
| **Periodic Notes** | `periodic-notes` | Daily / weekly / monthly note structure |
| **Tasks** | `obsidian-tasks-plugin` | Task management across all notes |
| **Kanban** | `obsidian-kanban` | Visual project boards |
| **Tag Wrangler** | `tag-wrangler` | Rename and organize tags in bulk |
| **Folder Note** | `folder-note-plugin` | Make folders clickable index notes |
| **Advanced URI** | `obsidian-advanced-uri` | Deep-link into notes from outside Obsidian |
| **QuickAdd** | `quickadd` | Fast note capture with custom forms |
| **Mind Map** | `obsidian-mind-map` | Visualize note hierarchies as mind maps |

### Optional but powerful

| Plugin | Purpose |
|---|---|
| **Excalidraw** | Whiteboard sketching inside notes |
| **Obsidian Git** | Auto-backup vault to GitHub |
| **Smart Connections** | AI-powered note similarity and chat |
| **Omnisearch** | Full-text search across everything |
| **Natural Language Dates** | Type "next Monday" and get a date link |

---

## Phase 3 — Evernote Migration

> **Time estimate:** 30 min setup, then runs unattended. Large vaults (1,000+ notes) take 1–3 hours.

### 3.1 Export from Evernote

You must export each notebook individually as `.enex` files. The agent cannot do this — Evernote requires you to click.

**For each notebook in Evernote:**
1. Right-click the notebook → **Export Notes**
2. Format: **Evernote XML Format (.enex)**
3. Check **Include tags**
4. Save to `~/Downloads/Evernote export/`
5. Name the file exactly: `NotebookName.enex`

**If you have Stacks (folders of notebooks):**
Name each file `StackName@@@NotebookName.enex` — the `@@@` delimiter tells the import script to create a proper folder hierarchy.

Example:
```
Work@@@Projects.enex
Work@@@Reference.enex
Personal@@@Journal.enex
```

### 3.2 Run the import

**Agent instructions:**
```bash
# Verify export files exist
ls ~/Downloads/Evernote\ export/*.enex | wc -l
echo "enex files found"
```

Then in Obsidian:
1. Open **Importer** plugin (ribbon icon or Cmd+P → "Import")
2. Select **Evernote**
3. Choose your `.enex` files from `~/Downloads/Evernote export/`
4. Set output folder to `Evernote/`
5. Click **Import**

**Agent post-import cleanup:**
```bash
# Fix any folders starting with . (hidden in Obsidian)
cd ~/Obsidian\ Vault/Evernote/

for dir in .*/; do
  if [ -d "$dir" ]; then
    clean="${dir#.}"
    newname="0 ${clean%/}"
    mv "$dir" "$newname"
    echo "Renamed: $dir → $newname"
  fi
done
```

```bash
# Verify import — count markdown files
find ~/Obsidian\ Vault/Evernote -name "*.md" | wc -l
echo "notes imported"
```

### 3.3 Finder visibility note

In macOS Finder, folders starting with `[` are treated as hidden. Press **Cmd+Shift+.** to toggle hidden file visibility, or prefix the folder with `0 ` (e.g., `0 [INBOX]`) so it sorts visibly without needing the toggle.

---

## Phase 4 — Apple Notes Migration

> **Time estimate:** 5 minutes. Obsidian Importer handles this natively.

### 4.1 Grant permissions

Apple Notes requires explicit permission before any app can read it.

1. Open **System Settings** → **Privacy & Security** → **Full Disk Access**
2. Make sure **Obsidian** is in the list and toggled ON
3. Restart Obsidian

### 4.2 Run the import

1. In Obsidian, open **Importer** (Cmd+P → "Import")
2. Select **Apple Notes**
3. Set output folder to `Apple Notes/`
4. Click **Import**

Obsidian Importer will:
- Read all your notes and folders via the native Apple Notes API
- Convert each note to Markdown
- Preserve your folder structure
- Carry over tags, images, and attachments

**Agent verification:**
```bash
find ~/Obsidian\ Vault/Apple\ Notes -name "*.md" | wc -l
echo "Apple Notes imported"
```

---

## Phase 5 — Voice Memos Migration

> **Time estimate:** Setup 10 min. Transcription runs overnight for large libraries.

### 5.1 Export your Voice Memos

Voice Memos on macOS 26 is TCC-sandboxed — no script can read recordings without Full Disk Access granted to the Terminal app.

**Grant FDA first:**
1. **System Settings** → **Privacy & Security** → **Full Disk Access**
2. Click **+** → navigate to `/Applications/Utilities/Terminal.app` → **Open**
3. Toggle Terminal ON → restart Terminal

**Then export all recordings:**
```bash
VM_SRC=~/Library/Containers/com.apple.VoiceMemos/Data/Library/Recordings
mkdir -p ~/Obsidian\ Vault/Voice\ Memos/audio
mkdir -p ~/Obsidian\ Vault/Voice\ Memos/transcripts
cp "$VM_SRC"/*.m4a ~/Obsidian\ Vault/Voice\ Memos/audio/ 2>/dev/null
echo "Copied $(ls ~/Obsidian\ Vault/Voice\ Memos/audio/*.m4a 2>/dev/null | wc -l) recordings"
```

### 5.2 Transcribe with Whisper

Apple's MLX Whisper runs locally on your Mac (no internet, no cost, fast on Apple Silicon).

```bash
pip3 install mlx-whisper --break-system-packages
```

```bash
AUDIO_DIR=~/Obsidian\ Vault/Voice\ Memos/audio
TRANSCRIPT_DIR=~/Obsidian\ Vault/Voice\ Memos/transcripts

for f in "$AUDIO_DIR"/*.m4a; do
  name=$(basename "$f" .m4a)
  out="$TRANSCRIPT_DIR/$name.md"
  if [ ! -f "$out" ]; then
    echo "Transcribing: $name"
    mlx_whisper "$f" --model mlx-community/whisper-large-v3-mlx --output-dir /tmp/whisper_out --output-format txt
    {
      echo "---"
      echo "source: voice-memo"
      echo "date: $(stat -f '%Sm' -t '%Y-%m-%d' "$f")"
      echo "audio: \"[[Voice Memos/audio/$(basename "$f")]]\"" 
      echo "---"
      echo ""
      echo "# $(basename "$f" .m4a)"
      echo ""
      cat /tmp/whisper_out/$(basename "$f" .m4a).txt
    } > "$out"
  fi
done
echo "Done. $(ls "$TRANSCRIPT_DIR"/*.md | wc -l) transcripts created."
```

---

## Phase 6 — Folder Structure

```
Obsidian Vault/
├── 0 [INBOX]/              ← daily capture, unsorted ideas
├── Evernote/               ← everything from Evernote
├── Apple Notes/            ← everything from Apple Notes
├── Voice Memos/
│   ├── audio/              ← .m4a files
│   └── transcripts/        ← one .md per recording
├── Journal/                ← daily notes (Periodic Notes plugin)
├── Projects/               ← active work
├── Areas/                  ← ongoing responsibilities
├── Resources/              ← reference material
└── Archive/                ← done/inactive
```

This follows the **PARA method** (Projects, Areas, Resources, Archive) by Tiago Forte.

---

## Phase 7 — Agentic OS Configuration

### 7.1 Local REST API

Install the **Local REST API** community plugin. Lets agents read/write notes via HTTP.

```bash
curl -s http://localhost:27123/vault/ -H "Authorization: Bearer YOUR_API_KEY" | head -20
```

### 7.2 Obsidian Git — auto-backup

```bash
cd ~/Obsidian\ Vault
git init
git remote add origin https://github.com/YOUR_USERNAME/second-brain.git
git add .
git commit -m "Initial vault"
git push -u origin main
```

### 7.3 Daily note template

Create `Templates/Daily Note.md`:

```markdown
---
date: {{date:YYYY-MM-DD}}
day: {{date:dddd}}
week: W{{date:WW}}
tags: [daily]
---

# {{date:dddd, MMMM D, YYYY}}

## Focus
> What's the one thing that makes everything else easier or unnecessary?

## Tasks
- [ ] 

## Notes

## End of day
- Win: 
- Learn: 
- Tomorrow: 
```

---

## Agent Quickstart Recon

Run this first — tells you what's already in place:

```bash
#!/bin/bash
echo "=== OBSIDIAN VAULT ===" 
ls ~/Obsidian\ Vault/ 2>/dev/null && echo "Vault found" || echo "No vault at ~/Obsidian Vault"
echo ""
echo "=== EVERNOTE EXPORTS ==="
ls ~/Downloads/Evernote\ export/*.enex 2>/dev/null | wc -l && echo "enex files"
echo ""
echo "=== APPLE NOTES ==="
sqlite3 ~/Library/Group\ Containers/group.com.apple.notes/NoteStore.sqlite \
  "SELECT COUNT(*) FROM ZICCLOUDSYNCINGOBJECT WHERE ZTITLE1 IS NOT NULL AND ZMARKEDFORDELETION=0;" \
  2>/dev/null || echo "Notes DB locked — close Apple Notes and retry"
echo ""
echo "=== VOICE MEMOS ==="
find ~/Library/Containers/com.apple.VoiceMemos/Data/Library/Recordings -name "*.m4a" 2>/dev/null | wc -l
echo "voice memos (0 = grant Full Disk Access to Terminal first)"
echo ""
echo "=== PLUGINS ==="
ls ~/Obsidian\ Vault/.obsidian/plugins/ 2>/dev/null || echo "No plugins yet"
```

---

## Troubleshooting

**[INBOX] not visible in Finder** → Press Cmd+Shift+. Folders starting with `[` are hidden by macOS. Rename to `0 [INBOX]` for permanent visibility.

**iCloud evicting vault files** → Move vault OUT of `~/Documents` to `~/Obsidian Vault`. iCloud doesn't touch the home folder root.

**Voice Memos count is 0** → Terminal needs Full Disk Access: System Settings → Privacy & Security → Full Disk Access → add Terminal.

**Evernote import stalls** → Let it run. A 500MB .enex can take 30 min. Don't force-quit.

**Apple Notes shows no folders** → Add Obsidian to Full Disk Access alongside Terminal.

**`brctl download` not working (macOS 26)** → That command was removed. Move vault off iCloud instead.

---

## Credits

Built with Claude (Anthropic).

> *"The goal isn't a perfect system. The goal is a system that thinks with you."*
