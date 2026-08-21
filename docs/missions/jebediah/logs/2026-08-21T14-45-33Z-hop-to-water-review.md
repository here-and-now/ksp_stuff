# Review 2026-08-21T14-45-33Z-hop-to-water

command: hop-to-water
exit: 2
abort: not splashed
log: docs/missions/jebediah/logs/2026-08-21T14-45-33Z-hop-to-water.jsonl
earth: 2026-08-21 14:45:33 UTC
kerbal_ut: 2d 12:35:16 UT
kerbal_met: MET 0d 00:00:00
samples: 2 (~1 Hz)
duration: 7.9 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 84.6
- peri min -6362518.6
- apo max 146.6
- met max 0.6
- EC 282.2 → 286.9 (min 282.2)
- fuel 450.0 → 434.7 (min 434.7)
- LF 450.0 → 434.7 (min 434.7)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {}

## First / last

- Earth pre_launch alt=84.64197272062302 peri=-6362518.485602481 apo=84.6419727485627 met=0.0 ec=282.19146728515625 fuel=450.0 warp=Nonex
- Earth landed alt=97.2521509481594 peri=-6362518.641195003 apo=146.5627720700577 met=0.5999999996856786 ec=286.882080078125 fuel=434.65130615234375 warp=Nonex

## Flag changes

- (none)

## Events

- T+0s start command=hop-to-water crew=
- T+8s end samples=3

## Handoff

```
command: hop-to-water
exit: 2
abort: not splashed
last:
  hop enter flight (space_center)
  hop apo=18000
  hop-to-water pitch 25° east, wait splash
  hop light
  ABORT not splashed

```

## Learn

14-45-33Z hop-to-water abort. Matching leftover east-pbc **lit** (fuel
450→435, thrust on). Sci **10.96 (+0)**. Pitch **25° never ran**.
`wait_water` treated pad `sit=landed` at MET **0.6** (alt 97, still
37.5 m / 49 m/s Shores, HDG 357) as a dry miss. Hop-off, not Water.
Lars: abort landed only after **left_pad**. leftover **matching
PRELAUNCH** east-pbc — light, do not Hangar. Flea still refused.
