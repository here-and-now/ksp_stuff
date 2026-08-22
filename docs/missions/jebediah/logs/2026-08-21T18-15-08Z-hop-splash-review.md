# Review 2026-08-21T18-15-08Z-hop-splash

command: hop-splash
exit: 2
abort: no science (wanted kerbalism_TELEMETRY)
log: docs/missions/jebediah/logs/2026-08-21T18-15-08Z-hop-splash.jsonl
earth: 2026-08-21 18:15:08 UTC
kerbal_ut: 2d 14:11:06 UT
kerbal_met: MET 0d 00:08:52
samples: 192 (~1 Hz)
duration: 507.6 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 0.5
- peri min -6369602.3
- apo max 91914.5
- met max 475.2
- EC 2409.9 → 0.0 (min 0.0)
- fuel 1575.0 → 0.0 (min 0.0)
- LF 1575.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 2}

## First / last

- Earth pre_launch alt=85.84102271776646 peri=-6362518.634174339 apo=85.84102234616876 met=0.0 ec=2409.905029296875 fuel=1575.0 warp=Nonex
- Earth splashed alt=0.4535288894549012 peri=-6360140.566095124 apo=198.94305671192706 met=475.15999975107843 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+507s  ec=0

## Events

- T+0s start command=hop-splash crew=
- T+508s end samples=193

## Handoff

```
command: hop-splash
exit: 2
abort: no science (wanted kerbalism_TELEMETRY)
last:
  hop leftover wreck sit=splashed recoverable=yes experiments=0 — recover, Hangar new
  recovered leftover wreck
  hop recover still listed after recover()
  hangar ready kspstuff-hop-valiant-t7-splash-pbc sit=VesselSituation.pre_launch parts=41
  hop apo=80000
  hop-splash light vertical, no flying Toggle, wait splash
  hop light
  hop airborne
  hop-splash splash
  splash wait water
  gate ec=0
  splash down
  science skip (no Experiment modules)
  ABORT no science (wanted kerbalism_TELEMETRY)

```

## Learn

Recover leftover wreck + Hangar t7 **worked**. Vertical loft **worked** (apo **91.9 km**, splash MET **475**, fuel/EC **0**). Envelope **heading 228 horiz 62 pitch 13 biome Forest** — **not Water** (Water-dead is heading never 090, not this fly). Science **skip**: Kerbalism **Experiment modules=0** at splash; wanted TELEMETRY. **+0** (10.96). Lars: start TELEMETRY PAW on Stayputnik **and Goo from parts** even with no Experiment modules / EC=0. leftover **PRELAUNCH ghost** — recover without lighting, then Hangar. Do not hop-to-water. Pair **3.20** still **0.84** short of ~4.04.
