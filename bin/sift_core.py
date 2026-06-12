"""sift_core — shared guts for the SIFT chunker.

One source of truth for: split a transcript into segments, ask Claude Haiku
(via OpenRouter) for atomic claims + verbatim quotes, and verify the quotes.
Both `sift-chunk` (CLI) and `sift-bench` (GUI) import this so they can't drift.
"""
import hashlib
import json
import os
import re
import urllib.request

# Cloud engine: Claude Haiku via OpenRouter. Needs OPENROUTER_API_KEY in ~/.sift.env.
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Local engine: ollama's OpenAI-compatible chat endpoint. No API key needed.
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"


def _env_file_val(name):
    """Read NAME from ~/.sift.env so the key + model live in one place."""
    p = os.path.expanduser("~/.sift.env")
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _cloud_key():
    return os.environ.get("OPENROUTER_API_KEY") or _env_file_val("OPENROUTER_API_KEY")


CLOUD_MODEL = (os.environ.get("SIFT_CLOUD_MODEL")
               or _env_file_val("SIFT_CLOUD_MODEL")
               or "anthropic/claude-haiku-4.5")

OLLAMA_MODEL = (os.environ.get("OLLAMA_MODEL")
                or _env_file_val("OLLAMA_MODEL")
                or "qwen2.5:14b")

# Substrings in a source path that force the LOCAL backend — private content
# must never leave the machine, no matter what SIFT_BACKEND says.
_PRIVATE_MARKERS = ("Voice Memos", "/private/", ".private.")

_FM_PRIVATE_RE = re.compile(r"^private\s*:\s*true\b", re.IGNORECASE)


def _frontmatter_private(src_path):
    """True if the file's YAML frontmatter says `private: true`.

    Cheap on purpose: reads only the first ~20 lines. Fail-safe: any read or
    parse problem returns False, leaving the path-based guard behavior
    unchanged."""
    try:
        with open(src_path, encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(20)]
        if lines[0].strip() != "---":
            return False
        for line in lines[1:]:
            if line.strip() == "---":
                return False  # frontmatter closed without the flag
            if _FM_PRIVATE_RE.match(line.strip()):
                return True
        return False
    except Exception:
        return False


def _resolve_backend(src_path=None):
    """Pick 'local' or 'cloud'. Default local. A private source — marked by
    path (`_PRIVATE_MARKERS`) OR by `private: true` frontmatter — forces local
    regardless of the toggle (leak-guard). Returns the backend name."""
    backend = (os.environ.get("SIFT_BACKEND")
               or _env_file_val("SIFT_BACKEND")
               or "local").strip().lower()
    if backend not in ("local", "cloud"):
        backend = "local"
    if src_path and backend != "local":
        s = str(src_path)
        if any(m in s for m in _PRIVATE_MARKERS) or _frontmatter_private(s):
            print(f"[leak-guard] private source -> forcing local backend "
                  f"(was {backend}): {s}")
            backend = "local"
    return backend

# The default rules the model follows. The bench lets you edit this live.
DEFAULT_PROMPT = (
    "You extract atomic items from a piece of someone's transcript and ROUTE each "
    "into one bucket. Output ONLY a JSON array, one object per item:\n"
    '[{"claim":"<one terse claim, idea, or action>",'
    '"quote":"<the EXACT words from the text this came from, copied verbatim>",'
    '"bucket":"claim|build|inspo|drop",'
    '"kind":"belief|event|fact|preference|decision",'
    '"salience":"high|medium|low",'
    '"bet":"<build ONLY: rough dollar value if shipped, number e.g. 5000, else empty>",'
    '"effort":"<build ONLY: 1=hours, 2=days, 3=weeks, else empty>",'
    '"feature":"<build ONLY: the feature or function this build belongs under, '
    'a short noun phrase; reuse the SAME name for related builds so they nest>"}]\n'
    "Buckets:\n"
    "- claim = a fact/belief/decision worth REMEMBERING (knowledge that floats to the brain).\n"
    "- build = an actionable thing to MAKE or SHIP that could earn or save money.\n"
    "- inspo = a reference or example to keep but not act on now.\n"
    "- drop = filler, greeting, or noise.\n"
    "Rules:\n"
    "- One item per object. Each must stand alone and be judgeable on its own.\n"
    "- The quote MUST be copied character-for-character from the text below. Do "
    "not paraphrase the quote. If you can't quote it exactly, don't make the item.\n"
    "- The quote MUST be ONE single contiguous span copied verbatim. NEVER stitch "
    "separate fragments together with '...' or '…'. If you cannot support the claim "
    "with one unbroken span, drop the item.\n"
    "- For build items ALWAYS fill bet (a number) and effort (1, 2, or 3); best guess if unsure.\n"
    "- Capture EVERY distinct item, not just the notable ones. Don't summarize.\n"
    "- Skip filler (greetings, 'um', 'you know'). No prose, no code fences, JSON only.\n"
    "- Empty array [] is valid only if the passage is truly all noise."
)


