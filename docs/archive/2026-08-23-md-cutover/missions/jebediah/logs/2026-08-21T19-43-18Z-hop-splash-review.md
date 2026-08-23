# Review 2026-08-21T19-43-18Z-hop-splash

command: hop-splash
exit: 2
abort: ec=0
log: docs/missions/jebediah/logs/2026-08-21T19-43-18Z-hop-splash.jsonl
earth: 2026-08-21 19:43:18 UTC
kerbal_ut: 2d 15:04:44 UT
kerbal_met: ?
samples: 189 (~1 Hz)
duration: 504.5 s wall
bodies: Earth
tags: {}

## Envelope

- alt min -0.2
- peri min -6365163.6
- apo max 98345.8
- met max 487.1
- EC 2409.9 → 0.0 (min 0.0)
- fuel 1575.0 → 0.0 (min 0.0)
- LF 1575.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 3}

## First / last

- Earth pre_launch alt=85.65017396118492 peri=-6362518.488865613 apo=85.65017300099134 met=0.0 ec=2409.904052734375 fuel=1575.0 warp=Nonex
- Earth splashed alt=-0.17324273101985455 peri=-6364870.195972306 apo=202.63022440113127 met=487.0599997448444 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+504s  ec=0

## Events

- T+0s start command=hop-splash crew=
- T+505s end samples=190

## Handoff

```
command: hop-splash
exit: 2
abort: ec=0
last:
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
  science keep kerbalism_TELEMETRY (already started or HD)
  science dwell
  pad unpause
  wait science none met=487.1 ut=227542.6 sit=splashed ec=0
  gate ec=0
  pad physics 1x
  ABORT ec=0

```

## Learn

Hangar t7 + vertical loft **worked** (apo **98.3 km**, splash MET **487**, Shores). Envelope **heading 19 horiz 62 pitch 13** — pad **299**, never 090 (vertical brief, not Water-dead). TELEMETRY **started airborne T+1** against brief. At splash: skip modules=0, keep TELEMETRY, **wait science none**, **ABORT ec=0**. goo never. desk **13.26 Δ0**. Need **~1.74**. 24×Z-100 still died loft. T-006 Lars: dwell at EC=0; first Toggle **splashed**. Do not re-fly. Do not Hangar. leftover n=0.
