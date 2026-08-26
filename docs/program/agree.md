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
dynamics: MECO@50km ~271s vac / ~260s FAR in 50–140 (vz 1.29 km/s apo 137 km); T-404 305s cannot pay
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
scan still unstarted). Envelope Shores loft ~268 km is InSpaceLow
every hop. LITE 10 s finishes; recover HD 0.25 MB. Closed S-516
InSpaceLow goo — science-scan capped (paid); desk leftover gone.
Closed S-515 TELEMETRY InSpaceLow — capped (paid). High / Forest /
splash leftover stays shelf — keep an eye; do not unbind forever;
not this-hop: T-368 FlyingHigh goo leftover 3.457, T-069 Forest
High TELEMETRY leftover 1.512, T-404 High PresMat 2.70 (305 s
cannot pay). Bank 5.13 need ~39.87 for advRocketry 45. Not Water.
Not Grasslands. Not Surface. Pulse Toggle in space. f013 LITE
hosted OKTO PAW on_craft=yes.

## Pulse (Lars)

This-hop is loft, not orbit. `hop_factory.py` inland compose. Pad-RF
`hop_factory_pad.py` (one sit). Throttle 1 + SAS vertical until lid.
MECO at 50 km **live** alt: MainThrottle 0, setpoint 0, independent
off. `_hold_lid` after lid is MECO — not inland-through-burnout
(17-01-10Z throttle 1 at 55 km; 17-13-14Z emptied tanks MET 153 apo
270 km). After lid, Toggle InSpaceLow when the live sit is space
(`_space_low_sit`); High cannot-pay is not space-done. Arm Nylon on
descent (`_space_silk_arm_sit`) — recover yes, hang owns silk. Do not
circularize: no vacuum engine; Pe stays on the ground. Circularize
pulse waits `advRocketry` 45 Terrier — Pe above ~140 km High lid is
that sit, not this file this hang. Leftover later. Do not retune MECO
/ lid / silk to High 305 s or to the last shear. Log must not print
hold inland through burnout after High lid.

## Dynamics (Katherine, opt-in)

Four loft-throughs agree at the lid: 50 km live vz 1.29 km/s (16-23-52Z
1.32), pitch 87–89, heading 299–302, Q_max ~23 kPa, Shores, throttle 1
through High. MECO at that state: vacuum apo 137 km, 50→apo→50 = 271 s
(16-23-52Z 249 s if apo 141 km nicks InSpaceLow). FAR Q ~1.1 kPa at lid
shaves a few seconds (~260 s), not 45. Kepler ceiling in-band (kiss
140 km) is 276 s. MECO earlier is worse (42 km vz 1.10 → apo 106 km →
216 s in High). Lid leftover ~290 kg hovers ~38 s, not 305. Loft-through
High is ~56 s up / ~50 s down (17-01-10Z). T-404 305 s cannot pay. Silk
is recover, not a High drogue.