def _ask_local(prompt_text, text, timeout=300):
    """Ask the local ollama model (OpenAI-compatible endpoint) for claims.

    Same prompt + same response shape as the cloud path — only the transport,
    endpoint, and model differ. No API key needed.
    """
    body = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": "TEXT:\n" + text + "\n\nJSON array:"},
        ],
        "temperature": 0.1,
        "max_tokens": 8000,
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        d = json.loads(resp.read())
        return d["choices"][0]["message"]["content"].strip()


def ask_model(prompt_text, text, timeout=300, src_path=None):
    """Ask the model for claims. Backend = SIFT_BACKEND (default 'local'); a
    private src_path forces local (leak-guard). The prompt, response parsing, and
    all gates are identical for both backends — only the transport differs."""
    if _resolve_backend(src_path) == "local":
        return _ask_local(prompt_text, text, timeout)
    key = _cloud_key()
    if not key:
        raise RuntimeError(
            "no OPENROUTER_API_KEY in ~/.sift.env — the chunker runs on "
            "Claude Haiku via OpenRouter and needs a key.")
    body = json.dumps({
        "model": CLOUD_MODEL,
        "messages": [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": "TEXT:\n" + text + "\n\nJSON array:"},
        ],
        "temperature": 0.1,
        "max_tokens": 8000,
    }).encode("utf-8")
    req = urllib.request.Request(
        OPENROUTER_URL, data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=min(timeout, 120)) as resp:
        d = json.loads(resp.read())
        return d["choices"][0]["message"]["content"].strip()


def parse_claims(raw):
    s = re.sub(r"\s*```$", "", re.sub(r"^```(?:json)?\s*", "", raw.strip()))
    try:
        d = json.loads(s)
        if isinstance(d, list):
            return d
        if isinstance(d, dict) and isinstance(d.get("claims"), list):
            return d["claims"]
    except Exception:
        pass
    m = re.search(r"\[[\s\S]*\]", s)
    if m:
        try:
            d = json.loads(m.group(0))
            if isinstance(d, list):
                return d
        except Exception:
            pass
    # last resort: scan balanced {...} objects. Survives a missing closing ],
    # a trailing comma, prose around the JSON, or a truncated final object.
    objs, depth, start = [], 0, None
    for i, ch in enumerate(s):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    o = json.loads(s[start:i + 1])
                    if isinstance(o, dict):
                        objs.append(o)
                except Exception:
                    pass
                start = None
    return objs or None


def norm(s):
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def strip_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip()
    return text


def segment(text, seg_words):
    paras = re.split(r"\n\s*\n", text)
    segs, cur, n = [], [], 0
    for p in paras:
        w = len(p.split())
        if cur and n + w > seg_words:
            segs.append("\n\n".join(cur)); cur, n = [], 0
        cur.append(p); n += w
    if cur:
        segs.append("\n\n".join(cur))
    return [s for s in segs if s.strip()]


# Any of these inside a quote means the model stitched non-contiguous fragments,
# so the quote-as-presented is fabricated even if each piece is verbatim.
_ELLIPSIS_RE = re.compile(r"\.\.\.|…|\s\.\.\s")


def quote_is_clean(quote):
    """False if the quote contains an ellipsis (stitched fragments), else True."""
    return not bool(_ELLIPSIS_RE.search(quote or ""))


