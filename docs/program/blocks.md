# Building blocks — Gene may only name these

Owned by the **stack engineer** (`ksp-stack`). If Gene needs a name
that is not here, parent spawns `ksp-stack` first. No heredocs.

| Phase | CLI | Plan keys | Expect | Not for |
|---|---|---|---|---|
| pad | `python main.py pad` / `phase pad` | craft, emergencies | start Kerbalism card → dwell (HD done or EC budget) → recover; empty HD + EC=0 aborts | crewed Mk1, hop, mun |
| recover | `python main.py phase recover` | parking_peri | peri ≥ air+extra | pad compose |

`python main.py pad` Hangars `kspstuff-pad-pbc` **uncrewed**, starts
Kerbalism `Experiment` modules via `part.modules` (field id / cfg /
part name — not PAW `Module.fields`), **dwells on the pad** until those
slots are done (Has Data / remaining / stopped after running, else cfg
`data_rate` × ScienceDefs size, **capped by remaining EC / `ec_rate`**)
with a `Telem` pulse — not FlightWatch. Watches EC/reliability/wreck.
Pad `pre_launch` EC=0 **recovers** if the HD has data or a slot already
ran; abort only if the HD is empty. Gene uplink `abort_pad` / `recover`
/ `hold` aborts the dwell. Recovers only if the briefed experiments
started **and** the vessel is recoverable. Do not recover on the Start
tick. Empty start with a card is an honest abort (pad cleared), not
exit 0. `science_ids=()` is Gene briefed none. `phase pad` is that
sequence on an already launched vessel.

Do **not** fly `hop` or `mun` (Kerbin-era compose). Helm takes `uplink.md`
verbs `hold|cut|no_warp|stage|recover|science|abort_pad` — same callables
as the helm. `loop.md` is not the stick. Missing name → `ksp-stack`.
