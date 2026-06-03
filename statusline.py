#!/usr/bin/env python3
"""Claude Code status line: model | dir | context usage %.
Context tokens = input + cache_read + cache_creation from the most recent
usage record in the session transcript. Cap is 200k, auto-bumped to 1M when a
session runs in the extended-context window (so % never reads >100%)."""
import json, os, sys

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("ctx ?")
        return

    model = (data.get("model") or {}).get("display_name") or "?"
    ws = data.get("workspace") or {}
    cwd = ws.get("current_dir") or data.get("cwd") or ""
    dirname = os.path.basename(cwd.rstrip("/")) or "~"
    transcript = data.get("transcript_path") or ""

    used = 0
    if transcript and os.path.exists(transcript):
        try:
            with open(transcript, "rb") as f:
                f.seek(0, 2)
                size = f.tell()
                f.seek(max(0, size - 600_000))
                tail = f.read().decode("utf-8", "replace")
            for line in reversed(tail.splitlines()):
                if '"usage"' not in line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                u = (obj.get("message") or {}).get("usage") or {}
                if u:
                    used = (u.get("input_tokens", 0)
                            + u.get("cache_read_input_tokens", 0)
                            + u.get("cache_creation_input_tokens", 0))
                    break
        except Exception:
            pass

    limit = 1_000_000 if (used > 200_000 or data.get("exceeds_200k_tokens")) else 200_000
    cap = "1M" if limit == 1_000_000 else "200k"
    pct = round(used / limit * 100) if used else 0
    print(f"{model} | {dirname} | ctx {pct}% ({round(used/1000)}k/{cap})")

main()
