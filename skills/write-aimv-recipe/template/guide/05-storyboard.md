# 5. Storyboard and timeline

`storyboard/index.html` loads `storyboard.json` and shows every slot on the clock with every take tried for it, the pick at each checkpoint, and why. The component is the same in every guide; only the JSON changes. Its schema is `storyboard/schema.json`.

## Open it

Browsers block `fetch` on `file://` pages, so serve the folder. From `guide/storyboard/`, run `python3 -m http.server 8000`, then open http://localhost:8000/index.html.

## Reading it

- The top row is the clock. Each slot below it is one shot.
- Each slot lists its takes in the order they were made, with the model, the cost and the verdict.
- The checkpoint selector replays the picks that made each published version.

## Media

Say which takes can be shown and how (see the options in `storyboard/README.md`).
