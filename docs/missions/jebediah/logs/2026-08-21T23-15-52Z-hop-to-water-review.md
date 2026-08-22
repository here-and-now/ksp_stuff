# Review 2026-08-21T23-15-52Z-hop-to-water

command: hop-to-water
exit: 2
abort: no science (wanted mysteryGoo)
log: docs/missions/jebediah/logs/2026-08-21T23-15-52Z-hop-to-water.jsonl
earth: 2026-08-21 23:15:52 UTC
kerbal_ut: 2d 15:32:16 UT
kerbal_met: MET 0d 00:03:46
samples: 127 (~1 Hz)
duration: 256.9 s wall
bodies: Earth
tags: {}

## Envelope

- alt min -1.6
- peri min -6363829.0
- apo max 18685.7
- met max 225.0
- EC 2009.9 → 0.0 (min 0.0)
- fuel 675.0 → 0.0 (min 0.0)
- LF 675.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 3}

## First / last

- Earth pre_launch alt=84.32102047093213 peri=-6362518.405687444 apo=84.32101888768375 met=0.0 ec=2009.905029296875 fuel=675.0 warp=Nonex
- Earth splashed alt=-1.6273994436487556 peri=-6361714.844727738 apo=2470.232232943177 met=224.9999998821295 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+256s  ec=0

## Events

- T+0s start command=hop-to-water crew=
- T+256s landing landing: catastrophic impact=220 m/s heading=304 sit=splashed
- T+257s landing landing: catastrophic impact=220 m/s heading=304 sit=splashed
- T+257s landing landing: catastrophic impact=220 m/s heading=304 sit=splashed
- T+257s end samples=131

## Handoff

```
command: hop-to-water
exit: 2
abort: no science (wanted mysteryGoo)
last:
  hop leftover wreck sit=splashed recoverable=yes experiments=0 — recover, Hangar new
  recovered leftover wreck
  hop recover still listed after recover()
  hangar ready kspstuff-hop-valiant-east-t3-pbc sit=VesselSituation.pre_launch parts=32
  hop apo=18000
  hop-to-water slew pitch 25° east after pad (throttle 0.4), hold through burnout, wait splash
  hop light
  hop airborne
  hop-to-water slew pitch east after pad throttle=0.4
  science skip kerbalism_TELEMETRY on probeCoreSphere.v2 (not in card)
  science skip temperatureScan on probeCoreSphere.v2 (not in card)
  science skip seismicScan on probeCoreSphere.v2 (not in card)
  science skip geigerCounter on probeCoreSphere.v2 (not in card)
  science skip kerbalism_LITE on probeCoreSphere.v2 (not in card)
  science skip kerbalism_MITE on probeCoreSphere.v2 (not in card)
  science skip kerbalism_SITE on probeCoreSphere.v2 (not in card)
  science skip telemetryReport on probeCoreSphere.v2 (not in card)
  science skip mysteryGoo on GooExperiment (not in card)
  science skip temperatureScan on sensorThermometer (not in card)
  hop-to-water pitch 25° east
  hop-to-water suicide leftover LF
  hop-to-water splash
  splash wait water
  gate ec=0
  splash down
  science skip (no Experiment modules)
  science keep kerbalism_TELEMETRY (already started or HD)
  science dwell
  pad unpause
  wait science none met=225.0 ut=228966.1 sit=splashed ec=0
  gate ec=0
  science dwell ec=0 splash
  pad physics 1x
  science skip (no Experiment modules)
  ABORT no science (wanted mysteryGoo)

```

## Learn

Latch **held**. MET **79.1** thr **0** fuel **111.1** apo **18.7 km**. Envelope heading **never 090** (pad **299**, burn **300**, splash **304**; three 080–100 fly-throughs, not a hold) horiz **24.3** vs briefed **090**. Suicide **in**: MET **171** thr **1** vz **−194**; held through vz **−65**; still thr **1** at vz **+24.5** fuel **47**; recut MET **176.5** vz **+140** leftover **16.6**. Relight MET **208.9** vz **−126** fuel **11.5**. Splash MET **225** sit=splashed biome **Shores** impact **220 m/s** heading **304** horiz **24.3**. sci **13.26 Δ0**. science skip no Experiment modules. Overburn past −20 then leftover crumbs lofted. T-024 **in** (cut when vz ≥ −20 **seen**). T-016 hardware.
