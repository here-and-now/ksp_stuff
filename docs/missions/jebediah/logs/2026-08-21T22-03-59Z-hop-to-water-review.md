# Review 2026-08-21T22-03-59Z-hop-to-water

command: hop-to-water
exit: 2
abort: no science (wanted mysteryGoo)
log: docs/missions/jebediah/logs/2026-08-21T22-03-59Z-hop-to-water.jsonl
earth: 2026-08-21 22:03:59 UTC
kerbal_ut: 2d 15:40:02 UT
kerbal_met: ?
samples: 99 (~1 Hz)
duration: 227.5 s wall
bodies: Earth
tags: {}

## Envelope

- alt min -2.6
- peri min -6362773.9
- apo max 19064.9
- met max 212.2
- EC 2009.9 → 0.0 (min 0.0)
- fuel 675.0 → 0.0 (min 0.0)
- LF 675.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 3}

## First / last

- Earth pre_launch alt=84.32101582922041 peri=-6362518.540839879 apo=84.3210137207061 met=0.0 ec=2009.9061279296875 fuel=675.0 warp=Nonex
- Earth splashed alt=-2.6049106465652585 peri=-6360848.519295679 apo=2689.7181875528768 met=212.199999888835 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+227s  ec=0

## Events

- T+0s start command=hop-to-water crew=
- T+228s end samples=100

## Handoff

```
command: hop-to-water
exit: 2
abort: no science (wanted mysteryGoo)
last:
  hangar ready kspstuff-hop-valiant-east-t3-pbc sit=VesselSituation.pre_launch parts=32
  hop apo=18000
  hop-to-water slew pitch 25° east after pad (throttle 0.4), hold through burnout, wait splash
  hop light
  hop airborne
  hop-to-water slew pitch east after pad throttle=0.4
  science skip kerbalism_TELEMETRY on probeCoreSphere.v2 (not in card)
  science skip temperatureScan on probeCoreSphere.v2 (not in card)
  science skip seismicScan on probeCoreSphere.v2 (not in card)
  science skip geigerCounter on probeCoreSphere.v2 (not in card)
  science skip kerbalism_LITE on probeCoreSphere.v2 (not in card)
  science skip kerbalism_MITE on probeCoreSphere.v2 (not in card)
  science skip kerbalism_SITE on probeCoreSphere.v2 (not in card)
  science skip telemetryReport on probeCoreSphere.v2 (not in card)
  science skip mysteryGoo on GooExperiment (not in card)
  science skip temperatureScan on sensorThermometer (not in card)
  hop-to-water pitch 25° east
  hop-to-water hold east through burnout
  hop-to-water splash
  splash wait water
  gate ec=0
  splash down
  science skip (no Experiment modules)
  science keep kerbalism_TELEMETRY (already started or HD)
  science dwell
  pad unpause
  wait science none met=212.2 ut=228427.9 sit=splashed ec=0
  gate ec=0
  science dwell ec=0 splash
  pad physics 1x
  science skip (no Experiment modules)
  ABORT no science (wanted mysteryGoo)

```

## Learn

_Gene fills this. What worked, what failed, what to change in
the library vs this pilot's style. One short paragraph._
