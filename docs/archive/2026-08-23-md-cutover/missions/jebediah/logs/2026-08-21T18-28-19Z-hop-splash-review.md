# Review 2026-08-21T18-28-19Z-hop-splash

command: hop-splash
exit: 2
abort: no science (wanted kerbalism_TELEMETRY)
log: docs/missions/jebediah/logs/2026-08-21T18-28-19Z-hop-splash.jsonl
earth: 2026-08-21 18:28:19 UTC
kerbal_ut: 2d 14:13:06 UT
kerbal_met: MET 0d 00:07:55
samples: 195 (~1 Hz)
duration: 517.5 s wall
bodies: Earth
tags: {}

## Envelope

- alt min -0.2
- peri min -6367935.1
- apo max 89717.0
- met max 485.4
- EC 2409.9 → 0.0 (min 0.0)
- fuel 1575.0 → 0.0 (min 0.0)
- LF 1575.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 2}

## First / last

- Earth pre_launch alt=85.84098974894732 peri=-6362518.605532019 apo=85.84099285118282 met=0.0 ec=2409.905029296875 fuel=1575.0 warp=Nonex
- Earth splashed alt=-0.24832972511649132 peri=-6362760.8238810515 apo=150.06987023632973 met=485.399999745714 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+517s  ec=0

## Events

- T+0s start command=hop-splash crew=
- T+518s end samples=196

## Handoff

```
command: hop-splash
exit: 2
abort: no science (wanted kerbalism_TELEMETRY)
last:
  hop leftover wreck sit=splashed recoverable=yes experiments=0 — recover, Hangar new
  recovered leftover wreck
  hop recover still listed after recover()
  hangar ready kspstuff-hop-valiant-t7-splash-pbc sit=VesselSituation.pre_launch parts=41
  hop apo=80000
  hop-splash light vertical, no flying Toggle, wait splash
  hop light
  hop airborne
  hop-splash splash
  splash wait water
  gate ec=0
  splash down
  science skip (no Experiment modules)
  ABORT no science (wanted kerbalism_TELEMETRY)

```

## Learn

Leftover wreck recover + Hangar t7 **worked**. Vertical loft splashed **Shores** MET **485** apo **89.7 km** EC=0. Envelope **heading 212 horiz 63 pitch 4**. Science skip modules=0, abort **no science TELEMETRY**. goo never. **+0**. Do not start airborne.