# Stopwords kept tiny on purpose — local heuristic, no deps.
_STOP = frozenset((
    "the a an and or but of to in on for with is are was were be been being it "
    "its this that these those as at by from into about you your we our they "
    "their he she his her i me my not no so if then than out up down over also "
    "just like can could would should will may might do does did has have had "
    "what which who whom how why when where there here all any some more most "
    "one two thing things get got make made go going").split())


def _tokens(s):
    return [w for w in re.findall(r"[a-z0-9]+", (s or "").lower())
            if w not in _STOP and len(w) > 2]


def relevance_ok(claim, quote, threshold=0.34):
    """Cheap local claim<->quote support check (no extra cloud calls).

    Fraction of the claim's content tokens that also appear in the quote. A
    verbatim quote can still fail to support its claim; if overlap < threshold
    the pair is flagged for the human. Threshold 0.34 = at least ~a third of the
    claim's key words must be grounded in the quoted span.
    """
    ct = set(_tokens(claim))
    if not ct:
        return True  # nothing to judge against; don't false-flag
    qt = set(_tokens(quote))
    overlap = len(ct & qt) / len(ct)
    return overlap >= threshold


def chunk_text(text, prompt_text=DEFAULT_PROMPT, seg_words=700, on_segment=None,
               src_path=None):
    """Run the chunker over one transcript's text. Returns a result dict.

    on_segment(idx, total, kept) is an optional live-progress callback.
    src_path (when given) feeds the leak-guard: a private path forces local.
    """
    body = strip_frontmatter(text)
    segs = segment(body, seg_words)
    claims, failed = [], []
    for idx, seg in enumerate(segs, 1):
        try:
            out = ask_model(prompt_text, seg, src_path=src_path)
        except Exception as e:
            failed.append({"seg": idx, "why": f"model error: {e}"})
            if on_segment: on_segment(idx, len(segs), 0)
            continue
        parsed = parse_claims(out)
        if parsed is None:
            failed.append({"seg": idx, "why": "unparseable JSON"})
            if on_segment: on_segment(idx, len(segs), 0)
            continue
        kept = 0
        for c in parsed:
            if not isinstance(c, dict):
                continue
            claim = (c.get("claim") or "").strip()
            quote = (c.get("quote") or "").strip()
            if not claim:
                continue
            verified = bool(quote) and norm(quote) in norm(seg)
            bucket = (c.get("bucket") or "claim").strip().lower()
            if bucket not in ("claim", "build", "inspo", "drop"):
                bucket = "claim"
            item = {
                "claim": claim, "quote": quote,
                "kind": (c.get("kind") or "fact").strip(),
                "salience": (c.get("salience") or "medium").strip(),
                "bucket": bucket,
                "verified": verified,
                "quote_clean": quote_is_clean(quote),
                "relevance_ok": relevance_ok(claim, quote),
                "seg": idx, "keep": True,
            }
            if bucket == "build":
                try:
                    item["bet"] = float(str(c.get("bet") or 0).replace(",", "").replace("$", "").strip() or 0)
                except Exception:
                    item["bet"] = 0.0
                try:
                    item["effort"] = max(1, int(str(c.get("effort") or 2).strip() or 2))
                except Exception:
                    item["effort"] = 2
                item["feature"] = (c.get("feature") or "Unsorted").strip() or "Unsorted"
            claims.append(item)
            kept += 1
        if on_segment: on_segment(idx, len(segs), kept)
    unverified = sum(1 for c in claims if not c["verified"])
    ellipsis_flagged = sum(1 for c in claims if not c.get("quote_clean", True))
    relevance_flagged = sum(1 for c in claims if not c.get("relevance_ok", True))
    by = lambda b: sum(1 for c in claims if c.get("bucket", "claim") == b)
    return {
        "claims": claims,
        "failed_segments": failed,
        "segments": len(segs),
        "words": len(body.split()),
        "counts": {
            "items": len(claims),
            "claims": by("claim"),
            "builds": by("build"),
            "inspo": by("inspo"),
            "drops": by("drop"),
            "verbatim": len(claims) - unverified,
            "unverified": unverified,
            "ellipsis_flagged": ellipsis_flagged,
            "relevance_flagged": relevance_flagged,
            "failed": len(failed),
        },
    }


