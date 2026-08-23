# Review 2026-08-21T16-06-15Z-hop-to-water

command: hop-to-water
exit: 2
abort: Hangar waits: KSC not clean (timed out waiting for KSC (still flight results (can_revert); Flight Results not dismissed)). Close until KSC, no revert, no launch_vessel
log: docs/missions/jebediah/logs/2026-08-21T16-06-15Z-hop-to-water.jsonl
earth: 2026-08-21 16:06:15 UTC
kerbal_ut: 2d 12:54:52 UT
kerbal_met: ?
samples: 0 (~1 Hz)
duration: 0.0 s wall
bodies: ?
tags: {}

## Envelope

- alt min None
- peri min None
- apo max None
- met max None
- EC None → None (min None)
- fuel None → None (min None)
- LF None → None (min None)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {}

## First / last

- 
- 

## Flag changes

- (none)

## Events

- T+0s start command=hop-to-water crew=
- T+95s end samples=1

## Handoff

```
command: hop-to-water
exit: 2
abort: Hangar waits: KSC not clean (timed out waiting for KSC (still flight results (can_revert); Flight Results not dismissed)). Close until KSC, no revert, no launch_vessel
last:
  hop leftover unmatched kspstuff-hop-valiant-east-pbc sit=pre_launch recoverable=yes — recover, do not light
  recovered unmatched leftover sit=pre_launch recoverable=yes
  ABORT Hangar waits: KSC not clean (timed out waiting for KSC (still flight results (can_revert); Flight Results not dismissed)). Close until KSC, no revert, no launch_vessel

```

## Learn

16-06-15Z hop-to-water abort +0. Unmatched leftover **east-pbc**
`sit=pre_launch recoverable=yes` recovered **without lighting**. Hangar
then waited: Flight Results still up (`can_revert`), timed out, no
`launch_vessel`. Envelope empty. Close until KSC, no revert. Next
Hangar **east-bare** only after the window is KSC.
