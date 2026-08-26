# PARKED — org-rsi applied (2026-08-26)

Not dispatch. Not work. Ticket bus is `python main.py tickets`.
This file is the apply closeout. Do not spawn-read it.

`do_apply=true` `overnuke=false` `skeptics_ok=true` `stamp=2026-08-26`
`archive_dir=docs/archive/2026-08-26-org-rsi` (not `docs-cutover`).
HEAD at closeout: `6254d492` (`org-rsi slice 4 git mv novels; inventory; blocks stub; NUKE sit-card/BOARD`).
No live `docs/program/org-rsi.md`. No Hangar. No hop. No pulse retune. No CHARTER creed rewrite. No slate goal rewrite.

Keep unless a later ticket proves otherwise: learn-rsi `attach_run` overwrite of uncrewed `payload.learn`; lars-rsi `ID_PREFIX` S/M/C + `hop_factory_pad.py` as the pad-RF file. Do not restore spotter as spawnable, Gene-as-merge, Batch Learn, Return keys, or `need_*` as the bus.

---

## 1 Sit

Live sit object (`docs/program/desk.md:1–16`, gitignored snapshot; not rewritten this closeout):

| kv | live |
|---|---|
| `lock` | `free` (`desk.md:1`) |
| leftover | **0** (`desk.md:5`) |
| sci | **2.2905** (`desk.md:7`) |
| tree | `start,engineering101,basicRocketry,survivability,stability` (`desk.md:10`) |
| `capable` | `yes` (`desk.md:11`) |
| craft | `kspstuff-hop-valiant-t7-wheel-pbc` (`desk.md:12`) |
| `card` | `barometerScan,geigerCounter,mysteryGoo` (`desk.md:14`) |
| last | `command=hop exit=0 abort=none` (`desk.md:15`) — postcard `docs/last-flight.md:1–3` is `exit: 2` `abort: abort` |
| bind | T-404 / T-460 / T-461 PresMat (`desk.md:26`) |

Tape id vs Commander (`docs/program/current.md:1–3`): `flight: uncrewed` / `pilot: none` / `capcom: Valentina Grokman`. INDEX lists tape id `uncrewed` vs Commander dossier `jebediah` (`docs/missions/INDEX.md:3–10`). `seated_id()` is `current.md` `flight:` (`missions.py:79–84`).

Fly ticket T-081 still `go: yes` / `campaign: uncrewed` / `cli: python main.py hop` (`docs/program/tickets/head.json:3339–3343`). Hangar name is vehicle ticket T-400 `capable: yes` + `payload.craft` `kspstuff-hop-valiant-t7-wheel-pbc` (`head.json:14698`, `:14759`; `tickets.py:370–380`, `missions.py:119–129`). Live pad miss is **T-471** `type=control` `desk=lars` `fingerprint=rf-ignition-ullage` empty payload (`head.json:17881–17901`). T-471 is pad-RF, not compose.

Radio rot (not rewritten; gitignored): `docs/program/ship.md:5–8` `as_of: 2026-08-25T22:09Z` `sit: pre_launch` `vessel: …t7-wheel-pbc` still `flight: jebediah`. Desk snapshot still clips frozen `note-tech:` (`desk.md:27`); kernel `desk.py` has **0** `note-tech` hits.

Goal unchanged: bigger rockets, more Δv, farther out. Ad astra. Next CTT `generalRocketry` **20**; bank 2.29 does not pay 20 (`docs/program/slate.md:3–11`; `CHARTER.md:3–11`).

Git apply (`.git/logs/HEAD:92–96`):

| commit | slice | title |
|---|---|---|
| `52c632e` | 1 | Unpin tests before novels/lessons/blocks move |
| `73373b5` | 2 | Kernel: skim, gates, hangar, dumps, twins, who |
| `a0ab910` | 3 | Strip inject; thin cards; NUKE leftover roles |
| `39fd065` | 5 | Tape id uncrewed; do not MOVE historical logs |
| `6254d492` | 4 | git mv novels; inventory; blocks stub; NUKE sit-card/BOARD |

