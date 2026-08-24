# Review 2026-08-24T14-53-59Z-hop-splash

command: hop-splash
exit: 2
abort: not splashed
log: docs/missions/jebediah/logs/2026-08-24T14-53-59Z-hop-splash.jsonl
earth: 2026-08-24 14:53:59 UTC
kerbal_ut: 3d 08:52:18 UT
kerbal_met: ?
samples: 3 (~1 Hz)
duration: 63.7 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 84.2
- peri min -6362520.7
- apo max 89.7
- met max 18.7
- EC 2049.9 → 2049.3 (min 2049.3)
- fuel 1080.0 → 1069.4 (min 1069.4)
- LF 1080.0 → 1069.4 (min 1069.4)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {}

## First / last

- Earth pre_launch alt=85.41845825780183 peri=-6362518.504824874 apo=85.41845658328384 met=0.0 ec=2049.917236328125 fuel=1080.0 warp=Nonex
- Earth landed alt=84.20841763168573 peri=-6362520.705468417 apo=84.20813253521919 met=18.66000001737848 ec=2049.333251953125 fuel=1069.426513671875 warp=Nonex

## Flag changes

- (none)

## Events

- T+0s start command=hop-splash crew=
- T+1s hangar launch kspstuff-hop-valiant-proc-stiff-pbc
- T+7s hangar scene flight
- T+28s recoverable recoverable=yes sit=pre_launch
- T+46s recoverable recoverable=no sit=flying
- T+64s landing landing: soft impact=0 m/s heading=36 horiz=0 pitch=-7 sit=landed
- T+64s recoverable recoverable=yes sit=landed
- T+64s sci_bank sci=9.4718
- T+64s end samples=11

## Handoff

```
command: hop-splash
exit: 2
abort: not splashed
sci: 9.4718
last:
  hangar ready kspstuff-hop-valiant-proc-stiff-pbc sit=VesselSituation.pre_launch parts=36
  hop apo=50000
  hop-splash light vertical, no flying Toggle, wait splash
  hop light
  hop airborne
  chute armed
  hop chute armed
  ABORT not splashed

```

## Learn

exit=2 abort=not splashed. envelope heading 299→36, horiz max 0, pitch 90→-7.
