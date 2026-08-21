# Review 2026-08-21T15-26-18Z-hop-to-water

command: hop-to-water
exit: 2
abort: not recoverable
log: docs/missions/jebediah/logs/2026-08-21T15-26-18Z-hop-to-water.jsonl
earth: 2026-08-21 15:26:18 UTC
kerbal_ut: 2d 12:39:26 UT
kerbal_met: ?
samples: 79 (~1 Hz)
duration: 125.8 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 28.5
- peri min -6362518.2
- apo max 10003.5
- met max 100.4
- EC 309.9 → 9.9 (min 9.9)
- fuel 450.0 → 0.0 (min 0.0)
- LF 450.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {}

## First / last

- Earth pre_launch alt=83.80684202816337 peri=-6362518.239136932 apo=83.80682498030365 met=0.0 ec=309.9040832519531 fuel=450.0 warp=Nonex
- Earth flying alt=28.500490020029247 peri=-6362459.992146066 apo=960.14729369618 met=100.39999994740356 ec=9.877701759338379 fuel=0.0 warp=Nonex

## Flag changes

- (none)

## Events

- T+0s start command=hop-to-water crew=
- T+177s end samples=80

## Handoff

```
command: hop-to-water
exit: 2
abort: not recoverable
last:
  hangar ready kspstuff-hop-valiant-east-pbc sit=VesselSituation.pre_launch parts=15
  hop apo=18000
  hop-to-water pitch 25° east, wait splash
  hop light
  hop-to-water pitch 25° east
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
  hop crash ui sit=flying recoverable=no met=100.40 alt=28.5 q=0
  hop unpause
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  ABORT not recoverable

```

## Learn

25° was a command, not a path. Hangar east-pbc ok; lit wet PRELAUNCH.
Pitch 25 heading 90 logged; T+2 HDG 090 horiz ~21–27 m/s. Burnout
MET~27 fuel=0 apo **10.0 km**. After cutoff Stayputnik had no torque:
T+63 Shores HDG **304**, lithobrake MET **100** alt **28.5** flying
recoverable=no q=0. Never splashed. Thermo+TELEMETRY started; no HD
recover. sci **10.96 (+0)**. jsonl `speed=0` all samples — heading is
note-tech, not the file. Lars now holds AP `target_pitch=65` heading
90 through burnout (surface frame, `engaged=True`); release when down.
leftover matching **PRELAUNCH** east-pbc — light, do not Hangar. If the
next hop still ~25 m/s east, that is tanks/gimbal vs FAR, not the pitch
number.
