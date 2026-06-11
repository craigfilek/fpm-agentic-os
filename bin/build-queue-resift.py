#!/usr/bin/env python3
"""build-queue-resift -- the deterministic half of the BUILD-QUEUE re-sift.

The queue rotted: zero-dollar rows, fact-claims mis-bucketed as builds, rows
naming systems that already shipped, near-duplicate twins, no dates. This
script is pass 1 of the re-sift plan: pure rules, no judgment calls. Agents
(pass 2) handle the gray rows it can't call.

Rules applied (in precedence order, one verdict per row):
  RECYCLE  -- fact-pattern rows (no build verb + fact signal). They are not
              builds; they ride the belt back into the brain as plain claims.
  GRAY     -- maybe-fact rows the heuristic can't call. Left on the queue,
              flagged for the agent judgment pass.
  KILL $0  -- bet is zero. No money claim, no seat on a money board.
  KILL dead-system -- row names GSD, a retired SIFT tower, or a system that
              already shipped (checked against the REAL bin/ script names and
              the REAL Rig room folders -- the lists are read, not hardcoded).
  MERGE    -- near-duplicate survivors collapse into one row; each absorbed
              twin bumps `touchpoints` (duplicates are reinforcement, not noise).
  Survivors are re-scored: ROI = (bet * near * pull * tp_bonus) / effort,
  with near/pull defaulting to 1.0 until the agent pass assigns them, and
  every row gets `added` / `last_reinforced` dates (backfilled from the
  source filename where possible).

Two modes -- the human gate is real:
  --propose   (default) writes a proposal JSON next to the queue and a plain
              kill-list for Craig. Touches NOTHING else.
  --approve   stamps the proposal approved (run after Craig says yes).
  --execute   applies an APPROVED proposal: kills go to an archive sidecar
              (recoverable, never deleted), recycled facts land on the belt
              (01-dump/inbox), grays stay flagged, merges collapse, scores and
              dates land, BUILD-QUEUE.md re-renders. Refuses to run without an
              approved proposal or if the queue changed since the proposal.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sift_core
import sift_stages

BIN_DIR = Path(__file__).resolve().parent

# ── paths (all derived; no user-specific literals) ───────────────────────────


def paths(vault=None):
    vault = sift_core._vault_dir(vault)
    proj = os.path.join(vault, "01 Projects")
    return {
        "queue": os.path.join(proj, ".build-queue.json"),
        "proposal": os.path.join(proj, ".build-queue.resift-proposal.json"),
        "archive": os.path.join(proj, ".build-queue.archive.json"),
        "kill_list": os.path.join(vault, "02 Company", "Dispatch",
                                  "resift-kill-list.md"),
        "rig_rooms": os.path.join(proj, "Rig"),
    }


# ── rule 1 material: fact-vs-build heuristic ─────────────────────────────────
# A build row tells someone to MAKE something. A fact row just states the world.
BUILD_VERB_STEMS = [
    "build", "create", "make", "add", "implement", "write", "design", "ship",
    "launch", "develop", "automate", "integrate", "fix", "refactor",
    "generate", "enable", "deploy", "render", "convert", "extract", "track",
    "score", "route", "sync", "migrate", "wire", "hook", "pipe", "transform",
    "configure", "install", "connect", "embed", "schedule", "publish",
    "transcribe", "parse", "scan", "detect", "flag", "sort", "filter",
    "cluster", "rank", "compile", "combine", "improve", "replace", "rebuild",
    "redesign", "streamline", "consolidate", "merge", "expose", "package",
    "sell", "offer", "monetize", "charge", "price", "pitch", "use", "copy",
    "check", "open", "store", "switch", "plan", "summarize", "change",
    "clear", "update", "organize", "push", "pull", "post", "record", "host",
    "draft", "edit", "test", "validate", "train", "cache", "stream",
    "archive", "index", "link", "tag", "label", "rename", "move", "split",
    "wrap", "support",
]


def _verb_forms(v):
    forms = {v, v + "s", v + "es"}
    if v.endswith("e"):
        forms |= {v + "d", v[:-1] + "ing"}      # make -> made? no: making
    elif v.endswith("y"):
        forms |= {v[:-1] + "ied", v + "ing"}
    else:
        forms |= {v + "ed", v + "ing"}
    return forms


_ALL_FORMS = set()
for _v in BUILD_VERB_STEMS:
    _ALL_FORMS |= _verb_forms(_v)
_ALL_FORMS |= {"built", "made", "wrote", "setup"}   # irregulars
BUILD_VERB_RE = re.compile(
    r"\b(?:%s)\b" % "|".join(sorted(_ALL_FORMS, key=len, reverse=True)))
MULTIWORD_BUILD_RE = re.compile(
    r"\b(?:set(?:s|ting)? up|stood up|stand(?:s|ing)? up|"
    r"work(?:s|ed|ing)? on|need(?:s|ed)? to|"
    r"turn(?:s|ed|ing)? .{0,40} into|broke .{0,40} into|"
    r"break(?:s|ing)? .{0,40} into)\b")
BUILD_NOUNS = (
    "system|tool|script|pipeline|dashboard|agent|bot|app|feature|workflow|"
    "automation|plugin|api|database|page|site|website|course|template|"
    "generator|parser|integration|skill|command|cron|server|interface|"
    "prompt|module|service|product|funnel|landing page|recipe|framework"
)
BUILD_NOUN_RE = re.compile(r"\b(?:%s)s?\b" % BUILD_NOUNS)
FIRST_PERSON_RE = re.compile(r"^(i|we|my|our)\b")
COPULA_RE = re.compile(r"\b(can|is|are|was|were|has|have|had)\b")
PAST_RE = re.compile(
    r"\b(\w{3,}ed|did|was|were|had|went|got|came|took|built|made|wrote|read|"
    r"began|grew|felt|saw|knew|met|left|spent|taught|bought|sold|told|"
    r"thought|found|ran|gave|held)\b")
INTENT_RE = re.compile(
    r"\b(will|want(s)? to|plan(s|ning)? to|going to|need(s)? to|should)\b")


def fact_verdict(claim):
    """Return 'recycle', 'gray', or None (treat as a build)."""
    c = sift_core.norm(claim)
    first = bool(FIRST_PERSON_RE.match(c))
    if first and PAST_RE.search(c) and not INTENT_RE.search(c):
        return "recycle"          # autobiography: "I developed...", "My mother was..."
    has_verb = bool(BUILD_VERB_RE.search(c)) or bool(MULTIWORD_BUILD_RE.search(c))
    has_noun = bool(BUILD_NOUN_RE.search(c))
    if has_verb:
        return None
    if first:
        return "recycle"          # first-person statement, nothing buildable
    if not has_noun and COPULA_RE.search(c):
        return "recycle"          # "X can Y" with nothing buildable
    if not has_noun:
        return "gray"             # no verb, no noun, no clear signal
    if COPULA_RE.search(c):
        return "gray"             # observation ABOUT a buildable thing
    return None


# ── rule 3 material: dead/shipped-system phrases from the REAL lists ─────────
GENERIC_WORDS = {
    "build", "course", "gtd", "sift", "feed", "canon", "services", "gallery",
    "lab", "reference", "boot", "doctor", "pulse", "reclaim", "backend",
    "test", "all", "core", "stages", "open", "on", "write", "to",
}


def dead_system_patterns(rig_rooms_dir):
    """Phrases meaning 'this already shipped or is retired'. Derived from the
    actual bin/ scripts and the actual Rig room folders, plus the two known
    retired names (GSD, the old SIFT towers)."""
    phrases = set()
    for p in BIN_DIR.iterdir():
        name = p.name
        if name.startswith((".", "_")) or name.endswith((".plist", ".py")):
            continue
        parts = [w for w in name.lower().split("-") if w]
        if len(parts) < 2 or all(w in GENERIC_WORDS for w in parts):
            continue
        phrases.add(" ".join(parts))
        phrases.add(" ".join(reversed(parts)))
        phrases.add(name.lower())
    rooms = Path(rig_rooms_dir)
    if rooms.is_dir():
        for p in sorted(rooms.iterdir()):
            if not p.is_dir() or p.name.startswith((".", "_")):
                continue
            words = p.name.lower().split()
            if len(words) < 2 or all(w in GENERIC_WORDS for w in words):
                continue
            phrases.add(" ".join(words))
    pats = [re.compile(r"\bgsd\b"), re.compile(r"\bsift towers?\b")]
    for ph in sorted(phrases):
        pats.append(re.compile(r"\b" + re.escape(ph) + r"\b"))
    return pats


def dead_system_hit(row, patterns):
    text = sift_core.norm(row.get("claim", "") + " " + row.get("feature", ""))
    for pat in patterns:
        if pat.search(text):
            return pat.pattern.strip("\\b")
    return None


# ── merge rule: near-duplicate clustering (deterministic union-find) ─────────
def merge_key(claim):
    c = sift_core.norm(claim)
    return re.sub(r"[^a-z0-9 ]+", "", c)


def find_clusters(rows, threshold=0.8):
    """rows: list of (index, claim). Returns clusters as lists of indexes."""
    keys = [(i, merge_key(c)) for i, c in rows]
    parent = {i: i for i, _ in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a in range(len(keys)):
        ia, ka = keys[a]
        for b in range(a + 1, len(keys)):
            ib, kb = keys[b]
            m = SequenceMatcher(None, ka, kb)
            if m.real_quick_ratio() < threshold:
                continue
            if m.quick_ratio() < threshold:
                continue
            if m.ratio() >= threshold:
                ra, rb = find(ia), find(ib)
                if ra != rb:
                    parent[max(ra, rb)] = min(ra, rb)
    clusters = {}
    for i, _ in keys:
        clusters.setdefault(find(i), []).append(i)
    return [sorted(v) for _, v in sorted(clusters.items()) if len(v) > 1]


# ── re-score + dates ─────────────────────────────────────────────────────────
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def source_date(source, fallback):
    m = DATE_RE.search(os.path.basename(str(source or "")))
    return m.group(1) if m else fallback


def rescore(row, today):
    bet = float(row.get("bet", 0) or 0)
    effort = max(1, int(row.get("effort", 2) or 2))
    near = float(row.get("near", 1.0))       # agent pass assigns; default 1.0
    pull = float(row.get("pull", 1.0))       # agent pass assigns; default 1.0
    tp = int(row.get("touchpoints", 1) or 1)
    tp_bonus = min(1.5, 1 + 0.1 * (tp - 1))
    row["touchpoints"] = tp
    row["near"] = near
    row["pull"] = pull
    row["roi"] = round(bet * near * pull * tp_bonus / effort, 1)
    row.setdefault("added", source_date(row.get("source"), today))
    row.setdefault("last_reinforced", row["added"])
    return row


# ── the propose pass ─────────────────────────────────────────────────────────
def build_proposal(queue, rig_rooms_dir, today):
    dead_pats = dead_system_patterns(rig_rooms_dir)
    verdicts = []  # one entry per row, same order as queue
    for i, row in enumerate(queue):
        claim = row.get("claim", "")
        fv = fact_verdict(claim)
        if fv == "recycle":
            verdicts.append({"index": i, "verdict": "recycle",
                             "reason": "fact-pattern, not a build"})
            continue
        if fv == "gray":
            verdicts.append({"index": i, "verdict": "gray",
                             "reason": "maybe-fact; agent pass decides"})
            continue
        if not float(row.get("bet", 0) or 0):
            verdicts.append({"index": i, "verdict": "kill-zero",
                             "reason": "bet is $0"})
            continue
        hit = dead_system_hit(row, dead_pats)
        if hit:
            verdicts.append({"index": i, "verdict": "kill-dead",
                             "reason": "names dead/shipped system: %s" % hit})
            continue
        verdicts.append({"index": i, "verdict": "survive", "reason": ""})

    surv_rows = [(v["index"], queue[v["index"]].get("claim", ""))
                 for v in verdicts if v["verdict"] == "survive"]
    merges = []
    absorbed = {}
    for cluster in find_clusters(surv_rows):
        canon = max(cluster, key=lambda i: (
            float(queue[i].get("bet", 0) or 0),
            len(queue[i].get("claim", "")), -i))
        twins = [i for i in cluster if i != canon]
        merges.append({"canonical": canon, "absorbed": twins,
                       "touchpoints": len(cluster)})
        for t in twins:
            absorbed[t] = canon
    for v in verdicts:
        if v["index"] in absorbed:
            v["verdict"] = "merge"
            v["reason"] = "near-duplicate of row %d" % absorbed[v["index"]]

    survivors = {}
    for v in verdicts:
        if v["verdict"] != "survive":
            continue
        i = v["index"]
        row = dict(queue[i])
        tp = next((m["touchpoints"] for m in merges if m["canonical"] == i), 1)
        row["touchpoints"] = tp
        row = rescore(row, today)
        if tp > 1:
            dates = [source_date(queue[t].get("source"), today)
                     for t in ([i] + next(m["absorbed"] for m in merges
                                          if m["canonical"] == i))]
            row["added"] = min(dates)
            row["last_reinforced"] = max(dates)
        survivors[str(i)] = row

    counts = {}
    for v in verdicts:
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
    return {"generated": today, "approved": False,
            "counts": counts, "verdicts": verdicts,
            "merges": merges, "survivors": survivors}


# ── the human kill-list (plain words, bold-number sections) ──────────────────
def fmt_money(x):
    x = float(x or 0)
    return "{:,.0f}".format(x) if x == int(x) else "{:,.1f}".format(x)


def fmt_row(row):
    src = os.path.basename(str(row.get("source", ""))).replace(".md", "")
    claim = row.get("claim", "").strip()
    if len(claim) > 110:
        claim = claim[:107] + "..."
    return '"%s" — $%s bet (%s)' % (claim, fmt_money(row.get("bet", 0)), src)


def write_kill_list(path, queue, prop):
    c = prop["counts"]
    total = len(queue)

    def examples(verdict, n=5):
        out = []
        for v in prop["verdicts"]:
            if v["verdict"] == verdict:
                out.append((v, queue[v["index"]]))
            if len(out) == n:
                break
        return out

    letters = "abcdefgh"
    L = ["# Resift kill-list — one yes clears the board", "",
         "The build queue has %d rows. These rules cut it down. Nothing is "
         "deleted yet — killed rows go to a recoverable archive, and fact "
         "rows ride the belt back into the brain as claims. You say yes to "
         "the whole list, or strike a whole rule. Never row by row." % total,
         ""]

    L.append("**1. Kill: zero-dollar bets — %d rows.**" % c.get("kill-zero", 0))
    L.append("No money claim, no seat on a money board. Examples:")
    for k, (v, row) in enumerate(examples("kill-zero")):
        L.append("%s. %s" % (letters[k], fmt_row(row)))
    L.append("")

    L.append("**2. Kill: already-shipped or dead systems — %d rows.**"
             % c.get("kill-dead", 0))
    L.append("These name GSD, retired SIFT towers, or things that already "
             "live as real scripts and Rig rooms. The script checked the "
             "actual file and folder lists. Examples:")
    for k, (v, row) in enumerate(examples("kill-dead")):
        L.append("%s. %s — %s" % (letters[k], fmt_row(row), v["reason"]))
    L.append("")

    L.append("**3. Recycle to the belt: fact rows — %d rows.**"
             % c.get("recycle", 0))
    L.append("These are statements about the world, not things to build. "
             "They leave the board and land in the dump inbox as plain "
             "claims, so the brain keeps them. Examples:")
    for k, (v, row) in enumerate(examples("recycle")):
        L.append("%s. %s" % (letters[k], fmt_row(row)))
    L.append("")

    n_merge = c.get("merge", 0)
    L.append("**4. Merge: near-duplicate twins — %d rows fold into %d "
             "keepers.**" % (n_merge, len(prop["merges"])))
    L.append("Twins collapse into the strongest row, and each absorbed twin "
             "bumps its touchpoint count — repeats are signal, not noise. "
             "Examples:")
    for k, m in enumerate(prop["merges"][:5]):
        canon = queue[m["canonical"]]
        L.append('%s. "%s" keeps %d touchpoints (absorbs %d twin%s)'
                 % (letters[k], canon.get("claim", "")[:100],
                    m["touchpoints"], len(m["absorbed"]),
                    "" if len(m["absorbed"]) == 1 else "s"))
    L.append("")

    L.append("**5. Gray rows: %d — left for the agent pass.**"
             % c.get("gray", 0))
    L.append("The script could not tell fact from build on these. They stay "
             "on the queue flagged gray; the judgment agents call them after "
             "your yes.")
    L.append("")

    surv = c.get("survive", 0)
    top = sorted(prop["survivors"].values(),
                 key=lambda r: (-r.get("roi", 0), r.get("claim", "")))[:5]
    L.append("**6. What survives: %d rows, re-scored and dated.**" % surv)
    L.append("New score per row: ROI = bet times nearness times pull times a "
             "touchpoint bonus, divided by effort. Nearness and pull start at "
             "1.0 until the agent pass sets them. Every row now carries added "
             "and last-reinforced dates. New top five:")
    for k, row in enumerate(top):
        L.append("%s. %s — ROI %s" % (letters[k], fmt_row(row),
                                      fmt_money(row.get("roi", 0))))
    L.append("")
    L.append("Say yes and --execute runs; say show X to expand a group.")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# ── the execute pass ─────────────────────────────────────────────────────────
def execute(p, today, vault=None):
    if not os.path.exists(p["proposal"]):
        sys.exit("REFUSED: no proposal found at %s — run --propose first."
                 % p["proposal"])
    prop = json.load(open(p["proposal"], encoding="utf-8"))
    if not prop.get("approved"):
        sys.exit("REFUSED: proposal is not approved. Craig says yes, then "
                 "run --approve, then --execute.")
    queue = json.load(open(p["queue"], encoding="utf-8"))
    qhash = hashlib.sha256(
        open(p["queue"], "rb").read()).hexdigest()
    if prop.get("queue_sha256") and prop["queue_sha256"] != qhash:
        sys.exit("REFUSED: the queue changed since this proposal was made. "
                 "Re-run --propose.")

    by_index = {v["index"]: v for v in prop["verdicts"]}
    archive = []
    if os.path.exists(p["archive"]):
        try:
            archive = json.load(open(p["archive"], encoding="utf-8"))
        except Exception:
            archive = []

    new_queue, recycled = [], []
    for i, row in enumerate(queue):
        v = by_index.get(i, {"verdict": "survive", "reason": ""})
        verdict = v["verdict"]
        if verdict in ("kill-zero", "kill-dead", "merge"):
            row = dict(row)
            row["resift"] = {"verdict": verdict, "reason": v["reason"],
                             "date": today}
            archive.append(row)
        elif verdict == "recycle":
            recycled.append(row)
            row = dict(row)
            row["resift"] = {"verdict": "recycle", "reason": v["reason"],
                             "date": today}
            archive.append(row)
        elif verdict == "gray":
            row = dict(row)
            row["gray"] = True
            row = rescore(row, today)
            new_queue.append(row)
        else:
            new_queue.append(prop["survivors"].get(str(i), rescore(dict(row),
                                                                   today)))

    with open(p["archive"], "w", encoding="utf-8") as f:
        json.dump(archive, f, indent=2, ensure_ascii=False)
    with open(p["queue"], "w", encoding="utf-8") as f:
        json.dump(new_queue, f, indent=2, ensure_ascii=False)

    # recycled facts ride the belt: one claims file into the dump inbox
    if recycled:
        sift_stages.ensure_dirs()
        belt = sift_stages.INBOX / ("%s resift recycled fact-claims.md" % today)
        lines = ["# Resift recycled fact-claims (%s)" % today, "",
                 "Fact rows pulled off the build queue — they are claims, "
                 "not builds. Source noted per line.", ""]
        for k, row in enumerate(recycled, 1):
            src = os.path.basename(str(row.get("source", "")))
            lines.append("%d. %s  (from %s)" % (k, row.get("claim", ""), src))
        belt.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("recycled %d fact rows -> %s" % (len(recycled), belt))

    sift_core.update_build_queue([], "", vault)  # re-render the tree
    prop["executed"] = today
    with open(p["proposal"], "w", encoding="utf-8") as f:
        json.dump(prop, f, indent=2, ensure_ascii=False)
    print("queue: %d -> %d rows · archived %d · gray kept %d"
          % (len(queue), len(new_queue), len(archive),
             sum(1 for r in new_queue if r.get("gray"))))


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--propose", action="store_true",
                      help="write proposal + kill-list (default; touches nothing)")
    mode.add_argument("--approve", action="store_true",
                      help="stamp the proposal approved (after Craig's yes)")
    mode.add_argument("--execute", action="store_true",
                      help="apply an approved proposal")
    ap.add_argument("--vault", default=None, help="vault dir override")
    args = ap.parse_args()
    p = paths(args.vault)
    today = date.today().isoformat()

    if args.approve:
        if not os.path.exists(p["proposal"]):
            sys.exit("REFUSED: no proposal to approve — run --propose first.")
        prop = json.load(open(p["proposal"], encoding="utf-8"))
        prop["approved"] = True
        prop["approved_on"] = today
        with open(p["proposal"], "w", encoding="utf-8") as f:
            json.dump(prop, f, indent=2, ensure_ascii=False)
        print("proposal approved -> %s" % p["proposal"])
        return

    if args.execute:
        execute(p, today, args.vault)
        return

    # default: --propose
    if not os.path.exists(p["queue"]):
        sys.exit("no queue at %s" % p["queue"])
    queue = json.load(open(p["queue"], encoding="utf-8"))
    prop = build_proposal(queue, p["rig_rooms"], today)
    prop["queue_sha256"] = hashlib.sha256(
        open(p["queue"], "rb").read()).hexdigest()
    with open(p["proposal"], "w", encoding="utf-8") as f:
        json.dump(prop, f, indent=2, ensure_ascii=False)
    os.makedirs(os.path.dirname(p["kill_list"]), exist_ok=True)
    write_kill_list(p["kill_list"], queue, prop)
    c = prop["counts"]
    print("proposal -> %s" % p["proposal"])
    print("kill-list -> %s" % p["kill_list"])
    print("counts: %s (of %d rows)" % (
        " · ".join("%s %d" % kv for kv in sorted(c.items())), len(queue)))


if __name__ == "__main__":
    main()
