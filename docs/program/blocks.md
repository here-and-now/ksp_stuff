# Building blocks — Gene may only name these

Owned by **Lars Grokman, Vehicle Engineering**. If Gene needs a name
that is not here, parent spawns Lars first. No heredocs. Missing name
means Lars writes it — do not keep leftover Kerbin/Mun compose around
for them.

| Phase | CLI | Expect |
|---|---|---|
| pad | `python main.py pad` / `phase pad` | Hangar **seated/VAB craft file** uncrewed (`kspstuff-geiger-pbc` Geiger Counter **part**, F-013). Not `pad_pbc()`. Dry-launch only if current stage is 0 (do not light a Flea). Dwell watches `wait science run= rem=` and UT, **not** vessel MET. Physics warp 2–4× on pad/landed; **rails 0**; never WarpTo; 1× after dwell. Empty HD with nothing recording still aborts. |
| hop | `python main.py hop` / `phase hop` | Hangar **seated/VAB craft file** uncrewed (Valiant sit: `kspstuff-hop-valiant-pbc`; Hammer sit: `kspstuff-hop-hammer-pbc`, 2HOT — F-013). Not Flea, not exact pad/geiger names. Light → bound flying card (thermo on 2HOT not Stayputnik). FlyingLow Toggle **airborne**. FlyingHigh Toggle **only ≥50 km** — not T+1 FlyingLow (~100 m); **one** Toggle (a second at the lid stops Kerbalism). **13-31-03Z:** t7 apo 88.8 km, lid MET~98 alt 50.4 km, card started T+1 FlyingLow, splash recover sci +0. `hop_apo` Gene **80 km** is a real cut on Valiant; FlyingLow clamp is **8–18 km**. OffPlan apo > **50 km** FlyingLow, or **140 km** Space when the card is FlyingHigh. **13-08-57Z:** Valiant + 2×FL-T100 dry MET~27 alt~7 km apo **12.3 km** — never FlyingHigh; that loft is Gus tanks, not hop.py. Unmatched leftover (PRELAUNCH Flea vs seated Valiant) recovers without lighting, then Hangars the seated craft. Recover HD when down (`vessel.recover()`). Low flying **≤250 m** calls `recover()` only if `recoverable` (199 m living hop). MET-still + q=0 flying is **down now** (do not wait the 600 s crash UI). Frozen MET + flying + q=0 + low alt is **Catastrophic Flight Results**: log sit/recoverable/met/alt/q, `recover()` if recoverable, else `go_space_center` (Close until KSC, not revert) and abort. Frozen landed `recoverable=no` is the same dialog (13-58-18Z Vessel is destroyed): Close now, do not unpause-spam `recover()`. Do not wait `sit=landed` that never comes (12-04-13Z). Post-dismiss `pre_launch` recoverable is **not** recovery@EarthFlew. 1 Hz recover line names sit + recoverable. Live kRPC hop ship leftover enters Flight — no second Hangar. Gate live sit/fuel/recoverable before light (disk PRELAUNCH is a lie). Dead GUID / FLYING Debris is not leftover; empty Tracking Hangars leftover scan, but **empty Tracking is not KSC clean** — Flight Results over Tracking (**14-52-25Z**) still has Revert; Hangar does not `launch_vessel` until scene is KSC and `can_revert_to_launch` is false. Splash goo is **not** a hop start. |
| splash | `python main.py splash` / `phase splash` | Leftover hop Flea only — no Hangar, no light, no pad motor. SpaceCenter leftover enters Flight. Wait until **splashed** (do not recover while flying even if recoverable). One Toggle `mysteryGoo` on GooExperiment. Dwell (641 s catalog, EC cap). Recover HD when splashed/recoverable. Landed is not Water. EC=0 with HD data recovers; empty HD aborts. Frozen MET / Flight Results recovers debris or leaves flight. |
| hop-to-water | `python main.py hop-to-water` / `phase hop-to-water` | **Valiant gimbal.** Hangar seated hop craft (Gus Water sit: `kspstuff-hop-valiant-east-pbc` / east-bare, 2×FL-T100 + LV-T15). Light **vertical**. **Slew** pitch **25°** from vertical, heading **90** (east), **after left_pad** at throttle **0.4** — do **not** slam `target_pitch=65` at light TWR 5 (**16-11-58Z** east-bare apo **5.3 km**, joints shear, no decoupler, Stayputnik no wheel). **Hold AP through burnout** — do not disengage at fuel=0 (**15-26-18Z** pitch 25 logged, horiz ~25 m/s, weathervaned HDG 304 after cutoff, lithobrake Shores never splashed). Gimbal **7.5°** is authority — **7.5° from vertical stayed Shores** (14-33-29Z apo 12.1 km, horiz ~34 m/s, lithobrake 74.5 m, never splashed). Stayputnik has no torque after cutoff — holding AP is the command, not a coast-SAS. Flying card once airborne. **Do not recover** on first flying recoverable. Wait **splashed**, then splash dwell + HD recover. Landed after **left_pad** is not Water (Shores abort `not splashed`). Pad `sit=landed` after light is hop-off (14-45-33Z MET 0.6, 37.5 m / 49 m/s) — do not abort before airborne. Flea still **refused** (no Hangar, no fake splash). Unmatched leftover recovers first, then Hangar. Matching leftover enters Flight. Gate live sit/fuel/recoverable before light — disk PRELAUNCH is a lie (**14-52-25Z** flying MET 13.8 fuel=0, science started on wreck). Dry wreck leftover: recover if `recoverable`, else Close until KSC (`can_revert` false — **14-52-25Z** Flight Results over Tracking is not KSC) and abort — do not light, do not Toggle. Never revert. Hangar waits; do not `launch_vessel` over the modal. `hop_apo` 80 km is the wrong cut for this 2×T100 hang. |
| tech-unlock | `python main.py tech-unlock [node]` / `phase tech-unlock` | Ground kRPC try. Disk checks tree/parents/bank. Opens R&D. **0.6 has no UnlockTech RPC — aborts.** Paid node: **Mortimer** edits `persistent.sfs` ResearchAndDevelopment only (Os 2026-08-20). Not GameData. Not a pad/geiger sit (F-013). |

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
is negative — not OFFPLAN. No chute: wait wreck-recoverable. Empty tanks
after the motor are expected. Start the **flying** card once airborne
(FlyingLow) or at alt **≥50 km** (FlyingHigh — 13-31-03Z Toggle at T+1
FlyingLow banked crumbs, not the lid). TELEMETRY on Stayputnik + thermo
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

