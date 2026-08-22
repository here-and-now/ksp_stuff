# Review 2026-08-22T09-48-51Z-hop-to-water

command: hop-to-water
exit: 2
abort: no science (wanted mysteryGoo)
log: docs/missions/jebediah/logs/2026-08-22T09-48-51Z-hop-to-water.jsonl
earth: 2026-08-22 09:48:51 UTC
kerbal_ut: 2d 16:48:44 UT
kerbal_met: MET 2d 16:48:44
samples: 138 (~1 Hz)
duration: 228.9 s wall
bodies: Earth
tags: {}

## Envelope

- alt min -1.0
- peri min -6363260.9
- apo max 18728.2
- met max 212.7
- EC 2009.9 → 0.0 (min 0.0)
- fuel 675.0 → 0.0 (min 0.0)
- LF 675.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 3}

## First / last

- Earth pre_launch alt=84.09152649156749 peri=-6362518.0470529245 apo=84.09152172785252 met=0.0 ec=2009.904052734375 fuel=675.0 warp=Nonex
- Earth splashed alt=-1.0260547790676355 peri=-6362205.827888954 apo=433.07571360003203 met=212.65999988859403 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+228s  ec=0

## Events

- T+0s start command=hop-to-water crew=
- T+228s landing landing: hard impact=92 m/s heading=296 sit=splashed
- T+228s landing landing: hard impact=92 m/s heading=296 sit=splashed
- T+229s landing landing: hard impact=92 m/s heading=296 sit=splashed
- T+229s end samples=142

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
  wait science none met=212.7 ut=231808.4 sit=splashed ec=0
  gate ec=0
  science dwell ec=0 splash
  pad physics 1x
  science skip (no Experiment modules)
  ABORT no science (wanted mysteryGoo)

```

## Learn

Latch **held**. MET **79.2** thr **0** leftover **110.1** apo **18.73 km**. Envelope heading **never 090** (pad **298.9**, burn **300.5**, splash **296.0**; one 080–100 fly-through MET **85.4** hdg **99.6**, not a hold) horiz **7.66** pitch **85.4** vs briefed **090**. Suicide 1 Hz **never thr=1** (only pad light MET **1.1**): MET **175.3** thr **0** fuel **110.1** vz **−223** alt **2378**; recut MET **180.4** leftover **50.4** vz **−7.7** alt **1675** then coast vz **−107**; pulse leftover **20.7** MET **193.9** vz **−5.2**; **4.0** MET **201.7**; crumbs **0.6** MET **207.3** vz **−43**. 20 Hz gate burned 110→50 between samples **before** armed latched — T-040 hover never lit. Splash MET **212.7** sit=splashed biome **Shores** speed **92.5** (landing class **82** vz last flying MET **211.7**) heading **296** horiz **7.66**. sci **13.26 Δ0**. science skip no Experiment modules — goo died, wanted mysteryGoo. T-045 **done**: watch TTI **≤12**, light live TTI **≤3.5**, latch armed even if the gate cuts, hover when vz **< −10** without another TTI wait. Leftover spent only if coast **≤** Goo **12**. T-016 heading 296 is hardware. T-041 **capable: yes**. Os: fly the patch. hangar none leftover n=0. `campaign: uncrewed`. `go: yes`.
