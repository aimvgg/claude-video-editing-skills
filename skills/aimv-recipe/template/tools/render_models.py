#!/usr/bin/env python3
"""Render guide/models.json into guide/06-models.md.

    python3 -I render_models.py <models.json> [<out.md>]    write the page (default: 06-models.md beside the JSON)
    python3 -I render_models.py --check <models.json> [<out.md>]    exit 1 when the page is stale
    python3 -I render_models.py --aimv <generators repo> <models.json>    also check every id against AIMV

The JSON is the record. Edit it, then rerun; never edit the page by hand. The same JSON
always renders the same bytes.
"""
import json
import os
import sys

LAYERS = ["agent", "research", "music", "image", "video", "upscale", "interpolation", "stems", "asr", "matting", "pose", "render", "encode"]
LAYER_NAMES = {
    "agent": "Agent",
    "research": "Research and study",
    "music": "Music generation",
    "image": "Image generation and edits",
    "video": "Video generation",
    "upscale": "Upscaling",
    "interpolation": "Retiming and interpolation",
    "stems": "Stem separation",
    "asr": "Speech to text",
    "matting": "Mattes and masks",
    "pose": "Faces and pose",
    "render": "Rendering",
    "encode": "Encoding and mixing",
}
OUTCOMES = ["won", "used", "lost", "refused", "blocked", "not-tried"]
BANNED = {"\u2014": "em dash", "\u2013": "en dash"}
AIMV_GENERATORS = "https://aimv.gg/generators"


class BadRecord(ValueError):
    pass


def need(cond, where, message):
    if not cond:
        raise BadRecord(f"{where}: {message}")


def check_text(value, where):
    if isinstance(value, str):
        for ch, name in BANNED.items():
            need(ch not in value, where, f"contains an {name}; rewrite the sentence")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            check_text(v, f"{where}[{i}]")
    elif isinstance(value, dict):
        for k, v in value.items():
            check_text(v, f"{where}.{k}")


def parse(doc):
    """Checks the record once, at the boundary. Everything after this trusts its shape."""
    need(isinstance(doc, dict), "models.json", "must be an object")
    for key in ("reel", "as_of", "intro", "rows"):
        need(key in doc, "models.json", f"missing {key}")
    for key in ("intro", "cost_notes", "notes"):
        need(isinstance(doc.get(key, []), list), key, "must be a list of paragraphs")
    if "aimv_first" in doc:
        first = doc["aimv_first"]
        need(isinstance(first, dict), "aimv_first", "must be an object with why (a list of paragraphs), and optional quotes and url")
        need(isinstance(first.get("why"), list), "aimv_first.why", "must be a list of paragraphs")
        need("url" not in first or first["url"] == AIMV_GENERATORS, "aimv_first.url", f"must be {AIMV_GENERATORS}")
    need(isinstance(doc["rows"], list) and doc["rows"], "rows", "must be a non-empty list")
    for i, row in enumerate(doc["rows"]):
        where = f"rows[{i}] ({row.get('name', '?')})"
        for key in ("name", "layer", "job", "provider", "endpoint", "runs", "cost_usd", "outcome", "evidence", "verdict", "sota"):
            need(key in row, where, f"missing {key}")
        need(row["layer"] in LAYERS, where, f"layer must be one of {', '.join(LAYERS)}")
        need(row["outcome"] in OUTCOMES, where, f"outcome must be one of {', '.join(OUTCOMES)}")
        has_id, has_proposed = row.get("aimv_id") is not None, row.get("proposed_id") is not None
        need(has_id != has_proposed, where, "set exactly one of aimv_id and proposed_id")
        if has_proposed:
            need(row.get("proposed_as") in ("tool", "model"), where, "proposed_as must be tool or model")
        need(row["runs"] is None or (isinstance(row["runs"], int) and row["runs"] >= 0), where, "runs must be a count or null")
        need(row["cost_usd"] is None or isinstance(row["cost_usd"], (int, float)), where, "cost_usd must be a number or null")
        need(set(row["evidence"]) <= {"log", "error", "quote"} and row["evidence"], where, "evidence holds log, error and quote")
        need(isinstance(row["evidence"], dict), where, "evidence must be an object")
        sota = row["sota"]
        need(isinstance(sota, dict) and isinstance(sota.get("is_sota"), bool) and sota.get("basis") and sota.get("as_of"), where, "sota needs is_sota, basis and as_of")
    check_text(doc, "models.json")
    return doc


def aimv_ids(root):
    """Model ids from taxonomy/models.yml and tool ids (file stems and slugs) from entries/tools."""
    ids = set()
    with open(os.path.join(root, "taxonomy", "models.yml"), encoding="utf-8") as f:
        ids |= {line.split(":", 1)[1].strip() for line in f if line.startswith("- id:")}
    tools = os.path.join(root, "entries", "tools")
    for name in os.listdir(tools):
        if name.endswith(".yml"):
            ids.add(name[:-4])
            with open(os.path.join(tools, name), encoding="utf-8") as f:
                ids |= {line.split(":", 1)[1].strip() for line in f if line.startswith("slug:")}
    return ids


