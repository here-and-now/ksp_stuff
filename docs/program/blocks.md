# Building blocks — Gene may only name these

Owned by **Lars Grokman, Vehicle Engineering**. If Gene needs a name
that is not here, parent spawns Lars first. No heredocs. Missing name
means Lars writes it — do not keep leftover Kerbin/Mun compose around
for them.

| Phase | CLI | Expect |
|---|---|---|
| pad | `python main.py pad` / `phase pad` | Hangar **seated/VAB craft file** uncrewed (`kspstuff-geiger-pbc` Geiger Counter **part**, F-013). Not `pad_pbc()`. Dry-launch only if current stage is 0 (do not light a Flea). Dwell watches `wait science run= rem=` and UT, **not** vessel MET. Physics warp 2–4× on pad/landed; **rails 0**; never WarpTo; 1× after dwell. Empty HD with nothing recording still aborts. |
| hop | `python main.py hop` / `phase hop` | Hangar **seated/VAB craft file** uncrewed (Valiant sit: `kspstuff-hop-valiant-pbc`; Hammer sit: `kspstuff-hop-hammer-pbc`, 2HOT — F-013). Not Flea, not exact pad/geiger names. Light → bound flying card (thermo on 2HOT not Stayputnik). `hop_apo` Gene **80 km** is a real cut on Valiant; FlyingLow clamp is **8–18 km**. OffPlan apo > **50 km** FlyingLow, or **140 km** Space when the card is FlyingHigh. Unmatched leftover (PRELAUNCH Flea vs seated Valiant) recovers without lighting, then Hangars the seated craft. Recover HD when down (`vessel.recover()`). Low flying **≤250 m** calls `recover()` only if `recoverable` (199 m living hop). MET-still + q=0 flying is **down now** (do not wait the 600 s crash UI). Frozen MET + flying + q=0 + low alt is **Catastrophic Flight Results**: log sit/recoverable/met/alt/q, `recover()` if recoverable, else `go_space_center` (Close / Space Center, not revert) and abort. Do not wait `sit=landed` (12-04-13Z). Post-dismiss `pre_launch` recoverable is **not** recovery@EarthFlew. 1 Hz recover line names sit + recoverable. Live kRPC hop ship leftover enters Flight — no second Hangar. Dead GUID / FLYING Debris is not leftover; empty Tracking Hangars. Splash goo is **not** a hop start. |
| splash | `python main.py splash` / `phase splash` | Leftover hop Flea only — no Hangar, no light, no pad motor. SpaceCenter leftover enters Flight. Wait until **splashed** (do not recover while flying even if recoverable). One Toggle `mysteryGoo` on GooExperiment. Dwell (641 s catalog, EC cap). Recover HD when splashed/recoverable. Landed is not Water. EC=0 with HD data recovers; empty HD aborts. Frozen MET / Flight Results recovers debris or leaves flight. |
| hop-to-water | `python main.py hop-to-water` / `phase hop-to-water` | **Refused.** Start Flea cannot steer Cape Shores to Water (Stayputnik no torque, Flea no gimbal, no chute). Vertical hop lithobrakes Shores (18-32: 74 m). Do not Hangar. Do not fake an east splash. need_builder for east pitch, or skip splash. |
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
pad/geiger → Hangar the hop motor. ``phase hop`` on an already-launched
matching hop craft skips Hangar. Leftover in tracking at SpaceCenter
enters Flight — do **not** Hangar a second stack. A kRPC active proxy
whose ``.name`` raises ``No such vessel`` is gone — scan the pool;
empty Tracking Hangars. Disk desk ``sit=FLYING`` debris is not leftover.
Unmatched leftover (Flea vs seated Valiant) ``recover()`` without lighting
— do not Hangar over it, then Hangar the seated craft. ``hop_apo`` 18 km
is throttle-cut (solids ignore it); FlyingHigh unclamps to Space so Gene
80 km is a real cut. OffPlan is FlyingLow **50 km** or FlyingHigh **140 km**
Space, not the 18 km clamp — Hammer 22-56Z 18.8 km was still FlyingLow. Ballistic peri
is negative — not OFFPLAN. No chute: wait wreck-recoverable. Empty tanks
after the motor are expected. Start the **flying** card once airborne
(TELEMETRY on Stayputnik + thermo on 2HOT; one Toggle per id; splash goo
is not a hop start). Do **not** Toggle Stayputnik ``temperatureScan`` —
that second start stops Kerbalism (1119Z). A hop this process
**lit** always starts that card. Do **not** skip start because idle
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
revert) and abort ``not recoverable``. Do not wait ``sit=landed`` —
that sit never comes. Post-dismiss
``pre_launch`` recoverable is not recovery@EarthFlew. 1 Hz recover line
names sit + recoverable. Still stuck: recover hop debris if KSP will
take it. Dismiss **without** ``recover()``
aborts — it does not bank the HD. Do not wait for a Recover click.
`python main.py splash` / `phase splash` never Hangars. Empty KSC or
pad motor → abort (hop first). Wait for Water; do **not** recover on
first flying recoverable (that is hop, and it kills splash dwell). Start
goo only when `splashed`. One Toggle. Dwell then recover HD.

`python main.py hop-to-water` does **not** fly. This Flea cannot pitch
east: no reaction wheel, no SRB gimbal, fins are passive, chute is
survivability 15. 18-32 fell on Shores. Gene: skip splash, or Gus a
stack that can steer.

`python main.py tech-unlock engineering101` (or `phase tech-unlock` with
plan `tech: engineering101`) is **not** a flight. No Hangar, no Toggle,
no Geiger dwell. kRPC 0.6 can open R&D and read the bank; it cannot
buy a node unless an UnlockTech RPC exists. Abort — do not patch the
save. After a real buy, `parts --unlocked` lists `kerbalism-geigercounter`.
Commander `uplink.md` verbs: `hold|cut|no_warp|stage|recover|science|abort_pad`.
`loop.md` is not the stick.
