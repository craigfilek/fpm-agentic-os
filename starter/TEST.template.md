# TEST — <this folder>

*The provable check for this folder. `bin/test-all` runs the `## Check` block from inside
this folder; exit 0 = pass. Prove it works — don't assume (like testing camera + mic after
granting an app access). Every folder carries one of these.*

**PASS WHEN:** <one plain line — what proves this folder is doing its job>

## Check
```bash
# Keep it fast + real. exit 0 = pass, non-zero = fail.
# Example: this folder has its router and isn't empty.
test -f CLAUDE.md && test -n "$(ls -A)"
```
