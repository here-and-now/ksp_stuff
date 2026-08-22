# Review 2026-08-21T22-45-26Z-hop-to-water

command: hop-to-water
exit: 0
abort: 
log: docs/missions/jebediah/logs/2026-08-21T22-45-26Z-hop-to-water.jsonl
earth: 2026-08-21 22:45:26 UTC
kerbal_ut: 2d 16:04:12 UT
kerbal_met: MET 0d 00:03:32
samples: 1 (~1 Hz)
duration: 0.2 s wall
bodies: Earth
tags: {}

## Envelope

- alt min -2.6
- peri min -6360848.5
- apo max 2689.7
- met max 212.2
- EC 0.0 → 0.0 (min 0.0)
- fuel 0.0 → 0.0 (min 0.0)
- LF 0.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {'ec=0': 1}

## First / last

- Earth splashed alt=-2.6049106465652585 peri=-6360848.519295679 apo=2689.7181875528768 met=212.199999888835 ec=0.0 fuel=0.0 warp=Nonex [ec=0]
- Earth splashed alt=-2.6049106465652585 peri=-6360848.519295679 apo=2689.7181875528768 met=212.199999888835 ec=0.0 fuel=0.0 warp=Nonex [ec=0]

## Flag changes

- T+0s  ec=0

## Events

- T+0s start command=hop-to-water crew=
- T+0s landing landing: catastrophic impact=230 m/s heading=300 sit=splashed
- T+1s end samples=3

## Handoff

```
command: hop-to-water
exit: 0
abort: 
last:
  hop apo=18000
  hop-to-water slew pitch 25° east after pad (throttle 0.4), hold through burnout, wait splash
  hop leftover sit=splashed fuel=0.0 recoverable=yes met=212.20 — do not light
  recovered sit=splashed recoverable=yes
  recovered

```

## Learn

Not a loft. Exit 0 `recovered`. desk sci **13.26 Δ0**. kind=state
heading **300.0** horiz **41.6** pitch **77.6** sit=splashed MET
**212.2** fuel=0 EC=0 biome Shores landing catastrophic impact
**230 m/s** — same 22-03 wreck, never lit. last-flight: leftover
`do not light` then `recovered`. CLI did not Hangar; latch + leftover-LF
suicide untested. Parent desk after recover: leftover **n=0**, hangar
**none**, pad empty, lock free. Lars recover-then-Hangar in. Heading
**300** is leftover wreck, not this hire's fly. Os: still test the
brake. T-016 hardware — do not wait a wheel. `go: yes`.