Slice 4 is HEAD **after** slice 5. APPLY 3 SKIP in the machine log is stale — slice 4 did land. Wernher log records slices 1/2/5/4 (`docs/crew/log/wernher.md:3–9`). Mortimer log already had slice 3 (`docs/crew/log/mortimer.md:3`).

Live coverage-set after apply (disk, not the parked census):

| set | live n | notes |
|---|---|---|
| `docs/program/*.md` | **17** | CHARTER PROTOCOL OPS GLOSSARY krpc mods ra-rate RO roster slate tech blocks current desk ship uplink world-model. desk/ship gitignored. |
| `docs/program/tickets/*.md` | **2** | BRIEF + README. `BOARD.md` **MISSING**. |
| `.grok/agents/*.md` | **16** | No `spotter.md`. Extra vs old census-16-with-spotter is `org-review.md`. `walt.md` still **MISSING**. |
| `docs/missions/` (not log bodies) | INDEX + `jebediah/` + `uncrewed/` | Historical `jebediah/logs` **442** (228 jsonl + 214 md) unmoved. `uncrewed/logs/` empty. |
| `docs/crew/` portraits | **15** | `builder.md` **MISSING**. |
| `docs/crew/log/` | **15** | No `spotter.md`. mortimer `^-` **53** before this closeout line. lars **89**. wernher **50**. jebediah file ends `:211`. |
| `docs/press/` | **9** | INDEX + STYLE + 7 stories. |
| `docs/lessons.md` | **MISSING** | Parked `docs/archive/2026-08-26-org-rsi/lessons.md` **2872** lines / **156** `##`. |
| `docs/agent-notes.md` | **790** | Still-true kRPC. |
| `AGENTS.md` | **360** | Spawn table 10 rows, no Spotter (`AGENTS.md:93–104`, `:205`). |

Parked dest `docs/archive/2026-08-26-org-rsi/` (this tree; `docs/archive/README.md:15–17`): `README.md`, `lessons.md`, `lars-rsi.md`, `learn-rsi.md`, `feedback-plan.md`, `plan.md`, `briefing.md`, `science.md`, `vab.md`, `note-tech.md`, `loop.md`, `world-model.md` (dump), `org-flow/` (html + 6 svg).

---

## 2 What changed (path | action)

Actions as landed on disk. Cite live path. PARKED dest named when the live path is gone.

### Slice 1 — unpin (`52c632e`)

| path | action |
|---|---|
| `tests/test_protocol.py` | REWRITE. Drop whole-file `docs/lessons.md` / `Forest is 270` / live `## ` pins. Keep press Forest (`:129–144`). Keep PROTOCOL headings (`:11–34`). Keep `agents_md: false` glob (`:46–48`). Keep seated `jebediah/science.md` `ec_rate` (`:176`). |
| `tests/test_tickets.py` | REWRITE. Packet still desk+BRIEF not BOARD. Inventory: `board.jsonl` `live_tape`; archive I-012/F-014 `parked_archive`; no leftover_migrated (`:1522–1561`). |
| `tests/test_hop.py` `tests/test_desk.py` `tests/test_protocol_gate.py` `tests/test_missions.py` | REWRITE. Drop hop-envelope pins that blocked moving novels/blocks. Keep CLI table needles (`phys-warp` / `no_warp` / `rails 0`) on the stub. `test_missing_ticket_is_wait` (`tests/test_protocol_gate.py:314–328`). |
| `protocol.py` `fly_gate` | REWRITE. Tickets-only go. Missing ticket = wait (`protocol.py:138–139`). Keep leftover / capable / f013 waits (`:146–215`). |

### Slice 2 — kernel (`73373b5`)

