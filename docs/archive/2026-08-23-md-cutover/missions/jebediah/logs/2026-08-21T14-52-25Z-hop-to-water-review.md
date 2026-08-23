# Review 2026-08-21T14-52-25Z-hop-to-water

command: hop-to-water
exit: 2
abort: not recoverable
log: docs/missions/jebediah/logs/2026-08-21T14-52-25Z-hop-to-water.jsonl
earth: 2026-08-21 14:52:25 UTC
kerbal_ut: 2d 12:36:31 UT
kerbal_met: MET 0d 00:00:13
samples: 11 (~1 Hz)
duration: 12.7 s wall
bodies: Earth
tags: {}

## Envelope

- alt min 83.2
- peri min -6362489.9
- apo max 264.5
- met max 13.8
- EC 9.3 → 9.3 (min 9.3)
- fuel 0.0 → 0.0 (min 0.0)
- LF 0.0 → 0.0 (min 0.0)
- warp max Nonex
- time ATMO 0.0s  DIP 0.0s  ESC 0.0s
- flags {}

## First / last

- Earth flying alt=83.22203269787133 peri=-6362489.905487717 apo=264.47540660668164 met=13.799999992770609 ec=9.349682807922363 fuel=0.0 warp=Nonex
- Earth flying alt=83.22203269787133 peri=-6362489.905487717 apo=264.47540660668164 met=13.799999992770609 ec=9.349682807922363 fuel=0.0 warp=Nonex

## Flag changes

- (none)

## Events

- T+0s start command=hop-to-water crew=
- T+18s end samples=12

## Handoff

```
command: hop-to-water
exit: 2
abort: not recoverable
last:
  hop apo=18000
  hop-to-water pitch 25° east, wait splash
  hop airborne
  science skip seismicScan on probeCoreSphere.v2 (not in card)
  science skip geigerCounter on probeCoreSphere.v2 (not in card)
  science skip kerbalism_LITE on probeCoreSphere.v2 (not in card)
  science skip kerbalism_MITE on probeCoreSphere.v2 (not in card)
  science skip kerbalism_SITE on probeCoreSphere.v2 (not in card)
  science skip telemetryReport on probeCoreSphere.v2 (not in card)
  science start temperatureScan
  science start kerbalism_TELEMETRY
  science temperatureScan,kerbalism_TELEMETRY
  science dwell
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop down
  hop recover sit=flying recoverable=no
  hop crash ui sit=flying recoverable=no met=13.80 alt=83.2 q=0
  hop unpause
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop recover sit=flying recoverable=no
  hop dismissed crash ui
  ABORT not recoverable

```

## Learn

Disk leftover PRELAUNCH was a lie. Live sit was already flying MET
**13.8** fuel=0 thrust=0 EC=9.3 speed=0 q=0 alt **83.2** apo **264 m**.
Hop logged airborne and started thermo+TELEMETRY on the wreck. Crash
UI Catastrophic Failure T+13 pad collision (Stayputnik / Goo / T100 /
Valiant into LaunchPad). sci **10.96 (+0)**. Envelope is not a Water
hop. Lars leftover sit/fuel/recoverable gate in. `go_space_center`
logged dismissed; **stuck still** `screenshots/stuck-flight-results.png`
(2026-08-21): Flight Results **still up** over Tracking, **no vessels**,
funds 11.0, Close/Space Center/Revert buttons live. Empty Tracking is
not KSC clean. Lars hangar-flight-results in: Close-poll until scene
KSC **and** `can_revert_to_launch` false; never revert; no
`launch_vessel` over the modal. Hangar waits. Do not Hangar from Gene.
desk sci_delta **+0**. `need_stack: none`. `campaign: uncrewed`.
`go: yes`. `python main.py hop-to-water`.