def _merge_existing_links(new_text, title):
    """Clobber-race fix: a sift-chunk re-run rewrites 02-chunk/<title>.md from
    scratch, which would silently erase the [[wikilinks]] that sift-frame-link
    wrote later. Read the existing note (default 02-chunk location) and carry
    over (a) the `links:` frontmatter line and (b) any trailing [[...]] suffix
    on a claim line, matched by the line's claim+quote text (number-agnostic).
    Fail-safe: any problem returns new_text unchanged."""
    try:
        import sift_stages as stages
        old_path = stages.CHUNK / f"{title}.md"
        if not old_path.exists():
            return new_text
        old = old_path.read_text(encoding="utf-8", errors="replace")
        # content-after-number -> trailing wikilink suffix, from the old note
        suffix_re = re.compile(r"^\d+\.\s(.*?)((?:\s*\[\[[^\]]+\]\])+)\s*$")
        carry = {}
        for line in old.split("\n"):
            m = suffix_re.match(line)
            if m:
                carry[norm(m.group(1))] = m.group(2)
        links_line = next((l for l in old.split("\n")
                           if l.startswith("links: [")), None)
        lines = new_text.split("\n")
        for i, line in enumerate(lines):
            m = re.match(r"^\d+\.\s(.*)$", line)
            if m and "[[" not in line:
                sfx = carry.get(norm(m.group(1)))
                if sfx:
                    lines[i] = line + sfx
        if links_line and lines and lines[0] == "---":
            end = next((j for j in range(1, len(lines)) if lines[j] == "---"), None)
            if end and not any(lines[j].startswith("links:") for j in range(1, end)):
                lines.insert(end, links_line)
        return "\n".join(lines)
    except Exception:
        return new_text


def render_note(title, source, claims, failed_segments):
    kept = [c for c in claims if c.get("keep", True)]
    claim_items = [c for c in kept if c.get("bucket", "claim") == "claim"]
    inspo_items = [c for c in kept if c.get("bucket") == "inspo"]
    build_items = [c for c in kept if c.get("bucket") == "build"]
    drop_items = [c for c in kept if c.get("bucket") == "drop"]
    unv = sum(1 for c in claim_items if not c["verified"])
    lines = [
        "---", f'title: "{title}"', "type: chunk", f"source: {source}",
        f"claims: {len(claim_items)}", f"quote_unverified: {unv}",
        f"builds_routed: {len(build_items)}", f"inspo: {len(inspo_items)}",
        f"dropped: {len(drop_items)}",
        f"segments_failed: {len(failed_segments)}", "---", "",
        f"# {title}", "",
        "## Claims (ship to the brain)", "",
    ]
    for n, c in enumerate(claim_items, 1):
        mark = "" if c["verified"] else "  ⚠ quote-unverified"
        lines.append(f'{n}. {c["claim"]}  —  "{c["quote"]}"  [{c["kind"]}/{c["salience"]}]{mark}')
    if inspo_items:
        lines += ["", "## Inspiration (kept local, not shipped to brain)", ""]
        for n, c in enumerate(inspo_items, 1):
            lines.append(f'{n}. {c["claim"]}  —  "{c["quote"]}"')
    if build_items:
        lines += ["", "## Builds (routed to the build queue)", ""]
        for n, c in enumerate(build_items, 1):
            lines.append(f'{n}. {c["claim"]}  —  bet ${c.get("bet", 0):g} / effort {c.get("effort", 2)}')
    if drop_items:
        lines += ["", f"## Dropped as noise: {len(drop_items)} (counted, not silently hidden)", ""]
    if failed_segments:
        lines += ["", "## Segments that failed (NOT silently dropped)", ""]
        for f in failed_segments:
            lines.append(f"- segment {f['seg']}: {f['why']}")
    return _merge_existing_links("\n".join(lines) + "\n", title)


# ── JSON sidecar: the contract the ship/fix agents consume ───────────
_MARKER_RE = re.compile(r"\*\*\[(\d{1,2}):(\d{2})\]\*\*")


