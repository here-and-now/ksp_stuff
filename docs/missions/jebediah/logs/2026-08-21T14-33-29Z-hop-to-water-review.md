# Review 2026-08-21T14-33-29Z-hop-to-water

command: hop-to-water
exit: 2
abort: not recoverable
log: docs/missions/jebediah/logs/2026-08-21T14-33-29Z-hop-to-water.jsonl
earth: 2026-08-21 14:33:29 UTC
kerbal_ut: 2d 12:26:11 UT
kerbal_met: ?
samples: 118 (~1 Hz)
duration: 176.1 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 74.5
- peri min -6363891.9
- apo max 12067.8
- met max 154.5
- EC 309.9 → 9.8 (min 9.8)
- fuel 450.0 → 0.0 (min 0.0)
- LF 450.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {}

## First / last

- Earth pre_launch alt=84.69845840334892 peri=-6362518.488755924 apo=84.69845634140074 met=0.0 ec=309.9040832519531 fuel=450.0 warp=Nonex
- Earth flying alt=74.47491811215878 peri=-6363891.9403925575 apo=206.123185175471 met=154.49999991906225 ec=9.7883882522583 fuel=0.0 warp=Nonex

## Flag changes

- (none)

## Events

- T+0s start command=hop-to-water crew=
- T+181s end samples=119

## Handoff

```
command: hop-to-water
exit: 2
abort: not recoverable
last:
  hangar ready kspstuff-hop-valiant-east-pbc sit=VesselSituation.pre_launch parts=15
  hop apo=18000
  hop-to-water pitch 7.5° east, wait splash
  hop light
  hop-to-water pitch 7.5° east
  hop airborne
  science skip seismicScan on probeCoreSphere.v2 (not in card)
  science skip geigerCounter on probeCoreSphere.v2 (not in card)
  science skip kerbalism_LITE on probeCoreSphere.v2 (not in card)
  science skip kerbalism_MITE on probeCoreSphere.v2 (not in card)
  science skip kerbalism_SITE on probeCoreSphere.v2 (not in card)
  science skip telemetryReport on probeCoreSphere.v2 (not in card)
  science skip mysteryGoo on GooExperiment (not in card)
  science skip temperatureScan on probeCoreSphere.v2 (prefer sensorThermometer)
  science skip geigerCounter on kerbalism-geigercounter (not in card)
  science start temperatureScan
  science start kerbalism_TELEMETRY
  science temperatureScan,kerbalism_TELEMETRY
  science dwell
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop down
  hop recover sit=flying recoverable=no
  hop crash ui sit=flying recoverable=no met=154.50 alt=74.5 q=0
  hop unpause
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop dismissed crash ui
  ABORT not recoverable

```

## Learn

14-33-29Z hop-to-water abort. Hangar east-pbc, card started, sci **10.96
(+0)**. Pitch **7.5°** from vertical stayed Shores: apo **12.1 km**
(vertical 13-08-57Z 12.3), horiz ~34 m/s, never `splashed`. Crash UI
flying recoverable=no met=154.50 alt=74.5 q=0; unpause then Close.
Lars: gimbal **7.5°** is authority; burn is **25°** from vertical
(`target_pitch=65` heading 90). leftover **matching PRELAUNCH**
east-pbc — light, do not Hangar, do not recover. Flea still refused.
