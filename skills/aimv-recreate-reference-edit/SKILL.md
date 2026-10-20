---
name: aimv-recreate-reference-edit
description: "Rebuilds an existing edit beat for beat around a new subject: same cuts, timing, camera moves and look, with the person, text and story swapped. Use when someone links a reel, TikTok or YouTube edit and says 'make this but about X', 'recreate this edit', 'remake this with my face' or 'do this style for our launch'. Measures the reference first, keeps its audio clock, and generates only what has to change."
---

# Recreate a reference edit

The reference is the spec. You measure it, keep everything that does not have to change, and replace slots one at a time against the reference's own clock. The worked example is the Dylan Patel reel, a remake of a 30 s basketball edit ([zealous1/dylan-patel-hype-edit](https://github.com/zealous1/dylan-patel-hype-edit), `RECIPE.md` and `guide/`).

Run every command from the user's project folder. `${CLAUDE_SKILL_DIR}` is this skill's folder. Downloads, takes and renders land in the project, never in the skill folder.

## Before you start

- **Consent.** Swapping a real person into footage needs that person's consent, recorded in the recipe. Never swap in someone who has not agreed. Keep the original subject's likeness out of anything you publish.
- **Rights.** Say once that a remake of broadcast, film or music-video footage carries copyright risk on every platform. Some video models refuse it on output (see Traps).
- **Models.** Before choosing a model, check the current leaders on https://aimv.gg/generators. The models named here won in October 2026; newer ones may beat them.
- **Access.** Generation runs through a hosted API such as OpenRouter (`OPENROUTER_API_KEY`). A privacy setting on the provider account can block some video and image models. Read the provider's error, and let the user decide any account change.
- **Budget.** Generation bills the user's provider account. Before the first paid call, list each slot you will generate with its model and price, give the total, and wait for a yes. Keep a running total in `costs.json` in the project. Stop and ask again before you pass the agreed amount. For scale, the Dylan Patel reel spent $21.54 on image and video generation and $11.94 on GPU time.

## 1. Measure the reference

Pull it whole with `find-youtube-clips-and-quotes`. Its `pull.mjs <url> --probe` shows the length first, and `pull.mjs <url> --name ref` downloads a short reel whole. Then build rulers before you look:

- `ffmpeg -vf "scdet=threshold=7,signalstats"` over every frame gives hard cuts, flashes and grayscale stretches in seconds. Write them to `analysis/reference.json`.
- Contact sheets: a 2 fps overview, then 10 fps only around flagged moments. Use a `trim` filter for a window; `-ss` as an output option groups frames from t=0.
- Per-frame luma, Laplacian sharpness, phase-correlation shift and frame diff give each move's shape and the film flicker you will borrow later.
- Song: identify it, get beats with librosa, and mark dropouts and hits. The reference's audio is the clock for everything after.

## 2. Write the slot sheet

One row per reference shot: start and end frame, what happens, and a verdict.

| Verdict | Use when | How |
| --- | --- | --- |
| keep | Nothing in it names or shows the old subject | Copy the span |
| overlay | Only text or graphics change (scorebug, banner, lower third) | Draw it in software over the kept span. Do not ask a model for text |
| swap | The subject's body or face is on screen | Video-to-video with references (step 4) |
| render | A designed insert (newspaper, card, end logo) | Code-render it (step 5) |
| replace | The beat needs new footage (podcast clips, product) | `find-youtube-clips-and-quotes`, then `aimv-repurpose` |

Minimize generated pixels. Each generated span is a place for artifacts to appear.

## 3. Audio

Keep the original mix wherever the old subject is not named. To remove a voice, separate with Demucs `htdemucs_ft` and use the vocal stem as a guide for where the words are; do not mute the stem across a span. The four stems do not sum back to the original, and muting a stem removes sung notes, reverb and width with the words. Replace only the words. Record new lines dry, split takes at pauses of 0.8 s or more, place each line by cross-correlation against the line it replaces, EQ toward the original voice, and match loudness section by section to the reference.

## 4. Swap the subject

1. **Character sheet first.** Six views on one image (front, side profile with room in front of the nose, back of head, three-quarter, full body front and back), then outfit, numbers and face in that order. GPT Image 2.5 Sunburst through OpenRouter `POST /api/v1/images` with `input_references` worked; about $0.06 an image. Sizes must divide by 16. For 16:9 use 1792x1008. If the safety check refuses a frame with the old subject, grey out their head and retry.
2. **Start and end frames** per slot from the sheet and the reference frame.
3. **Generate.** Wan 3.0 on `POST /api/v1/videos` with `input_references` = the source span as an HTTPS `video_url`, the sheet, and the start and end frames as images. Leave `frame_images` empty: pinning frames makes Wan ignore the clip. Slow the span 2x to a whole number of seconds, generate, then speed back up, because Wan fills its duration and invents motion past the end of the source. About $0.50 to $0.90 a shot.
4. **When the clip leaks.** If the result copies source text or numbers, run frames-only image-to-video instead (pinned start and end, sheet, short prompt).
5. **Fix residue with short spans.** A second V2V over half a second costs about $0.50 and is cheaper than regenerating the shot.
6. **Look match.** Match each generated shot to the reference frame by frame: colour curves, a spatial gain grid and blur type. Generated shots are too clean next to broadcast footage.

## 5. Code-rendered inserts

Build designed beats as an HTML canvas page and render it frame by frame in headless Chrome over the DevTools protocol, starting on the previous shot's exact last frame. Render text at 2x to 4x and downscale. Capture big frames in horizontal strips; one multi-megabyte screenshot can stall the socket. Credit every fact on the insert to a source you checked.

## 6. Review and assemble

- A cut player page: one `takes.json` per slot, the reference audio as the clock, picks saved per viewer. The person picks takes there.
- Assemble with one deterministic render script that takes scene overrides and a tag, so a candidate never overwrites the current cut. Swap audio with a `-c:v copy` remux.
- Show finishing choices as full exports side by side, not browser previews: frame rate, film look, upscale, opener. In the example, 30 fps beat 60 because RIFE in-betweens smeared text, cuts and whips; Worn film borrowed the reference's measured flicker; SeedVR2 7B at 1440 then Lanczos to 1080 beat a 1080 pass, which pads to 1088 and leaves a seam.

## 7. Gate and publish

Run `aimv-checks` on every candidate before anyone watches it. Write the recipe with `aimv-recipe`.

## Traps

- Seedance 2.5 refused every attempt on broadcast sports footage, with the clip removed and scorebugs blurred. It checks the output.
- Hailuo 3 rejects `frame_images` and references together; frames-only runs invented motion and drifted jersey numbers.
- Video references must be HTTPS URLs. Use signed URLs that expire within a day (R2 or S3 presigned), never a public bucket, and delete the objects when the reel ships. The references carry broadcast footage and a real person's face.
- Wan can hallucinate a flash frame at the end of a take. Step through the last frames.
- Random effects must match across reruns. Fix the generator's starting value, and keep the order of calls that draw from it.
