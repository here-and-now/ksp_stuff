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
meco: lid 50 km live; independent off; High dwell coast
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
scan still unstarted) + S-516 mysteryGoo InSpaceLow leftover
641/0.18/3.41 seq1 (sample, silk recover). Envelope Shores loft
~268 km is InSpaceLow every hop. Unbound S-515 TELEMETRY InSpaceLow
(capped, paid). LITE 10 s finishes. Goo leftover 2.590/6.000
remaining ~364 s may not finish a ~300 s coast — leftover still
pays if complete; recover the can (429 MB). T-368 High goo same eid
unbound. T-404 High PresMat unbound. T-069 Forest High TELEMETRY
unbound (Shores). Not Water. Not Grasslands. Not Surface. Pulse
Toggle in space. f013 Goo start on_craft; LITE hosted OKTO PAW.

## Pulse (Lars)

`hop_factory.py` inland compose. Pad-RF `hop_factory_pad.py` (one
sit). Throttle 1 + SAS vertical until lid. MECO at 50 km **live**
alt: MainThrottle 0, setpoint 0, independent off. Then High dwell
coast — not a burn, not inland-through-burnout. 17-01-10Z printed
that sit at 55 km throttle 1. After that gate, 17-13-14Z still
emptied tanks by MET 153 alt 98 km apo 270 km; PresMat dwell in
space, sci +0. `_hold_lid` after lid is MECO. Log must not print
hold inland through burnout after High lid. Residual vz at lid
still exits 140 km — that is the fight; 305 s in 50–140 km is not
MECO-at-lid alone. Hang owns recover. Do not retune MECO / lid /
silk to the last shear.

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