`python main.py hop-to-water` Hangars the **named** Valiant hop
(`kspstuff-hop-valiant-east-pbc` / east-bare when seated/VAB). Lights
**vertical** (throttle 1). After `left_pad`, slews AP toward
`target_pitch=65` `target_heading=90` at **10 °/s** and throttle
**0.4** (25° from vertical; gimbal 7.5° is authority) — do **not**
slam 65 at light (16-11-58Z TWR 5 sheared east-bare, apo 5.3 km, no
decoupler). **Holds AP through burnout** — do not `disengage` at
fuel=0 (15-26-18Z weathervaned HDG 304, horiz stayed ~25 m/s, never
splashed). Stayputnik still has no torque after cutoff. Starts the
flying card airborne. Matching leftover: live sit/fuel/recoverable
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

`python main.py tech-unlock engineering101` (or `phase tech-unlock` with
plan `tech: engineering101`) is **not** a flight. No Hangar, no Toggle,
no Geiger dwell. kRPC 0.6 can open R&D and read the bank; it cannot
buy a node unless an UnlockTech RPC exists. Abort — do not patch the
save. After a real buy, `parts --unlocked` lists `kerbalism-geigercounter`.
Commander `uplink.md` verbs: `hold|cut|no_warp|stage|recover|science|abort_pad`.
`loop.md` is not the stick.
