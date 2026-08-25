# Words we use

Os asked what else sounds like leftover jargon. Keep MCC/SpaceX
titles. Drop RAF/spy/radio-compact.

| Word | Verdict |
|---|---|
| **sortie** | **Retired.** RAF/USAF. We say **run** (one `python main.py pad`). Folder `logs/`. |
| **1235Z** | **Retired** as speech. Earth UTC with seconds: `2026-08-20T12-35-42Z`. |
| **mission** | Seated folder `docs/missions/jebediah/`. Not “dossier.” |
| **handoff** | Shift-change. File is `last-flight.md`. |
| **Commander** | Abort officer on crewed/firsts (`commander: jebediah`). The hop/pad **pid** is the Flight writer. Uncrewed: parent starts `cli:`. |
| **uplink** | RF to a spacecraft. File is a stick note. Keep until it hurts. |
| **slate** | Film. Mortimer’s board. Keep. |
| **capable:** | Gus sign-off. Keep. |
| **go: / wait** | MCC. Keep. |
| **campaign:** | Fly ticket `payload.campaign` (`protocol fly` prints it). `uncrewed` = parent re-flies last `cli` on clean 0 without Gene. Uncrewed `payload.learn` is hop-exit `attach-run` (kernel), not Gene. `ops next` hires Gene for Learn only when campaign is not `uncrewed` and learn is empty. `none` = Learn each hop. Plan.md is a render. |
| **CAPCOM** | NASA loop. Walt. Verena is Communications. Keep the split. |
| **Hangar** | KSP building + our launch helper. Keep. |
| **leftover / KSC** | Space Center wreck or unmatched vessel (includes timeout still-flying). **Hank** walk home: `recover()` if recoverable, else Close (`recover-probe --recover` when recoverable). Commander hop does not recover leftover. This-hop splash HD after a briefed dwell is mission. Never revert. |
| **leftover-ksc** | **Retired.** Named save/load of the overlay looked like a reload / return to pre-launch. Os disabled reverting flights. Overlay dismiss is `recover()` + Close. Never that load. |
| **pad** | Launch pad / `python main.py pad`. Keep. |
| **F-014 / I-012** | Gym ids live only inside a ticket **title**. Speech is the twin **T-id** (F-014 → T-184). |
| **need_*** | Do not emit. Open `--type control|vehicle|science|…`. Parent may still shim a leftover token. |
| **world model** | `docs/program/world-model.md`. Gene chairs flight layers. Mortimer chairs **Practice**. |
| **Practice** | House pitfalls / QOL / still-true ops. Mortimer last-write. |
| **improve:** | Leftover blob. After the hire: `tickets feedback T-NNN --claim "…"` on the work ticket. Stumble *during* work: `type=ops --tag feedback` or `type=rsi`. `I-NNN` twins are tickets. |
| **tickets feedback** | Mandatory after every hire. `--claim` required; `--evidence` `--owner` `--real` optional. Appends `payload.findings` on the packet T-id. Close harvests `close_why` if empty. Not Return keys. Not a child ticket per hire. |
| **ask:** | Leftover. Open `type=ops --tag ask` (desk = addressee). P1 if it blocks `go`. |
| **explore:** | Leftover. Open `type=ops --tag explore` P3. Rare field itch. |
| **note-tech.md** | Tape, not the bus. Commander may still append; miss opens `type=control\|recover`. |
| **desk** | `python main.py desk` writes `docs/program/desk.md` — lock, hangar, f013, sci, stack. Packet food. Gitignored live tape. |
| **KSP-RO** | Parked Express RO tree. Do not seat. Live gym is `~/Games/KSP-rss` / letsgrok. |
| **science-scan** | Linus. Live MM experiment defs + leftovers vs REACH. Samples recover; files credit while recording. |
| **comms** | Gus/Linus. Disk dump is ConfigCache (TL rates, craft, ground LIVE/SILENT). Live RA kRPC is `conn.real_antennas` (Os 2026-08-25). Do not cheat a link. |
| **Flight Dynamics** | Katherine. Tape windows (`telem --window`), not jsonl in the prompt. Relays by ticket. Not Linus bind, not Lars burns, not Wernher schema. |
| **sit-card** | **Retired.** Sit is `python main.py desk` / `desk.md`. |
| **krpc.md** | Wernher’s desk briefing. Traps stay in `agent-notes.md`. Never write GameData. |
| **tech-unlock** | Catalog CLI (kRPC). 0.6 has no purchase RPC — aborts. Paid node: Mortimer edits the save then `python main.py load rd-<node>`. **Never** `load persistent` (F-014 / I-010). |
| **Kerman** | **Retired house name.** We are **Grokman**. Stock KSP roster may still say Kerman; Hangar aliases it. |
| **ksp-ceo.md** etc. | **Retired.** Agent files are `mortimer.md`, `gene.md`, `linus.md`, `gus.md`, `lars.md`, `wernher.md`, `verena.md`. Shared writer: `pilot.md`. Spawn types match those names. |

Packet field is `live_run:`, path `docs/missions/<id>/logs/`.