| path | action |
|---|---|
| `tickets.py` `infer_links` | REWRITE. Always desk+BRIEF (`tickets.py:470–496`). Drop type extras `science.md` / `vab.md` / `blocks.md` / hardcoded `jebediah/briefing.md`. `add()` drops `FORBIDDEN_DISPATCH`. `live_run` via `seated_logs_dir` or `payload.telem_run` (`:446–457`). Keep `ID_PREFIX` (`:59–63`), `attach_run` (`:1419`), `commander_for` none (`:987–994`), `NEED_MAP` shim (`:121–129`), TYPES 11 (`:19–31`). |
| `tickets.py` `migrate_second_bus` | REWRITE. I/F twins only. **No lesson mint** (`:1692–1693`). Keep 90 done `legacy-twin` tickets. |
| `tickets.py` `_write_board_md` / `tickets board` | NUKE writer. `PRINT = …/BOARD.md` leftover constant only (`:16`). `_rebuild` writes HEAD + fingerprints (`:301–302`). |
| `tickets.py` `DEFAULT_ROUTE` | REWRITE. `recover: hank` (`:109`). |
| `protocol.py` | REWRITE. `fly_gate` tickets-only like ops. Keep `python main.py protocol fly` CLI. Keep `SCHEMAS` (`:12–21`) for later ticket. |
| `ops.py` | REWRITE. Delete `"batch Learn"` why-string (live grep **0**). Lock-live still no Gene. |
| `main.py` | REWRITE. `attach_run(..., who="hank")` (`main.py:106`). Kill `sync_shim`. Retire note-tech CLI. |
| `house_dump.py` | REWRITE. `seated_*_path()` (`:8–12`). `render_all` writes seated science/plan/briefing + slate (`:419–436`). Do not retarget slate goal. Stop program-twin `write_text`. |
| `desk.py` | REWRITE. Capable from ticket, not `vab_kv`. Drop note-tech clip (grep **0**). Snapshot `desk.md` not scheduled. |
| `missions.py` | REWRITE. `hangar_craft_name` from `capable_hangar` (`:119–129`). Kill `sync_shim`. |
| `uplink.py` `crew.py` | REWRITE. No shim fallback. Skip crew-log append when `commander_for` is none. Katherine in `_SLUG` (`crew.py:37`). |

### Slice 3 — inject / cards (`a0ab910`)

| path | action |
|---|---|
| `AGENTS.md` | REWRITE. Miss physics = helper docstring + `findings` / `close_why` (`AGENTS.md:8–9`). Packet no lessons/science/vab/blocks/BOARD (`:160–162`). Spawn table drop Spotter (`:93–104`, `:205`). Floors Lars/Jeb **medium**, Mortimer **high** (`:134–136`). `flight:` is tape id (`:5`). First command packets the Hank-named id (`:137–138`). Keep Handoffs/Parallel/packet law. Do not hire Gene as merge (`:170`). |
| `docs/program/PROTOCOL.md` | REWRITE. Keep `## Handoffs` / `## Parallel` / `## Spawn packet` / `## Return (this job)` (tests pin). Packet desk+BRIEF+named helper (`PROTOCOL.md:336–358`). No Batch Learn (`:253`). Floors Jeb/Lars medium, Mortimer high (`:346–348`). Drop lessons-as-bus sentence (EOF Feedback `:534–565`; **0** live `lessons.md` duty in OPS). |
| `docs/program/OPS.md` | REWRITE. Data-flow is desk + head.json + jsonl envelope + last-flight + ship (`OPS.md:362–370`). `protocol fly` tickets-only; missing ticket = wait (`:374–375`, `:432`). |
| `docs/program/tickets/BRIEF.md` | REWRITE. First command `tickets packet <Hank-named id>` (`BRIEF.md:6–10`). Attach-run Learn (`:12–17`). Named helper third path (`:73–82`). Miss physics = docstring + `--claim` (`:81–82`). Example attach-run `docs/missions/<id>/logs/` (`:61`). |
| `docs/program/tickets/README.md` | REWRITE. Floors match kernel. Drop plan+science fallback lie. |
| `docs/program/GLOSSARY.md` | REWRITE. Mission folder is tape id; uncrewed id is `uncrewed` (`GLOSSARY.md:10`). sit-card **Retired** (`:37`). Agent-file list has katherine, no spotter (`:41`). |
| `docs/program/roster.md` | REWRITE. Katherine row (`roster.md:16`). |
| `README.md` | REWRITE. Drop `Letsgrok lessons: docs/lessons.md` (live grep **0**). |
| `docs/flights/README.md` | REWRITE. Attach-run path `docs/missions/<id>/logs/` (`:15`). Uncrewed Learn is Hank `attach-run` (`:9`). |
| `docs/crew/lars.md` Notes | REWRITE. Helper docstring + `--claim`; warp is Wernher (`:32–36`). Voice/Inner/Thesis untouched. |
| `.grok/agents/{hank,lars,gene,wernher,gus,linus,mortimer,verena,katherine,pilot,jebediah,grok}.md` | REWRITE. First command packets the Hank-named T-id (live T- stay; new S/M/C). Drop lessons append, dump rewrites, kerbin-lessons needle, from-need sermons. Keep `agents_md: false`. Keep pad-RF table. Thin Return = `SCHEMAS` keys + `--claim`. |
| `.grok/agents/spotter.md` | **NUKE**. File **MISSING**. |
| `docs/crew/builder.md` | **NUKE**. File **MISSING**. |
| `.grok/agents/org-review.md` | KEEP. Historian card. Not a flight hire. |
| `.grok/agents/{bill,bob,valentina}.md` | KEEP thin overlays. |
| `.grok/agents/walt.md` | LEAVE **MISSING**. Speech, never hire. |
| `.grok/workflows/{lars-rsi,learn-rsi,feedback-plan}.rhai` | REWRITE dest to `write_scratch_file` / not live `docs/program/<jump>.md`. |
| `docs/program/CHARTER.md` `docs/program/slate.md` | LEAVE. Creed + goal untouched. |

