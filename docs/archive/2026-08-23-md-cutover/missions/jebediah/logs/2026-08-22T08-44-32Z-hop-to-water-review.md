# Review 2026-08-22T08-44-32Z-hop-to-water

command: hop-to-water
exit: 2
abort: no science (wanted mysteryGoo)
log: docs/missions/jebediah/logs/2026-08-22T08-44-32Z-hop-to-water.jsonl
earth: 2026-08-22 08:44:32 UTC
kerbal_ut: 2d 16:12:53 UT
kerbal_met: ?
samples: 147 (~1 Hz)
duration: 235.4 s wall
bodies: Earth
tags: {}

## Envelope

- alt min -1.0
- peri min -6363154.4
- apo max 18477.6
- met max 218.4
- EC 2009.9 → 0.0 (min 0.0)
- fuel 675.0 → 0.0 (min 0.0)
- LF 675.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 3}

## First / last

- Earth pre_launch alt=84.1493228180334 peri=-6362518.6128707025 apo=84.14929169137031 met=0.0 ec=2009.903076171875 fuel=675.0 warp=Nonex
- Earth splashed alt=-1.0095816673710942 peri=-6361933.770855541 apo=717.2940200278535 met=218.35999988560798 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+234s  ec=0

## Events

- T+0s start command=hop-to-water crew=
- T+234s landing landing: catastrophic impact=119 m/s heading=298 sit=splashed
- T+235s landing landing: catastrophic impact=119 m/s heading=298 sit=splashed
- T+235s landing landing: catastrophic impact=119 m/s heading=298 sit=splashed
- T+235s end samples=151

## Handoff

```
command: hop-to-water
exit: 2
abort: no science (wanted mysteryGoo)
last:
  hangar ready kspstuff-hop-valiant-east-t3-pbc sit=VesselSituation.pre_launch parts=32
  hop apo=18000
  hop-to-water slew pitch 25° east after pad (throttle 0.4), hold through burnout, wait splash
  hop light
  hop airborne
  hop-to-water slew pitch east after pad throttle=0.4
  science wait FlyingHigh
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
  wait science none met=218.4 ut=231083.1 sit=splashed ec=0
  gate ec=0
  science dwell ec=0 splash
  pad physics 1x
  science skip (no Experiment modules)
  ABORT no science (wanted mysteryGoo)

```

## Learn

Latch **held**. MET **78.6** thr **0** fuel **114.2** apo **18.48 km**. Envelope heading **never 090** (pad **298.9**, burn **300.6**, splash **298.0**; 080–100 fly-throughs MET **86.2** / **92.1** / **197.2**, not a hold) horiz **17.9** vs briefed **090**. Suicide **in**: MET **174.9** thr **1** vz **−209.5**; MET **176.5** vz **−113** still thr 1; **recut MET 178.0 thr 0 vz −29.9 leftover 60.6** (predictor cut before vz ≥ −20 seen). Relight MET **187.2** vz **−103**; overburn MET **188.9** vz **+2.7** leftover **30.3** then loft vz **+85**. Crumb slam MET **209.6** fuel **6.1**. Splash MET **218.4** sit=splashed biome **Shores** impact **119 m/s** speed **120** heading **298** horiz **17.9**. sci **13.26 Δ0**. science skip no Experiment modules — wreck-class, not start_experiments. T-031 **in**: hold until vz ≥ −20 **seen**, 20 Hz gate, crumbs not a relight. T-016 heading 298 is hardware. Os: fly the patch.
