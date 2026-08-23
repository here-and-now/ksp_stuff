# Building blocks — Gene may only name `pad` `hop` `splash` `tech-unlock`

Owned by **Lars Grokman, Vehicle Engineering**. If Gene needs a name
that is not here, parent spawns Lars first. No heredocs. Missing name
means Lars writes it — do not keep leftover Kerbin/Mun compose around
for them.

| Phase | CLI | Expect |
|---|---|---|
| pad | `python main.py pad` / `phase pad` | Hangar **seated/VAB craft file** uncrewed (`kspstuff-geiger-pbc` Geiger Counter **part**, F-013). Not `pad_pbc()`. Dry-launch only if current stage is 0 (do not light a Flea). Dwell watches `wait science run= rem=` and UT, **not** vessel MET. Physics warp 2–4× on pad/landed; **rails 0**; never WarpTo; 1× after dwell. Empty HD with nothing recording still aborts. |
| hop | `python main.py hop` / `phase hop` | Hangar **seated/VAB craft file** uncrewed (Valiant sit: `kspstuff-hop-valiant-pbc`; Hammer sit: `kspstuff-hop-hammer-pbc`, 2HOT — F-013). Not Flea, not exact pad/geiger names. Light → **bound** flying card (thermo on 2HOT not Stayputnik). FlyingLow Toggle **airborne**. FlyingHigh Toggle **only ≥50 km** — not T+1 FlyingLow (~100 m); **one** Toggle (a second at the lid stops Kerbalism). Unbound leftover FlyingHigh tickets are **not** the lid (**22-33-17Z** T-068 FlyingLow waited 50 km because T-069 leftover High). **13-31-03Z:** t7 apo 88.8 km, lid MET~98 alt 50.4 km, card started T+1 FlyingLow, splash recover sci +0. `hop_apo` Gene **80 km** is a real cut on Valiant; FlyingLow clamp is **8–18 km**. OffPlan apo > **50 km** FlyingLow, or **140 km** Space when the card is FlyingHigh. **13-08-57Z:** Valiant + 2×FL-T100 dry MET~27 alt~7 km apo **12.3 km** — never FlyingHigh; that loft is Gus tanks, not hop.py. Unmatched leftover (PRELAUNCH Flea vs seated Valiant) recovers without lighting, then Hangars the seated craft. Recover HD when down (`vessel.recover()`). Low flying **≤250 m** calls `recover()` only if `recoverable` (199 m living hop). MET-still + q=0 flying is **down now** (do not wait the 600 s crash UI). Frozen MET is **wall seconds** not pulses (**23-35-40Z** 20 Hz Close flying 72.6 m q=0 before sit=landed; **23-14-23Z** landed recovered 90 m/s). Frozen MET + flying + q=0 + low alt is **Catastrophic Flight Results**: log sit/recoverable/met/alt/q, unpause, wait sit=landed/`recoverable`, `recover()` if recoverable, else `go_space_center` (Close until KSC, not revert) and abort. Frozen landed `recoverable=no` is the same dialog (13-58-18Z Vessel is destroyed): Close now, do not unpause-spam `recover()`. Do not wait `sit=landed` that never comes (12-04-13Z). Post-dismiss `pre_launch` recoverable is **not** recovery@EarthFlew. 1 Hz recover line names sit + recoverable. Live kRPC hop ship leftover enters Flight — no second Hangar. Gate live sit/fuel/recoverable before light (disk PRELAUNCH is a lie). Dead GUID / FLYING Debris is not leftover; empty Tracking Hangars leftover scan, but **empty Tracking is not KSC clean** — Flight Results over Tracking (**14-52-25Z**) still has Revert; Hangar does not `launch_vessel` until scene is KSC and `can_revert_to_launch` is false. Splash goo is **not** a hop start. **FAR shear:** mass/parts drop beyond propellant (`stack_sheared`) → hold+abort. **07-06-08Z** 1283→270 kg at burnout pitch −58, `broken=null`, dwelt to crash UI. **07-21-05Z** stiff 36 parts through apex; parts 36→0 / mass 0 at 412 m is kRPC death, not boost shear — do not abort `shear` (91 m/s after chute). **07-50-48Z** same death rec=no impact 89 m/s: abort `ksc leftover` (Hank `recover-probe --space-center`); do not spin `hop recover sit=flying recoverable=no` + `gate ec=0` then `go_space_center` (Flight Results overlay is not leftover-clean). **Mk16 / RealChute:** `arm_chutes` once airborne, then `deploy_chutes` on the **descent** below 2 km (vz < 0). Do **not** extra-stage at light. Do **not** Deploy at `apo_cut` / apex (**08-54-41Z** 13 km dumped inland horiz; **09-59-28Z** 5 km still dumped, Shores). **Inland slew:** after `left_pad`, yaw **10°** off zenith heading **270**, then pitch **25°** west (08-29-36Z heading 299 horiz 0 stayed Shores; **7.5° stayed Shores** 14-33-29Z; **09-16-24Z** logged 270, apex 297 pitch 87 horiz 22; **09-28-59Z** 298/86; **09-44-59Z** 10 °/s on telem 0.05 s dt engaged at ~90, burn 340/43 MET 51, weathercock 299; **09-59-28Z** MET20 297/66 then burnout 336 — do not rewrite the same vector; **10-17-18Z** engaged-latch flew 38/−10 — re-point if flipped while burning; **10-33-44Z** 353/26 missed 90° — write ``target_direction``; **16-47-21Z** slam 65 held pitch, flew pad 297, envelope cutoff 15/16 — do not rewrite fuel=0). Do **not** glue hop-to-water **090**. Do **not** slam `target_pitch=65` at light. Do **not** set `target_pitch`/`target_heading` (Eulers stay pad 299). Point `set_direction_and_up` (north up); engage once off zenith (re-engage restarts 0.6 soft-start; zenith engage has no heading); hold AP through burnout (do not rewrite cutoff). Coast after **real** burnout physics 2–4× (`physics_warp`, fuel gone or throttle 0 after loft well above pad — **18-34-22Z** throttle-0 at 101 m fuel 1054 is not cutoff; factory 3×, rails 0, never WarpTo; 1× burn/chute/recover/shear; uplink `phys-warp`/`no_warp`). Factory inland pulse is `hop_factory.py` (no water/splash flags). Do not hop-down a full tank at pad alt. Stiff survived q~37 kPa vertical — throttle 1. kRPC `armed` is not a canopy — **06-53-50Z** stayed armed through 206 m / **154 m/s**, then none. **00-10-20Z** never armed. No chute on the hang: wait wreck-recoverable. |
| splash | `python main.py splash` / `phase splash` | Leftover hop Flea only — no Hangar, no light, no pad motor. SpaceCenter leftover enters Flight. Wait until **splashed** (do not recover while flying even if recoverable). One Toggle `mysteryGoo` on GooExperiment. Dwell (641 s catalog, EC cap). Recover HD when splashed/recoverable. Landed is not Water. EC=0 with HD data recovers; empty HD aborts. Frozen MET / Flight Results recovers debris or leaves flight. |
| tech-unlock | `python main.py tech-unlock [node]` / `phase tech-unlock` | Ground kRPC try. Disk checks tree/parents/bank. Opens R&D. **0.6 has no UnlockTech RPC — aborts.** Paid node: **Mortimer** edits `persistent.sfs` ResearchAndDevelopment only (Os 2026-08-20). Not GameData. Not a pad/geiger sit (F-013). |

