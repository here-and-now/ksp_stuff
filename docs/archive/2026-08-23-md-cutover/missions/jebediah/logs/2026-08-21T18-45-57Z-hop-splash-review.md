# Review 2026-08-21T18-45-57Z-hop-splash

command: hop-splash
exit: 2
abort: not recoverable
log: docs/missions/jebediah/logs/2026-08-21T18-45-57Z-hop-splash.jsonl
earth: 2026-08-21 18:45:57 UTC
kerbal_ut: 2d 14:29:13 UT
kerbal_met: MET 0d 00:05:53
samples: 212 (~1 Hz)
duration: 557.9 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 60.2
- peri min -6367680.4
- apo max 92424.2
- met max 514.5
- EC 2409.9 → 0.0 (min 0.0)
- fuel 1575.0 → 0.0 (min 0.0)
- LF 1575.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 10, 'empty tanks': 10}

## First / last

- Earth pre_launch alt=85.84099371731281 peri=-6362518.487251161 apo=85.84099788032472 met=0.0 ec=2409.904052734375 fuel=1575.0 warp=Nonex
- Earth flying alt=60.18191303871572 peri=-6363242.703069832 apo=211.7090969858691 met=514.4799997304799 ec=0.0 fuel=0.0 warp=Nonex [ec=0 empty tanks]

## Flag changes

- T+548s  ec=0 empty tanks

## Events

- T+0s start command=hop-splash crew=
- T+607s end samples=213

## Handoff

```
command: hop-splash
exit: 2
abort: not recoverable
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
  hop crash ui sit=flying recoverable=no met=514.48 alt=60.2 q=0
  hop unpause
  gate ec=0
  gate ec=0
  gate ec=0
  gate ec=0
  gate ec=0
  ABORT not recoverable

```

## Learn

Hangar t7 vertical. Never splashed. Last **flying 60 m Shores** MET **514** EC=0 recoverable=no. Envelope **heading 299 horiz 63 pitch 90**. TELEMETRY airborne. abort **not recoverable**. **+0**. Crash UI Tracking — do not unpause-spam.
