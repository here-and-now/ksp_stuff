# Building blocks — Gene may only name these

Owned by **Lars Grokman, Vehicle Engineering**. If Gene needs a name
that is not here, parent spawns Lars first. No heredocs. Missing name
means Lars writes it — do not keep leftover Kerbin/Mun compose around
for them.

| Phase | CLI | Expect |
|---|---|---|
| pad | `python main.py pad` / `phase pad` | Kerbalism card start → dwell → recover HD |
| hop | `python main.py hop` / `phase hop` | Hangar Flea uncrewed → light → FlyingLow card start → dwell → recover HD when landed/recoverable (EC=0 with data recovers; leftover HD/no Experiment modules recovers without a fresh start; paused Flight Results / frozen MET recovers debris or leaves flight; do not timeout-dump a live fall) |

`python main.py pad` Hangars `kspstuff-pad-pbc` **uncrewed**. Empty start
with a card is abort.

`python main.py hop` Hangars `kspstuff-hop-flea-pbc` **uncrewed**, then
lights. Does **not** Hangar `kspstuff-pad-pbc` (pad stack is not a hop
motor). Empty space center or leftover pad motor → Hangar the Flea.
`phase hop` on an already-launched hop craft skips Hangar. `hop_apo`
15 km (FlyingLow; cut at target; OffPlan above ~18 km). Ballistic peri
is negative — not OFFPLAN. No chute: wait wreck-recoverable. Empty tanks
after the motor are expected. Start the **flying** card once airborne
(TELEMETRY + thermo; splash goo is not a hop start). Do **not** require a
fresh Experiment start when the HardDrive already has data or Experiment
modules are gone — recover that HD. Empty card on a clean pad still
aborts. EC=0 with HD data recovers on first recoverable; abort timeout
only if the HD is empty. Frozen MET / Flight Results (recoverable never
true) recovers hop debris or `go_space_center` so the HD banks — do not
wait for a Recover click.
Helm `uplink.md` verbs: `hold|cut|no_warp|stage|recover|science|abort_pad`.
`loop.md` is not the stick.
