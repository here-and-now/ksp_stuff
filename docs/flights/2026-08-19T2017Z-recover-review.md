# Review 2026-08-19T2017Z-recover

command: recover
exit: 0
abort: 
log: docs/flights/2026-08-19T2017Z-recover.jsonl
samples: 3 (~1 Hz)
duration: 13.6 s wall
bodies: Kerbin
tags: {'recover': 3}

## Envelope

- alt min 965999.7
- peri min 69133.3
- apo max 1594227.0
- LF 547.2 → 545.3 (min 545.3)
- warp max 1.0x
- time ATMO 0.0s  DIP 11.5s  ESC 0.0s
- flags {'DIP': 2}

## First / last

- recoverKerbin sub_orbital alt=965999.7415527983 peri=69133.286547128 apo=1580866.7283397769 LF=547.2293701171875 warp=1.0x [DIP]
- recoverKerbin orbiting alt=975202.5231274299 peri=81156.89238648023 apo=1594227.0266208546 LF=545.345947265625 warp=1.0x

## Flag changes

- T+1s recover DIP
- T+14s recover (clear)

## Events

- T+0s start command=recover crew=Grok Kerman 4373
- T+14s end samples=4

## Handoff

```
command: recover
exit: 0
abort: 
last:
  recover periapsis → 80000 m
  recover Kerbin sub_orbital alt=966000 peri=69133 apo=1580867 ecc=0.530 LF=547 stg=1 thr=0.00 F=60000N parts=7 warp=1x tpe=4567 [DIP]
  AP prograde aligned=False err=44.3294563293457
  recover Kerbin sub_orbital alt=974270 peri=69301 apo=1581008 ecc=0.530 LF=547 stg=1 thr=1.00 F=60000N parts=7 warp=1x tpe=4563 [DIP]
  recover Kerbin orbiting alt=975203 peri=81157 apo=1594227 ecc=0.525 LF=545 stg=1 thr=1.00 F=60000N parts=7 warp=1x tpe=4664
  recover-done Kerbin orbiting alt=976135 peri=89080 apo=1608545 ecc=0.524 LF=543 stg=1 thr=0.00 F=60000N parts=7 warp=1x tpe=4696

```

## Learn

_Gene fills this. What worked, what failed, what to change in
the library vs this pilot's style. One short paragraph._
