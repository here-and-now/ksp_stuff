# Review 2026-08-22T10-11-27Z-hop-to-water

command: hop-to-water
exit: 2
abort: no science (wanted mysteryGoo)
log: docs/missions/jebediah/logs/2026-08-22T10-11-27Z-hop-to-water.jsonl
earth: 2026-08-22 10:11:27 UTC
kerbal_ut: 2d 16:36:45 UT
kerbal_met: MET 2d 16:36:45
samples: 107 (~1 Hz)
duration: 230.9 s wall
bodies: Earth
tags: {}

## Envelope

- alt min -0.0
- peri min -6363161.7
- apo max 18946.3
- met max 214.3
- EC 2009.9 → 0.0 (min 0.0)
- fuel 675.0 → 0.0 (min 0.0)
- LF 675.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 3}

## First / last

- Earth pre_launch alt=84.31540123093873 peri=-6362518.496374856 apo=84.31540022976696 met=0.0 ec=2009.903076171875 fuel=675.0 warp=Nonex
- Earth splashed alt=-0.023064058274030685 peri=-6362435.57660048 apo=197.70737919583917 met=214.29999988773488 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+230s  ec=0

## Events

- T+0s start command=hop-to-water crew=
- T+230s landing landing: hard impact=62 m/s heading=305 sit=splashed
- T+230s landing landing: hard impact=62 m/s heading=305 sit=splashed
- T+231s landing landing: hard impact=62 m/s heading=305 sit=splashed
- T+231s end samples=111

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
  hop-to-water splash
  splash wait water
  gate ec=0
  splash down
  science skip (no Experiment modules)
  science keep kerbalism_TELEMETRY (already started or HD)
  science dwell
  pad unpause
  wait science none met=214.3 ut=232042.7 sit=splashed ec=0
  gate ec=0
  science dwell ec=0 splash
  pad physics 1x
  science skip (no Experiment modules)
  ABORT no science (wanted mysteryGoo)

```

## Learn

Latch held: MET **79.4** thr **0** leftover **108.7** apo **18.95 km**. Envelope heading **never 090** (pad **298.9**, burn **301.1**, splash **304.6**; 080–100 fly-through MET **86.0** hdg **93.4** and MET **93.0** hdg **86.6**) splash horiz **2.00** pitch **81.7** (horiz max **152.1** at hop_apo; 0.4 pitch reached **65.5**). Suicide 1 Hz **never thr=1** after pad-light (only MET **1.14** thr 1). MET **176.1** thr **0** leftover **108.7** vz **−223** alt **2415** heading **292** horiz **21.6** speed **224**. Gap MET **176→209** dumped **108.7→crumbs 1.98**. MET **208.9** thr **0** fuel **1.98** speed **9.2** vz **−9.4** alt **195**, then rebuild **−23/−35/−48/−61**. Splash MET **214.3** sit=splashed Shores speed **62.3** landing hard **62 m/s**. sci **13.26 Δ0**. Modules gone wanted mysteryGoo. T-045 slam/cut at vz ≥ −10 spent the leftover; T-046/T-047 **TWR≈1 hover until coast ≤ Goo 12** — no slam 1, no drop-out at the cut. Crumbs not a relight. T-016 heading hardware. Os: fly the hover.