def parse_source_meta(md_text):
    """Pull source_url + video_id from a DUMP header.

    Header line looks like: `**Source:** https://youtu.be/dxq7WtWxi44`.
    Returns (source_url, video_id); either may be "" if absent.
    """
    url = ""
    m = re.search(r"\*\*Source:\*\*\s*(\S+)", md_text)
    if m:
        url = m.group(1).strip()
    vid = ""
    mv = re.search(r"(?:youtu\.be/|[?&]v=)([A-Za-z0-9_-]{6,})", url)
    if mv:
        vid = mv.group(1)
    return url, vid


def _marker_index(md_text):
    """List of (char_offset, seconds) for every **[MM:SS]** marker, in order."""
    out = []
    for m in _MARKER_RE.finditer(md_text):
        secs = int(m.group(1)) * 60 + int(m.group(2))
        out.append((m.start(), secs))
    return out


def _seg_first_marker(seg, total_segs, markers):
    """The seconds of the FIRST marker inside segment `seg` (1-based).

    Segments split the body by word count, so map them proportionally onto the
    ordered marker list — a robust fallback when a quote can't be located.
    """
    if not markers:
        return 0
    if not seg or not total_segs:
        return markers[0][1]
    idx = int((seg - 1) / total_segs * len(markers))
    idx = max(0, min(idx, len(markers) - 1))
    return markers[idx][1]


def _timestamp_for_quote(quote, md_text, markers, seg=None, total_segs=None):
    """Seconds of the nearest PRECEDING marker before the quote's position.

    If the quote can't be located, fall back to the quote's SEGMENT's first
    marker; if still nothing, 0.
    """
    if not markers:
        return 0
    pos = md_text.find(quote) if quote else -1
    if pos == -1:
        return _seg_first_marker(seg, total_segs, markers)
    secs = markers[0][1]
    for off, s in markers:
        if off <= pos:
            secs = s
        else:
            break
    return secs


