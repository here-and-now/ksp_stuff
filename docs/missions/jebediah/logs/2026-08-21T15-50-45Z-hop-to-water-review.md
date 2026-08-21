# Review 2026-08-21T15-50-45Z-hop-to-water

command: hop-to-water
exit: 2
abort: not splashed
log: docs/missions/jebediah/logs/2026-08-21T15-50-45Z-hop-to-water.jsonl
earth: 2026-08-21 15:50:45 UTC
kerbal_ut: 2d 12:47:32 UT
kerbal_met: ?
samples: 104 (~1 Hz)
duration: 158.6 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 78.3
- peri min -6364400.7
- apo max 10338.7
- met max 148.3
- EC 279.8 → 0.0 (min 0.0)
- fuel 450.0 → 0.0 (min 0.0)
- LF 450.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 1}

## First / last

- Earth pre_launch alt=84.5054513933137 peri=-6362518.484329566 apo=84.5054519791156 met=0.0 ec=279.76434326171875 fuel=450.0 warp=Nonex
- Earth landed alt=78.34921785350889 peri=-6363018.894530506 apo=78.4135593380779 met=148.29999992231023 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+159s  ec=0

## Events

- T+0s start command=hop-to-water crew=
- T+208s end samples=105

## Handoff

```
command: hop-to-water
exit: 2
abort: not splashed
last:
  hop enter flight (space_center)
  hop apo=18000
  hop-to-water pitch 25° east, hold through burnout, wait splash
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
  ABORT not splashed

```

## Learn

15-50-45Z hop-to-water abort +0. Matching leftover **east-pbc** wet
PRELAUNCH, lit (no Hangar). AP **held through burnout**: T+2 HDG 090
horiz ~20 m/s, burnout MET~27 fuel=0 apo **10.3 km**. After cutoff
fins+FAR weathercocked HDG 090→290, horiz **44 m/s**, lithobrake
Shores MET 148 alt 78 KSC roads, never splash. Thermo+TELEMETRY
started; no HD. Envelope vs expect: Earth, peri ballistic, apo
10.3 km < 50 km. Yeet was Restock **ModuleJettison** + fins on the
engine, not a stack decoupler. 25° hold is not a bigger pitch
number. Next: unmatched leftover recover without lighting, Hangar
**east-bare**. Do not light the finned hang.
