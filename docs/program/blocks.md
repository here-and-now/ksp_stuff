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
| hop-to-water | `python main.py hop-to-water` / `phase hop-to-water` | **Valiant gimbal.** Hangar seated hop craft (Gus Water sit: `kspstuff-hop-valiant-east-pbc` / east-bare, 2×FL-T100 + LV-T15). Light **vertical**. **Slew** pitch **25°** from vertical, heading **90** (east), **after left_pad** at throttle **0.4** — do **not** slam `target_pitch=65` at light TWR 5 (**16-11-58Z** east-bare apo **5.3 km**, joints shear, no decoupler, Stayputnik no wheel). Point east with surface **`target_direction`**; do **not** `target_roll=0` near vertical (**16-57-24Z** heading never 090: pad **299**, tumble, horiz max **85.6**, apo **3.66 km**, lithobrake Shores). **090 is hardware-dead** on Stayputnik (no wheel): **23-15-52Z** pad **299** burn **300** splash **304**, three 080–100 fly-throughs after cutoff — do **not** fake 090 in code. **Hold AP through burnout** — do not disengage at fuel=0 (**15-26-18Z** pitch 25 logged, horiz ~25 m/s, weathervaned HDG 304 after cutoff, lithobrake Shores never splashed). **Latch** `hop_apo` — do **not** recut 0.4 when apo falls (**22-03-59Z** MET 81.8 thr 0, MET 84/136 thr 0.4 leftover dump, splash **230 m/s** Shores). Leftover LF is a **suicide burn** near Water, not apo-1 — **arm TTI ≤12**, **hold until vz ≥ −20 is seen** (20 Hz gate; do **not** predict-cut); TTI rising is not a recut (**22-57-36Z** MET 179.7 thr 1, MET 181 TTI 19 cut then relights lofted leftover, splash **119 m/s**). **23-15-52Z** armed tti 18 alt 3.75 km: MET 173 vz **−65** still thr 1, MET 174 vz **+24** fuel 47, leftover loft, splash **220 m/s** Shores. **08-44-32Z** predictor recut MET 178 thr 0 vz **−29.9 leftover 60.6**, relight MET 187 loft vz **+85**, splash **119 m/s** Shores, Experiment modules gone. **09-11-59Z** seen-vz recut MET 179.2 vz **−19.3 leftover 57**, then TTI≤12 pulse-relight to crumbs, splash **82 m/s** Shores, Experiment modules gone. **09-48-51Z** hop_apo latch MET **79.2 leftover 110.1**. Suicide 1 Hz **never thr=1** (20 Hz gate between Telem.read). Recut leftover **50.4 vz −7.7** then TTI≤12 pulses to crumbs; splash heading **296** horiz **7.66** speed **92.5** landing hard Shores. Gate cut before **suicide_armed** latched — T-040 hover never lit. **Watch** TTI ≤12, **light** live TTI ≤ **3.5**, latch armed even if the gate cuts. Crumb leftover is not a relight. Leftover after the vz-cut is **spent only if** vacuum coast ≤ **GooExperiment crashTolerance 12** — else **TWR≈1 hover** until coast ≤12 (do not slam throttle 1, do not drop out at vz ≥ **−10**). **10-11-27Z** hop_apo MET **79.4 leftover 108.7**. MET **176.1** thr 0 leftover 108.7 vz **−223** alt 2415; 20 Hz gate MET **176→209** dumped **108.7→crumbs 1.98** (1 Hz never thr=1). MET **208.9** thr 0 fuel **1.98** speed **9.2** vz **−9.4** alt **195**, then rebuild splash heading **305** horiz **2.00** speed **62.3** landing hard Shores. 09-11 recut at 1766 m coasts ~186 m/s; chutes LOCKED. **090 is hardware-dead** (Stayputnik no wheel): **08-44-32Z** pad **299** burn **301** splash **298**. Gimbal **7.5°** is authority — **7.5° from vertical stayed Shores** (14-33-29Z apo 12.1 km, horiz ~34 m/s, lithobrake 74.5 m, never splashed). Stayputnik has no torque after cutoff — holding AP is the command, not a coast-SAS. Flying card once airborne. **Do not recover** on first flying recoverable. Wait **splashed**, then splash dwell + HD recover. Landed after **left_pad** is not Water (Shores abort `not splashed`). Pad `sit=landed` after light is hop-off (14-45-33Z MET 0.6, 37.5 m / 49 m/s) — do not abort before airborne. Flea still **refused** (no Hangar, no fake splash). Unmatched leftover recovers first, then Hangar. Matching leftover already down (splashed/landed dry **22-45-26Z**) recovers, then Hangar seated craft — do **not** exit recovered. Matching living leftover enters Flight. Gate live sit/fuel/recoverable before light — disk PRELAUNCH is a lie (**14-52-25Z** flying MET 13.8 fuel=0, science started on wreck). Dry wreck leftover: recover if `recoverable`, else Close until KSC (`can_revert` false — **14-52-25Z** Flight Results over Tracking is not KSC) and abort — do not light, do not Toggle. Never revert. Hangar waits; do not `launch_vessel` over the modal. `hop_apo` 80 km is the wrong cut for this 2×T100 hang. |
| hop-splash | `python main.py hop-splash` / `phase hop-splash` | **Vertical t7 splash loft.** Hangar seated `kspstuff-hop-valiant-t7-splash-pbc`. Light **vertical**. **No** east slew (16-57-24Z heading never 090; Stayputnik no wheel; hop-to-water 090 is dead). **No** flying Toggle — Linus splash TELEMETRY **then** mysteryGoo 641 s (**19-43-18Z** T+1 airborne TELEMETRY is wrong). `hop_apo` Gene **80 km** is a real cut **and stays cut** — do **not** recut throttle 1 when apo falls (**18-15-08Z** / **19-43-18Z** / **21-14-09Z** thr 1 at apo<80 km, leftover dump ~37 km). Leftover LF is a **suicide burn** near Water (**watch TTI ≤12, light live TTI ≤ 3.5, kill then TWR≈1 hover until coast ≤12** — **22-57-36Z** TTI-rise recut; **23-15-52Z** overburn past −20; **08-44-32Z** predict-cut at −30 leftover loft; **09-11-59Z** leftover 57 pulse-relight after vz-cut; **09-48-51Z** 1 Hz never thr=1 leftover 50 splash 92; **10-11-27Z** dump 108→crumbs then 9→62). Leftover after vz ≥ −10 is spent only if coast ≤ Goo 12; else hover, do not slam 1. Latch armed even if the gate cuts. FlyingLow 18 km clamp is wrong; 13-49 apo 88.9 km splashed. OffPlan **140 km**. **Do not recover** on first flying recoverable. Wait **splashed**, then splash dwell + HD recover. **EC=0 before TELEMETRY/goo starts does not abort** (17-46-04Z wait; **19-43-18Z dwell** — 2401 EC at 68 m flying, snapshot 0 on first splashed sample). **Splashed leftover** (18-03-12Z MET 532 fuel=0 EC=0 recoverable=yes biome Shores) **starts the splash card** — do not leftover-wreck recover dark. **Kerbalism Experiment modules gone at splash** (18-15-08Z Forest MET 475, skip no modules, wanted TELEMETRY): still Toggle Stayputnik TELEMETRY PAW + GooExperiment. Landed after **left_pad** is Shores (`not splashed`). Pad `sit=landed` after light is hop-off — do not abort before airborne. Flea still **refused**. Unmatched leftover (**east-fin PRELAUNCH ghost**) recovers without lighting, then Hangar t7-splash. Matching leftover enters Flight. Gate live sit/fuel/recoverable before light. Crash UI Tracking Station, **not** Space Center (pad reload). Never revert. jsonl logs pitch/AoA/biome. |
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
**vertical** (throttle 1). After `left_pad`, slews AP toward pitch
**65** heading **90** at **10 °/s** and throttle **0.4** (25° from
vertical; gimbal 7.5° is authority) — do **not** slam 65 at light
(16-11-58Z TWR 5 sheared east-bare, apo 5.3 km, no decoupler). Command
east as surface **`target_direction`**; do **not** `target_roll=0`
near vertical (16-57-24Z heading never 090, pad 299 tumble). **Holds
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
Commander `uplink.md` verbs: `hold|cut|no_warp|stage|recover|science|abort_pad`.
`loop.md` is not the stick.