### Slice 5 — tape id (`39fd065`; committed before slice 4)

| path | action |
|---|---|
| `docs/program/current.md` | REWRITE. `flight: uncrewed` / `pilot: none`. Capcom stays Valentina. |
| `docs/missions/INDEX.md` | REWRITE. Tape id `uncrewed` vs Commander `jebediah`. |
| `docs/missions/uncrewed/{plan,briefing,science,craft,loop}.md` | CREATE from live seated dumps (t7-wheel / T-081 / T-404), not archived program shims. `uncrewed/plan.md:13–18` craft t7-wheel, `cli: python main.py hop`, `campaign: uncrewed`. |
| `docs/missions/uncrewed/logs/` | CREATE empty. First hop after apply writes here. |
| `docs/missions/jebediah/logs/` (442) | TAPE in place. Do not MOVE. T-081 `telem_run` still those jsonl. |
| `missions.py` | REWRITE. `seated_id()` follows `current.md`. |

### Slice 4 — novels / inventory (`6254d492`; HEAD)

| path | action |
|---|---|
| `docs/lessons.md` | ARCHIVE → `docs/archive/2026-08-26-org-rsi/lessons.md`. No live stub. 2872 / 156 `##`. |
| `docs/program/{lars-rsi,learn-rsi,feedback-plan}.md` | ARCHIVE. Law already in kernel/BRIEF/`hop_factory_pad.py`. |
| `docs/program/{plan,briefing,science,vab,note-tech,loop}.md` | ARCHIVE. Dual boards / dumps / mailbox. |
| `docs/program/world-model.md` dump | ARCHIVE → parked `world-model.md`. Live path is **17-line chair stub** (`docs/program/world-model.md:1–17`). |
| `docs/program/org-flow/` | ARCHIVE whole tree. |
| `docs/program/blocks.md` | REWRITE. Gene CLI `pad`/`hop`/`splash`/`tech-unlock` + `phys-warp` / `no_warp` / **rails 0** (`blocks.md:1–15`). Hop-envelope novel gone. |
| `docs/program/sit-card.json` | **NUKE**. **MISSING**. |
| `docs/program/tickets/BOARD.md` | **NUKE**. **MISSING**. Writer already dead. |
| `docs_inventory.py` | REWRITE. `docs/archive/` **before** `_IF_ITEM` (`:320–323`). `lars-rsi.md`/`learn-rsi.md`/`feedback-plan.md`/`lessons.md` in `_ORG_NOVEL_NAMES` (`:54–70`). `board.jsonl` `live_tape` (`:338–339`). missions `loop.md` `live_tape` (`:348–349`). `FORBIDDEN_DISPATCH` adds lessons, RSI letters, BOARD, sit-card, org-flow, spotter (`:26–38`). `lesson_headings` not a live bus (`:302–309`). |
| `docs/archive/README.md` | KEEP + line for this dest (`:15–17`). |
| `docs/program/RO.md` | LEAVE. CHARTER `:61` still points here. Parked switchover, not an RSI novel. |
| `docs/missions/jebediah/science.md` | LEAVE. `pad.py:66–81` ticket-first then MD fallback. Later ticket. |
| `docs/program/tickets/board.jsonl` `head.json` `fingerprints.json` | KEEP. Event log / snapshot / stem catalog. |

