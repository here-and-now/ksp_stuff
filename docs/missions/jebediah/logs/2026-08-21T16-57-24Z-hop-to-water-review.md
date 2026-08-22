# Review 2026-08-21T16-57-24Z-hop-to-water

command: hop-to-water
exit: 2
abort: not recoverable
log: docs/missions/jebediah/logs/2026-08-21T16-57-24Z-hop-to-water.jsonl
earth: 2026-08-21 16:57:24 UTC
kerbal_ut: 2d 13:29:18 UT
kerbal_met: ?
samples: 69 (~1 Hz)
duration: 115.0 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 70.5
- peri min -6363682.5
- apo max 3659.9
- met max 89.6
- EC 109.9 → 0.0 (min 0.0)
- fuel 450.0 → 0.0 (min 0.0)
- LF 450.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'empty tanks': 29, 'ec=0': 11}

## First / last

- Earth pre_launch alt=84.2212884677574 peri=-6362518.4588458575 apo=84.22128697764128 met=0.0 ec=109.90509796142578 fuel=450.0 warp=Nonex
- Earth flying alt=70.47838971670717 peri=-6361911.3499779515 apo=2371.0016216356307 met=89.63999995304039 ec=0.0 fuel=0.0 warp=Nonex [ec=0 empty tanks]

## Flag changes

- T+76s  empty tanks
- T+103s  ec=0 empty tanks

## Events

- T+0s start command=hop-to-water crew=
- T+160s end samples=70

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
  hop recover sit=flying recoverable=no
  gate ec=0
  hop down
  hop recover sit=flying recoverable=no
  hop crash ui sit=flying recoverable=no met=89.64 alt=70.5 q=0
  hop unpause
  gate ec=0
  gate ec=0
  gate ec=0
  gate ec=0
  gate ec=0
  ABORT not recoverable

```

## Learn

Tape is honest (body-frame speed/horiz/heading). East program is not.
Hangar **east-fin**, lit vertical, slew 0.4 after left_pad. Heading
**never holds 090** (pad 299, tumble 144/273/301…, five fly-throughs
±15°, impact 299 horiz 14). apo **3.66 km**, horiz max **85.6**,
burnout MET~62.8, lithobrake MET **89.64** alt 70.5 flying
recoverable=no EC=0 q=0 never splash. sci **+0**. 3× basicFin on the
lower tank did not fly east. Stayputnik has no wheel; **stability
LOCKED**. leftover PRELAUNCH east-fin after Close is a **ghost pad
reload** — do not light, do not Hangar, do not revert. Water is dead
on this hang. Not a pitch number. Not more fins. Bank 10.96. Need
~4.04. need_builder + need_science. `go: wait`.
