# Words we use

Os asked what else sounds like leftover jargon. Keep MCC/SpaceX
titles. Drop RAF/spy/radio-compact.

| Word | Verdict |
|---|---|
| **sortie** | **Retired.** RAF/USAF. We say **run** (one `python main.py pad`). Folder `logs/`. |
| **1235Z** | **Retired** as speech. Earth UTC with seconds: `2026-08-20T12-35-42Z`. |
| **mission** | Tape id folder `docs/missions/<id>/`. Uncrewed tape id is `uncrewed`, not a kerbal seat. Crewed Commander dossier stays `jebediah`. |
| **handoff** | Shift-change. File is `last-flight.md`. |
| **Commander** | Abort officer on crewed/firsts (`commander: jebediah`). The hop/pad **pid** is the **control** writer. kRPC GET readers are other Sessions; they do not take the stick. Uncrewed: parent starts `cli:`. |
| **uplink** | RF to a spacecraft. File is a stick note. Keep until it hurts. |
| **slate** | Film. Mortimer’s board. Keep. |
| **capable:** | Gus sign-off. Keep. **FED** proof (`python main.py craft fuel <craft>`) is part of the stamp: tanks must reach the engine. Starved / `fuelCrossFeed=False` inline HS is `capable: no` (C-477). |
| **FED** | Fuel path from tank to engine on disk. `craft fuel` dumps attach + `fuelCrossFeed`. Ablator-only on the engine is starved. |
| **go: / wait** | MCC. Keep. |
| **campaign:** | Fly ticket `payload.campaign` (`protocol fly` prints it). `uncrewed` = parent re-flies last `cli` on clean 0 without Gene. Uncrewed `payload.learn` is hop-exit `attach-run` (kernel), not Gene. `ops next` hires Gene for Learn only when campaign is not `uncrewed` and learn is empty. `none` = Learn each hop. Seated `plan.md` is envelope (`hop_apo` / `expect_*` / `emergencies`) — not a copy of `go` / `cli` / `campaign`. |
| **CAPCOM** | NASA loop. **Walt**. TUI is phase start / phase end / unexpected only. Verena is Communications. Keep the split. |
| **Hangar** | KSP building + our launch helper. Keep. |
| **leftover / KSC** | Space Center wreck or unmatched vessel (includes timeout still-flying). **Hank** walk home: `recover()` if recoverable, else Close (`recover-probe --recover` when recoverable). Commander hop does not recover leftover. This-hop splash HD after a briefed dwell is mission. Never revert. |
| **leftover-ksc** | **Retired.** Named save/load of the overlay looked like a reload / return to pre-launch. Os disabled reverting flights. Overlay dismiss is `recover()` + Close. Never that load. |
| **pad** | Launch pad / `python main.py pad`. Keep. |
| **F-014 / I-012** | Gym ids live only inside a ticket **title**. Speech is the twin **T-id** (F-014 → T-184). |
| **need_*** | Do not emit. Open `--type control|vehicle|science|…`. Not a hire token. |
| **world model** | `docs/program/world-model.md`. Gene chairs flight layers. Mortimer chairs **Practice**. |
| **Practice** | House pitfalls / QOL / still-true ops. Mortimer last-write. |
| **improve:** | Leftover blob. After the hire: `tickets feedback T-NNN --claim "…"` on the work ticket. Stumble *during* work: `type=ops --tag feedback` or `type=rsi`. `I-NNN` twins are tickets. |
| **tickets feedback** | Mandatory after every hire. `--claim` required; `--evidence` `--owner` `--real` optional. Appends `payload.findings` on the packet T-id. Close harvests `close_why` if empty. Not Return keys. Not a child ticket per hire. |
| **ask:** | Leftover. Open `type=ops --tag ask` (desk = addressee). P1 if it blocks `go`. |
| **explore:** | Leftover. Open `type=ops --tag explore` P3. Rare field itch. |
| **note-tech.md** | **MISSING / retired.** Parked mailbox (`docs/archive/2026-08-26-org-rsi/note-tech.md`). Not a desk bus. Miss opens `type=control\|recover`. |
| **hop light / ship.md** | `hop light` on hop stdout is pad plume — **not airborne**. Parent mid-hop reads `ship.md`. Do not wait hop stdout. Lock live ≠ flying. Sit/MET/log disagree → one `stuck-<stem>` PNG, then read it. |
| **desk** | `python main.py desk` writes `docs/program/desk.md` — lock, hangar, f013, sci, stack. Packet food. Gitignored live tape. |
| **KSP-RO** | Parked Express RO tree. Do not seat. Live gym is `~/Games/KSP-rss` / letsgrok. |
| **science-scan** | Linus. Live MM experiment defs + leftovers vs REACH. Samples recover; files credit while recording. |
| **comms** | Gus/Linus. Disk dump is ConfigCache (TL rates, craft, ground LIVE/SILENT). Live RA kRPC is `conn.real_antennas` (Os 2026-08-25). Do not cheat a link. |
| **Flight Dynamics** | Katherine. Tape windows (`telem --window`), not jsonl in the prompt. Relays by ticket. Not Linus bind, not Lars burns, not Wernher schema. |
| **sit-card** | **Retired.** Sit is `python main.py desk` / `desk.md`. |
| **krpc.md** | Wernher’s desk briefing. Traps stay in `agent-notes.md`. Never write GameData. |
| **tech-unlock** | Catalog CLI (kRPC). 0.6 has no purchase RPC — aborts. Paid node: Mortimer edits the save then `python main.py load rd-<node>`. **Never** `load persistent` (F-014 / I-010). |
| **Kerman** | **Retired house name.** We are **Grokman**. Stock KSP roster may still say Kerman; Hangar aliases it. |
| **ksp-ceo.md** etc. | **Retired.** Agent files are `mortimer.md`, `gene.md`, `linus.md`, `gus.md`, `lars.md`, `wernher.md`, `verena.md`, `katherine.md`. Shared writer: `pilot.md`. Spawn types match those names. |

Packet field is `live_run:`, path `docs/missions/<id>/logs/`.