### Pulse / creed / save (all slices)

| path | action |
|---|---|
| `hop.py` `hop_factory.py` `hop_factory_pad.py` `physics_warp.py` `pad.py` `splash.py` `science.py` | LEAVE. Last content: hop **3301**, factory **1051**, pad-RF **202** / **8** defs, warp **429**, pad **771**, splash **342**, science **1450**. **0** `org-rsi` in those files this apply. |
| `docs/program/CHARTER.md` | LEAVE. **200** lines. Kardashev `:3`, RSI door `:16–21`, idle pad `:29`, Os founder `:35`. **0** `org-rsi`. Stale `:69` still names `plan.md` fallback (do_not_touch). |
| `docs/program/slate.md` | LEAVE. Goal `:3–4`. `house_dump.py:435` writes without goal retarget. |
| GameData / `persistent.sfs` / `crafts/` | LEAVE. Repo `GameData` **MISSING**. |

---

## 3 Injection after

Cold child (`agents_md: false` on all 16 remaining cards; `tests/test_protocol.py:46–48`):

| layer | after apply |
|---|---|
| Packet skim | `docs/program/desk.md` + `docs/program/tickets/BRIEF.md` only (`tickets.py:495–496`). Org/rsi still adds OPS (`:521–522`) — kernel, not a dump. |
| Forbidden | `FORBIDDEN_DISPATCH` (`docs_inventory.py:26–38`) includes `docs/archive/`, `docs/lessons.md`, RSI letters, `BOARD.md`, `sit-card.json`, `org-flow/`, `spotter.md`. `infer_links.add` drops those paths (`tickets.py:488–491`). |
| Not in skim | BOARD, jsonl rows, lessons, `science.md`, `vab.md`, `blocks.md`, hardcoded jebediah briefing. Tests: `test_tickets.py:1547–1551`. |
| Parent AGENTS | CHARTER → PROTOCOL → desk → `current.md` (`flight:` tape id) → slate → INDEX. Miss physics is helper docstring + findings (`AGENTS.md:3–9`). Children do not receive AGENTS (`:6–8`). |
| Lars After a miss | Named helper + `tickets feedback --claim` (`.grok/agents/lars.md:157–164`). Grep `docs/lessons.md` on that card = **0**. |
| Wernher miss | Do not append lessons (`.grok/agents/wernher.md:91`). |
| Learn | Hop-exit `attach_run` overwrites `payload.learn` (`who=hank`) (`main.py:106`; `tickets.py:1419–1452`). Uncrewed `needs_learn` false. Do not hire Gene. |
| Fly gate | Tickets-only. Missing ticket wait (`protocol.py:138–139`; `OPS.md:374–375`). T-081 still flies if leftover/capable/f013 clean. |
| Hangar | T-400 `capable: yes` + `payload.craft` (`missions.py:119–129`; `tickets.py:379`). Not `vab.md`. |
| Tape dest | New hops `docs/missions/uncrewed/logs/`. Historical `jebediah/logs` stay. |

Residual inject (not the bus; listed in §7): `AGENTS.md:122` still names archived `docs/program/briefing.md`; `AGENTS.md:354–356` still says “Lessons already record kRPC 0.6 traps”; CHARTER `:69` still says `plan.md` fallback; gitignored `desk.md:27` still clips note-tech.

---

## 4 Tests

Re-run this closeout: **not executed** (no kRPC; this desk does not fly). Apply-run results, as recorded by the slice owners:

