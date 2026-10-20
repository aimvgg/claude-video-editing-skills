# 1. Research: direction and findings

Fill this from your clip log (`clips/clips.json`, where each row's `found` holds the call that found the clip and its exact input) and from `research-calls.json` if you keep one. Every clip on screen must trace back to one row here.

## What we were going for

One paragraph. The feeling, the person or event, and what the found clips had to prove.

## The searches

One row per call that produced a shot: an Arcmira search, a YouTube search, a web search, or a URL someone handed you.

| Slot | Program | Inputs | Why this filter | What came back | Used |
| --- | --- | --- | --- | --- | --- |

## How a hit became a shot (clips of someone speaking)

1. Resolve the person to an entity id once, with context (`arcmira.resolve`).
2. Search one idea per call, filtered to the speaker id. Add a channel id when a show has no speaker labels.
3. Read 30 seconds either side with `arcmira.transcript` before choosing.
4. Download with yt-dlp from the YouTube URL built from `video_id`, not `watch_url`.
5. Cut in a silence that FFmpeg `silencedetect` reports. Transcript times are not cut points.
6. Record the call in the edit list, so the on-screen tag is literally the search.

For footage found another way, say how in one line per source.

## For agents

- The rules that made research reliable for this reel, written as instructions.

## Not found by search

List any shot that came from elsewhere and say so.
