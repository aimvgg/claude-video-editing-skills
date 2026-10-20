---
name: aimv-checks
description: "Gates an AI music video, hype edit or reel render before anyone watches or posts it: frame count, audio length and silent tails, loudness and true peak, browser playability, cuts that cross source shots, faces inside punch-ins, text legibility, and the rights and consent ledger. Use after every render, before 'is it ready', before sending a candidate, and before publishing a recipe."
---

# Check a render

Run the script first; it catches the mechanical failures. Then do the checks that need eyes.

Run it from the user's project folder. `${CLAUDE_SKILL_DIR}` is this skill's folder; outside Claude Code, use the path of the folder that holds this file.

## 1. Run the script

```bash
python3 -I "${CLAUDE_SKILL_DIR}/scripts/check.py" out/reel.mp4 --frames 902 --fps 30 --lufs -14 --cuts
```

Pass `--frames` and `--fps` from the plan. Without `--fps` the frame rate is printed, not checked.

It fails on:

- **Frame count** different from the plan. ffmpeg `-shortest` once cut 3 frames off a 902-frame reel. Drop `-shortest` and trim to the planned frame count yourself.
- **Audio shorter than video** by more than a frame, or **a silent tail**. A mix filter (`amix`, sidechain) ended early once and the last second went silent in the shipped file.
- **Loudness** off target (pass `--lufs`; -14 for most platforms, or the reference's own level when you remake an edit) and **true peak** above -1 dBTP, measured on the encoded file. AAC at 320k raised the true peak; 256k did not.
- **Browser playability.** H.264 above level 5.1 (for example a CRF 8 master at level 6.2) fails to decode in Chrome. Keep the master for a desktop player and make a share copy: H.264 High, level 4.2 for 1080p30, `yuv420p`, `+faststart`, about CRF 19 capped near 20 Mbps.

`--cuts` lists every frame scoring over 7 on `scdet`. Compare it with the cuts you planned. An extra cut means a shot runs into the next shot of its source.

## 2. Look

- **Contact sheets.** Tile the start, middle and end of every shot. Read them yourself; agents and people both miss things at playback speed.
- **Faces in punch-ins.** For every zoom, punch or crop, detect the face and fail it when more than 15% of the window has the face outside the crop. A deliberate exception (a punch onto a sweater) is written down.
- **Last frames of generated takes.** Step through them. Video models can add a flash or a morph at the end.
- **Text.** Check every tag and title at phone size. A second line under a tag is often unreadable; cut it. Interpolated frames smear text.
- **Generated residue.** Look for the old subject's face, jersey numbers or logos leaking through a swap.

## 3. Listen

Compare against the reference or the previous cut: momentary and short-term loudness, true peak, six bands per second, stereo width, and a spectrogram overlay. Listen to every seam and the last two seconds.

## 4. Rights and consent ledger

Before anything is shared, every clip in the edit has a row with its public URL, source seconds and what it is used for. Every real person who is swapped or impersonated has consent recorded. Commercial music, sports and film footage are flagged so the user decides where to post. The ledger is what the recipe cites.
