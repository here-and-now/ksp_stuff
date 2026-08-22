# Review 2026-08-21T18-08-07Z-hop-splash

command: hop-splash
exit: 2
abort: no science (wanted kerbalism_TELEMETRY)
log: docs/missions/jebediah/logs/2026-08-21T18-08-07Z-hop-splash.jsonl
earth: 2026-08-21 18:08:07 UTC
kerbal_ut: 2d 14:04:07 UT
kerbal_met: MET 0d 00:08:52
samples: 2 (~1 Hz)
duration: 0.5 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 0.6
- peri min -6362680.9
- apo max 113.1
- met max 532.2
- EC 0.0 → 0.0 (min 0.0)
- fuel 0.0 → 0.0 (min 0.0)
- LF 0.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 2}

## First / last

- Earth splashed alt=0.5585159128531814 peri=-6362680.90576927 apo=113.05066428985447 met=532.1799997212074 ec=0.0 fuel=0.0 warp=Nonex [ec=0]
- Earth splashed alt=0.5585159128531814 peri=-6362680.90576927 apo=113.05066428985447 met=532.1799997212074 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+0s  ec=0

## Events

- T+0s start command=hop-splash crew=
- T+1s end samples=3

## Handoff

```
command: hop-splash
exit: 2
abort: no science (wanted kerbalism_TELEMETRY)
last:
  hop apo=80000
  hop-splash light vertical, no flying Toggle, wait splash
  hop-splash splash
  splash wait water
  gate ec=0
  splash down
  science skip (no Experiment modules)
  ABORT no science (wanted kerbalism_TELEMETRY)

```

## Learn

_Gene fills this. What worked, what failed, what to change in
the library vs this pilot's style. One short paragraph._
