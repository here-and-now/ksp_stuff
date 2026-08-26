# World model — House Grokman

Gene Grokman, Flight Director chairs **flight** layers. Mortimer chairs
**Practice**. Others propose. Dump parked:
`docs/archive/2026-08-26-org-rsi/world-model.md`.

| Layer | Owner | Source of truth |
|---|---|---|
| **Facts** | disk | `docs/program/desk.md` / `python main.py world` |
| **Meaning** | Gene | Learn from `tickets landing` envelope |
| **Horizon** | Linus | remaining subjects, what a node buys |
| **Story** | Verena | `docs/press/` + README — never invent orbit |
| **Practice** | Mortimer | pitfalls / house / QOL — tickets |
| **Dynamics** | Katherine | `telem --window` / landing envelope |

Kardashev III is creed here. Joke in the TUI. Nobody preaches mid-burn.

## Practice (Mortimer last-write)

Patterns still true as ops. Not a dump. Not a dispatch novel.

| Stem | Count | Pitfall |
|---|---|---|
| `inner-circle-plan` | 1 (T-519) | Lars / Gus / Linus overfit the last miss (Linus rebinds, Gus rehangs, Lars retunes pulse) instead of sitting one achievable plan. Confer on `docs/program/agree.md` (sit, hang, bind duration vs High window, recover yes/no, MECO). Hank hires the three in parallel on **one** `ops --tag plan` ticket, then they split. Not leftover wreck tickets. Not Gene as merge. Not a 15 min novel. Katherine opt-in (`ops --tag ask --desk katherine` / `--tag dynamics`). Wreck rec=no re-flies last `cli:` — do not reopen the plan. Fly ready that still pays `agree.md` still flies. Kernel emit is Wernher `ops.py`. |
| `telem-eyes-library` | 8 (T-508) | throttle / thrust / plume / fuel-frozen while parts intact is **unexpected** — not FAR shear. Radio (`ship.md`) is the bus; do not wait hop stdout / last-flight `shear`. 16-05-34Z: MET 21 thrust=0 fuel frozen parts=30; hop logged shear 30→9 at impact. Kernel still names parts-drop as hop abort — Wernher T-511 (Tape / telem flags / last-flight class; not hop.py). Engine cutoff is Lars T-509 (`rf-ignition-ullage`). After CLI: `telem --window`. Thin 13/68s is `thin-tape`, not this letter. |
| `rf-ignition-ullage` | 12 (T-510 ×11) | Hop light is **plume**, not ignitions 1→0. kRPC GET throttle is not the burn. Independent setpoint is the RF live. Empty stage is not hop light. Pad-dead-no-plume on a **fed** engine is Lars `hop_factory_pad.py` (T-471). After hop light keep MainThrottle 1 until lid MECO (T-509). **Honest MECO is not engine-dead**: 16-23-52Z held MET 22–128 thrust 89–100 kN fuel 2015→216 parts=30; burnout MET 147 alt 88 km fuel 28 thrust 0 apo 268 km — leftover fuel at MECO is the coast. MET-21 throttle 1 + thrust 0 + fuel frozen + parts intact **with a burn still owed** is this stem, not shear. Starved Δv 0/0 is `craft fuel` / vab-helper, not RF. Pad 1 g still lights; restart is not free; do not raise ignitions. |
| `bigger-dv` | 22 (T-505 ×21) | Loft hang is **C-504** `kspstuff-hop-valiant-proc-loft-pbc` (FED, Hangar-safe, no HS/chute). Pad belongs to C-504 until `generalRocketry` 20 then one node after. 16-23-52Z held through burnout apo 268 km rec=no (coast shear) — iterate **this** hang. C-477 is the blob exhibit (Hangar 15-52-38Z parts=397 even after T-500 dish) — do not Hangar. t7-wheel-pbc lithobrake is not recover. Do not Hangar 4t / dv5 / lite / t7-chute Mk16 / C-477. T-406 / T-428 / T-430 stay alts. |
| `vab-helper` | 22 (T-507 ×21) | A hang you cannot prove is **FED** is not capable. FED is not enough: HS splice must leave **collider clearance** (T-500). C-504 loft is **no-HS** — a helper that writes a loft hang must autostrut Heaviest/rigid + stage-engine `sqor=0` **without** requiring HS/chute. T-506 owns that helper. `--payload` SAS-first tank is the FED path (T-498); tank-engine splice stays refused (T-497). `craft fuel` dumps attach + `fuelCrossFeed` (T-495). Engine first fire and HS VAB dish still hold when a hang *has* an HS. T-503 owns VAB test still pinning C-477 SAS-HS 0.191. Do not write GameData. Pad flies C-504 — do not idle for helpers. |
| `leftover-ksc` | 4 (T-502 ×3) | Persist must survive a split wreck. Recoverable ground Debris (pad Goo) is leftover — leftover_ship must see it; wait recover by GUID not name. Harmony skip-dup is persist fail-open, not the broom. recover() is persist-then-KSC; flying rec=0 blobs that throw Kerbalism persist make recover a no-op. Quit KSP is walk home that sit. Never leftover-ksc load. Never revert. Code T-501. |
