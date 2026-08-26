# Agree — this sit (Lars / Gus / Linus)

Shared achievable plan. Not seated `plan.md`. Not last-miss leftovers.
Inner circle last-writes **only their section**. Gene does not merge.
Katherine last-writes **Dynamics** when pulled (`ops --tag ask --desk
katherine` or `--tag dynamics`) — not every pad.

```
sit: InSpaceLow
hang: C-504 kspstuff-hop-valiant-proc-loft-pbc
bind: S-514 kerbalism_LITE InSpaceLow 10/0.03; S-516 mysteryGoo InSpaceLow 641/0.18 leftover 3.41
duration_vs_high: High cannot pay; this loft sits InSpaceLow ~268 km; LITE 10s finishes; goo leftover remaining ~364s — silk recover the can
recover: yes
meco: lid 50 km live; independent off; Toggle InSpaceLow; silk descent — not circularize
dynamics: loft-through apo 249–270 km InSpaceLow; lid-MECO 137 km High; cannot circularize ~7.7 km/s; Terrier after 45
agreed: yes
blocker: none
```

Wreck rec=no re-flies last `cli:` — do **not** reopen this file.
Change hang / bind / recover / MECO only on an `ops --tag plan`
hire (three in parallel on that ticket, then split).

## Hang (Gus)

This tree: C-504 `kspstuff-hop-valiant-proc-loft-pbc`. FED (last tank
attN bottom=Valiant). Nylon `RC_cone` 50 m payload-side on OKTO
(Stayputnik has no top; cone `srfAttach=0`). Engine `istg=0` `sqor=0`
first fire; chute `istg=1` `sqor=0` last. No HS. Recover: silk.
`capable: yes`. Pad until `advRocketry` 45. 268 km loft is not orbit —
Pe on the ground. Silk recover banks InSpaceLow toward 45. Do not
replace C-504 because the last hop sheared. Do not idle the pad
building Reliant / Thumper / TD-06 alts this sit — they stay shelf,
not hang. C-477 blob is not capable. t7-wheel-pbc lithobrake is not
recover. T-428 / T-430 stay alts.

After `advRocketry` 45: Terrier (LV-909) vacuum hang — two-stage
atmospheric first (Valiant / Reliant) + Terrier circularize. Orbit is
Pe above ~140 km High lid, not apo 268 km. rec=no is honest if
orbiting. Do not write or Hangar that stack before the node. Do not
Hangar C-477. Leftover High / Forest / splash hangs wait a living
orbit.

## Bind (Linus)

This-hop: S-514 kerbalism_LITE InSpaceLow 10/0.03/2.00 seq0 (file,
scan still unstarted ~2.00). Envelope Shores loft-through apo
249–270 km sits InSpaceLow; LITE 10 s finishes; recover HD 0.25 MB.
Lid-MECO apo 137 km is High — cannot pay LITE; do not re-pin High
305 s. Successor no-girder bigger-tank hang still this sit while
OKTO PAW on_craft. Closed S-516 InSpaceLow goo — capped (paid).
Closed S-515 TELEMETRY InSpaceLow — capped (paid). High / Forest /
splash leftover stays shelf — keep an eye; do not unbind forever;
not this-hop: T-368 FlyingHigh goo leftover 3.00, T-069 Forest High
TELEMETRY leftover 1.512, T-404 High PresMat 2.70 (305 s cannot
pay). Bank 5.58 need ~39.42 for advRocketry 45. Not Water. Not
Grasslands. Not Surface. Pulse Toggle in space. f013 LITE hosted
OKTO PAW on_craft=yes.

## Pulse (Lars)

This-hop is loft, not orbit. Successor hang still this compose —
girders **none** in pulse. `hop_factory.py` inland. Pad-RF
`hop_factory_pad.py` (one sit). Throttle 1 + SAS vertical until lid.
MECO at 50 km **live** alt: MainThrottle 0, setpoint 0, independent
off. `_hold_lid` after lid is MECO — not inland-through-burnout
(17-01-10Z throttle 1 at 55 km; 17-13-14Z emptied tanks MET 153 apo
270 km). After lid, Toggle InSpaceLow when the live sit is space
(`_space_low_sit`); High cannot-pay is not space-done. Arm Nylon on
descent (`_space_silk_arm_sit`) — recover yes. Do not circularize: no
Terrier; Pe stays on the ground. Do not write truss/girder into
`hop_factory`. Stiffness is hang autostrut, not a pulse part. Forest
/ Grasslands: same. Do not retune MECO / lid / silk to High 305 s or
to the last shear. Log must not print hold inland through burnout
after High lid.

## Dynamics (Katherine, opt-in)

Phase 1 this hang cannot circularize. Two apo families, both Pe
through the planet (sit=sub_orbital, apex horiz 39–84 m/s vs
circular ~7.75 km/s — Δv ~7.7 km/s; leftover 0–32 kg is ~30–50 m/s,
Valiant 100 kN / Isp 270 vac / 1 ignition spent).

Loft-through (tape, tanks empty or ~30 kg): apo 249–270 km
(16-23-52Z 268; 17-13-14Z / 18-45-23Z / 18-57-09Z 269–270;
18-34-15Z 255 leftover 23 kg; 19-08-49Z 249 leftover 32 kg). Apex
heading 297 pitch 65 Q=0 Shores. That is InSpaceLow. Burnout pitch
86–89 heading 299–302 horiz <100 m/s — vertical, not a gravity
turn. Q_max 22–24 kPa up; FAR at apo is zero. Tape rec=no (chute
armed/stowed; last-flight shear is abort; stack intact at last
sample). Silk recovers this loft, not orbit.

Commanded lid-MECO at 50 km vz 1.29 km/s (T-523): vacuum apo 137 km
— High, short of InSpaceLow 140 km. FAR Q ~1.1 kPa at lid shaves
seconds, not 3 km. S-514 InSpaceLow pays loft-through, not a true
lid-MECO.

Phase 2 waits `advRocketry` 45 Terrier (LV-909). Buys a restartable
vacuum second stage so Pe can sit above the ~140 km High lid — not
apo 268 km. Mass ratio for 7.7 km/s at ~330 s vac is ~10.8; cannot
bolt onto C-504 dry ~1.85 t. First stage must gravity-turn east so
burnout horiz is km/s, not 50 m/s. Do not Hangar that stack before
the node.
