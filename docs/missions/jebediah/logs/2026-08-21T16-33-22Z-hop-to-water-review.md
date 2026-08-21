# Review 2026-08-21T16-33-22Z-hop-to-water

command: hop-to-water
exit: 2
abort: not recoverable
log: docs/missions/jebediah/logs/2026-08-21T16-33-22Z-hop-to-water.jsonl
earth: 2026-08-21 16:33:22 UTC
kerbal_ut: 2d 13:13:38 UT
kerbal_met: ?
samples: 77 (~1 Hz)
duration: 119.0 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 60.1
- peri min -6364225.9
- apo max 4554.2
- met max 97.5
- EC 90.9 → 0.0 (min 0.0)
- fuel 450.0 → 0.0 (min 0.0)
- LF 450.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 11, 'empty tanks': 11}

## First / last

- Earth pre_launch alt=84.31528161279857 peri=-6362518.481565978 apo=84.31528159696609 met=0.0 ec=90.85893249511719 fuel=450.0 warp=Nonex
- Earth flying alt=60.14611416589469 peri=-6361529.130850481 apo=2329.251280452125 met=97.5199999489123 ec=0.0 fuel=0.0 warp=Nonex [ec=0 empty tanks]

## Flag changes

- T+107s  ec=0 empty tanks

## Events

- T+0s start command=hop-to-water crew=
- T+168s end samples=78

## Handoff

```
command: hop-to-water
exit: 2
abort: not recoverable
last:
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
  gate ec=0
  hop ec=0 wait splash
  hop-to-water hold east through burnout
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
  hop crash ui sit=flying recoverable=no met=97.52 alt=60.1 q=0
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
