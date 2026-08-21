# Building blocks — Gene may only name these

Owned by **Lars Grokman, Vehicle Engineering**. If Gene needs a name
that is not here, parent spawns Lars first. No heredocs. Missing name
means Lars writes it — do not keep leftover Kerbin/Mun compose around
for them.

| Phase | CLI | Expect |
|---|---|---|
| pad | `python main.py pad` / `phase pad` | Hangar **seated/VAB craft file** uncrewed (`kspstuff-geiger-pbc` Geiger Counter **part**, F-013). Not `pad_pbc()`. Dry-launch only if current stage is 0 (do not light a Flea). Dwell watches `wait science run= rem=` and UT, **not** vessel MET. Physics warp 2–4× on pad/landed; **rails 0**; never WarpTo; 1× after dwell. Empty HD with nothing recording still aborts. |
| hop | `python main.py hop` / `phase hop` | Hangar **seated/VAB craft file** uncrewed (Hammer sit: `kspstuff-hop-hammer-pbc`, 2HOT, no Geiger — F-013). Not Flea, not pad/geiger. Light → FlyingLow card (thermo on 2HOT not Stayputnik). `hop_apo` Gene 18 km is a **cut wish** (SRB cannot hold). OffPlan apo > **50 km** FlyingLow, not the 18 km clamp. Recover HD when down. Leftover matching that name in tracking enters Flight — no second Hangar. Splash goo is **not** a hop start. |
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
``kspstuff-pad-pbc`` or ``kspstuff-geiger-pbc``. Empty KSC or leftover
pad/geiger → Hangar the hop motor. ``phase hop`` on an already-launched
matching hop craft skips Hangar. Leftover in tracking at SpaceCenter
enters Flight — do **not** Hangar a second stack. ``hop_apo`` 18 km
is throttle-cut (solids ignore it). OffPlan is FlyingLow **50 km**, not
the 18 km clamp — Hammer 22-56Z 18.8 km was still FlyingLow. Ballistic peri
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
only if the HD is empty. Frozen MET / Flight Results (recoverable never
true) recovers hop debris or `go_space_center` so the HD banks — do not
wait for a Recover click.
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
