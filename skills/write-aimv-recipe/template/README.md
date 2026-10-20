# How-we-made-it guide template

One template for every AI music video or hype video guide. A video's repo copies the generic parts and fills the per-video data. The Dylan Patel hype video fills it, and it is the only public example so far.

## The system

Every video, whatever it starts from, reduces to the same four things:

1. **A clock.** The reference edit's audio for a remake, the song's beat grid for a hype video, a voiceover for an explainer.
2. **Slots on the clock.** Measured from the reference's cuts, placed on beats and story moments, or taken from source shots.
3. **Takes per slot.** Each take is found (a clip from research), generated (an image model, then a video model), code-rendered, kept from the reference, or overlaid on it.
4. **Picks at checkpoints.** A checkpoint is a set of picks that renders to a publishable file and passes the gates.

The starting direction only changes how slots are made and where takes come from.

| Starting point | The clock | Slots come from | Takes come mostly from | Example |
| --- | --- | --- | --- | --- |
| A reference edit to remake | Its audio | Its measured cuts | Swaps (V2V), overlays, code inserts, research | Dylan Patel hype video |
| A song and your own footage | The beat grid | Beats and story moments | Your footage, found clips, code effects | |
| An idea or a script | The song or voiceover | The script's beats | Generators and code | |
| Footage to repurpose | The source's own timing | Source shots | Transforms of the source | |

Around that core sit the same layers every time. Research finds and logs sources. Generation and code make takes. Finishing sets the look, frame rate, resolution and audio master. Gates check every render. The recipe publishes it. The guide has one section per layer, so two guides with radically different starts still read the same way.

## Repo layout

```
README.md                  what it is, watch link, consent, the guide's table of contents
RECIPE.md                  the human recipe: one heading per step
recipe.yml                 the AIMV recipe folder file (entry fields, with `file` paths)
prompts/<n>-<stage>.md     every prompt longer than a line, as written or recalled
code/                      the code that made the video, as it ran, paths relative, keys from the environment
code/LICENSE               the code licence
sources.json               every third-party source by public URL and second
guide/
  01-research.md           research direction and findings       + research-calls.json
  02-libraries.md          the open-source libraries, by layer
  03-software.md           the purpose-built software
  04-checkpoints.md        the path to each publishable checkpoint and the last-mile taste calls
  05-storyboard.md         how to read the storyboard            + storyboard/ (component + storyboard.json)
  06-models.md             model tests, winners, SOTA calls       + models.json
  07-scaffolding.md        the tools built before the first shot, and what they made possible
  08-chat.md               the chat analysis                      + chat.json
```

## Generic and per-video

| Piece | Generic, copied from this template | Per video, filled from data |
| --- | --- | --- |
| README, RECIPE, guide section headings | `README.skeleton.md`, `RECIPE.skeleton.md` and the skeletons in `guide/` here | the prose |
| Research | the method in `01-research.md` | `research-calls.json` and the findings |
| Libraries, software | the layer list | which ones, what each did |
| Checkpoints | the checkpoint table shape | the checkpoints and taste calls |
| Storyboard | `storyboard/index.html`, `storyboard.js`, `storyboard.css`, `schema.json` | `storyboard.json`, approved stills |
| Models | `tools/render_models.py` | `models.json` |
| Chat analysis | the section headings in `guide/08-chat.md` | the output of your own chat-log script, `chat.json` and `08-chat.md` |
| Gates | `check-video-render` skill (`check.py`) | the thresholds for this video |
| Recipe | `recipe.yml` here, and the prompt naming | the values |

## Rules for every guide

- No media from third parties. Sources go in `sources.json` by URL and second.
- Every model and tool is an AIMV id from the generators repo, or a proposed id with a drafted tool entry.
- Before choosing a model, check the current leaders on https://aimv.gg/generators.
- Quotes of the artist's own words are welcome. Nothing about accounts, keys, the systems behind a product, other people's private work, or machine paths.
- Before any push, scrub every file by the list in the write-aimv-recipe skill ("Then scrub the repo and the entry"). Search the repo for your home folder path, personal email addresses, key prefixes such as `sk-`, and `.env` files.

## What is here

- `README.skeleton.md` and `RECIPE.skeleton.md`: the repo's front page and recipe, in the order the worked examples use.
- `recipe.yml`: the recipe folder file, with every field commented.
- `guide/`: the eight section skeletons.
- `storyboard/`: the storyboard page (`index.html`, `storyboard.js`, `storyboard.css`), its `schema.json`, `validate.py` and an example. Copy it to `guide/storyboard/` and add your `storyboard.json`.
- `tools/render_models.py`: renders `guide/models.json` into `guide/06-models.md`.

The chat analysis section comes from a script that reads your own chat logs. Keep that script and its config out of the public repo, and ship only what it writes.

## Storyboard media options

When the takes cannot be published, see `storyboard/README.md` for the options and the recommendation.
