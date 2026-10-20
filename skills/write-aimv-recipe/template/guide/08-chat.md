# 8. The chat behind the video

Write this from your own chat logs, by hand or with your own script. Keep that script and its config out of the public repo, and ship only what it writes, this page and `chat.json`. Scrub both like every other file.

## How the artist directed

Two to four sentences on how direction was given, such as one-line notes after each render, long briefs, options side by side or recorded takes. Then the counts from `chat.json`, which are the artist's messages, the agent's replies and tool calls, the helper agents, and the time from the first message to the last checkpoint.

## In the artist's words

Four to six messages, picked by hand and copied exactly, typos kept. Give each its turn number and one line on what it changed. Check every quote against the log before you ship.

## Reversals

Only the reversals you can tell in one true line, saying what was proposed or built, what the artist said, and what replaced it.

## Tokens and what they would cost

Replies and tokens by model, from the usage the logs record, priced at the provider's list prices with the month of the prices. Say it is a price for the tokens, not an invoice. Name every model that ran, helper agents included, so the list matches the recipe's Agent line.

## Media and API costs

What generation, GPU time and search credits cost, and whether each figure is measured or estimated.

## Timeline

Each checkpoint with its turn and time, in the same time zone as `04-checkpoints.md`.
