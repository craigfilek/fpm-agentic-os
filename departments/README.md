# departments/

This is how the system **builds itself over time**. You don't draw an org chart on
day one. You run `/level-up` weekly; each shipped workflow lands in a department, and
that department's manager improves its own workflows from real run-logs.

## The shape (deliberately boring)

```
departments/
  <name>/                 ← a department (sales, ops, content, finance, …)
    MANAGER.md            ← the manager's charter: what it owns, the outcome it's accountable for
    workflows/
      <workflow>/
        CONTEXT.md        ← the stage-contract: Inputs / Process / Outputs
        <the workflow>    ← a prompt, a checklist, or built code (gStack lane)
        runs/             ← one file per run: the output + a one-line outcome note
```

## The three rules that keep this from becoming Build A

1. **A department is a folder.** A manager is a **charter + a retro you run** (or
   Hermes fires on a cadence you opt into). Not a swarm of always-on agents.
2. **Workflows beat agents. Boring is beautiful.** (Nate Herk's rule, kept.) Ship the
   smallest thing that produces the artifact; don't agentify what a checklist can do.
3. **Grow by accretion.** Start with zero departments. Each `/level-up` adds at most
   one workflow and improves one existing one. Compounding beats sweeping.

## Self-improvement (the "self-evolves" part)

Each manager's retro reads its department's `runs/` logs, finds what produced good
outputs vs. what needed correction, and applies **one** improvement per cycle —
tightening a CONTEXT.md step, fixing a recurring miss, or raising an autonomy level
that's earned trust. Where installed, it leans on `gstack-retro` + `gstack-learn` and
fpm-ai's council to do the reasoning. Nothing runs unasked until a human has watched
it work manually first.

Copy `_template/` to start a new department by hand, or just let `/level-up` do it.
