# Review 2026-08-21T19-04-15Z-hop-splash

command: hop-splash
exit: 2
abort: not splashed
log: docs/missions/jebediah/logs/2026-08-21T19-04-15Z-hop-splash.jsonl
earth: 2026-08-21 19:04:15 UTC
kerbal_ut: 2d 14:36:04 UT
kerbal_met: MET 0d 00:05:41
samples: 193 (~1 Hz)
duration: 525.9 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 81.2
- peri min -6366390.1
- apo max 100047.6
- met max 492.9
- EC 2409.9 → 2301.3 (min 2301.3)
- fuel 1575.0 → 0.7 (min 0.7)
- LF 1575.0 → 0.7 (min 0.7)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {}

## First / last

- Earth pre_launch alt=85.58670531027019 peri=-6362518.629663557 apo=85.58670463413 met=0.0 ec=2409.904052734375 fuel=1575.0 warp=Nonex
- Earth landed alt=81.16551478113979 peri=-6361622.462219546 apo=82.07968298532069 met=492.93999974176404 ec=2301.33740234375 fuel=0.6806601285934448 warp=Nonex

## Flag changes

- (none)

## Events

- T+0s start command=hop-splash crew=
- T+528s end samples=194

## Handoff

```
command: hop-splash
exit: 2
abort: not splashed
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
  hop crash ui tracking (not pad reload)
  ABORT not splashed

```

## Learn

Hangar t7 vertical. Landed **Shores 81 m** MET **493** EC **2301** (did not die). Envelope **heading 245 horiz 23 pitch 31**. TELEMETRY airborne. abort **not splashed** (crash UI Tracking). **+0**. Not Water.
