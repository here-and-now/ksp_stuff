# Review 2026-08-21T19-21-40Z-hop-splash

command: hop-splash
exit: 2
abort: not splashed
log: docs/missions/jebediah/logs/2026-08-21T19-21-40Z-hop-splash.jsonl
earth: 2026-08-21 19:21:40 UTC
kerbal_ut: 2d 14:44:16 UT
kerbal_met: MET 0d 00:07:07
samples: 12 (~1 Hz)
duration: 35.4 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 23.1
- peri min -6364755.6
- apo max 2620.7
- met max 462.4
- EC 2401.9 → 2000.9 (min 2000.9)
- fuel 1.2 → 0.5 (min 0.5)
- LF 1.2 → 0.5 (min 0.5)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {}

## First / last

- Earth flying alt=2313.3833843767643 peri=-6359432.915757126 apo=2620.6506981747225 met=428.03999977576314 ec=2401.8994140625 fuel=1.2471249103546143 warp=Nonex
- Earth landed alt=23.080939293839037 peri=-6362379.91384474 apo=23.349366119131446 met=462.3799997577735 ec=2000.8719482421875 fuel=0.5344821214675903 warp=Nonex

## Flag changes

- (none)

## Events

- T+0s start command=hop-splash crew=
- T+36s end samples=13

## Handoff

```
command: hop-splash
exit: 2
abort: not splashed
last:
  hop apo=80000
  hop-splash light vertical, no flying Toggle, wait splash
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
  ABORT not splashed

```

## Learn

Leftover **flying Forest** entered Flight — no Hangar. Landed **23 m Forest** MET **462**. Envelope **heading 14 horiz 6 pitch 8**. TELEMETRY airborne. abort **not splashed**. **+0**.
