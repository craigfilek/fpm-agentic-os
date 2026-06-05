# Keys — what the rig needs to run

Your assistant asks for these during install (input is hidden, never shown on screen)
and again in the CEO interview. Each key is stored in a local file with `chmod 600`
and **never** committed to any repo. Here's every key, what it powers, and where to get it.

| Key | Needed? | Powers | Get it from | Stored in |
|---|---|---|---|---|
| **Anthropic API key** | **Required** | The agent itself — Claude Code + Hermes. Nothing talks without it. | console.anthropic.com/settings/keys | `~/.hermes/.env`, `~/.env.anthropic` |
| **ZeroEntropy key** | **Recommended** | *Semantic* recall in gbrain (search by meaning). Without it you still get **keyword** recall — the brain works, just less smart. | ZeroEntropy (your embedding provider) — or switch gbrain to OpenAI embeddings if you already have an OpenAI key | `~/.gbrain/config.json` |
| **Telegram bot token** | Optional | Talking to your assistant from your phone (Telegram). | @BotFather on Telegram (`/newbot`) | `~/.hermes/.env` |

## The rule

- **Required** = the rig won't function without it. Install will keep going, but flag loudly.
- **Recommended** = the rig runs, but a core feature is degraded until you add it.
- **Optional** = a bonus capability you can turn on any time later.

## How to check what's set

```
boot                      # the green health lamp — tells you if the brain is live
gbrain doctor --fast      # brain health, incl. whether embeddings are configured
```

## Adding a key later

You never have to reinstall. Re-run `install.sh` (it's idempotent and re-prompts for
anything missing), or set the key directly:

- **Anthropic:** add `ANTHROPIC_API_KEY=...` to `~/.hermes/.env`
- **ZeroEntropy:** add `"zeroentropy_api_key": "..."` to `~/.gbrain/config.json` (then `gbrain embed --stale` to upgrade existing notes to semantic)
- **Telegram:** run `hermes gateway setup`

## Security

Keys are read with a hidden prompt, written only to local dotfiles, and `chmod 600`.
They are never passed on the command line (so they can't show up in `ps`) and never
enter git — the kit's leak hooks block any commit that contains a key pattern.
