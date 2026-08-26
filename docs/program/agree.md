# Agree — this sit (Lars / Gus / Linus)

Shared achievable plan. Not seated `plan.md`. Not last-miss leftovers.
Inner circle last-writes **only their section**. Gene does not merge.
Katherine last-writes **Dynamics** when pulled (`ops --tag ask --desk
katherine` or `--tag dynamics`) — not every pad. Eleanor last-writes
**Constellation** when pulled (`ops --tag ask --desk eleanor` or
`--tag constellation`) — not every pad. Hank talks to her directly.

```
sit: InSpaceLow
hang: C-534 kspstuff-hop-valiant-proc-redstone-pbc
bind: S-514 kerbalism_LITE InSpaceLow 10/0.03; S-516 mysteryGoo InSpaceLow 641/0.18 leftover 3.41
duration_vs_high: High cannot pay; this loft sits InSpaceLow ~268 km; LITE 10s finishes; goo leftover remaining ~364s — silk recover the can
recover: yes
meco: lid 50 km live; independent off; Toggle InSpaceLow; silk descent — not circularize
dynamics: still loft-only; C-534 4x1500 Valiant same 249–270 km family as C-504 (+~0.1 km/s); 7x1500 Valiant TWR~0.78 sits; 7x1500 Reliant Δv~4.5 km/s apo~400–500 km Pe through planet; circularize still Terrier after 45
agreed: yes
blocker: none
```

Wreck rec=no re-flies last `cli:` — do **not** reopen this file.
Change hang / bind / recover / MECO only on an `ops --tag plan`
hire (three in parallel on that ticket, then split).

## Hang (Gus)

This tree: C-534 `kspstuff-hop-valiant-proc-redstone-pbc`. FED (last
tank attN bottom=Valiant). Nylon `RC_cone` 50 m payload-side on OKTO
(Stayputnik has no top; cone `srfAttach=0`). Engine `istg=0` `sqor=0`
first fire; chute `istg=1` `sqor=0` last. No girders. 4× proc
1.25×1.222 Cylinder `RedstoneStripes` 1500 L Default 2700 kero
(`ProceduralPartsTank1500L` generalRocketry spent) vs C-504 7×767 +
3× girder 2415 kero. Stack Heaviest/rigid. No HS. Recover: silk.
`capable: yes`. Pad until `advRocketry` 45. 268 km loft is not orbit —
Pe on the ground. Silk recover banks InSpaceLow toward 45. C-504
`kspstuff-hop-valiant-proc-loft-pbc` stays shelf, not pad. Do not
idle Reliant / Thumper / TD-06 alts this sit — they stay shelf. C-477
blob is not capable. t7-wheel-pbc lithobrake is not recover. T-428 /
T-430 stay alts. Girderless lite T-362 is not this hang.

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

Still loft-only. C-534 (4×1500 L Valiant, 2700 kero, no girders)
is the same apo/Pe family as C-504 tape. Six C-504 hops agree
(16-23-52Z through 19-08-49Z): loft-through apo **249–270 km**,
sit=sub_orbital, Pe through the planet (ship peri ~−6358 km), apex
horiz **39–84 m/s** vs circular **7.75–7.82 km/s**. Pad mass
**7.19 t** / dry **1.84 t** / kero **2415** (7×767 L = 5369 L,
already the basicRocketry 800 L cap). Vac Δv **3.50–3.74 km/s**
(Isp 270, MR 3.8–4.1). Short **~4.1 km/s** of circular speed;
**~5.7 km/s** of a ~9.4 km/s LEO budget. Valiant 100 kN / 1
ignition spent at light. Burnout pitch 86–89 heading 299–302 horiz
<100 m/s — vertical, not a gravity turn. Q_max 22–24 kPa; FAR at
apo is zero. InSpaceLow. Silk recovers this loft, not orbit.

C-534 vs that tape: 4×1500 L = 6000 L / 2700 kero vs 5369 L /
2415 (~**+12%** propellant, girders gone). Vac Δv **~3.7–3.8 km/s**
(TWR ~1.3). Apo maybe **~280–300 km**, still InSpaceLow, still Pe
through the planet. What more tank buys at 4×1500: tens of km of
apo, not a new family.

`generalRocketry` also unlocks Reliant (RF 215 kN / 0.42 t / Isp
~256–270 / **1 ignition**) and lets a tank fill to 1500 L. It does
not buy a restart or 330 s.

- **7×1500 L Valiant:** pad TWR ~0.78. Does not loft.
- **7×1500 L Reliant:** TWR ~1.7 so the extra tank *flies*. Vac Δv
  ~4.4–4.6 km/s. Vertical ballistic apo maybe **~400–500 km**,
  still sit=sub_orbital, Pe still through the planet. A gravity
  turn at 4.5 km/s still leaves Pe on the ground (need ~7.8 km/s
  horiz). Mass ratio for 7.7 km/s at 270 s is ~18; this hang is
  ~6.
- **Reliant vs Valiant** is TWR (and 0.33 t) so 7×1500 can leave
  the pad — not circularize Δv. Both 1 ignition.

Lid-MECO at 50 km vz 1.29 km/s is still apo 137 km High. Phase 2
remains `advRocketry` 45 Terrier: restartable vacuum second stage,
Pe above the ~140 km High lid, first stage gravity-turn east. Do
not Hangar a circularize claim on this tree. C-534 is the loft
successor, not an orbit hang.
