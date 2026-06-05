# Versions

The components track their upstream repos (gbrain installs from
`github:garrytan/gbrain` HEAD, the others are `git clone`d), so pinning exact
numbers here just rots. To see what you actually have, ask the machine:

```bash
boot                                   # the health lamp (vault · index · MCP · sync)
~/.bun/bin/gbrain --version            # gbrain
~/hermes-agent/.venv/bin/hermes --version
bun --version ; uv --version
( cd ~/fpm-ai && git rev-parse --short HEAD )
( cd ~/gstack && git rev-parse --short HEAD )
```

## Reference baseline (the machine this was built on, 2026-06)

Use these only to sanity-check a wildly different environment — not as pins.

| Component | Baseline |
|---|---|
| gbrain | 0.42.x (from `github:garrytan/gbrain`) |
| Hermes | 0.15.1 (2026.5.29) |
| bun | 1.3.x |
| uv | 0.10.x |
| Python (Hermes venv) | 3.11 |
| macOS | 13 (Ventura) or later |