`hop-to-water` / `hop-splash` are **not** Gene names. Loops stay in `hop.py`
(`run_hop_to_water` / `run_hop_splash`). CLI `python main.py hop-to-water`
and `hop-splash` still run those loops. Factory is `hop`.

`python main.py pad` Hangars the **named** stack uncrewed (seated
``craft.md`` / VAB ``craft:``). Geiger sit: byte-copy
``crafts/kspstuff-geiger-pbc.craft`` — do **not** generate
``pad_pbc()`` (no Geiger part). Template ``kspstuff-pad-pbc`` only
when that is the name and no file. Then ``run_physics``. Dry-launch
(throttle-0 stage) only at ``current_stage=0``; a Flea at stage 1
would light — skip. Kerbalism file science is rem / running / UT,
not ``vessel.met``. Pad dwell physics-warps 2–4× (``physics_warp_factor``
1–3, rails **0**, never ``WarpTo``), then 1×. Starts the seated pad
card. Recording (run=1 or rem dropping) does **not** abort because
MET is 0. Empty HD with nothing recording still aborts.

`python main.py hop` Hangars the **named** hop craft uncrewed (seated
``craft.md`` / VAB ``craft:``). Hammer sit: byte-copy
``crafts/kspstuff-hop-hammer-pbc.craft``. Does **not** Hangar
``kspstuff-pad-pbc`` or ``kspstuff-geiger-pbc`` (exact names, not a
``geiger-pbc`` substring). Empty KSC or leftover
pad/geiger → Hangar the hop motor. Hangar ``go_space_center`` Closes
until KSC is clean (scene ``space_center``, ``can_revert_to_launch``
false) **before** ``launch_vessel``. Flight Results over Tracking
(14-52-25Z) is not KSC — empty Tracking is not a green light. Never
revert. ``phase hop`` on an already-launched
matching hop craft skips Hangar. Leftover in tracking at SpaceCenter
enters Flight — do **not** Hangar a second stack. A kRPC active proxy
whose ``.name`` raises ``No such vessel`` is gone — scan the pool;
empty Tracking Hangars. Disk desk ``sit=FLYING`` debris is not leftover.
Disk PRELAUNCH is a lie: gate live sit/fuel/recoverable before light.
Unmatched leftover (Flea vs seated Valiant) ``recover()`` without lighting
— do not Hangar over it, then Hangar the seated craft. ``hop_apo`` 18 km
is throttle-cut (solids ignore it); FlyingHigh unclamps to Space so Gene
80 km is a real cut **if the stack can reach it**. OffPlan is FlyingLow
**50 km** or FlyingHigh **140 km** Space, not the 18 km clamp — Hammer
22-56Z 18.8 km was still FlyingLow. Valiant 13-08-57Z (2×FL-T100, throttle
1 until dry) peaked apo 12.3 km — do **not** fake FlyingHigh in
``hop.py``; that is Gus tanks/Δv. Ballistic peri
is negative — not OFFPLAN. Mk16: ``arm_chutes`` airborne then ``deploy_chutes`` on the descent
below 2 km (vz < 0; not extra-stage; not at apo — **08-54-41Z** 13 km
dumped inland horiz; **09-59-28Z** 5 km still dumped; 06-53-50Z kRPC
armed stayed packed 154 m/s). After
``left_pad``, yaw **10°** off zenith heading **270**, then **25°** inland
(08-29-36Z pad 299 horiz 0 stayed Shores; 7.5° stayed Shores;
09-16-24Z logged 270 flew 297/87; **09-28-59Z** same 298/86 — engage
once, ``set_direction_and_up`` north up, not Eulers / re-engage;
**09-44-59Z** 10 °/s on 0.05 s dt engaged at zenith, burn 340/43;
**09-59-28Z** MET20 297/66 burnout 336 — do not rewrite the same vector;
**10-17-18Z** 38/−10 past horizon — re-point if flipped while burning, do not skip on ``engaged``; **10-33-44Z** 353/26 missed 90° — write ``target_direction``; **16-47-21Z** slam 65 held pitch, flew pad 297, envelope cutoff 15/16 — do not rewrite fuel=0).
Do **not** engage at ~90. Not
**090**. Hold AP through burnout. Coast physics 2–4× after **real**
burnout (fuel gone or throttle 0 after loft well above pad —
not a pad throttle-0 tick; factory 3×, rails 0, never WarpTo;
1× burn/chute/recover/shear; uplink
`phys-warp 2|3|4` / `no_warp`). No chute
on the hang: wait wreck-recoverable. Empty tanks
after the motor are expected. Start the **bound** flying card once airborne
(FlyingLow) or at alt **≥50 km** (FlyingHigh — 13-31-03Z Toggle at T+1
FlyingLow banked crumbs, not the lid). Unbound leftover FlyingHigh
tickets are not a 50 km lid (**22-33-17Z** bound T-068 FlyingLow never
Toggle). TELEMETRY on Stayputnik + thermo
on 2HOT; **one** Toggle per id; do **not** Toggle again at the lid
(that second start stops Kerbalism). Splash goo is not a hop start. Do
**not** Toggle Stayputnik ``temperatureScan`` — that second start stops
Kerbalism (1119Z). A hop this process **lit** always starts that card
at the right lid. Do **not** skip start because idle
TELEMETRY remaining=0. Leftover-HD skip (HardDrive files or Experiment
modules gone, no second Toggle) is for an already-dead probe this process
did not light. Empty card on a clean pad still
aborts. EC=0 with HD data recovers on first recoverable; abort timeout
only if the HD is empty. Flying ≤250 m calls ``vessel.recover()`` only
when recoverable (earlier hop banked at ~199 m; 11-09-13Z after dismiss
did not). MET-still
+ q=0 while flying is lithobrake down now — do not wait the wreck-dialog
wall. Frozen MET + flying + q=0 + low alt is Catastrophic Flight
Results (12-04-13Z): log sit/recoverable/met/alt/q, ``recover()`` if
KSP will take it, else ``go_space_center`` (Close / Space Center, not
revert) and abort ``not recoverable``. Frozen landed
``recoverable=no`` (13-58-18Z Vessel is destroyed) is that same Close
— do not unpause-spam. Do not wait ``sit=landed`` that never comes. Post-dismiss
``pre_launch`` recoverable is not recovery@EarthFlew. 1 Hz recover line
names sit + recoverable. Still stuck: recover hop debris if KSP will
take it. Dismiss **without** ``recover()``
aborts — it does not bank the HD. Do not wait for a Recover click.
`python main.py splash` / `phase splash` never Hangars. Empty KSC or
pad motor → abort (hop first). Wait for Water; do **not** recover on
first flying recoverable (that is hop, and it kills splash dwell). Start
goo only when `splashed`. One Toggle. Dwell then recover HD.

