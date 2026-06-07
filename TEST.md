# TEST — agentic OS root (install proof)

**PASS WHEN:** the kit is portable + self-verifying — `bin/doctor` is green and the JVC + onboard
pieces ship in the repo.

## Check
```bash
test -x bin/doctor || exit 1
test -s starter/CONSTITUTION.md || exit 1          # JVC structure ships
test -x bin/test-onboard || exit 1                 # onboard is provable
# note: starter/jvc-method-card.md is HELD from public ship (Jake's paid-course IP) — not required here
grep -q "Step 0 — lay the JVC structure FIRST" .claude/skills/onboard/SKILL.md || exit 1
./bin/doctor >/dev/null 2>&1
```
