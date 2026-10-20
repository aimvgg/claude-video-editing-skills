# Claude video editing skills

Six Claude Code skills for hype edits and AI music videos. They find the second someone said a line and cut it between words, remake a reference edit shot for shot, cut footage on the beat, and check the render before you post it.

<p align="center"><img src="https://github.com/zealous1/dylan-patel-hype-edit/raw/master/assets/newspaper-to-podcast.gif" width="520" alt="The podcast section of the Dylan Patel reel, where each clip shows the search that found it"></p>

**[Watch the Dylan Patel reel](VIDEO_POST_URL)** · [Install](#install) · [The skills](#the-skills) · [How the videos were made](#the-family)

- Each skill was written from a video that shipped, and each video has its prompts, its code and an eight-section guide.
- You do not need to know FFmpeg or WebGL. The agent writes and runs the code.
- The skills ask before a long download or any paid model run, and keep a log of every clip by source URL and second.

By [Zeal](https://x.com/zealcaiden).

## Install

In Claude Code:

```
/plugin marketplace add zealous1/claude-video-editing-skills
/plugin install video-editing-skills@claude-video-editing-skills
/mcp
```

The plugin also registers the Arcmira MCP server, and the last line signs you in to it. [Arcmira](https://arcmira.com) is a search engine for what people say in podcasts and videos. It knows who is speaking, so a search can ask for one person's own words, and it returns the second each line starts. In `/mcp`, pick arcmira and sign in. A Free account works.

Zeal builds Arcmira. Only `find-youtube-clips-and-quotes` uses it, and it falls back to plain URLs without it. If a video or channel you need is not in the index, the skill offers to ask Arcmira to add it through `arcmira_feedback`.

If you added Arcmira yourself before, Claude Code keeps your server and hides the plugin's copy. Without the plugin, connect it from your shell:

```
claude mcp add --scope user --transport http arcmira https://mcp.arcmira.com/mcp
```

Then run `/mcp` in Claude Code and sign in. Other hosts: https://arcmira.com/docs/mcp-server

On your machine you need `ffmpeg`, Node 20 or newer, `uv` and Python 3, and Google Chrome to render. On a Mac, run `brew install ffmpeg node uv`.

Other agents that read `SKILL.md` files can load the folders under `skills/` directly.

## The skills

`aimv` stands for AI music video. Most edits start with `find-youtube-clips-and-quotes`.

| Skill | Use it for | Say something like |
| --- | --- | --- |
| [`find-youtube-clips-and-quotes`](skills/find-youtube-clips-and-quotes/SKILL.md) | Find the moment someone said something, by speaker, with the Arcmira MCP, then pull the exact span with yt-dlp | "Find three clips of Jensen Huang saying 'accelerated computing' since 2024" |
| [`aimv-recreate-reference-edit`](skills/aimv-recreate-reference-edit/SKILL.md) | A shot-for-shot remake of a reference edit with a new subject, against the reference's own clock | "Remake this TikTok edit with our founder in it" |
| [`aimv-repurpose`](skills/aimv-repurpose/SKILL.md) | One-shot transforms: podcast clips that pop, subject swaps, voice removal, sign cleanup, upscale, frame rate, film look | "Make these podcast clips hit on the beat" |
| [`aimv-checks`](skills/aimv-checks/SKILL.md) | Gates every render before anyone watches it: frames, audio to the last frame, loudness, true peak, browser playback | "Is the render ready to post?" |
| [`aimv-recipe`](skills/aimv-recipe/SKILL.md) | Look up how other AI music videos were made on AIMV, and write your own recipe and entry | "Write up how we made it" |

Before choosing any model, check the current leaders on [aimv.gg/generators](https://aimv.gg/generators).

## Your first prompt

Paste this and fill in the brackets:

```
Make me a 30 second 9:16 hype edit of [person] from their podcast clips.
Find 8 moments since 2024 where they say something bold about [topic], and
show me the quotes and links before you download anything. Cut my picks to
[song file], run the checks, and stop before anything costs money.
```

## What it costs

Arcmira searches use credits from your plan. A search that returns up to 5 passages uses none, and the clip finder keeps searches at 5. Each transcript window it reads uses 4 credits, so one search run uses at most 20. For scale, the Dylan Patel reel used an estimated 1,000 credits over 51 searches, most of it in wide searches of 20 passages.

Cutting, rendering and checks run on your machine. A remake that swaps a person in with a video model bills your own provider account, about $0.50 to $0.90 a shot. The Dylan Patel reel spent $21.54 on image and video generation and $11.94 on GPU time. The skills name the price and wait for your yes before any paid run.

## Rights and consent

Reposting sports, film, music or creator footage carries copyright risk. Swapping a real person into footage needs their consent, and the skills record it. The clip log keeps every source by URL and second, so you can credit it.

## Why we remix

Zeal is a digital art enthusiast, and the videos in this family are remixes. Remixing and sampling are a lot of the fun of making music and DJing. You flip a sample, cut an edit to someone else's track, or recut a famous clip around a new face. Most of that culture runs on a tacit understanding that it's all good. Sometimes labels get weird, and in some cases a rights holder can take a video down. We think people should be free to make art out of the culture around them, as long as nobody is printing money off someone else's work. None of these videos is sold, and the sources are credited by link, not shipped.

## The family

Each video gets the same eight-section guide, and the work turns into Claude Code skills. Two more videos are coming: a robot fight night reel and a techno-optimist music video.

| Repo | What it is |
| --- | --- |
| [dylan-patel-hype-edit](https://github.com/zealous1/dylan-patel-hype-edit) | A 30-second remake of a viral LeBron edit, with Dylan Patel of SemiAnalysis swapped in |
| [claude-video-editing-skills](https://github.com/zealous1/claude-video-editing-skills) | The Claude Code skills these videos became |

## Licence

Apache-2.0.
