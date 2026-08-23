# Review 2026-08-22T09-11-59Z-hop-to-water

command: hop-to-water
exit: 2
abort: no science (wanted mysteryGoo)
log: docs/missions/jebediah/logs/2026-08-22T09-11-59Z-hop-to-water.jsonl
earth: 2026-08-22 09:11:59 UTC
kerbal_ut: 2d 16:30:22 UT
kerbal_met: ?
samples: 137 (~1 Hz)
duration: 228.1 s wall
bodies: Earth
tags: {}

## Envelope

- alt min -0.8
- peri min -6362813.0
- apo max 18518.2
- met max 211.8
- EC 2009.9 → 0.0 (min 0.0)
- fuel 675.0 → 0.0 (min 0.0)
- LF 675.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 3}

## First / last

- Earth pre_launch alt=84.17806131020188 peri=-6362518.497772609 apo=84.17806001845747 met=0.0 ec=2009.904052734375 fuel=675.0 warp=Nonex
- Earth splashed alt=-0.8065027045086026 peri=-6362586.335339332 apo=343.27094411477447 met=211.79999988904456 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+227s  ec=0

## Events

- T+0s start command=hop-to-water crew=
- T+227s landing landing: hard impact=82 m/s heading=299 sit=splashed
- T+228s landing landing: hard impact=82 m/s heading=299 sit=splashed
- T+228s landing landing: hard impact=82 m/s heading=299 sit=splashed
- T+228s end samples=141

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
  wait science none met=211.8 ut=231531.1 sit=splashed ec=0
  gate ec=0
  science dwell ec=0 splash
  pad physics 1x
  science skip (no Experiment modules)
  ABORT no science (wanted mysteryGoo)

```

## Learn

Latch **held**. MET **78.6** thr **0** leftover **114.1** apo **18.52 km**. Envelope heading **never 090** (pad **298.9**, burn **300.4**, splash **299.0**; one 080–100 fly-through MET **92.6** hdg **96**, not a hold) horiz **2.2** vs briefed **090**. Suicide **seen-vz in**: 1 Hz unseen MET **174.4** thr **0** fuel **114** vz **−222**; recut MET **179.2** thr **0** vz **−19.3 leftover 57**. Then **pulse-relight** MET **191.7** fuel **28.8** vz **−13.7**; **199.0** fuel **13.8** vz **−16.2**; **205.2** crumbs **1.2** vz **−16.8**. No 1 Hz thr=1. Splash MET **211.8** sit=splashed biome **Shores** speed **82** (landing class **67** vz) heading **299** horiz **2.2** pitch **87.1**. sci **13.26 Δ0**. science skip no Experiment modules — goo died, wanted mysteryGoo. T-033 spent-latch **superseded** by T-040: leftover 57 coasts ~186 if not hover-slam (Goo crashTolerance **12**; no chute). T-016 heading 299 is hardware. T-035 **done** `capable: no` vs 82 m/s tape still honest. T-041 **capable: yes** east-t3 suicide test hang. Os: fly the patch. hangar none leftover n=0. `campaign: uncrewed`. `go: yes`.
