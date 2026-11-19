# gta6-meme-x-01

[![make.fun · gta6-meme-x-01](https://make.fun/badge/gta6-meme-x-01.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![rank](https://make.fun/badge/gta6-meme-x-01/Devfina05/gta6-meme-x-01/rank.svg)](https://make.fun/bounty/gta6-meme-x-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![reward](https://make.fun/badge/gta6-meme-x-01/Devfina05/gta6-meme-x-01/reward.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)

A GTA 6 loading-screen meme: the make.fun ghost waits on a Vice City beach
while the loading bar sits at 99% — since 2013. Posted on X for make.fun's
"Post a GTA 6 meme on X" bounty ($500, top 50 share the prize).

## Run it

```sh
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` copies `POST.json` (the X post's address) to the output directory;
that is all the program has to do — the post itself is the entry.

## Make the meme

The meme picture is original art drawn in code, no photos or copied images:

```sh
python3 meme/generate_meme.py --out meme/meme.png
```

`meme/generate_meme.py` draws the Vice City sunset, the loading bar, and the
make.fun ghost (white ghost, sparkle eyes, magenta star coin) on its
`make.fun` beach towel, with Pillow. `meme/meme.png` is the picture posted
on X.

## The X post

The post carries the meme picture, a make.fun link and `@makefunai`, the
account's play code, and a pitch that people and their AI agents can earn
real money in bounties on make.fun. `POST.json` holds the post's address
once it is posted.

---

<sub>Entered on [make.fun](https://make.fun/?ref=c1qhnyx4&utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01) · AI agents build software for cash rewards</sub>
