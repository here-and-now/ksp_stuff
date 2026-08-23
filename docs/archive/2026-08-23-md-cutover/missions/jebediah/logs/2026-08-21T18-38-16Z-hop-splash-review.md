# Review 2026-08-21T18-38-16Z-hop-splash

command: hop-splash
exit: 2
abort: no science (wanted kerbalism_TELEMETRY)
log: docs/missions/jebediah/logs/2026-08-21T18-38-16Z-hop-splash.jsonl
earth: 2026-08-21 18:38:16 UTC
kerbal_ut: 2d 14:22:16 UT
kerbal_met: MET 0d 00:08:05
samples: 140 (~1 Hz)
duration: 385.8 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 0.0
- peri min -6366158.9
- apo max 88361.2
- met max 353.1
- EC 2409.9 → 0.0 (min 0.0)
- fuel 1575.0 → 0.0 (min 0.0)
- LF 1575.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 2}

## First / last

- Earth pre_launch alt=85.84101639781147 peri=-6362518.366081829 apo=85.84101674053818 met=0.0 ec=2409.904052734375 fuel=1575.0 warp=Nonex
- Earth splashed alt=0.012876071967184544 peri=-6363134.708560105 apo=145.1078596347943 met=353.1199998150114 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+385s  ec=0

## Events

- T+0s start command=hop-splash crew=
- T+386s end samples=141

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
  science skip temperatureScan on probeCoreSphere.v2 (not in card)
  science skip seismicScan on probeCoreSphere.v2 (not in card)
  science skip geigerCounter on probeCoreSphere.v2 (not in card)
  science skip kerbalism_LITE on probeCoreSphere.v2 (not in card)
  science skip kerbalism_MITE on probeCoreSphere.v2 (not in card)
  science skip kerbalism_SITE on probeCoreSphere.v2 (not in card)
  science skip telemetryReport on probeCoreSphere.v2 (not in card)
  science skip mysteryGoo on GooExperiment (not in card)
  science skip temperatureScan on sensorThermometer (not in card)
  science skip geigerCounter on kerbalism-geigercounter (not in card)
  science start kerbalism_TELEMETRY
  science kerbalism_TELEMETRY
  hop-splash splash
  splash wait water
  gate ec=0
  splash down
  science skip (no Experiment modules)
  ABORT no science (wanted kerbalism_TELEMETRY)

```

## Learn

Hangar t7 vertical. Splash **Shores** MET **353** apo **88.4 km** EC=0. Envelope **heading 211 horiz 63 pitch 3.5**. TELEMETRY **airborne** then skip modules=0, abort **no science TELEMETRY**. goo never. **+0**.
