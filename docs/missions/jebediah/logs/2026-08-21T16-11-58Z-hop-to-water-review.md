# Review 2026-08-21T16-11-58Z-hop-to-water

command: hop-to-water
exit: 2
abort: not splashed
log: docs/missions/jebediah/logs/2026-08-21T16-11-58Z-hop-to-water.jsonl
earth: 2026-08-21 16:11:58 UTC
kerbal_ut: 2d 12:57:48 UT
kerbal_met: ?
samples: 39 (~1 Hz)
duration: 67.4 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 71.5
- peri min -6362518.3
- apo max 5296.3
- met max 54.8
- EC 309.9 → 0.0 (min 0.0)
- fuel 450.0 → 0.0 (min 0.0)
- LF 450.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 1}

## First / last

- Earth pre_launch alt=84.33649306744337 peri=-6362518.349157858 apo=84.33646872173995 met=0.0 ec=309.9040832519531 fuel=450.0 warp=Nonex
- Earth landed alt=71.494603051804 peri=-6361801.121215464 apo=988.9792602099478 met=54.77999997130246 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+67s  ec=0

## Events

- T+0s start command=hop-to-water crew=
- T+117s end samples=40

## Handoff

```
command: hop-to-water
exit: 2
abort: not splashed
last:
  hangar ready kspstuff-hop-valiant-east-bare-pbc sit=VesselSituation.pre_launch parts=12
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
  hop-to-water hold east through burnout
  ABORT not splashed

```

## Learn

16-11-58Z hop-to-water abort +0. Hangar **east-bare** ok. Slam AP
`target_pitch=65` at light, TWR ~5, no decoupler, Stayputnik no wheel:
joints sheared. Kero 276→0 in ~1.5 s MET **11.7** q≈39 kPa — dump, not
burnout. Apo **5.3 km** (prior hops 10–12). jsonl `speed` always 0.
T+54 `sit=landed` Shores alt **71** EC=0 crash UI, never splash. Card
started; no HD. Envelope vs expect: Earth, apo 5.3 km < 50 km, peri
ballistic. Os: shear. Next: unmatched leftover recover without lighting,
Hangar **east-one**. Light **vertical**; after `left_pad` slew **10°/s**
to 65 at throttle **0.4**; hold AP through burnout. Do not light
east-bare or the finned hang.
