# Finding what someone said with Arcmira

Arcmira indexes the transcripts of YouTube shows and podcasts and labels who is speaking. Use it to find the exact moment a person said something. Then cut that moment with `scripts/pull.mjs` from this skill's folder (the folder that holds `SKILL.md`). Run it from the project folder, so the clips land there.

Two ways in. Both take the same arguments.

- **MCP.** When the Arcmira MCP server is connected, call `arcmira_describe` once, then run programs with `arcmira_execute_read`. Method names are below.
- **REST.** `https://api.arcmira.com/v1`, with the header `Authorization: Bearer $ARCMIRA_API_KEY`. The full reference is https://api.arcmira.com/v1/openapi.json.

## The four steps

### 1. Resolve the name to an id

Filters take ids, never names.

```bash
curl -s -H "Authorization: Bearer $ARCMIRA_API_KEY" \
  "https://api.arcmira.com/v1/entities/resolve?q=Dylan%20Patel&type=person&context=SemiAnalysis"
```

MCP: `arcmira.resolve("Dylan Patel", { type: "person", context: "SemiAnalysis" })`.

The answer has one of three shapes:

- `best`: use it.
- `suggested`: use it, and tell the user you assumed it.
- `ask`: show the options and let the user pick.

Only pass `context` when it's the user's own words about the name.

### 2. Search for passages where they say the words

```bash
curl -s -H "Authorization: Bearer $ARCMIRA_API_KEY" \
  "https://api.arcmira.com/v1/search?q=TSMC&by=ent_140776&after=2025-10-01&limit=5"
```

MCP: `arcmira.search({ query: "TSMC", speakerIds: ["ent_140776"], after, limit: 5 })`.

- Up to 5 passages a search use no credits. Add topics rather than raising `limit`.
- Each chunk carries `video_id`, `video_title`, `start_seconds` and `text`. Every line in `text` starts with `Name: `, so keep only the target speaker's lines.
- Search with one topic or phrase per call. For hype lines, try short concrete words the person would say with energy, such as a company, a number or a claim.
- Speaker labels don't cover every video. When a `by` search comes back empty, read `note`. Then try `about` with the same id for what others said about them.

### 3. Read the transcript around the hit

```bash
curl -s -H "Authorization: Bearer $ARCMIRA_API_KEY" \
  "https://api.arcmira.com/v1/transcripts/mDG_Hx3BSUE?start=8575&end=8605"
```

MCP: `arcmira.transcript("mDG_Hx3BSUE", { start: 8575, end: 8605 })`.

Check `state` first. The lines are `{ start, end, text }`. A caption line can start before the phrase you want, so set the span from the line around the phrase, then fix the exact cut with `speech_gaps` in step 4.

### 4. Pull and trim

```bash
node "<skill folder>/scripts/pull.mjs" "https://www.youtube.com/watch?v=mDG_Hx3BSUE" --from 8580 --to 8586.4 --name dylan-huawei
```

- Put the in and out points inside the reported `speech_gaps`. Gap times are clip seconds, so source second = `source_seconds[0]` + gap.
- Then open `sheet.jpg` and confirm the person is on screen.

## Credits

Every read uses credits from the user's Arcmira plan:

- A search uses 4 credits for each passage past the first 5.
- A captions transcript read uses 4 credits per started 15 minutes of the `start` to `end` window. Pass a window, never the whole video.
- Premium transcripts (`quality=premium`) are diarized and spelled better, and use 300 credits per started 15 minutes of the whole video. Use them only when the user asks.
- On the Free plan the newest 30 days are not served, and a window that starts inside them is refused with `freshness_requires_paid`.
- The API reports a blocked read with a code such as `quota_exceeded` and an `unlock` link. Pass that on to the user and stop.

## Worked example (2026-10-16)

The goal was hype lines from Dylan Patel for a SemiAnalysis hype video.

1. Resolving "Dylan Patel" with context SemiAnalysis gave `best` = `ent_140776` (188 mentions, 38 of them appearances).
2. A `by` search for "nvidia" since 2024 found him on Dwarkesh Patel's "The Single Biggest Bottleneck to Scaling AI Compute" at 8581 s: "Huawei has cracked software engineers. Huawei has cracked networking technologies."
3. The transcript window 8575 to 8605 showed the phrase starts inside the line at 8575.12.
4. `pull.mjs --from 8580 --to 8586.4` returned a 1080p clip in about 15 s. The sheet showed Dylan on camera, gesturing, the whole time.
