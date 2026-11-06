# Ocarina of Time on the Mac, in two commands

Two scripts take a Mac from nothing to The Legend of Zelda: Ocarina of Time (Switch 2, `0400486024DEC000`) as a Mac app. This is a fork: upstream [nxnative](https://github.com/seedds/nxnative) has not merged this game's support yet, and the `oot-mac5` branch gathers the open work of several contributors. Expect an unfinished game (see [PR #1299](https://github.com/seedds/nxnative/pull/1299) and [issue #1265](https://github.com/seedds/nxnative/issues/1265)). Bugs of this branch belong here, not upstream.

## What you need

- A Mac with Apple silicon and Xcode, opened once. Xcode 27.2 is the tested one; with another the script adds `--allow-other-metal`, and the graphics may differ.
- Your own copy of the game as one `.nup` file. No `prod.keys`. Neither the game nor keys belong in this repository or its issues.
- About twice the game's size plus 10 GB of free disk.
- 24 GB of memory or more is recommended. On 16 GB Macs testers report heavy swapping and GPU out-of-memory stops at scene changes, and a kernel panic in the GPU driver was reported on a 24 GB Mac. Save your work before playing.

## Install and build

Everything else is installed for you: Homebrew, the tools, the Metal toolchain and a clone in `~/nxnative-oot`. The build took about an hour on an M1 Pro; keep the Mac plugged in with the lid open. It stays awake by itself.

```sh
curl -fsSLO https://raw.githubusercontent.com/LeonardoBai12/nxnative/oot-mac5/scripts/oot_mac_setup.py
python3 oot_mac_setup.py ~/Games/ocarina.nup
```

If it stops, run the same command again: finished steps are skipped. The app appears beside the `.nup`, as `Zelda OOT.app`.

## Play

```sh
python3 ~/nxnative-oot/scripts/oot_mac_play.py
```

## What the branch holds

On current `main`, which now holds this game: #1331 (with any output size, for Handheld), #1453, #1497, #1377, #1379, #1484, #1493, #1503, #1522, #1558, #1390, #1556, #1557, #1544, and a guard that lets the macOS 26 SDK compile MetalFX's macOS 27 properties.

This branch also keeps the game at real speed below 60 fps (see the results below) and skips the movie library's NDVE network, on by default through `scripts/oot_mac.env` (`DM_NVN_NDVE_MOVIE_DIRECT=1`): the decoded frame is scaled straight to the output. On GPUs without tensor cores that network is nearly all of a movie frame ([issue #1375](https://github.com/seedds/nxnative/issues/1375)), and the title screen's background is such a movie. The picture loses the filter, a small difference. A workaround, not a fix of the network's speed.

## Measured on an M1 Pro with 16 GB

One player's two sessions of this branch, Handheld, on AC power (Xcode 26.6, macOS 26), not a benchmark. Only the second left a log, about 3.5 minutes at Render scale 0.7:

| | Render scale 1 | Render scale 0.7 |
|---|---|---|
| Speed | normal | normal |
| Ground on arrival | about 10 s late, with a strange light from the ground until then | no visible delay |
| Water | hitches a little | hardly hitches |
| Girls pointing at the Deku Tree | no stall | no stall |
| Frame time in play, per 300 frames (median) | not logged | 27 to 37 ms, 27 to 37 fps |

- **Playable?** Yes in this short test, at both scales: vegetation was right and the white squares did not come back. Render scale 0.7 is the better setting here.
- **Long frames at 0.7:** the three of 2 to 2.6 s were first-time pipeline compiles, which later runs keep.
- **One GPU address fault:** 1 of 17,978 command buffers failed, as the first 3D scene loaded. The game went on.
- **Memory at 0.7:** 9.5 GB resident, 15.2 GB allocated.
- **Three shaders do not build here:** one opcode 481 entry and two `agl_technique_pfx` compute shaders. Nothing looked wrong for it; `main` has since fixed them.
- **Not tested here:** long sessions. The collapse below may still happen.

The earlier `oot-mac` branch, on an older base:

| Scene | GPU a frame | Frame rate |
|---|---|---|
| Movies, title screen, the opening up to Link waking | about 5 ms | 60 fps |
| Real-time cutscenes and Kokiri Forest, Handheld | 36 to 58 ms | 19 to 31 fps |
| Light real-time moments, Handheld | about 7 ms | 48 fps and up |

- **Playable?** Roughly. Link now walks at normal speed at about 20 fps, and collision held up in a 5-minute Handheld session with no GPU hang, but open views still stall.
- **Slow motion fixed:** the game stepped a fixed amount per frame. Its step now follows the measured frame time (`DM_FRAME_DELTA=0` turns this off), found by gunvalk in [Lichii PR #216](https://github.com/zortos293/Lichii/pull/216). The frame rate does not change.
- **Stalls in open views:** views of the whole village or the horizon draw about 2,500 times a frame, against about 860, and frames then reach 1 s. In that window 3.3 GB moved in and out of the residency set per 300 frames, with 11.2 GB resident on 16 GB. Other stalls of 1 to 3.5 s are first-time pipeline compiles.
- **Late ground:** ground can stay missing for a while in some places; the cause is not known.
- **Collapse to about 4 fps:** in Docked mode after 11 minutes, on a Mac up 88 days, with GPU time at 190 to 350 ms a frame, two Metal GPU hangs and 11.3 GB resident. A restart and Handheld gave a session without it, but that session lasted only about 3.5 minutes, and it had two GPU hangs too.
- **What helps:** restart the Mac first, close other apps, stay on AC power and choose Handheld. Handheld and MetalFX changed nothing in the movies.
- **First visits load slowly:** ground and models appear late while new pipelines compile; they are kept for later runs.
- **Render scale:** the launcher's setting (`DM_RENDER_SCALE`, 0.5 to 1) lowers the size of the 3D views, from #1497. That earlier branch did not have it.
