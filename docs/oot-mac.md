# Ocarina of Time on the Mac, in two commands

Two scripts take a Mac from nothing to The Legend of Zelda: Ocarina of Time (Switch 2, `0400486024DEC000`) as a Mac app. This is a fork: upstream [nxnative](https://github.com/seedds/nxnative) has not merged this game's support yet, and the `oot-mac` branch gathers the open work of several contributors. Expect an unfinished game (see [PR #1299](https://github.com/seedds/nxnative/pull/1299) and [issue #1265](https://github.com/seedds/nxnative/issues/1265)). Bugs of this branch belong here, not upstream.

## What you need

- A Mac with Apple silicon and Xcode, opened once. Xcode 27.2 is the tested one; with another the script adds `--allow-other-metal`, and the graphics may differ.
- Your own copy of the game as one `.nup` file. No `prod.keys`. Neither the game nor keys belong in this repository or its issues.
- About twice the game's size plus 10 GB of free disk.
- 24 GB of memory or more is recommended. On 16 GB Macs testers report heavy swapping and GPU out-of-memory stops at scene changes, and a kernel panic in the GPU driver was reported on a 24 GB Mac. Save your work before playing.

## Install and build

Everything else is installed for you: Homebrew, the tools, the Metal toolchain and a clone in `~/nxnative-oot`. The build took about an hour on an M1 Pro; keep the Mac plugged in with the lid open. It stays awake by itself.

```sh
curl -fsSLO https://raw.githubusercontent.com/LeonardoBai12/nxnative/oot-mac/scripts/oot_mac_setup.py
python3 oot_mac_setup.py ~/Games/ocarina.nup
```

If it stops, run the same command again: finished steps are skipped. The app appears beside the `.nup`, as `Zelda OOT.app`.

## Play

```sh
python3 ~/nxnative-oot/scripts/oot_mac_play.py
```

## What the branch holds

On stan69b's `oot-clean` (#1299, #1300, #1312, #1320, #1353, the pool table, float atomics, ATOMG.CAS and the memory work): #1345, #1343, #1376, #1331, #1377 and #1379, the shader translator rebuilt from that merged source, and a guard that lets the macOS 26 SDK compile MetalFX's macOS 27 properties. Conflicts were only in docs and generated files, which keep this branch's side.

This branch also skips the movie library's NDVE network, on by default through `scripts/oot_mac.env` (`DM_NVN_NDVE_MOVIE_DIRECT=1`): the decoded frame is scaled straight to the output. On GPUs without tensor cores that network is nearly all of a movie frame ([issue #1375](https://github.com/seedds/nxnative/issues/1375)), and the title screen's background is such a movie. The picture loses the filter, a small difference. A workaround, not a fix of the network's speed.

## Measured on an M1 Pro with 16 GB

One player's sessions of this branch (Xcode 26.6, macOS 26), not a benchmark:

| Scene | GPU a frame | Frame rate |
|---|---|---|
| Movies, title screen, the opening up to Link waking | about 5 ms | 60 fps |
| Real-time cutscenes and Kokiri Forest, Handheld | 36 to 58 ms | 19 to 31 fps |
| Light real-time moments, Handheld | about 7 ms | 48 fps and up |

- **Playable?** Not yet. Below about 30 fps the game runs in slow motion rather than only dropping frames; the cause is not confirmed.
- **Collapse to about 4 fps:** in Docked mode after 11 minutes, on a Mac up 88 days, with GPU time at 190 to 350 ms a frame, two Metal GPU hangs and 11.3 GB resident. A restart and Handheld gave a session without it, but that session lasted only about 3.5 minutes, and it had two GPU hangs too.
- **What helps:** restart the Mac first, close other apps, stay on AC power and choose Handheld. Handheld and MetalFX changed nothing in the movies.
- **First visits load slowly:** ground and models appear late while new pipelines compile; they are kept for later runs.
- `DM_RENDER_SCALE` has no effect on this game: it has no render scale stub.
