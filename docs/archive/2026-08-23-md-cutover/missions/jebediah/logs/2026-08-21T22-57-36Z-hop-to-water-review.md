# Review 2026-08-21T22-57-36Z-hop-to-water

command: hop-to-water
exit: 2
abort: no science (wanted mysteryGoo)
log: docs/missions/jebediah/logs/2026-08-21T22-57-36Z-hop-to-water.jsonl
earth: 2026-08-21 22:57:36 UTC
kerbal_ut: 2d 16:16:23 UT
kerbal_met: MET 0d 00:03:32
samples: 126 (~1 Hz)
duration: 257.1 s wall
bodies: Earth
tags: {}

## Envelope

- alt min -0.7
- peri min -6364811.5
- apo max 18967.6
- met max 226.3
- EC 2009.9 → 0.0 (min 0.0)
- fuel 675.0 → 0.0 (min 0.0)
- LF 675.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 3}

## First / last

- Earth pre_launch alt=84.32101572211832 peri=-6362518.568491349 apo=84.32101497612894 met=0.0 ec=2009.905029296875 fuel=675.0 warp=Nonex
- Earth splashed alt=-0.7103569321334362 peri=-6362292.119425005 apo=790.6709331646562 met=226.3399998814275 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+256s  ec=0

## Events

- T+0s start command=hop-to-water crew=
- T+256s landing landing: catastrophic impact=124 m/s heading=300 sit=splashed
- T+257s landing landing: catastrophic impact=124 m/s heading=300 sit=splashed
- T+257s landing landing: catastrophic impact=124 m/s heading=300 sit=splashed
- T+257s end samples=130

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
  hop-to-water hold east through burnout
  hop-to-water suicide leftover LF
  hop-to-water splash
  splash wait water
  gate ec=0
  splash down
  science skip (no Experiment modules)
  science keep kerbalism_TELEMETRY (already started or HD)
  science dwell
  pad unpause
  wait science none met=226.3 ut=228677.1 sit=splashed ec=0
  gate ec=0
  science dwell ec=0 splash
  pad physics 1x
  science skip (no Experiment modules)
  ABORT no science (wanted mysteryGoo)

```

## Learn

Latch **held**. MET **79.2** thr **0** apo **18.97 km** fuel **109.5** — not the 22-03 recut. Envelope heading **never 090** (pad **299**, burn **300**, splash **300/314**; 080–100 fly-throughs MET **104.7** heading **91.6** and MET **188.5** heading **98.6**, not a hold) horiz **8.1** vs briefed **090** pitch suicide **61→89**. First suicide **in**: MET **179.7** thr **1** alt 1.95 km speed 201; MET **181.6** tti rose vz **−72** still descending; MET **183** thr **0** fuel **46** vz **+19**; relight MET **198.7** lofted leftover. Splash MET **226.3** sit=splashed biome **Shores** impact **119 m/s** heading **314** horiz **8.1** fuel=0 EC=0. sci **13.26 Δ0**. science skip no Experiment modules; ABORT mysteryGoo — same 119 m/s wreck, not start_experiments. TTI-as-cut spent the brake. Next: arm TTI, **hold until vz ≥ −20 or fuel=0**. T-016 heading 301 is hardware. T-023 **in**.
