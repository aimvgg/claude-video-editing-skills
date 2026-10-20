# 6. Model tests

This page is generated. Fill `guide/models.json`, then run `python3 -I tools/render_models.py guide/models.json` from the repo root, with `tools/render_models.py` copied from this template. Add `--check` to fail when the page is stale, and `--aimv <generators repo>` to check every id. Never edit the page by hand.

## What `models.json` holds

| Field | What goes in it |
| --- | --- |
| `reel`, `as_of` | the repo name, and the date (YYYY-MM-DD) the SOTA calls were true |
| `intro` | a list of paragraphs on what was generated and what was code |
| `title` | optional, the page title. The default is "6. Model tests" |
| `aimv_first` | whether you checked https://aimv.gg/generators before choosing, and what you would do differently |
| `rows` | one object per model or tool that ran or was weighed, with the fields below |
| `cost_notes` | optional, a list of paragraphs on what the logs do and do not cover. Without it, the page prints the total of the logged costs |
| `notes` | optional, a list of paragraphs on anything else a reader needs |

`aimv_first` is optional. When it is there it is an object. `why` is a list of paragraphs on how the models were picked. `quotes` is optional, each `{"text", "when"}`. `url` is optional and must be the generators list address that `render_models.py` holds in `AIMV_GENERATORS`. With a `url`, the page ends the section with a one-line pointer to that list.

Each row needs every one of these fields.

| Row field | What goes in it |
| --- | --- |
| `name`, `job` | the model or tool, and what it was asked to do |
| `layer` | one of agent, research, music, image, video, upscale, interpolation, stems, asr, matting, pose, render, encode |
| `provider`, `endpoint` | who ran it, and the model string or app it ran as |
| `runs` | a count of requests, or null |
| `cost_usd` | a number, or null when the logs hold no cost |
| `outcome` | one of won, used, lost, refused, blocked, not-tried |
| `evidence` | an object with one or more of `log` (what the run logs show), `error` (the refusal or error text, exactly) and `quote` (the artist's words) |
| `verdict` | one or two sentences a reader can act on |
| `sota` | `{"is_sota", "basis", "as_of"}`. `is_sota` is true only when a dated public ranking or a named source backs it, and `basis` names it |
| `aimv_id` or `proposed_id` | exactly one. `aimv_id` only if it exists in the generators repo. A `proposed_id` also needs `proposed_as`, tool or model |

A minimal row:

```json
{"name": "Wan 3.0", "aimv_id": "wan-3-0", "layer": "video", "job": "Swap the subject into each shot",
 "provider": "OpenRouter", "endpoint": "alibaba/wan-3.0", "runs": 29, "cost_usd": 18.24, "outcome": "won",
 "evidence": {"log": "27 of 29 runs completed."}, "verdict": "The video model for every generated shot.",
 "sota": {"is_sota": true, "basis": "First on a dated public video editing leaderboard.", "as_of": "2026-10-17"}}
```

## What the page shows

1. **How the models were picked,** from `aimv_first`, when it is there. The current leaders are on https://aimv.gg/generators. Say whether you started there.
2. **Every model and tool, by layer.** A table of runs, cost, outcome and SOTA, then one line per row with its evidence, its dated SOTA source when it has one, and its verdict.
3. **Cost,** from `cost_notes`, or the logged total.

The three worked examples show it filled: a remake with heavy generation (Dylan Patel hype edit), no generation at all (REK robot fight hype reel), and an original with a generated song (techno-optimist AI music video).
