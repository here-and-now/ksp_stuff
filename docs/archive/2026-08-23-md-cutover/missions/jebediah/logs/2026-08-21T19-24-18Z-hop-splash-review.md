# Review 2026-08-21T19-24-18Z-hop-splash

command: hop-splash
exit: 2
abort: recover
log: docs/missions/jebediah/logs/2026-08-21T19-24-18Z-hop-splash.jsonl
earth: 2026-08-21 19:24:18 UTC
kerbal_ut: 2d 14:46:53 UT
kerbal_met: MET 0d 00:09:44
samples: 520 (~1 Hz)
duration: 1030.9 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 22.4
- peri min -6362461.8
- apo max 22.4
- met max 1614.2
- EC 1992.8 → 1939.1 (min 1939.1)
- fuel 0.5 → 0.5 (min 0.5)
- LF 0.5 → 0.5 (min 0.5)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {}

## First / last

- Earth landed alt=22.369610957801342 peri=-6362461.401763123 apo=22.369549465365708 met=585.1799996934424 ec=1992.8270263671875 fuel=0.5344821214675903 warp=Nonex
- Earth landed alt=22.369492043741047 peri=-6362461.697070899 apo=22.369571085087955 met=1614.1799991543812 ec=1939.132568359375 fuel=0.5344821214675903 warp=Nonex

## Flag changes

- (none)

## Events

- T+0s start command=hop-splash crew=
- T+1032s uplink recover
- T+1032s end samples=522

## Handoff

```
command: hop-splash
exit: 2
abort: recover
last:
  hop apo=80000
  hop-splash light vertical, no flying Toggle, wait splash
  hop light
  ABORT recover

```

## Learn

Leftover **landed Forest** 22 m. Envelope **heading 157 horiz 0 pitch -19** MET **585–1614** (still). uplink **recover**. abort **recover**. KSC empty after. **+0**. Do not Hangar over landed crew/probe — this one recovered.
