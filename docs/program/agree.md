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
bind: S-514 kerbalism_LITE InSpaceLow 10/0.03
duration_vs_high: High cannot pay; C-534 loft sits InSpaceLow ~249–300 km; LITE 10s finishes; lid-MECO 137 km High cannot pay LITE; S-516 InSpaceLow goo capped (paid)
recover: yes
meco: this-hop lid 50 km live + independent off; Terrier stack no lid-MECO — AP east while thrusting, circ Pe>140 km
dynamics: still loft-only; C-534 4x1500 Valiant same 249–270 km family as C-504 (+~0.1 km/s); 7x1500 Valiant TWR~0.78 sits; 7x1500 Reliant Δv~4.5 km/s apo~400–500 km Pe through planet; circularize still Terrier after 45
constellation: Cape LIVE 64 bps omni SurfAntenna; loft stays Cape sky; DSN L LIVE TL2; minRelayTL=3 no sat
agreed: yes
blocker: none
```

Wreck rec=no re-flies last `cli:` — do **not** reopen this file.
Change hang / bind / recover / MECO only on an `ops --tag plan`
hire (three in parallel on that ticket, then split).

## Hang (Gus)

This tree pad: C-534 `kspstuff-hop-valiant-proc-redstone-pbc`. Flies
`python main.py ascent` now (T-552). FED (last tank attN
bottom=Valiant). Nylon `RC_cone` 50 m payload-side on OKTO
(Stayputnik has no top; cone `srfAttach=0`). Engine `istg=0`
`sqor=0` first fire; chute `istg=1` `sqor=0` last. No girders. 4×
proc 1.25×1.222 Cylinder `RedstoneStripes` 1500 L Default 2700 kero.
Stack Heaviest/rigid. No HS. Recover: silk. `capable: yes`. Pad until
`advRocketry` 45. 268 km loft is not orbit — Pe on the ground. Did
not replace C-534. Did not Hangar C-534.

Orbit donor on disk until 45, not pad: C-544
`kspstuff-hop-valiant-proc-orbit-pbc`. Clone C-534 + 2 extra
`sasModule` (3 total, Heaviest/rigid) for FAR heading. Same Valiant
5° gimbal (cfg; FAR ×1.5 may read 7.5 — tape still HDG 297). Same
4×1500 L Redstone 2700 kero, no girders, no HS, silk, engine first
fire. `craft fuel` FED. Terrier `liquidEngine3_v2` **LOCKED**
`advRocketry` 45 — not on the file; do not Hangar a locked part.
Reliant has no gimbal. Swivel gimbal 3° is worse. `capable: no`
(first-stage donor, not two-stage circularize). Helper T-546:
two-stage compose (extra wheel CLI, proc decoupler + upper tanks +
Terrier after unlock; `liquid` must not flatten the split; staging
Valiant first / decoupler / Terrier / chute last). After 45: splice
Terrier vacuum upper, Pe above ~140 km High lid. rec=no is honest if
orbiting. Do not Hangar the donor until the node. Do not Hangar
C-477. C-504 loft-pbc stays shelf. Leftover High / Forest / splash
hangs wait a living orbit.

## Bind (Linus)

This-hop: S-514 kerbalism_LITE InSpaceLow 10/0.03/2.00 seq0 (file,
scan still unstarted ~2.00) on C-534
`kspstuff-hop-valiant-proc-redstone-pbc` OKTO PAW. Envelope Shores
loft-through apo 249–300 km sits InSpaceLow; LITE 10 s finishes;
recover HD 0.25 MB. Lid-MECO apo 137 km is High — cannot pay LITE;
do not unbind S-514; do not re-pin High 305 s. T-533: keep
loft-through (apo>140 km). Closed S-516 InSpaceLow goo — capped
(paid). Closed S-515 TELEMETRY InSpaceLow — capped (paid). Thermo
InSpaceLow capped; PresMat has no InSpaceLow sit. High / Forest /
splash leftover stays shelf — keep an eye; do not unbind forever;
not this-hop: T-368 FlyingHigh goo leftover 0.293 (crumbs), T-069
Forest High TELEMETRY leftover 1.512, T-404 High PresMat 2.70 (305 s
cannot pay). Bank 8.29 need ~36.71 for advRocketry 45. This-hop LITE
~2.00 still leaves ~34.71. Not Water. Not Grasslands. Not Surface.
Pulse Toggle in space. f013 LITE hosted OKTO PAW on_craft=yes.

## Pulse (Lars)

This-hop C-534 is loft, not orbit. `hop_factory.py` inland. Pad-RF
`hop_factory_pad.py` (one sit). Throttle 1 + SAS vertical until lid.
MECO at 50 km **live** alt: MainThrottle 0, setpoint 0, independent
off. `_hold_lid` after lid is MECO — not inland-through-burnout.
After lid, Toggle InSpaceLow (`_space_low_sit`). Arm Nylon on
descent (`_space_silk_arm_sit`) — recover yes. Do not circularize
this hang: no Terrier; Pe stays on the ground. Inland slew after lid
MECO has no plume (Valiant `ModuleGimbal` 5° idle; heading 297
weathercock). Pulse never writes gimbal. Girders none in pulse.
Do not retune MECO / lid / silk to High 305 s. Log must not print
hold inland through burnout after High lid.

When the hang is the Terrier orbit stack (`_orbit_stack_sit`): do
**not** MECO at 50 km. SAS on the pad, then AP **while thrusting**
so the 5° gimbal turns. Gravity turn **east** (heading 90) through
first-stage burnout. Then Terrier at apo until Pe ≥ ~140 km High
lid. rec=no is honest if orbiting. Same compose — not a stamp
helper. Forest / Grasslands: same.

## Dynamics (Katherine, opt-in)

Still loft-only. C-534 tape two hops (19-48-52Z / 20-07-41Z)
agree with the C-504 family — not circularize. Pad **7.47 t** /
2700 kero / parts 25. Loft-through apo **243–281 km**,
sit=sub_orbital, apex horiz **24–30 m/s** vs circular
**7.75–7.82 km/s**. Leftover kero **161–221**. Q_max **22.6–22.8 kPa**
at 7–8 km; FAR at apo is zero. Burnout pitch 65 heading 297 horiz
<40 m/s — vertical, not a gravity turn. InSpaceLow. Pe through the
planet. Short **~7.7 km/s** of circular speed.

C-504 handful (17-13-14Z / 18-57-09Z / 19-08-49Z / 19-31-20Z): apo
**249–270 km**, apex horiz **61–84 m/s**, same sit. C-534 20-07-41Z
**281 km** is the extra tank; 19-48-52Z leftover 221 cut apo to
**243 km**. Same envelope, tens of km of apo, not a new family.

High-band: loft-through is the envelope. 50 km live is still
throttle 1 (19-48-52Z 59 km; 20-07-41Z 49 km). Ascent High ~60 s;
InSpaceLow hundreds of seconds; descent High ~60 s then abort.
T-404 PresMat 305 s in 50–140 km cannot pay. Lid-MECO apo 137 km
High is worse (T-523). Same answer on C-534 as C-504.

Descent vs last-flight recover: last-flight is abort/exit, not
sit. 19-48-52Z chute armed ~237 km then shear 25→12 at 27.7 km
q=39 kPa landing catastrophic Shores. 20-07-41Z chute armed
~277 km; tape cuts flying 101 km vz −1829 landing catastrophic
Shores. Do not Learn recover from those exits.

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

Phase 2 remains `advRocketry` 45 Terrier: restartable vacuum
second stage, Pe above the ~140 km High lid, first stage
gravity-turn east. Do not Hangar a circularize claim on this
tree. C-534 is the loft successor, not an orbit hang.

## Constellation (Eleanor, opt-in)

Cape is **live** for C-534. Dump: `US - Cape Canaveral` L 1.5 dBi
Tx 40 dBm need_TL=0 **LIVE**. GSTL=2. TL2 **64 bps** is table and
Cape path (T-427). Hang omni `SurfAntenna` (Communotron 16-S,
start, gain=2, L). Last flying snap of this craft: `link: yes`
`rate_bps: 64` `via: US - Cape Canaveral`. Hangar none this sit —
that snap is the path, not a live RateToHome. Loft is vertical
over Cape (apex horiz tens of m/s); silk recover stays Cape sky.
Do not cheat a link. Do not plan dump hours as RateToHome.

Also LIVE at GSTL=2 (need_TL=0): Wallops, Bermuda, DSN L
Goldstone / Canberra / Madrid (gain 8). Rest of the map is
**SILENT** until commsTL3 / `basicScience`. `minRelayTL = 3`.
Every relay part is **LOCKED**. T-065: keep 16-S on the chute
hang. HG-5 is `basicScience` locked. Omni until a hop goes deaf.

A future orbit craft needs a path that is **not Cape-only**. This
hang never leaves Cape sky and does not stay up. Ground DSN L is
already LIVE at TL2 — that is the candidate, not a satellite.
Dump LIVE is need_TL, not close at LEO range from 16-S. A sat
cannot relay until `minRelayTL` and a relay part. Do not invent a
constellation. Antenna on the hang is Gus when omni is the miss
— it is not the miss here.