| slice | command (apply record) | result |
|---|---|---|
| 1 | `python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk -q` | **128 OK**. Extra missions + hop catalog **182 OK**. |
| 2 | `… test_tickets test_protocol test_protocol_gate test_desk test_missions test_crew -q` | **143 OK**. |
| 3 | `… test_protocol test_protocol_gate test_tickets test_desk -q` | **132 OK**. |
| 5 | `… test_tickets test_protocol test_protocol_gate test_desk test_missions -q` | **140 OK**. |
| 4 | `… test_tickets test_protocol test_protocol_gate test_desk -q` | **132 OK**. Extra catalog pins **28 OK**. |

Pins that now match disk (`tests/test_tickets.py:1522–1561`; `tests/test_protocol.py:11–54`; `tests/test_protocol_gate.py:314–328`):

- CHARTER / PROTOCOL / OPS / BRIEF = `live_kernel`
- seated `jebediah/plan.md` + `science.md` = `live_kernel` (kept)
- `board.jsonl` + missions `loop.md` (jebediah **and** uncrewed) = `live_tape`
- parked `docs/archive/2026-08-26-org-rsi/lessons.md` = `parked_archive`
- leftover_migrated list **empty**; I-012 / F-014 under archive = `parked_archive`
- live MISSING: `docs/lessons.md`, `BOARD.md`, `sit-card.json`, `lars-rsi.md`, `org-flow/index.html`
- `classify("docs/lessons.md")` = `parked_archive` even though the live file is gone
- missing fly ticket = wait
- TYPES 11
- every remaining `.grok/agents/*.md` has `agents_md: false`

Tape (`board.jsonl` / `head.json` / fingerprints / jebediah logs) was left unstaged on apply commits — gitignored / live bus, not this report.

---

## 5 Skeptics

Eight overnuke classes were **false** after HEAD `6254d49` (POST-SKEPTICS `real=false`). Re-opened live paths this closeout; disk still agrees.

| # | claim | live |
|---|---|---|
| 1 | CHARTER creed intact | `CHARTER.md` **200**. Kardashev `:3`. RSI `--claim` `:16–21`. Not Return keys `:21`. Idle pad `:29`. Os founder `:35`. **0** `org-rsi`. |
| 2 | slate goal intact | `slate.md:3–4` bigger rockets / Ad astra. `house_dump.py:435` writes without goal retarget. |
| 3 | pulse law unedited | hop **3301**, factory **1051**, pad-RF **202**/8 defs, warp **429**, pad **771**, splash **342**, science **1450**. Not in slice file lists as edits. |
| 4 | one control writer | `session.py:7–11,26–27` WRITE=`kspstuff` READ=`kspstuff-read`. `fly_gate` writer hop-pid (`protocol.py:40,135`). Hangar side clients pre-existing; `hangar.py` not in slices. |
| 5 | `protocol fly` CLI live | `protocol.py:138–215` leftover/capable/f013 waits; missing ticket wait; T-081 `go: yes`. `plan.go` unused is intended. CHARTER `:69` prose still names fallback (LEAVE). |
| 6 | no GameData write | repo `GameData` **MISSING**. |
| 7 | no `persistent.sfs` edit | repo `persistent.sfs` **MISSING** (not opened). |
| 8 | no new live `docs/program/` org novel | Live set is constitution + sit/radio + blocks stub + world-model chair + RO + BRIEF/README. Novels PARKED under this dest. `docs/program/org-rsi.md` **MISSING**. |

Per-skeptic `overnuke` all **false**. Skeptics 2 and 3 flagged `undernuke=true` (unpin incomplete / Gus+PROTOCOL dump writers / seated science ARCHIVE / desk capable from vab). Merge absorbed those into slices 1–4 (`undernuke 2+3 absorbed`). Post-apply undernuke gates (lessons miss-physics, spotter spawnable, BOARD skim, live RSI novels as dispatch) are **false** on disk:

