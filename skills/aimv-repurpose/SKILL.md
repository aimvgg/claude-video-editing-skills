---
name: aimv-repurpose
description: "Transforms existing footage shot by shot so it fits a new edit: podcast and interview clips made to pop on a beat, a subject swapped by video-to-video, a voice removed from a mix, an object or logo cleaned out, a shot upscaled, its frame rate or film look changed. Use for 'make these podcast clips hit', 'swap him for me in this shot', 'remove the announcer', 'clean the sign off the wall', 'upscale this', or 'make it look like film'."
---

# Repurpose footage

Each technique below takes one shot or one mix in and gives one out, and each has a measured win from a shipped reel. Pick the ones the edit needs. `aimv-recreate-reference-edit` calls into this skill; it also works alone. Before choosing a model for a transform, check the current leaders on https://aimv.gg/generators.

Run every command from the user's project folder, and write every output there. Upscales on a rented GPU, clean plates from an image model and subject swaps are paid runs. Name the model, the price per shot and the shot count, and get a yes before each batch.

## Podcast clips that hit on a beat

From the Dylan Patel reel's 7-second podcast section, which cuts ten beats from ten different videos in a row.

- **Source honestly.** Find every clip with `find-youtube-clips-and-quotes`, one episode per beat. Any on-screen search tag must be the query that actually found the clip. Write tags lowercase, speaker first, for example `arcmira.search(speaker: "dylan patel", query: "nvidia")` under the channel name.
- **Face-matched zoom-through.** Detect the face in every clip (OpenCV DNN or MediaPipe Face Detection; OpenCV 5 dropped `CascadeClassifier`, so pin `opencv-python-headless<5` if you use it). Scale and place each clip so the face lands at the same size and spot as the last, and keep the zoom moving through the cut. Face wander across cuts went from 6 to 9% of the frame to 2%.
- **Pacing.** Never put three moves in under half a second. Retime a beat later instead. Shake vertically only.
- **Make the person pop.** Brighten the face against the room. Measure the face-to-room brightness ratio in the reference (2.18 in the example; raw podcast footage is about 1.0) and aim near it. A halation wrap off a MediaPipe person-segmentation matte, keeping the person whose region holds the target face, beat print-room and burn treatments.
- **Text over flashes.** Burn hits whiten tags. Put a soft shadow under the letters that scales with the burn.

## Swap a subject

Video-to-video with references, as in `aimv-recreate-reference-edit` step 4. Get the person's consent first and record it in the recipe.

## Remove or replace a voice in a mix

Separate with Demucs `htdemucs_ft`. Keep the original mix everywhere except the words, and take only the words out. Stems do not sum to the original, so a muted stem also loses notes, reverb and stereo width. Re-transcribe the result (Deepgram Nova-3 or Whisper) to prove the words are gone. Whisper invents text over silence, so ignore its lines in quiet stretches.

## Clean an object, sign or logo out of a moving shot

Make one clean plate of the frame with an image model, align it to every frame with OpenCV ECC (affine), and matte it in around the subject. This is cheaper and steadier than generating the shot again.

## Upscale

SeedVR2 7B on a rented GPU (an H100 on Modal took 200 to 280 s per test shot). Render at 1440 and downscale to 1080 with Lanczos. At 1080 the model pads to 1088 and leaves a seam on the bottom row. A local Apple-silicon run ran out of memory at the 1080p encode. Measure the win with Laplacian sharpness per shot; in the example the gains were about 2x to 2.6x.

## Frame rate

RIFE in-betweens halve detail on whips, morph across cuts (doubled tags and hands) and melt flashes. If you need 60 fps, render code graphics natively at 60 and interpolate only pairs inside a shot. Compare full exports of both rates before deciding. The example stayed at 30.

## Film look

Borrow the reference's measured per-frame flicker rather than inventing one. Apply an S-curve before lifting blacks; a lift alone washes the picture out. Scratches live 3 to 14 frames, dust and hairs one frame. Leave the last 3 frames clean. Presets that shipped: match, classic (grain 7, weave 1, halation 0.35, vignette 0.35, black floor 20) and worn (adds about 5% projector flicker, floor 26, grain 12, weave 2, halation 0.5, vignette 0.5).

## Look match a generated shot

Match colour curves, a spatial gain grid and blur type to the neighbouring source frames. Generated shots read too clean beside real footage.

## After each transform

Run `aimv-checks` on the shot. Record the tool, model, settings and cost per shot for `aimv-recipe`.