def check_ids(doc, known):
    for row in doc["rows"]:
        where = f"rows ({row['name']})"
        if row.get("aimv_id"):
            need(row["aimv_id"] in known, where, f"aimv_id {row['aimv_id']} is not in AIMV; use proposed_id")
        else:
            need(row["proposed_id"] not in known, where, f"proposed_id {row['proposed_id']} already exists in AIMV; use aimv_id")


def money(v):
    return "not logged" if v is None else f"${v:,.2f}"


def runs(v):
    return "n/a" if v is None else str(v)


def quoted(prefix, text, mark):
    end = "" if text.endswith((".", "?", "!")) else "."
    return f"{prefix} {mark}{text}{mark}{end}"


def cell(text):
    return text.replace("|", "\\|")


def ordered(rows):
    return sorted(rows, key=lambda r: (LAYERS.index(r["layer"]), OUTCOMES.index(r["outcome"])))


def evidence_line(row):
    ev, parts = row["evidence"], []
    if ev.get("log"):
        parts.append(ev["log"])
    if ev.get("error"):
        parts.append(quoted("The error read", ev["error"], "`"))
    if ev.get("quote"):
        parts.append(quoted("Zeal said", ev["quote"], '"'))
    return " ".join(p if p.endswith((".", "?", "!", '"', "`")) else p + "." for p in parts)


def render(doc):
    rows = ordered(doc["rows"])
    out = [f"# {doc.get('title', '6. Model tests')}", ""]
    out += [p + "\n" for p in doc["intro"]]

    first = doc.get("aimv_first") or {}
    pointer = (
        f"Before you pick a model for any type of generation, open [aimv.gg/generators]({first['url']}). "
        "It lists the current SOTA tools for each type, with the music videos made with them. "
        "Start from that list, then test on one shot."
    ) if first.get("url") else "Check the current state-of-the-art tools list before picking models for any type of generation. Start from that list, then test on one shot."
    if "aimv_first" in doc:
        out += ["## How the models were picked", ""]
        out += [p + "\n" for p in first["why"]]
        for q in first.get("quotes", []):
            out += [f"> {q['text']}", ">", f"> Zeal, {q['when']}", ""]
        out += [pointer, ""]

    out += ["## Every model and tool that ran or was weighed", ""]
    out.append("A row is marked SOTA only when a dated public ranking or a named source backs it. Unmarked means not claimed, not that it is worse.")
    out.append("")
    for layer in LAYERS:
        group = [r for r in rows if r["layer"] == layer]
        if not group:
            continue
        out += [f"### {LAYER_NAMES[layer]}", ""]
        out += ["| Model or tool | Job | Provider and endpoint | Runs | Cost | Outcome | SOTA |", "| --- | --- | --- | --- | --- | --- | --- |"]
        for r in group:
            out.append(
                f"| {cell(r['name'])} | {cell(r['job'])} | {cell(r['provider'])}, {cell(r['endpoint'])} | {runs(r['runs'])} | "
                f"{'none' if r['outcome'] == 'not-tried' else money(r['cost_usd'])} | {r['outcome']} | {'yes' if r['sota']['is_sota'] else 'no'} |"
            )
        out.append("")
        for r in group:
            sota = f" SOTA as of {r['sota']['as_of']}. {r['sota']['basis']}" if r["sota"]["is_sota"] else ""
            out.append(f"- **{r['name']}.** {evidence_line(r)}{sota} Verdict: {r['verdict']}")
        out.append("")

    notes = doc.get("cost_notes", [])
    priced = [r["cost_usd"] for r in rows if r["cost_usd"]]
    if notes or priced:
        out += ["## Cost", ""]
        if notes:
            out += [p + "\n" for p in notes]
        else:
            out += [f"The rows with a logged cost add up to {money(sum(priced))}.", ""]

    out += [p + "\n" for p in doc.get("notes", [])]
    out.append("This page is generated from `models.json` by `render_models.py`, which ships in the `aimv-recipe` skill of [claude-video-editing-skills](https://github.com/zealous1/claude-video-editing-skills) (`skills/aimv-recipe/template/tools/`). Edit the JSON and rerun it. The JSON also holds each row's AIMV id.")
    return "\n".join(out).rstrip("\n") + "\n"


def main(argv):
    if "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    check = "--check" in argv
    argv = [a for a in argv if a != "--check"]
    aimv_root = None
    if "--aimv" in argv:
        i = argv.index("--aimv")
        if i + 1 >= len(argv):
            print(__doc__.strip(), file=sys.stderr)
            return 2
        aimv_root, argv = argv[i + 1], argv[:i] + argv[i + 2:]
    paths = argv
    if not 1 <= len(paths) <= 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    src = paths[0]
    dst = paths[1] if len(paths) == 2 else os.path.join(os.path.dirname(os.path.abspath(src)), "06-models.md")
    try:
        with open(src, encoding="utf-8") as f:
            doc = parse(json.load(f))
        if aimv_root:
            check_ids(doc, aimv_ids(aimv_root))
        page = render(doc)
    except (BadRecord, json.JSONDecodeError) as e:
        print(f"{src}: {e}", file=sys.stderr)
        return 1
    if check:
        current = open(dst, encoding="utf-8").read() if os.path.exists(dst) else None
        if current != page:
            print(f"{dst} is stale. Rerun render_models.py.", file=sys.stderr)
            return 1
        return 0
    with open(dst, "w", encoding="utf-8") as f:
        f.write(page)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
