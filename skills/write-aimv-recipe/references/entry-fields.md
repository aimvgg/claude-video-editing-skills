# Video entry fields

Every field of a video entry, from the AIMV video schema of 2026-10-17. Required fields are marked **required**. `../example-entry.yml` is a complete entry that uses most of them.

An id is lowercase letters, digits and hyphens (`wan-3-0`). Model, tool, framework, kind and tag ids come from `aimvgg/awesome-ai-music-video-generators`. An id that does not exist yet is allowed. The Entry check flags it as new, and a maintainer adds it.

## Top level

| Field | Type | Notes |
| --- | --- | --- |
| `type` | `video` | **required** |
| `title` | text, at most 80 characters | **required** |
| `artist` | object | **required**. See below |
| `video` | object | **required**. See below |
| `kind` | 1 to 3 kind ids | **required**. For example `music-video`, `lyric-video`, `motion-graphics`, `anime`, `3d-scene`, `demoscene`, `hype-edit`, `short-film`, `explainer`, `footage-edit`, `product-promo` |
| `tags` | tag ids | Optional. For example `remix`, `beat-sync` |
| `rating` | `general`, `mature` or `adult` | Follows the content, never the title |
| `made_with` | object | **required**. See below |
| `audio` | object | See below |
| `prompt` | object | `shared` (**required** inside it): `full`, `partial` or `none`. `text`: the prompt |
| `process` | object | The recipe. See below |
| `source_repo` | URL | The recipe repo. The artist's own repo makes the recipe SUPER |
| `people` | list of names | Every real person depicted |
| `version_of` | video id | When this video is a version of another entry |
| `inferred` | list of field names | Fields the editors read rather than the artist stated |
| `unknown` | list of field names | Fields nobody knows yet |
| `evidence` | `artist-post`, `source-repo`, `prompt-only` or `third-party` | **required**. What the entry rests on |
| `i_am_the_artist` | true or false | **required** |
| `submitted_by`, `added`, `recipe_score`, `status` | | Set by maintainers. Leave them out |

## `artist`

| Field | Notes |
| --- | --- |
| `x` | **required**. The X handle without `@`, 1 to 15 letters, digits or underscores |
| `name` | Display name |
| `youtube` | Channel handle or URL |
| `github` | Leave it out unless the artist asks. It ties their X account to that GitHub account publicly |

## `video`

| Field | Notes |
| --- | --- |
| `url` | **required**. The X, YouTube or Vimeo post |
| `also_at` | Other URLs of the same video |
| `duration_s` | Whole seconds |
| `aspect` | `16:9`, `9:16`, `1:1`, `4:5` or `other` |

## `made_with`

| Field | Notes |
| --- | --- |
| `method` | **required**. `code-rendered`, `generative`, `hybrid` or `edit` |
| `models` | **required**. At least one model id |
| `agent` | An agent id from the schema's list, such as `claude-code` or `claude-app`, or else `other` or `none` |
| `frameworks`, `tools`, `generators` | Ids |
| `repos` | `owner/repo` of open-source projects used |
| `notes` | Free text for anything without an id yet |
| `sources` | Maps an id to where the artist said it: `{from: post}`, `{from: reply, url: ...}` or `{from: page, url: ...}` |

## `audio`

| Field | Notes |
| --- | --- |
| `tracks[]` | `role` (**required**): `music`, `vocals`, `intro`, `sample`, `sfx`, `voiceover` or `stem`. `source`: `generated`, `recorded`, `licensed` or `existing`. Also `title`, `artist`, `generator` (an id), `model`, `models`, `parts`, `code_engine`, `url`, `prompt`, `lyrics`. An existing song is `source: existing` with its `artist`. Never paste its lyrics |
| `post` | Up to 300 characters on how the audio was mixed and mastered |
| `post_tools` | Ids |

## `clips`

Top level. Every outside clip in the video, whether the edit used its sound, its picture or both.

| Field | Notes |
| --- | --- |
| `from` | **Required.** The https URL of the source |
| `at_s`, `len_s` | Start in the source and length, in seconds |
| `used` | `audio`, `video` or `audio+video` (the default) |
| `speaker`, `what` | Who is speaking, and what the clip is |
| `found.via` | `arcmira`, `url`, `web-search`, `manual` or `other`. Inferred when left out: a `call` means `arcmira`, an `in` link alone means `url`, otherwise `manual` |
| `found.call` | The Arcmira client method or MCP tool that found it, such as `search`. At most 60 characters |
| `found.input` | The call's exact input, as a map. Public, so never an email or a local path |
| `found.in` | The https URL of the upload the hit was found in, when it differs from `from` |
| `found.note` | Free text. A plain string for `found` becomes a note |

`audio.spoken_clips` and `found_with` are retired, and both are errors. A clip Arcmira found needs `arcmira` in `made_with.tools`.

## `process`

| Field | Notes |
| --- | --- |
| `steps[]` | `part`, `did` and `source` are **required** in each step. `part` is `idea`, `research`, `lyrics`, `song`, `vocals`, `stills`, `motion`, `lip-sync`, `graphics`, `3d`, `beat-map`, `edit`, `render` or `agent-run`. `did` is at most 140 characters. `source` is a URL that says it, and a `RECIPE.md` anchor works. Add `tool` or `model` (an id), and `inferred: true` when the editors read it rather than the artist said it. Every step's tool or model must also appear in `made_with` (the `agent` field counts) or `audio` |
| `prompts[]` | `stage` and `text` **required**, `tool` optional |
| `answers[]` | The artist's own words: `a` and `url` **required**, `q` and `q_url` optional |
| `traces[]` | Agent transcripts or logs: `kind` **required**, `url` or `file` |
| `artifacts[]` | Project files: `kind` and `url` **required** |
| `guide` | A list of URLs, or `{url, file}` |
| `prompt_post` | URL of the post that shares the prompt |
| `time_spent`, `cost` | Free text |