Retired campaign notes (not Gene names):

`python main.py hop-to-water` Hangars the **named** Valiant hop
(`kspstuff-hop-valiant-east-pbc` / east-bare when seated/VAB). Lights
**vertical** (throttle 1). After `left_pad`, slews AP toward pitch
**65** heading **90** at **10 °/s** and throttle **0.4** (25° from
vertical; gimbal 7.5° is authority) — do **not** slam 65 at light
(16-11-58Z TWR 5 sheared east-bare, apo 5.3 km, no decoupler). Command
east as **`set_direction_and_up`** (north up); do **not** `target_roll=0`
vs zenith (16-57-24Z heading never 090, pad 299 tumble). **Holds
AP through burnout** — do not `disengage` at fuel=0 (15-26-18Z
weathervaned HDG 304, horiz stayed ~25 m/s, never splashed).
**Latch** `hop_apo` (do not recut 0.4 when apo falls — 22-03-59Z
splash 230 m/s). Leftover LF suicide near Water: **watch** TTI ≤12,
**light** at live TTI ≤ 3.5, kill until vz ≥ −10, then TWR≈1 hover
until coast ≤12 (Goo crashTolerance 12; 20 Hz gate — 08-44-32Z recut
at vz −29.9 leftover 60 then loft, splash 119 m/s Shores;
**09-48-51Z** 1 Hz never thr=1, recut leftover 50.4 vz −7.7, hover
unlatched, splash 92.5 m/s; **10-11-27Z** MET 176→209 dump 108.7→crumbs
1.98, MET 208.9 vz −9.4 alt 195 then rebuild splash 62 m/s). Latch
armed on first braking even if the gate cuts. Leftover is spent
**only if** vacuum coast ≤12; else hover (do not slam 1, do not
drop out at vz ≥ −10 — 09-11 TTI≤12 pulse 82 m/s; 09-48 leftover 50
splash 92; 10-11 crumbs splash 62).
Stayputnik still has no torque after cutoff; heading 090 never
holds (pad 299 burn 300 splash 298). Starts the
flying card airborne. Matching leftover already down recovers then
Hangar (22-45-26Z). Matching living leftover: live sit/fuel/recoverable
before light (disk PRELAUNCH is a lie). Dry wreck leftover does not
Toggle. Hangar waits for KSC with no Flight Results before
`launch_vessel` (14-52-25Z). Never revert.
Does **not** recover while flying (hop recover-on-down would kill
splash). Wait `sit=splashed`, then the splash card dwell and HD
recover — same Water wait as `splash`. Landed after left_pad (Shores)
aborts `not splashed`. Pad `sit=landed` after light is hop-off — same
as `_down(flown)`: do not treat it as a Shores miss. Start Flea still
aborts before Hangar: no torque, no gimbal, 18-32 lithobrake 74 m. Do
not fake an east splash on a vertical Flea.