| gate | live |
|---|---|
| lessons miss-physics | `docs/lessons.md` **MISSING**. Lars After a miss is docstring + `--claim`. Packet forbids the file. |
| spotter spawnable | `.grok/agents/spotter.md` **MISSING**. Spawn table 10 rows, no Spotter. `AGENTS.md:205` No spotter. |
| BOARD packet skim | `BOARD.md` **MISSING**. `infer_links` never adds it. Tests forbid it. |
| live RSI novels | `docs/program/{lars-rsi,learn-rsi,feedback-plan}.md` and `org-flow/` **MISSING**. Parked here. |

`skeptics_ok=true`. This closeout did not restore any NUKE.

---

## 6 Tickets opened or deferred

Merge named five later tickets. Grep of `docs/program/tickets/` for those titles: **0**. Fingerprints already exist (`fingerprints.json`: `control-blocks` **7**, `feedback-return` **2**, `fly-science-ids-stale` **1**, `thin-tape` **2`). T-471 stays the live pad-RF inbox — do not steal it. Compose is not this apply.

This Mortimer closeout **does not open them here**. Merge notes said do not open tickets in the apply burst; pad occupancy is T-471 pad-RF; opening five systems/control tickets mid-closeout is a second bus. Hank opens after this report, lock free, type/desk/fingerprint copy-paste:

```
python main.py tickets open --type control --desk lars --fingerprint control-blocks --title "Compose one living t7-wheel pulse from Wernher catalog; retire immortal run_factory_vessel"
python main.py tickets open --type systems --desk wernher --fingerprint control-blocks --title "Inventory hop.py leftover sits vs physics_warp dest"
python main.py tickets open --type systems --desk wernher --fingerprint feedback-return --title "Drop protocol SCHEMAS recommended/lesson/ask; parse fences match findings"
python main.py tickets open --type control --desk lars --fingerprint fly-science-ids-stale --title "Empty bound science aborts; drop seated science.md pulse fallback"
python main.py tickets open --type systems --desk wernher --fingerprint thin-tape --title "MOVE 442 jebediah/logs after test_telem unpin; new hops already uncrewed/logs"
```

No pulse work on those opens. No new fingerprint stems. Control/systems stay `T-`. Live T- science/fly/vehicle stay. **0** live `S-`/`M-`/`C-` ids (`head.json` grep empty).

T-471 `inbox` control lars `rf-ignition-ullage` — pad occupancy. Named helper `hop_factory_pad.py`. Not compose.

---

## 7 Open risks

House leftover after apply. Not pulse. Not creed.

1. **Gitignored sit still lies.** `desk.md:15` last hop `exit=0` vs `docs/last-flight.md:1–3` `exit: 2` abort. `desk.md:27` still clips 08-22 note-tech though `desk.py` no longer injects. Next `python main.py desk` should drop the clip; do not hand-edit the snapshot.

2. **`ship.md:8` still `flight: jebediah`.** Radio as_of 2026-08-25T22:09Z pre_launch t7-wheel. Next hop-pid write follows `seated_id()` = `uncrewed`. Do not Learn from this file.

3. **`AGENTS.md:122` still names `docs/program/briefing.md`.** That path is PARKED. Gene radio is seated `docs/missions/<id>/briefing.md` (`CHARTER.md:192`). Parent switchboard rot.

4. **`AGENTS.md:354–356` still says “Lessons already record kRPC 0.6 traps.”** Traps live in `docs/agent-notes.md`. Not packet skim. Not a child gospel (`agents_md: false`). Still a parent-TUI poison sentence.

5. **`CHARTER.md:69` still documents `protocol fly` “plan.md fallback.”** Kernel is tickets-only (`protocol.py:138–139`). Creed/LEAVE; PROTOCOL/OPS already carry the cut (`PROTOCOL.md:245`; `OPS.md:374–375`).

6. **`protocol.py` `SCHEMAS` still require Gene `recommended`, Lars `lesson`, Katherine `ask` (`:12–21`).** CHARTER not Return keys (`CHARTER.md:21`). Findings CLI is the return (`PROTOCOL.md:534–557`). Merge ticket `feedback-return` (deferred §6). Do not land `from-feedback`.

7. **`tickets.py:16` `PRINT = TICKET_DIR / "BOARD.md"` leftover.** Writer gone. File gone. Constant can recreate a temptation if someone restores `_write_board_md`.

8. **`pad.py:66–81` still falls back to seated `science.md` when ticket ids empty.** `docs/missions/jebediah/science.md` and `uncrewed/science.md` kept on purpose. Merge ticket `fly-science-ids-stale`. Do not patch pulse this apply.

9. **`docs/missions/uncrewed/loop.md` copied Hank abort acks** (T-459/462/465/Os scrap, `:13–22`) instead of an empty Gene stub. Design said empty; slice 5 copied live seated dumps. Talk tape, not stick. Do not mint ops ask from it.

10. **442 `jebediah/logs` still the historical bucket.** New writers target `uncrewed/logs`. MOVE waits `test_telem` unpin (merge `thin-tape`). Press links stay valid because we did not MOVE.

11. **Immortal `run_factory_vessel` still the inland pulse** (`hop_factory.py:1051`). Card already allows a t7-only compose (`.grok/agents/lars.md:19–22`). Merge `control-blocks` compose ticket is later. T-471 is not that ticket. `hop.py:909` `leftover_wreck_before_light` still the inventory dest.

12. **Prefix law unused on the board.** Kernel will mint S/M/C; live science/fly/vehicle still T-404 / T-081 / T-387.

13. **`NEED_MAP` / `from_need` shim remains** (`tickets.py:121–129`). Not the bus. Cards stopped teaching it.

14. **Stale letters inside PARKED files** (learn-rsi sci 8.7721; lars-rsi T-465 inbox; feedback-plan t7-chute) are bibliography. Next hire must not treat archive as sit.

15. **`org-review.md` still a 16th card.** Workflow historian. Archive with the workflow when cutover ends; do not spawn as Hank.

Do not mint world-model Open questions as `ops --tag ask` (Gene-as-merge). Do not idle the pad for these risks. T-471 is the living control miss.

---

## 8 This did not retune pulse / CHARTER creed

Did **not**:

- Edit `hop.py`, `hop_factory.py`, `hop_factory_pad.py`, `physics_warp.py`, `pad.py`, `splash.py`, `science.py` sit / warp / ignition / lid / chute / `_hold_or_cut` / `_pad_*`.
- Raise ignitions. Write GameData. Edit `persistent.sfs`. `load persistent`. Hangar. Fly. `ops next`. Stamp `go:`.
- Rewrite CHARTER **creed** (Kardashev III, idle-pad religion, RSI `--claim` door, Os founder). Roster compose row stays. RO pointer `:61` stays.
- Rewrite `docs/program/slate.md` goal.
- Restore spotter as spawnable, Gene-as-merge, Batch Learn, Return keys, `need_*` as the bus.
- Undo learn-rsi `attach_run` overwrite of uncrewed `payload.learn`.
- Undo lars-rsi `ID_PREFIX` or move pad-RF out of `hop_factory_pad.py`.
- MOVE 442 `jebediah/logs`. NUKE `docs/missions/jebediah/` Commander dossier.
- Create `walt.md`. Create a live `docs/program/org-rsi.md`. Leave a live `docs/lessons.md` stub.
- Extract lid/chute from `hop_factory.py`. Grow `run_factory_vessel` with `wait_water` / `wait_splash`. Add `_pad_*` per stamp.
- Change TYPES (still 11). Rename live T- science/fly/vehicle ids.
- Rewrite portraits-as-voice (kv before first `##`). Style numbers are not flight.
- Change jsonl schema (`live_run`, `telem_run`, `payload.learn`, index keys).

Did:

- Park novels. Kill dump inject. Tickets-only fly gate. Hangar from T-400. Tape id `uncrewed`. Chair stub. Gene CLI blocks. NUKE leftover roles / sit-card / BOARD. Keep attach-run, S/M/C, pad-RF file, one writer, depth 1, pad occupancy doctrine.
- This closeout: `docs/archive/2026-08-26-org-rsi/APPLIED.md` (this file) + one line `docs/crew/log/mortimer.md`. No live program novel.

Pad still flies. An RSI letter does not empty the pad. T-471 is the named helper miss.
