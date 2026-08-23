# Review 2026-08-21T18-03-12Z-hop-splash

command: hop-splash
exit: 0
abort: 
log: docs/missions/jebediah/logs/2026-08-21T18-03-12Z-hop-splash.jsonl
earth: 2026-08-21 18:03:12 UTC
kerbal_ut: 2d 14:04:07 UT
kerbal_met: MET 0d 00:08:52
samples: 1 (~1 Hz)
duration: 0.1 s wall
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
- flags {'ec=0': 1}

## First / last

- Earth splashed alt=0.5585159128531814 peri=-6362680.90576927 apo=113.05066428985447 met=532.1799997212074 ec=0.0 fuel=0.0 warp=Nonex [ec=0]
- Earth splashed alt=0.5585159128531814 peri=-6362680.90576927 apo=113.05066428985447 met=532.1799997212074 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+0s  ec=0

## Events

- T+0s start command=hop-splash crew=
- T+0s end samples=2

## Handoff

```
command: hop-splash
exit: 0
abort: 
last:
  hop apo=80000
  hop-splash light vertical, no flying Toggle, wait splash
  hop leftover sit=splashed fuel=0.0 recoverable=yes met=532.18 — do not light
  recovered sit=splashed recoverable=yes
  recovered

```

## Learn

18-03 leftover splash recover **before** TELEMETRY/goo. exit 0. sci
**+0** (10.96). jsonl samples **1**: heading **29** horiz **78.45**
pitch **0.77** aoa **0** biome **Shores** (not Water) alt 0.56 m
MET **532** EC **0** fuel **0** apo 113 m peri −6363 km. 17-46 loft
apo **96.9 km** splash MET 532 EC 0 — FAR coast not a re-entry burn.
Card never lit. Lars: splashed leftover **starts** splash card at
EC=0. hangar **none**. Same t7 24×Z-100. Do not Hangar. Do not
hop-to-water. Pair 3.20 still 0.84 short.