def write_claims_json(out_path, stem, md_text, claims, counts):
    """Write the <stem>.claims.json sidecar. md_text = the DUMP source,
    used to resolve per-claim timestamps and the source url/video id."""
    from datetime import date
    source_url, video_id = parse_source_meta(md_text)
    markers = _marker_index(md_text)
    kept = [c for c in claims if c.get("keep", True)]
    total_segs = max((c.get("seg") or 0 for c in kept), default=0)

    def cite(secs):
        if source_url and video_id:
            base = source_url.split("?")[0].split("&")[0]
            return f"{base}?t={secs}"
        return source_url

    rows = []
    for c in kept:
        quote = c.get("quote", "")
        secs = _timestamp_for_quote(quote, md_text, markers, c.get("seg"), total_segs)
        cid = hashlib.sha256((stem + "|" + quote).encode("utf-8")).hexdigest()[:16]
        rows.append({
            "id": cid,
            "claim": c.get("claim", ""), "quote": quote,
            "bucket": c.get("bucket", "claim"),
            "kind": c.get("kind", "fact"),
            "salience": c.get("salience", "medium"),
            "verified": bool(c.get("verified")),
            "quote_clean": bool(c.get("quote_clean", True)),
            "relevance_ok": bool(c.get("relevance_ok", True)),
            "seg": c.get("seg"),
            "timestamp_sec": secs,
            "cite_url": cite(secs),
        })

    doc = {
        "stem": stem,
        "source_url": source_url,
        "video_id": video_id,
        "generated": date.today().isoformat(),
        "counts": {
            "claims": len(rows),
            "verbatim": sum(1 for r in rows if r["verified"]),
            "ellipsis_flagged": sum(1 for r in rows if not r["quote_clean"]),
            "relevance_flagged": sum(1 for r in rows if not r["relevance_ok"]),
            "builds": sum(1 for r in rows if r["bucket"] == "build"),
            "inspo": sum(1 for r in rows if r["bucket"] == "inspo"),
            "dropped": sum(1 for r in rows if r["bucket"] == "drop"),
        },
        "claims": rows,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    return out_path, doc["counts"]


def _vault_dir(vault=None):
    return (vault or os.environ.get("OBSIDIAN_VAULT")
            or os.path.expanduser("~/Obsidian Vault"))


def update_build_queue(build_items, source, vault=None):
    """Route build items into the build tree (the money lane).

    Builds constellate into feature stalagmites: each build nests under its
    `feature`, features are ordered by total ROI, and builds float by ROI
    (bet / effort) inside each feature. Source of truth is a JSON sidecar;
    BUILD-QUEUE.md is the rendered tree. Dedupes by claim text.
    Returns (added, total, md_path).
    """
    proj = os.path.join(_vault_dir(vault), "01 Projects")
    os.makedirs(proj, exist_ok=True)
    json_path = os.path.join(proj, ".build-queue.json")
    md_path = os.path.join(proj, "BUILD-QUEUE.md")

    queue = []
    if os.path.exists(json_path):
        try:
            queue = json.loads(open(json_path, encoding="utf-8").read())
            if not isinstance(queue, list):
                queue = []
        except Exception:
            queue = []

    seen = {norm(e.get("claim", "")) for e in queue}
    added = 0
    for b in build_items:
        key = norm(b.get("claim", ""))
        if not key:
            continue
        if key in seen:
            # touchpoints = reinforcement signal, never noise (no-dedupe law)
            import datetime as _dt
            for e in queue:
                if norm(e.get("claim", "")) == key:
                    e["touchpoints"] = int(e.get("touchpoints", 1) or 1) + 1
                    e["last_reinforced"] = _dt.date.today().isoformat()
                    break
            continue
        bet = float(b.get("bet", 0) or 0)
        # noise gate (2026-06-11): session transcripts flooded the queue with
        # $0 chatter rows (~72/session). The claim already rides the belt as
        # knowledge; only money-backed session ideas earn a queue seat.
        if bet == 0 and ".private." in str(source):
            continue
        effort = max(1, int(b.get("effort", 2) or 2))
        queue.append({
            "claim": b["claim"], "quote": b.get("quote", ""),
            "feature": (b.get("feature") or "Unsorted").strip() or "Unsorted",
            "bet": bet, "effort": effort, "roi": round(bet / effort, 1),
            "status": "bet", "source": str(source),
        })
        seen.add(key)
        added += 1

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

    # constellate: group builds into feature stalagmites
    features = {}
    for e in queue:
        feat = e.get("feature", "Unsorted") or "Unsorted"
        features.setdefault(feat, []).append(e)
    # each feature's builds float by ROI; features ordered by total ROI
    ordered = sorted(
        features.items(),
        key=lambda kv: sum(b.get("roi", 0) for b in kv[1]),
        reverse=True,
    )

    eff_name = {1: "hrs", 2: "days", 3: "wks"}
    out = [
        "---", "title: Build Queue", "type: build-tree",
        "shape: features (stalagmites) -> builds, ordered by ROI = bet / effort",
        f"features: {len(ordered)}", f"builds: {len(queue)}", "---", "",
        "# Build Tree", "",
        "_The money lane. Builds nest under the feature they grow._",
        "_Within a feature and across features, highest ROI floats up._",
        "_Status per build: bet -> building -> shipped -> scored. Edit in place._", "",
    ]
    for feat, builds in ordered:
        builds = sorted(builds, key=lambda b: (b.get("roi", 0), b.get("bet", 0)), reverse=True)
        total_roi = sum(b.get("roi", 0) for b in builds)
        total_bet = sum(b.get("bet", 0) for b in builds)
        out.append(f"## {feat}  ·  ROI {total_roi:g} · ${total_bet:g} · {len(builds)} build(s)")
        for b in builds:
            eff = eff_name.get(b.get("effort", 2), b.get("effort", 2))
            tail = ""
            if b.get("status") == "scored":
                tail = f' · ✓ earned ${b.get("earned", 0):g} → claim shipped'
            out.append(
                f'- **[{b.get("status", "bet")}]** {b["claim"]}  '
                f'— ROI {b.get("roi", 0):g} (${b.get("bet", 0):g} / {eff}){tail}'
            )
        out.append("")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return added, len(queue), md_path


# ── The shared claim writer + the toroid close ──────────────────────────────
GBRAIN_BIN = os.path.expanduser("~/.bun/bin/gbrain")


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s or "untitled"


def render_claim_page(title, source, claim_lines, extra=None):
    """The ONE claim-page writer — used by sift-ship (chunk-time claims) AND
    score_build (shipped-build outcomes), so the claim schema can never drift.
    This single shared writer is what makes the toroid coherent."""
    from datetime import date
    fm = ["---", f'title: "{title}"', "type: distilled", f"source: {source}",
          f"claims: {len(claim_lines)}", f"shipped: {date.today().isoformat()}",
          "bucket: claim"]
    for k, v in (extra or {}).items():
        fm.append(f"{k}: {v}")
    fm.append("---")
    return "\n".join(fm + ["", f"# {title}", "", "## Claims", ""]
                     + list(claim_lines) + [""])


def put_to_gbrain(slug, page_markdown, timeout=120):
    """Write one page into gbrain (idempotent: put = create/update)."""
    import subprocess
    try:
        r = subprocess.run([GBRAIN_BIN, "put", slug], input=page_markdown,
                           text=True, capture_output=True, timeout=timeout)
    except FileNotFoundError:
        return False, f"gbrain not found at {GBRAIN_BIN}"
    return r.returncode == 0, (r.stderr or r.stdout)


def loopback(slug, title, source, claim_lines, extra=None):
    """THE autopoietic primitive — the single function that makes the rig feed
    itself. Metabolize any rig output of lasting value into a claim and return it
    to the brain. One currency (the claim), one feed (this function), three sources:

      • read-loop    — distilled claims from a source        (caller: sift-ship)
      • earning-loop — a shipped build's $ outcome           (caller: build-ship)
      • learning-loop— a kept/killed verdict about the rig    (self-evolving; future)

    Triangulation: SELF-EVOLVING IS AUTOPOIESIS POINTED INWARD. A verdict like
    "the extractor over-keeps trivia" is just a claim about the rig itself, fed
    back through this same door. So there is no separate self-evolving machine —
    only loopback, aimed at the world (autopoiesis) or at the rig (self-evolving).

    Returns (ok, msg)."""
    page = render_claim_page(title, source, claim_lines, extra)
    return put_to_gbrain(slug, page)


def score_build(match, earned, lesson=None, vault=None, dry=False):
    """Close the toroid: mark a queued build shipped+scored, then mint its
    OUTCOME as a claim and ship it to gbrain via the shared writer — so what
    paid off becomes searchable knowledge that sharpens the next bet.
    Returns a (status, *rest) tuple for the CLI to render."""
    earned = float(str(earned).replace(",", "").replace("$", "").strip() or 0)
    proj = os.path.join(_vault_dir(vault), "01 Projects")
    json_path = os.path.join(proj, ".build-queue.json")
    if not os.path.exists(json_path):
        return ("empty",)
    queue = json.loads(open(json_path, encoding="utf-8").read())
    hits = [e for e in queue if norm(match) in norm(e.get("claim", ""))]
    if not hits:
        return ("none", [e.get("claim", "") for e in queue])
    if len(hits) > 1:
        return ("ambiguous", [e["claim"] for e in hits])
    entry = hits[0]

    lesson_text = lesson or (
        f"Shipping '{entry['claim']}' earned ${earned:g} "
        f"(bet was ${entry.get('bet', 0):g}, effort {entry.get('effort', 2)})."
    )
    claim_line = f'1. {lesson_text}  —  "{entry["claim"]}"  [outcome/high]'
    title = f"Shipped — {entry['claim'][:60]}"
    src = entry.get("source", "build-queue")
    slug = "distilled/shipped-" + slugify(entry["claim"])
    extra = {"from_build": "true", "earned": f"{earned:g}",
             "bet": f"{entry.get('bet', 0):g}"}
    if dry:
        return ("dry", slug, render_claim_page(title, src, [claim_line], extra))

    from datetime import date
    entry["status"] = "scored"
    entry["earned"] = earned
    entry["scored"] = date.today().isoformat()
    if lesson:
        entry["lesson"] = lesson
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

    ok, msg = loopback(slug, title, src, [claim_line], extra)  # the one feed
    update_build_queue([], "", vault)  # re-render the tree from updated JSON
    if not ok:
        return ("ship-failed", slug, msg)
    return ("ok", slug, earned)
