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
| `rf-ignition-ullage` | 10 (T-470 ×8) | Hop light is **plume**, not ignitions 1→0. kRPC GET throttle is not the burn. Independent setpoint is the RF live. Empty stage is not hop light. Pad-dead-no-plume on a **fed** engine is Lars `hop_factory_pad.py`. Starved Δv 0/0 is `craft fuel` / vab-helper, not RF. Pad 1 g still lights; restart is not free; do not raise ignitions. T-471 owns the live miss. |
| `bigger-dv` | 20 (T-478 ×19) | Loft hang is a **fed** stack — not C-477 (starved `capable: no`). t7-wheel-pbc lithobrake is not recover. Do not Hangar 4t / dv5 / lite / t7-chute Mk16 / C-477. Gus rebuilding. T-406 / T-428 / T-430 stay alts. |
| `vab-helper` | 20 (T-499 ×17) | A hang you cannot prove is **FED** is not capable. FED is not enough: HS splice must leave **collider clearance** (T-500 Hangar 15-14-43Z detonated a FED SAS-HS-tank). `--payload` SAS-first tank is the FED path (T-498); tank-engine splice stays refused (T-497). `craft fuel` dumps attach + `fuelCrossFeed` (T-495). Engine first fire (`sqor=0`) and HS VAB dish still hold. T-503 owns VAB test still pinning C-477 SAS-HS 0.191 after the 0.5 m rebuild. Do not write GameData. Pad flies a fed hang — do not idle. |
| `leftover-ksc` | 4 (T-502 ×3) | Persist must survive a split wreck. Recoverable ground Debris (pad Goo) is leftover — leftover_ship must see it; wait recover by GUID not name. Harmony skip-dup is persist fail-open, not the broom. recover() is persist-then-KSC; flying rec=0 blobs that throw Kerbalism persist make recover a no-op. Quit KSP is walk home that sit. Never leftover-ksc load. Never revert. Code T-501. |
