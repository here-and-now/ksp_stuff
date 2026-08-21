# Review 2026-08-21T16-25-47Z-hop-to-water

command: hop-to-water
exit: 2
abort: not recoverable
log: docs/missions/jebediah/logs/2026-08-21T16-25-47Z-hop-to-water.jsonl
earth: 2026-08-21 16:25:47 UTC
kerbal_ut: 2d 13:07:26 UT
kerbal_met: ?
samples: 40 (~1 Hz)
duration: 75.0 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 71.2
- peri min -6364695.1
- apo max 1844.1
- met max 42.0
- EC 109.9 → 0.0 (min 0.0)
- fuel 450.0 → 0.0 (min 0.0)
- LF 450.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 10}

## First / last

- Earth pre_launch alt=84.2792161302641 peri=-6362518.687271877 apo=84.27921834774315 met=0.0 ec=109.90612030029297 fuel=450.0 warp=Nonex
- Earth flying alt=71.18313346803188 peri=-6362777.746766595 apo=1368.2669919505715 met=41.999999977997504 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+65s  ec=0

## Events

- T+0s start command=hop-to-water crew=
- T+124s end samples=41

## Handoff

```
command: hop-to-water
exit: 2
abort: not recoverable
last:
  recovered unmatched leftover sit=pre_launch recoverable=yes
  hangar ready kspstuff-hop-valiant-east-one-pbc sit=VesselSituation.pre_launch parts=8
  hop apo=18000
  hop-to-water slew pitch 25° east after pad (throttle 0.4), hold through burnout, wait splash
  hop light
  hop airborne
  hop-to-water slew pitch east after pad throttle=0.4
  science skip seismicScan on probeCoreSphere.v2 (not in card)
  science skip geigerCounter on probeCoreSphere.v2 (not in card)
  science skip kerbalism_LITE on probeCoreSphere.v2 (not in card)
  science skip kerbalism_MITE on probeCoreSphere.v2 (not in card)
  science skip kerbalism_SITE on probeCoreSphere.v2 (not in card)
  science skip telemetryReport on probeCoreSphere.v2 (not in card)
  science skip temperatureScan on probeCoreSphere.v2 (prefer sensorThermometer)
  science start temperatureScan
  science start kerbalism_TELEMETRY
  science temperatureScan,kerbalism_TELEMETRY
  science dwell
  hop-to-water pitch 25° east
  hop-to-water hold east through burnout
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
  hop down
  hop recover sit=flying recoverable=no
  hop crash ui sit=flying recoverable=no met=42.00 alt=71.2 q=0
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
