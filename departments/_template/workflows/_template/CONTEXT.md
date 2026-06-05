# Workflow — <name>

The stage-contract. One agent reads this, does the work, writes the output. Keep it
small enough that "did it work?" is obvious.

| | |
|---|---|
| **Inputs** | <what files/data/context this workflow may read> |
| **Process** | <the steps the agent runs — the literal hand-process, automated> |
| **Outputs** | <the artifact it produces, and where it drops in `runs/`> |

**Autonomy:** draft-for-approval  ·  **Outcome ("this worked"):** <one sentence>
**Tie to:** <the department outcome / KPI this serves>

Each run drops its artifact + a one-line outcome note in `runs/`. The manager's retro
reads those to improve this contract.