`python main.py hop-splash` Hangars the **named** t7 splash Valiant
(``kspstuff-hop-valiant-t7-splash-pbc`` when seated/VAB). Lights
**vertical** (throttle 1 until ``hop_apo``, then **stay cut** —
18-15-08Z recut at apo<80 km dumped leftover at ~37 km). Leftover
LF suicide near Water (watch TTI ≤12, light at 3.5, kill then TWR≈1
hover until coast ≤ Goo 12 — leftover 57/108, no TTI slam, no vz-cut
rebuild). **No** east slew — do not
glue hop-to-water 090 (16-57-24Z heading never holds; Stayputnik no
wheel). **No** flying Toggle (19-43-18Z T+1 airborne TELEMETRY is
wrong). Wait ``sit=splashed``, then splash
TELEMETRY then goo dwell + HD recover. EC=0 **before** that start does
not abort (17-46-04Z wait; 19-43-18Z dwell — snapshot 0 is not empty
batteries). Splashed leftover (18-03-12Z) starts the card
before recover — leftover-wreck is flying/landed dry, not Water.
If Kerbalism ``Experiment`` modules are gone (18-15-08Z), still start
Stayputnik TELEMETRY PAW and GooExperiment.
``hop_apo`` **80 km** is a real
cut (not FlyingLow 18 km). OffPlan **140 km**. Unmatched leftover
(east-fin PRELAUNCH ghost) recovers without lighting, then Hangar.
Matching leftover enters Flight. Landed after left_pad aborts
``not splashed``. Flea still aborts before Hangar. Crash UI Tracking
Station, not Space Center. Never revert. jsonl includes pitch, AoA, biome.

`python main.py tech-unlock engineering101` (or `phase tech-unlock` with
plan `tech: engineering101`) is **not** a flight. No Hangar, no Toggle,
no Geiger dwell. kRPC 0.6 can open R&D and read the bank; it cannot
buy a node unless an UnlockTech RPC exists. Abort — do not patch the
save. After a real buy, `parts --unlocked` lists `kerbalism-geigercounter`.
Commander `uplink.md` verbs: `hold|cut|no_warp|phys-warp|warp|stage|recover|science|abort_pad`.
`loop.md` is not the stick.
