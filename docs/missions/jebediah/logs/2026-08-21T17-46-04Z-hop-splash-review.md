# Review 2026-08-21T17-46-04Z-hop-splash

command: hop-splash
exit: 2
abort: ec=0
log: docs/missions/jebediah/logs/2026-08-21T17-46-04Z-hop-splash.jsonl
earth: 2026-08-21 17:46:04 UTC
kerbal_ut: 2d 13:54:11 UT
kerbal_met: MET 0d 00:00:00
samples: 262 (~1 Hz)
duration: 552.2 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 0.6
- peri min -6366945.2
- apo max 96919.5
- met max 532.2
- EC 1009.9 → 0.0 (min 0.0)
- fuel 1575.0 → 0.0 (min 0.0)
- LF 1575.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 2}

## First / last

- Earth pre_launch alt=85.81672825757414 peri=-6362518.378084979 apo=85.8167307972908 met=0.0 ec=1009.904052734375 fuel=1575.0 warp=Nonex
- Earth splashed alt=0.5585159128531814 peri=-6362680.90576927 apo=113.05066428985447 met=532.1799997212074 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+552s  ec=0

## Events

- T+0s start command=hop-splash crew=
- T+552s end samples=263

## Handoff

```
command: hop-splash
exit: 2
abort: ec=0
last:
  hop leftover unmatched kspstuff-hop-valiant-east-fin-pbc sit=pre_launch recoverable=yes — recover, do not light
  recovered unmatched leftover sit=pre_launch recoverable=yes
  hop recover gone
  hangar ready kspstuff-hop-valiant-t7-splash-pbc sit=VesselSituation.pre_launch parts=27
  hop apo=80000
  hop-splash light vertical, no flying Toggle, wait splash
  hop light
  hop airborne
  hop-splash splash
  splash wait water
  gate ec=0
  ABORT ec=0

```

## Learn

17-46-04Z hop-splash abort +0 (10.96 → 10.96). Ghost east-fin recovered
dark; Hangar t7-splash 27 parts; light vertical; splash Water MET
**532.2** alt **0.56 m**. Envelope vs briefed heading **never** (no 090
program): pad HDG **299**, burn HDG **299–302**, coast tumble
**0.6–359**, splash **29**. horiz max **168.4 m/s** (FAR coast flop —
not a re-entry burn). apo max **96.9 km**. pitch/AoA/biome **absent**
this tape (262 state). EC **1010 → 0** at splash — science never
started. 10×Z-100 cannot buy TELEMETRY 30/0.052 + goo 641/0.18 after
~1.9/s loft drain. Next hang **24×Z-100**. Lars: dwell may start at
EC=0. hangar none. Same hop-splash.
