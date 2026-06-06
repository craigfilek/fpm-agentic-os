#!/usr/bin/env python3
"""send_telegram.py — post a markdown file's contents to Telegram via the bot.

The reliable "mailman" half of Cron Central: GitHub Actions runs this on a
schedule and sends whatever the local rig prepared. No rig state needed in the
cloud — it only delivers a file.

Usage:   python3 cron/send_telegram.py cron/daily.md
Secrets (from env / GitHub repo secrets):
   TELEGRAM_BOT_TOKEN   the Telegram bot token
   TELEGRAM_CHAT_ID     the chat to send to (a number, e.g. -1002116222415)
"""
import os
import sys
import json
import urllib.request

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        print("ERROR: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set (GitHub secrets).",
              file=sys.stderr)
        return 1

    path = sys.argv[1] if len(sys.argv) > 1 else "cron/daily.md"
    try:
        text = open(path, encoding="utf-8").read().strip()
    except FileNotFoundError:
        text = "☀️ Integrator beat — no update was prepared today."
    if not text:
        text = "☀️ Integrator beat — (empty update)."
    text = text[:4000]  # Telegram message cap

    body = json.dumps({
        "chat_id": chat,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            ok = json.loads(resp.read()).get("ok")
            print("sent ✓" if ok else "send failed")
            return 0 if ok else 1
    except Exception as e:
        print(f"ERROR sending: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
