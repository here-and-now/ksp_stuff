# Review 2026-08-21T21-14-09Z-hop-splash

command: hop-splash
exit: 2
abort: not recoverable
log: docs/missions/jebediah/logs/2026-08-21T21-14-09Z-hop-splash.jsonl
earth: 2026-08-21 21:14:09 UTC
kerbal_ut: 2d 15:42:17 UT
kerbal_met: ?
samples: 214 (~1 Hz)
duration: 527.3 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 71.7
- peri min -6365763.4
- apo max 101362.6
- met max 500.4
- EC 2409.9 → 0.0 (min 0.0)
- fuel 1575.0 → 0.0 (min 0.0)
- LF 1575.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 11, 'empty tanks': 11}

## First / last

- Earth pre_launch alt=85.39453661814332 peri=-6362517.904033842 apo=85.3945260476321 met=0.0 ec=2409.901123046875 fuel=1575.0 warp=Nonex
- Earth flying alt=71.71196420490742 peri=-6360310.945004973 apo=222.07320215459913 met=500.399999737856 ec=0.0 fuel=0.0 warp=Nonex [ec=0 empty tanks]

## Flag changes

- T+516s  ec=0 empty tanks

## Events

- T+0s start command=hop-splash crew=
- T+577s end samples=215

## Handoff

```
command: hop-splash
exit: 2
abort: not recoverable
last:
  hangar ready kspstuff-hop-valiant-t7-splash-pbc sit=VesselSituation.pre_launch parts=41
  hop apo=80000
  hop-splash light vertical, no flying Toggle, wait splash
  hop light
  hop airborne
  gate ec=0
  hop ec=0 wait splash
  hop recover sit=flying recoverable=no
  gate ec=0
  hop recover sit=flying recoverable=no
  gate ec=0
  hop recover sit=flying recoverable=no
  gate ec=0
  hop recover sit=flying recoverable=no
  gate ec=0
  hop recover sit=flying recoverable=no
  gate ec=0
  hop down
  hop recover sit=flying recoverable=no
  hop crash ui sit=flying recoverable=no met=500.40 alt=71.7 q=0
  hop unpause
  gate ec=0
  gate ec=0
  gate ec=0
  gate ec=0
  gate ec=0
  ABORT not recoverable

```

## Learn

_Gene fills this. What worked, what failed, what to change in
the library vs this pilot's style. One short paragraph._
