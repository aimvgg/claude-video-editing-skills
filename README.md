# Claude video editing skills

Six Claude video editing skills for hype videos and AI music videos. They find the second someone said a line and cut it between words, restyle a reference video shot for shot, swap a person into a clip with video-to-video, clean up and finish AI shots, and check the render before you post it.

They are plain Agent Skills folders, so they install into Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, OpenCode and about 70 more agents.

<p align="center"><img src="https://github.com/zealous1/dylan-patel-hype-video/raw/master/assets/newspaper-to-podcast.gif" width="520" alt="The podcast section of the Dylan Patel hype video, where each clip shows the search that found it"></p>

**[Watch the Dylan Patel hype video](https://x.com/zealcaiden/status/2112239444040499475)** · [Install](#install) · [The skills](#the-skills) · [How the videos were made](#the-family)

- Each skill was written from a video that shipped, and each video has its prompts, its code and an eight-section guide.
- You do not need to know FFmpeg or WebGL. The agent writes and runs the code.
- The skills ask before a long download or any paid model run, and keep a log of every clip by source URL and second.

By [Zeal](https://x.com/zealcaiden).

## Install

**Any agent.** One command installs the skills into the agents on your machine:

```
npx skills add aimvgg/claude-video-editing-skills
```

Add `--skill restyle-reference-video` to install one skill, or `--list` to see them first.

**Claude Code.** Add the marketplace and install the `aimv` plugin:

```
claude plugin marketplace add aimvgg/claude-video-editing-skills
claude plugin install aimv@aimv
```

The skills then appear as `/aimv:<skill>`, for example `/aimv:restyle-reference-video`. The plugin also registers one optional MCP server, Arcmira, which the clip finder uses to search podcasts by speaker. Sign in with `/mcp` when you want it, or leave it off.

**claude.ai.** Zip one skill folder with the folder at the top level of the zip, for example `restyle-reference-video/SKILL.md`. Upload it under Customize, then Skills. Repeat for each skill you want.

On your machine you need `ffmpeg`, Node 20 or newer, `uv`, Python 3 and Google Chrome, which renders headless. On a Mac, run `brew install ffmpeg node uv`. A remake also needs the Python packages librosa, demucs, opencv-python-headless and mediapipe, an R2 or S3 bucket for signed URLs, and a Modal account for upscales.

## The skills

`aimv` stands for AI music video. The table follows the order in which a real video is made, and most videos start with `find-youtube-clips-and-quotes`. Each skill works when installed alone. Where one skill hands off to another, it names it, so install them together for the whole flow.

| Stage | Skill | Use it for | Say something like |
| --- | --- | --- | --- |
| 1. Find the moments | [`find-youtube-clips-and-quotes`](skills/find-youtube-clips-and-quotes/SKILL.md) | Find the second someone said a line, by speaker, and cut the span between words | "Find three clips of Jensen Huang saying 'accelerated computing' since 2024" |
| 2. Build the cut from a reference | [`restyle-reference-video`](skills/restyle-reference-video/SKILL.md) | Remake a reference video shot for shot with a new subject, against the reference's own clock. Covers audio, podcast beats and code-rendered inserts | "Make this hype video but about our founder" |
| 3. Swap a person in | [`v2v-video-to-video-swap`](skills/v2v-video-to-video-swap/SKILL.md) | Put a person into any clip with video-to-video: character sheet, start and end frames, Wan 3.0, residue fixes, look match | "Put me in this clip" |
| 4. Finish each shot | [`clean-up-ai-video`](skills/clean-up-ai-video/SKILL.md) | Clean a sign or logo out of a moving shot, upscale, frame rate, film look, and match generated shots to real footage | "Upscale this shot and give it a film look" |
| 5. Gate the render | [`check-video-render`](skills/check-video-render/SKILL.md) | Gates every render before anyone watches it: frames, audio to the last frame, loudness, true peak, browser playback | "Is the render ready to post?" |
| 6. Write the recipe, and read others' first | [`write-aimv-recipe`](skills/write-aimv-recipe/SKILL.md) | Look up how other AI music videos were made on AIMV, and write your own recipe and entry | "Write up how we made it" |

`skills/restyle-reference-video/scripts/pull.mjs` is a byte-identical copy of `skills/find-youtube-clips-and-quotes/scripts/pull.mjs`, so the restyle skill can download a reference when it is installed alone. Change both copies together.

Before choosing any model, check the current leaders on [aimv.gg/generators](https://aimv.gg/generators).

### Searching by speaker

[Arcmira](https://arcmira.com) knows who is speaking in podcasts and videos, so the clip finder can ask for one person's own words and get the second each line starts. A Free account works. Without it, the clip finder cuts by URL and searches YouTube by title.

Arcmira is a remote MCP server at `https://mcp.arcmira.com/mcp`, declared in this repo's `.mcp.json`.

- With the Claude Code plugin, run `/mcp`, pick arcmira and sign in.
- In Claude Code without the plugin, connect it from your shell, then run `/mcp` and sign in:

  ```
  claude mcp add --scope user --transport http arcmira https://mcp.arcmira.com/mcp
  ```

- Any other MCP-capable agent can add the same URL as a remote HTTP server, then sign in when it opens arcmira.com. Steps for each host are at [arcmira.com/docs/mcp-server](https://arcmira.com/docs/mcp-server).

## Your first prompt

Paste this and fill in the brackets:

```
Find 8 moments since 2024 where [person] says something bold about
[topic] on a podcast. Show me the quotes and links before you download
anything. Cut each pick between words. Run the checks on each clip, and
stop before anything costs money.
```

## What it costs

Cutting, rendering and checks run on your machine. A remake that swaps a person in with a video model bills your own provider account, about $0.50 to $0.90 a shot. The Dylan Patel hype video spent $21.54 on image and video generation and $11.94 on GPU time. The skills name the price and wait for your yes before any paid run.

Arcmira searches use credits from your plan. A search that returns up to 5 passages uses none, and the clip finder keeps searches at 5. Each transcript window it reads uses 4 credits, so one search run uses at most 20. For scale, the Dylan Patel hype video used an estimated 1,000 credits over 51 searches, most of it in wide searches of 20 passages.

## Rights and consent

Reposting sports, film, music or creator footage carries copyright risk. Swapping a real person into footage needs their consent, and the skills record it. The clip log keeps every source by URL and second, so you can credit it.

## Why we remix

Zeal is a digital art enthusiast, and the videos in this family are remixes. Remixing and sampling are a lot of the fun of making music and DJing. You flip a sample, cut an edit to someone else's track, or recut a famous clip around a new face. Most of that culture runs on a tacit understanding that it's all good. Sometimes music labels get weird, and in some cases a rights holder can take a video down. We think people should be free to make art out of the culture around them. None of these videos is sold, and the sources are credited by link, not shipped.

## The family

Each video gets the same eight-section guide, and the work turns into Claude skills. More are coming, and each one lands on [aimv.gg/zealcaiden](https://aimv.gg/zealcaiden) with its recipe.

| Repo | What it is |
| --- | --- |
| [dylan-patel-hype-video](https://github.com/zealous1/dylan-patel-hype-video) | A 30-second remake of a viral LeBron hype video, with Dylan Patel of SemiAnalysis swapped in |
| [claude-video-editing-skills](https://github.com/aimvgg/claude-video-editing-skills) | The Claude skills these videos became |

## Licence

Apache-2.0.

## About

Made free and open source by [Arcmira](https://arcmira.com), the search engine for what people say in podcasts and videos. These are the [Claude video editing skills](https://github.com/aimvgg/claude-video-editing-skills), written while making real hype videos and AI music videos. Arcmira is optional, and every skill works without it. Shipped by [Zeal](https://x.com/zealcaiden).
