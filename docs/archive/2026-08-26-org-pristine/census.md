

===== CENSUS 0 =====
Dual `plan.md` / `briefing.md` / `science.md` / `loop.md` exist. Child packet is `desk.md` + BRIEF, not CHARTER/PROTOCOL. RSI papers and `sit-card.json` sit beside live kv.

## Topic
Live `docs/program/*.md` (not `tickets/*.json`). Shim vs seated. What a cold hire is told to open.

## Counts
`docs/program/`: 24 `*.md` + `sit-card.json` + `org-flow/` (html+6 svg, 0 md) + `overlay.last`/`uplink.last`/`unrecoverable.last`. `tickets/` json skipped.

| path | n |
|---|---|
| `world-model.md` | 800 |
| `PROTOCOL.md` | 566 |
| `OPS.md` | 437 |
| `krpc.md` | 259 |
| `CHARTER.md` | 200 |
| `learn-rsi.md` | 186 |
| `blocks.md` | 174 |
| `tickets/BRIEF.md` | 132 |
| `ra-rate.md` | 88 |
| `science.md` | 85 |
| `mods.md` | 78 |
| `note-tech.md` | 65 |
| `RO.md` | 59 |
| `desk.md` | 57 |
| `lars-rsi.md` | 54 |
| `feedback-plan.md` / `slate.md` | 47 |
| `GLOSSARY.md` / `tickets/README.md` | 44 |
| `vab.md` | 40 |
| `ship.md` | 24 |
| `roster.md` | 23 |
| `briefing.md` / `tech.md` | 20 |
| `plan.md` | 17 |
| `current.md` | 3 |
| `loop.md` / `uplink.md` | 1 |

Seated: `docs/missions/jebediah/plan.md` 20, `briefing.md` 13, `science.md` 37, `loop.md` talk tape (not the 1-line shim).

## Who writes it
`PROTOCOL.md:498-509` / `CHARTER.md:127-132`: Gene last-writes **briefing prose + seated `plan.md` render**; flight layers of `world-model.md`. Mortimer last-writes **Practice**, PROTOCOL, job cards, slate. Gus `vab.md`/`.craft`. Linus **science dump** (`PROTOCOL.md:478`; bind = ticket payload). Verena README/press. Commander **takes** `uplink.md`. `loop.md` is talk. Hank/`desk` CLI writes `desk.md`. Hop pid writes `ship.md`. `note-tech.md:3` seated Commander. `blocks.md:3` Lars. `current.md` seat. `lars-rsi.md` / `learn-rsi.md` **applied** papers. `feedback-plan.md:1` compile, no apply. `ra-rate.md:1` Os 2026-08-25 prove. `RO.md:3` parked. `sit-card.json` still on disk; `GLOSSARY.md:37` **Retired** (sit = `desk.md`).

## Who is told to read it
**Parent (Hank TUI):** `AGENTS.md:3-6` CHARTER → PROTOCOL; then `desk` → `desk.md`; `current.md`, `slate.md`, `OPS.md`. `CHARTER.md:61-62` GLOSSARY + parked RO.
**Cold child:** every job card `agents_md: false`. Packet `PROTOCOL.md:327-345` / `BRIEF.md:3-5` / gene `35-36`: `desk.md` + inbox + ticket + `tickets/BRIEF.md`. `read:` desk + **≤2** role paths. First command inbox. **Not** BOARD.md. **Not** CHARTER/PROTOCOL/OPS/world-model unless that card names them.
Role extras in cards (not packet `read:`): `krpc.md` Gene/Lars/Gus/Katherine/Hank (`OPS.md:41-42`). Hank kernel `OPS.md` (`hank.md:78`). Gus `vab.md` after stamp (`gus.md:101`). Linus: `science.md` dump not bind (`linus.md:16`). Gene: do not dispatch via world-model novels or `science.md` (`gene.md:20`). Verena story layer of world-model (`verena.md:14`). Mortimer mutates PROTOCOL/Practice (`mortimer.md:5-6`). Pilot: `current.md`, `note-tech` during hop (`pilot.md:12,64`). Lars miss: named helper `.py` + `lessons.md` heading (`lars.md:165`). Katherine: `ship.md` / Tape (`katherine.md:19-23`). Commander takes `uplink.md` (`CHARTER.md:191`). `CHARTER.md:192` seated `briefing.md` + seated `plan.md`.
**Not named in spawn packet:** `lars-rsi.md`, `learn-rsi.md`, `feedback-plan.md`, `org-flow/`, `sit-card.json`, `mods.md`, `tech.md`, `ra-rate.md`, `roster.md`, `note-tech.md`, `loop.md`, `blocks.md` (Lars card says update `lars.md:169`).

## Injected every hire?
| source | what |
|---|---|
| Parent `AGENTS.md:3` | CHARTER then PROTOCOL |
| Child job card | role prompt; `agents_md: false` (no AGENTS.md) |
| Packet | `desk.md` + `tickets packet` + `BRIEF.md` (`PROTOCOL.md:340-345`) |
| `lessons.md` | Lars/Wernher **on a miss** (`lars.md:165`, `wernher.md:92`); `PROTOCOL.md:564` “stays run headings” — not packet |
| RSI papers / org-flow / sit-card | not packet |

## Stale vs live
Live kv: `desk.md:1-14` lock free leftover 0 sci **2.2905** craft **t7-wheel-pbc**; `ship.md:5-7` `as_of: 2026-08-25T22:09Z` same craft pre_launch; seated `briefing.md:3-9` T-081 hop t7-wheel-pbc, bound T-404/460/461, landing `2026-08-25T10-57-36Z`.
**Dual plan** (`OPS.md:5` render; `plan.md:1` points seated): shim `docs/program/plan.md:12-15` `expect_apo_max: 140000` `go: yes` **no** `cli`/`campaign`/`science_ids`; seated `docs/missions/jebediah/plan.md:12-18` `expect_apo_max: 400000` `cli: python main.py hop` `campaign: uncrewed` `science_ids: barometerScan,geigerCounter,mysteryGoo`.
**Dual briefing:** `docs/program/briefing.md:3-17` craft **proc-long-pbc**, bank **8.7721**, T-077/T-287 thermo+TELEMETRY, hops 21-46-20Z vs seated `briefing.md:3-10` t7-wheel + barometer T-ids.
**Science dump:** `science.md:6-24` t7-wheel bank 2.2905 bound T-404/460/461; seated `science.md:1-9` T-081 dump. `PROTOCOL.md:478` dump only.
**sit-card.json:2** craft **east-t3-pbc**; GLOSSARY retired.
**loop.md:** program 1-line stub (`loop.md:1`) vs seated abort/`no_warp` tape.
`slate.md:4-11` Os 2026-08-24 bank **2.09** vs desk 2.2905. `CHARTER.md:10` bank **2.29**. `learn-rsi.md:13` sit sci **8.7721**. `feedback-plan.md:7` t7-**chute**-pbc compile. `note-tech.md:62-65` last Jeb 2026-08-22. `world-model.md:29-40` Meaning still T-013 10-11-27Z hop-to-water; open questions last Gene **2026-08-22** (`:799`). `lars-rsi.md:1-7` applied, sit matches desk 2.2905. `ra-rate.md:1` 2026-08-25. `RO.md:3` parked 2026-08-21. `roster.md` has no Katherine row. `uplink.md:1` cleared.

## Files read
`docs/program/` listing; OPS `:1-80`; PROTOCOL Handoffs/Files/Return/packet; world-model `:1-40` + `:761-800`; note-tech `:1-20`; loop; plan `:1-20`; science `:1-20`; lars-rsi/learn-rsi/feedback-plan `:1-20`; CHARTER `:1-80` `:110-199`; desk/current/slate/roster/GLOSSARY/krpc/blocks/briefing/mods/RO/ra-rate/tech/vab/ship/uplink/sit-card.json; org-flow `index.html`; seated `docs/missions/jebediah/{plan,briefing,science,loop}.md`; `AGENTS.md`; `.grok/agents/{gene,hank,lars,linus,gus,wernher,mortimer,pilot,verena,katherine}.md`; `tickets/BRIEF.md`. Archive grep hits = PARKED. Crew logs not opened.

===== CENSUS 1 =====
## Topic
`docs/missions` is one seated folder: `jebediah`. `current.md` `flight: jebediah`. INDEX has one table row. Uncrewed hops still tape under that seat. `crew=` is empty on tape. `loop.md` still acks Hank abort. `plan`/`science`/`craft`/`briefing` dual with `docs/program` (craft twin is `vab.md`).

## Counts (path:line or wc)
- Tree: `docs/missions/` = `INDEX.md` + `jebediah/` only (`list_dir`).
- INDEX one row: `jebediah` ← seated (`docs/missions/INDEX.md:7`).
- Logs: 442 files (228 jsonl, 214 md) (`list_dir` `jebediah/logs/`).
- **2026-08-25:** 15 `*.md` (`^command:`), 18 jsonl (`"kind": "start"`): 15 hop + 3 hangar (`07-27-09Z`, `07-27-52Z`, `10-44-16Z`). Index/crew-log hops **10** (`docs/flights/index.jsonl:131-140`, `docs/crew/log/jebediah.md:202-211`). Five hop stamps on disk not in those 10: `08-20-54Z` `08-40-14Z` `08-48-18Z` `08-56-15Z` `09-01-24Z`.
- **2026-08-26:** 0 files, 0 index, 0 crew-log.
- Crew log: **209** `-` lines (`jebediah.md:3-211`). Last 40 start `2026-08-24T15-24-17Z` (`:173`). Last line `:211` `2026-08-25T22-06-37Z hop exit=2 abort=abort`.
- Last crewed Jeb tape line: **MISSING**. `crew=Jeb` / `crew=[A-Za-z]` = 0. First hop also `crew=` (`2026-08-20T15-58-12Z-hop.jsonl:1`). Named-Commander prose only `:8` (2026-08-20 uncrewed Stayputnik). `command: phase` in logs: 0.
- Index: 140 rows, all `"flight": "jebediah"` (`index.jsonl:1-140`).

## Who writes it
- INDEX: `missions.write_index` (`missions.py:261`); `seat` (`:230`); `main.py missions` (`:938`).
- `plan.md`: Gene render / `house_dump.render_plan` (`house_dump.py:428`); `uplink.write_plan_file` (`uplink.py:203`).
- `briefing.md`: `house_dump` (`:431`); Gene `main.py brief` (`main.py:916`).
- `science.md`: `house_dump` seated+program (`:421-425`). Linus owns dump (`docs/crew/linus.md:30`).
- `craft.md`: no `write_text` in `.py`. Gus card owns `vab.md` + `crafts/*.craft` (`.grok/agents/gus.md:5`).
- `loop.md`: `uplink.note` → `seated_loop_path` (`uplink.py:50-57,222-226`).
- Logs jsonl: hop pid `flightlog` → `seated_logs_dir` (`flightlog.py:246-259`). `.md` review/handoff: `review.py:280`. Crew log: `crew.append_log` (`crew.py:126`).
- attach-run: Hank, path `docs/missions/jebediah/logs/<run>.jsonl` (`BRIEF.md:63`).

## Who is told to read it
- Parent: INDEX (`AGENTS.md:7`). Gene: seated `plan.md` (`.grok/agents/gene.md:44`). Fly packet skim: `docs/missions/jebediah/briefing.md` (`tickets.py:406`). Science packet: `docs/program/science.md` not seated (`tickets.py:414`). Control `--deep`: `jebediah/logs/{live}.jsonl` (`tickets.py:424`). CHARTER radio: missions briefing + seated plan (`CHARTER.md:192`). `python main.py plan` prints seated plan (`main.py:902`). Commander job: `current.md` + CLI; no missions path in `.grok/agents/jebediah.md` / `pilot.md`.

## Injected every hire? (job card / AGENTS.md / packet / PROTOCOL)
- **AGENTS.md:** INDEX yes (`:7`). Children `agents_md: false`. Radio names seated `plan.md` and **`docs/program/briefing.md`** (`AGENTS.md:121-124`).
- **Packet:** desk + BRIEF + ≤2 (`PROTOCOL.md:335-345`). Fly skim adds missions briefing (`tickets.py:406`). Not INDEX. Commander `cli` is ticket, not seated plan (`PROTOCOL.md:355-356`).
- **Job cards:** Gene `plan.md`; Linus `science.md` dump; Hank attach-run `<seat>/logs`; Gus `vab.md`; Jeb/pilot none.
- **PROTOCOL:** logs `docs/missions/<id>/logs/` (`:417`). Uncrewed: `commander: none`, do not hire Jeb (`:246-252`).

## Stale vs live (dated last write)
- **Live seated:** `plan.md` `campaign: uncrewed` `cli: hop` (`plan.md:15-17`); briefing T-081 / t7-wheel-pbc / last landing `2026-08-25T10-57-36Z` (`briefing.md:3-7`); science T-404/460/461 (`science.md:20-32`); craft t7-wheel-pbc (`craft.md:4`); loop Hank abort T-459/462/465 (`loop.md:15-21`); last hop md/jsonl `22-06-37Z`; last-flight same abort (`docs/last-flight.md:1-9`).
- **Diverge:** seated plan `craft: …proc-long-pbc` (`plan.md:13`) vs craft.md/briefing/vab `t7-wheel-pbc`. `docs/program/plan.md` `expect_apo_max: 140000`, no `campaign`/`cli` (`program/plan.md:12-16`) vs seated `400000` + campaign. `docs/program/briefing.md` old proc-long / T-077 (`:4-10`) vs seated T-404. `docs/program/loop.md` stub (`:1`) vs seated acks. `docs/program/science.md` bound table live T-404 (`:22`). `docs_inventory.py:327-344`: missions `loop.md` **parked_archive**; `craft.md` + logs **live_tape**; plan/science/briefing fall through **live_kernel**. Reviews under `docs/archive/reviews/` are PARKED.

## Files read
`docs/program/current.md`, `INDEX.md`, `jebediah/{loop,plan,science,craft,briefing}.md`, `logs/` (dir + dated globs + `22-06-37Z` + `09-01-24Z` + `15-58-12Z` start lines), `docs/crew/log/jebediah.md` (counts + last 40), `docs/flights/index.jsonl` last 20 + 08-25/26, `BRIEF.md`, `CHARTER.md`, `PROTOCOL.md`, `AGENTS.md`, `GLOSSARY.md`, `OPS.md`, `program/{plan,briefing,science,loop,vab}.md`, `last-flight.md`, `missions.py`, `house_dump.py`, `tickets.py`, `uplink.py`, `flightlog.py`, `crew.py`, `docs_inventory.py`, `.grok/agents/{jebediah,gene,gus,linus,pilot,hank}.md`.

===== CENSUS 2 =====
## Topic
`.grok/agents/` job cards and leftover roles, AS-IS. Sixteen cards on disk. No `walt.md`. Spotter still DEPRECATED. No `## Inputs` heading on any card.

## Counts (path:line or wc)
Last content line (= `wc -l` if trailing newline): `hank.md` 194, `lars.md` 192, `gene.md` 170, `wernher.md` 146, `gus.md` 127, `linus.md` 115, `mortimer.md` 97, `verena.md` 94, `pilot.md` 87, `katherine.md` 86, `jebediah.md` 23, `grok.md` 18, `spotter.md` 13, `bill.md`/`bob.md`/`valentina.md` 12. `.grok/agents/walt.md` MISSING. `.grok/agents/builder.md` MISSING. `docs/crew/builder.md` 24. `docs/crew/walt.md` 26. Crew logs `^-` count 1 each: `docs/crew/log/{walt,bill,bob,valentina,grok}.md` (all 2026-08-20). No `docs/crew/log/spotter.md`.

## Who writes it
Mortimer mutates PROTOCOL / job cards / Practice on org (`mortimer.md:4-6`, `:38-39`; `PROTOCOL.md:505`; `CHARTER.md:154`). Parent switchboard is `AGENTS.md`. Portraits live under `docs/crew/`. `docs/crew/builder.md:1-4` is a pointer to `docs/crew/gus.md`.

## Who is told to read it
Child spawn prompt **is** the card (`CHARTER.md:100-101`; `AGENTS.md:108-109`). Stubs: follow `pilot.md` (`bill.md:11-12`, `bob.md:11-12`, `valentina.md:11-12`, `grok.md:13`, `jebediah.md:16`). Packet `read:` is `desk.md` + ≤2 role paths (`PROTOCOL.md:335`, `:340-345`) — not the card, not BOARD. Gene: “Do not read BOARD.md” (`gene.md:38`). Verena `## Read` (`verena.md:58-66`): desk, dossier, `STYLE.md`/`INDEX.md`/`README.md`; voice on `world-model.md` (`verena.md:14`); do not ingest `docs/archive/kerbin-lessons.md` (PARKED). Linus: `science.md` is dump, not bind (`linus.md:16`, `:96`; bind = ticket payload `:75-77`). Parent `AGENTS.md:7-8`: children do not receive `AGENTS.md`.

## Injected every hire? (job card / AGENTS.md / packet / PROTOCOL)
Job card: yes — `prompt_mode: full`, every card `agents_md: false`. `AGENTS.md`: no (`AGENTS.md:7-8`). Packet: desk + `tickets packet` + BRIEF, “No BOARD.md novel” (`PROTOCOL.md:328-345`). PROTOCOL fences are copied onto cards (`PROTOCOL.md:428-496`); packet template `return: ## Return (this job)` (`PROTOCOL.md:337`). `lessons.md` is parent miss-physics (`AGENTS.md:8`), not a child packet Input. `CHARTER.md:98`: spawn prompts do not inject niche notebooks.

## Stale vs live (dated last write)
Live desks still carry **Os 2026-08-25** tape/git in-card (hank/gene/lars/wernher/gus/linus/mortimer/verena/katherine). First-command prefixes: Linus `S-NNN` (`linus.md:22`; live T- science stay `:26-27`); Gene `M-NNN` (`gene.md:31`; live T-081 `:36-37`); Gus `C-NNN` (`gus.md:42`; live T- stay `:47-48`); Lars/Wernher/Mortimer/Katherine `T-NNN` also S-/M-/C- (`lars.md:73`, `wernher.md:65`, `mortimer.md:23`, `katherine.md:29`); Hank first is `desk` + `ops next` (`hank.md:48-50`); Verena has no `## First command`; stubs/spotter none. Return still `tickets: T-NNN` on S/M/C desks (`gene.md:149` vs `:31`; `gus.md:120` vs `:42`; `linus.md:107` vs `:22`). PROTOCOL Gene `tickets: T-NNN [go=yes|wait]` (`PROTOCOL.md:453`); gene card `tickets: T-NNN | none` + separate `go:` (`gene.md:154-155`). BOARD / lessons / world-model / note-tech / science.md are Do-not or write-after-miss, not Inputs: Lars miss appends `lessons.md` (`lars.md:163-167`); Wernher same (`wernher.md:92`); Verena must not edit `lessons.md` (`verena.md:24`); `note-tech` is tape (`pilot.md:64`; `AGENTS.md:127`); Gene forbids world-model novels / science.md dispatch (`gene.md:20`). `spotter.md:2-11` DEPRECATED; spawn table **Do not spawn** (`AGENTS.md:106`); `AGENTS.md:206` “No spotter.” Bill/Bob/Valentina 12-line stubs; Jeb 23; Grok 18. `builder.md` pointer; its log 2026-08-20 (`docs/crew/builder.md:21-24`). Walt: no card; portrait `docs/crew/walt.md:1-26`; log one line 2026-08-20 (`docs/crew/log/walt.md:3`); AGENTS speech (`AGENTS.md:79`, `:136`). Hank floors still “Lars **low**” Os 2026-08-23 (`hank.md:54`); PROTOCOL same (`PROTOCOL.md:349`); AGENTS “everyone else **medium**” (`AGENTS.md:137-138`).

## Files read
`.grok/agents/` (16 files), `spotter.md`, `lars.md` miss+Return, `hank.md:1-80`+Return, `gene.md:1-40`+Return, `wernher.md:1-40`+Return, `pilot.md:1-40`+Return, stubs `bill`/`bob`/`valentina`/`grok`/`jebediah`, `katherine.md`, `mortimer.md`, `verena.md`, `gus.md`, `linus.md`, `docs/crew/builder.md`, `docs/crew/walt.md`, `docs/crew/log/{walt,bill,bob,valentina,grok}.md`, `AGENTS.md` spawn table, `PROTOCOL.md` packet+Return, `CHARTER.md:96-101`. `docs/archive/` hits PARKED.

===== CENSUS 3 =====
## Topic
`docs/lessons.md` is a live letsgrok **run-heading** log. `docs/agent-notes.md` is the kRPC trap bible. Packet skim does not name either. Parent AGENTS.md still points at both as mission/kRPC facts.

## Counts
- `docs/lessons.md`: **2871** lines; **156** `##` (`grep ^##`). Newest `## 2026-08-25T21-57-33Z-hop — rf-ignition-ullage` (`docs/lessons.md:24`).
- **2026-08-25 `##`:** **22**. Unique titles after ` — ` **as written: 12**. Repeat stems: `rf-ignition-ullage` **6**, `hop-coast-phys-warp` **4**, `hold-ground-card` **3**, `telem-eyes-library` **2** (one tagged `(reader)`). Singles: `thin-tape`, `flyinghigh-lid`, `ra-rate`, `ctt-stability`, plus prose `Valiant RF ullage + one ignition`, `RA 64 bps…`, `Close is Tracking, then KSC`.
- `docs/agent-notes.md`: **791** lines; **13** `##` + **2** `###`. Log newest **2026-08-25** T-454 (`:564`). Environment still `live 2026-08-21` (`:32`).
- PARKED `docs/archive/kerbin-lessons.md`: **41** `## L-NNN`. `FORBIDDEN_DISPATCH` (`docs_inventory.py:31`).
- `classify("docs/lessons.md")` falls through to **`live_kernel`** (`docs_inventory.py:345`).

## Who writes it
- File self: append `## run — title` after unexpected (`docs/lessons.md:7–14`); patch agent-notes if API still current (`:14`).
- **Lars** After a miss: append `## <run> — <fingerprint>` (`/.grok/agents/lars.md:163–167`). `docs/crew/lars.md:32–33` same.
- **Wernher** on a miss: one `## <sortie> — <fingerprint>` (`/.grok/agents/wernher.md:92–94`). `docs/crew/wernher.md` has **no** `lessons` string.
- Parent **R&D contract:** one dated heading; Lars **or** Wernher (`AGENTS.md:326–328`, `:345–346`).
- BRIEF: Lars heading **names** the fingerprint (`docs/program/tickets/BRIEF.md:83`).
- OPS data-flow: `lessons.md ← VSE/CSE dated physics/API` (`docs/program/OPS.md:369`).
- Verena **must not** edit lessons (`/.grok/agents/verena.md:24`).
- Ticket bus: `migrate_second_bus` mints a **done** `type=control` twin per heading, `fingerprint=""` (`tickets.py:1666–1687`).

## Who is told to read it
- **Parent AGENTS.md only:** `Miss physics: docs/lessons.md` (`:9`); `mission facts in docs/lessons.md` (`:19`); Order of work “Lessons already record kRPC 0.6 traps” (`:354–355`). Children **`agents_md: false`** (e.g. `lars.md:11`, `wernher.md:10`).
- Tests **whole-file** `read_text`: `tests/test_protocol.py:145–147` (needles `latitude` / `Forest is 270`); `:197–200` (`## ` present, no `L-NNN`).
- `docs_inventory.lesson_headings` reads the whole file (`:291–300`).
- PARKED kerbin file tells letsgrok agents to read live lessons (`docs/archive/kerbin-lessons.md:3`).
- Lars/Wernher cards say **append**, not “read the novel.” Packet third path is the helper `.py` (`lars.md:80–82`), not lessons.
- CHARTER/krpc: traps in agent-notes (`CHARTER.md:78–79`, `krpc.md:5`). CHARTER has **no** `lessons.md`.
- Gene/Hank/Gus/Linus/Mortimer/Jeb/Katherine cards: **no** `lessons` string.

## Injected every hire?
- **Packet skim:** desk + BRIEF (+ type extras). `infer_links` **never** adds `docs/lessons.md`. `agent-notes.md` is **`--deep` only** on `type=systems` (`tickets.py:396–397`, `:425–426`).
- **PROTOCOL spawn `read:`** desk + ≤2 role paths (`PROTOCOL.md:335–343`). One line: `lessons.md stays run headings` (`:564`) — not a spawn path.
- Parent AGENTS.md injects **both files as fact sources** every parent turn. Children do not receive AGENTS.md; Lars/Wernher still open lessons **to append** because the **job card** says so.

## Stale vs live
- Live writes: lessons **2026-08-25T21-57-33Z**; agent-notes Log **2026-08-25**. Environment block still **2026-08-21**.
- Kerbin `L-*` chain is PARKED, not live dispatch.

## Files read
`docs/lessons.md` `:1–80` + `^##` + `:2840–2871`; `docs/agent-notes.md` `:1–40` + `^##` + `:560–599` + `:762–791`; `AGENTS.md` `:1–20` `:326–356`; `.grok/agents/lars.md` `:1–40` `:60–86` `:163–181`; `docs/crew/lars.md`; `docs/crew/wernher.md`; `.grok/agents/wernher.md` `:1–15` `:60–97`; `.grok/agents/verena.md` `:24`; `OPS.md:369`; `PROTOCOL.md:325–360` `:564`; `BRIEF.md:83`; `CHARTER.md:78–79`; `krpc.md:1–5`; `tests/test_protocol.py:128–200`; `docs_inventory.py:17–31` `:291–345`; `tickets.py:371–448` `:1632–1693`; `docs/archive/kerbin-lessons.md` PARKED; `README.md:270`.

===== CENSUS 4 =====
## Topic
Ticket bus vs leftover markdown boards. Source of truth is `board.jsonl` + `head.json`. `BOARD.md` is a human table dump. Seated `plan.md` is a Gene **render**. `protocol fly` prefers the fly ticket, then plan+card.

## Counts (path:line or wc)
- TYPES 11 `tickets.py:19–31`. ID_PREFIX science `S` / fly `M` / vehicle `C` else `T` `:59–63`. Live T- ids stay.
- BOARD `open: 74 / 471` `tickets/BOARD.md:3`; table ends `:80`.
- No `def packet()`. Skim is `format_packet` `:477–547`. Links `infer_links` `:371–448`. Always skim: `desk.md` + `BRIEF.md` `:396–397`. By type: fly→`missions/jebediah/briefing.md`; science→`science.md`; vehicle→`vab.md`; control→`blocks.md`; org/rsi→`OPS.md`. **Not** `BOARD.md`. Tests `test_tickets.py:1034` assert that.
- `_FLY_PAYLOAD` `{cli,campaign,phase,science_ids,recommended,learn}` `:887–889`. `fly_fields` also `go`/`learn` `:892–924`. `STAMP_RULES` go=gene, capable=gus, science_payload=linus `:92–98`. Findings `payload.findings` (legacy `feedback`) `:632–698`. Fingerprints `fingerprints.json`.
- `sit-card.json` keys: `craft`, `hangar`, `slots[eid,part,hang_s,on_craft,unlocked,host]`, `do_not_toggle`, `wait`. **No `.py` reads it.** GLOSSARY: retired `:37`.
- Crew dated bullets: jebediah ≥199 last `2026-08-25T22-06-37Z`; lars 89 (08-25 T-469); gene 106 (**last 08-24**); linus 77; gus 53; mortimer 52; wernher 46; verena 21; hank 12; katherine 2; walt/bill/bob/valentina/grok 1.
- `note-tech.md` last `2026-08-22T23:18Z`. `loop.md` heading only.

## Who writes it
- Tickets: any desk `open`; Hank route; Gene `go`/`cli`/`campaign`/`phase`/`learn` (crewed); Hank `attach-run` overwrites uncrewed `learn`; Gus `capable`; Linus bind payload; `tickets feedback` → findings; `_rebuild` writes `BOARD.md` `:303,719–744`; `tickets dump` → `house_dump.render_all` science/seated-science/seated-plan/seated-briefing/slate `:418–436`.
- Gene: seated `plan.md` render + briefing prose `PROTOCOL.md:500–503` `gene.md:43–44`. Linus: `science.md` dump `:478`. Gus: `vab.md` after stamp `.grok/agents/gus.md:101`. Mortimer: world-model **Practice** `PROTOCOL.md:504`. Commander CLI: `loop.md` / `note-tech.md` `main.py:751–756`. Crew logs: each desk one line. `card.py` still parses `science.md` fallback (`hop.py:317`, `pad.py:66`, `splash.py:60`, `protocol.py:97–118`).

## Who is told to read it
- Spawn: desk + `tickets packet` + BRIEF. **No BOARD.md** `BRIEF.md:4` `PROTOCOL.md:341–342` `AGENTS.md:162–163` `OPS.md:379–380` `gene.md:38`.
- Fly gate: `protocol.fly_gate` ticket then `plan.get(go/cli/campaign)` + `science.md` card `:132–135,262–268`. `ops.fly_gate` tickets-only `:414–419`.
- Packet still names leftover boards: science hire `science.md`; vehicle `vab.md`; fly `missions/jebediah/briefing.md`; control `blocks.md`.
- `BOARD.md` live “read”: OPS human dump `:90`; CLI `tickets board` `:1895–1897`. Archive cites PARKED. `feedback-plan.md` cites `BOARD.md:3–7`. No job card says read BOARD; Gene is told not to.

## Injected every hire? (job card / AGENTS.md / packet / PROTOCOL)
- Yes: `desk.md` + BRIEF + packet stdout (`AGENTS.md:162`, PROTOCOL spawn `:328–345`, every `.grok/agents/*.md` BRIEF). Children `agents_md: false`.
- Packet skim injects type boards above. Not `BOARD.md`, `plan.md`, `world-model.md`, `loop.md`, `note-tech.md`, crew logs.
- `lessons.md`: parent AGENTS miss-physics `:9,19,326` — **not** packet. PROTOCOL `:564` run headings.

## Stale vs live (dated last write)
- **Live bus:** `head.json` / `board.jsonl` / `fingerprints.json`; BOARD table regenerated on patch; science dump bound T-404/T-460/T-461 `science.md:22–24`; seated briefing dump `missions/jebediah/briefing.md:3–10` (T-081 uncrewed hop, t7-wheel, 10-57-36Z); seated plan `cli/campaign/science_ids` `plan.md:15–18`.
- **Diverged leftovers:** `docs/program/briefing.md` still Forest thermo T-077 / proc-long (`:3–9`) — **not** in `render_all`. `docs/program/plan.md` stub, no `cli`/`campaign`, `expect_apo_max: 140000` vs seated `400000`. `sit-card.json` craft `east-t3-pbc`, TELEMETRY `unlocked: false`. `note-tech` frozen 08-22. `loop.md` empty. Gene log last 08-24 Ad astra proc-long vs 08-25 hops/Linus PresMat. Practice dated 08-25 `world-model.md:686–718`. `vab.md` t7-wheel capable yes, Gus 08-25.

## Files read
`tickets/BRIEF.md` `README.md` `BOARD.md:1–40,77–80` `tickets.py` `OPS.md` `PROTOCOL.md` `protocol.py` `ops.py` `house_dump.py` `card.py` `sit-card.json` `plan.md` (program+seated) `science.md` `vab.md` `briefing.md` (program+seated) `world-model.md` `loop.md` `note-tech.md` `GLOSSARY.md` `AGENTS.md` `.grok/agents/{gene,gus}.md` `docs/crew/log/*` (counts + last stamps). Archive ticket-bus-cutover **PARKED**.

===== CENSUS 5 =====
Kernel still writes several live MDs on hop/desk/CLI; `lessons.md` has **no** Python writer (honor-system append). Packet skim is `desk.md`+BRIEF, not lessons. Children `agents_md: false`; parent AGENTS still names lessons.

## Topic
Kernel `docs/*.md` writers AS-IS. `hop.py` / `hop_factory.py` / `protocol.py` / `ops.py`: **0** `write_text` of `docs/*.md`.

## Counts (path:line or wc)
- `lessons.md` `^##`: **156** (top `docs/lessons.md:24`; file ~2872).
- `last-flight.md`: **10** lines (`docs/last-flight.md:1`–`:9`).
- `ship.md`: live kv; `as_of: 2026-08-25T22:09Z` (`docs/program/ship.md:5`).
- Crew `2026-08-25` grep (cap 80): mortimer/linus/lars/gus/verena/jeb/wernher/hank present; gene first line **08-24** (`docs/crew/log/gene.md:3`); bill/bob/grok/valentina/walt **08-20** only.
- Jeb kernel log last stamp **22-06-37Z** (`docs/crew/log/jebediah.md:211`). Lars honor last **T-469** (`docs/crew/log/lars.md:3`).
- `note-tech.md` last dated **08-22T23:18Z** (`docs/program/note-tech.md` EOF). Seated `loop.md` last Hank abort T-465 (`docs/missions/jebediah/loop.md:21`).
- `tickets.py` `lessons.md`: **read** twins only (`tickets.py:1633`–`:1687`).

## Who writes it
| file | kernel | honor |
|---|---|---|
| `docs/last-flight.md` | `main.write_handoff` `HANDOFF.write_text` (`main.py:30`,`77`) | — |
| twin `…/logs/{stamp}-{cmd}.md` | same (`main.py:81`–`:85`) | — |
| `docs/archive/reviews/*-review.md` | `review.write_review` if jsonl under `docs/missions/` (`review.py:177`–`:225`); `learn_block` is `## Learn` **in that review** (`review.py:247`–`:276`), not lessons | — |
| `docs/program/desk.md` | `desk.write_desk_md` via `format_desk` (`desk.py:640`–`:648`); `main.py desk` (`main.py:993`) | — |
| `docs/program/ship.md` | `flightlog._publish_ship` / `publish_hangar_radio` (`flightlog.py:30`,`626`,`639`) | — |
| jsonl | `flightlog` `seated_logs_dir` = `docs/missions/<seat>/logs/{stamp}-{cmd}.jsonl` (`flightlog.py:246`–`:259`; `missions.py:103`) | — |
| `attach_run` | JSON ticket + `payload.learn`; `who="wernher"` from hop exit (`main.py:106`; `tickets.py:1359`–`:1392`). Packet `live_run` **hardcodes** `docs/missions/jebediah/logs/{live}.jsonl` (`tickets.py:424`,`458`) | — |
| `BOARD.md` | `tickets._write_board_md` (`tickets.py:16`,`744`) | — |
| `plan.md` / `briefing.md` | `house_dump.render_all` on `tickets dump` (`house_dump.py:21`–`:22`,`428`–`:432`); `uplink.write_plan_file` (`uplink.py:209`); `main.py brief` (`main.py:916`); `missions.sync_shim` → `docs/program/plan.md`+`briefing.md` (`missions.py:192`–`:209`) | Gene render (`PROTOCOL.md` + `.grok/agents/gene.md:43`) |
| `loop.md` | `uplink.note` append seated `…/loop.md` (`uplink.py:56`,`222`); CLI `main.py note` (`main.py:866`) | — |
| `note-tech.md` | `uplink.note_tech` append (`uplink.py:229`–`:249`); CLI `main.py note-tech` (`main.py:871`) | Commander card |
| `docs/crew/log/<pilot>.md` | **kernel only `current_pilot`** on hop close (`crew.py:126`; `main.py:117`) | job cards “one log line” (gus/linus/lars/wernher/gene/…) |
| `docs/lessons.md` | **none in `*.py`** | Lars XOR Wernher |
| `current.md` | `missions.write_current` (`missions.py:186`) | — |
| `uplink.md` | `uplink` (`uplink.py:209`,`399`) | Gene CLI |

## Who is told to read it
- Packet skim: always `desk.md` + BRIEF (`tickets.py:396`–`:397`; `PROTOCOL.md:340`; BRIEF `docs/program/tickets/BRIEF.md:3`). `last-flight` on `--deep` for fly/control/recover (`tickets.py:412`,`421`,`428`). **lessons.md not in `packet()`.**
- Parent AGENTS: CHARTER/PROTOCOL; last-flight before fly; miss physics = lessons (`AGENTS.md:3`–`:9`,`19`).
- Walt/Hank: `ship.md` (`AGENTS.md`; `.grok/agents/hank.md:16`,`104`). Gene mid-hop: `ship.md` (`.grok/agents/gene.md:22`).
- Lars portrait: append lessons (`docs/crew/lars.md:33`). Verena: do **not** edit lessons (`.grok/agents/verena.md:24`).

## Injected every hire? (job card / AGENTS.md / packet / PROTOCOL)
- **desk.md:** yes — packet + every job card “Packet is desk.md” + parent `python main.py desk`.
- **BRIEF.md:** yes — packet skim (`PROTOCOL.md:345`).
- **lessons.md:** not packet. Parent AGENTS **yes** (`AGENTS.md:9`,`19`,`326`–`:345`). Children `agents_md: false` (`AGENTS.md:7`) **but** Lars After a miss (`.grok/agents/lars.md:165`) and Wernher miss heading (`.grok/agents/wernher.md:92`) still command append. BRIEF fingerprint line (`BRIEF.md:83`). OPS map (`OPS.md:369`). PROTOCOL: “stays run headings” only (`PROTOCOL.md:564`).
- **last-flight / ship:** AGENTS parent + Hank/Gene/pilot cards; not skim unless `--deep`.
- **note-tech / loop / plan / crew log / lessons:** not `packet()` skim.

## Stale vs live (dated last write)
- last-flight **exit=2 abort**, 10 lines, no stamp (`docs/last-flight.md:1`–`:9`) vs desk `last: … exit=0` (`docs/program/desk.md:15`); `review: docs/last-flight.md` (`desk.md:16`).
- ship **22:09Z** `sit: pre_launch` t7-wheel (`ship.md:4`–`:8`) vs last-flight hop ABORT.
- plan craft **proc-long-pbc** (`docs/missions/jebediah/plan.md:13`) vs desk **t7-wheel-pbc** (`desk.md:12`). Seated briefing t7-wheel (`briefing.md:4`); shim `docs/program/briefing.md:4` still **proc-long**.
- note-tech frozen **08-22**; hops/logs **08-25**.
- lessons newest **21-57-33Z-hop — rf-ignition-ullage** (`lessons.md:24`); jeb kernel **22-06-37Z** (`jebediah.md:211`) has no newer heading. EOF still 08-23 leftover (`lessons.md:2852`).
- gene log newest **08-24** (`gene.md:3`). Seat `flight: jebediah` (`current.md:1`).

## Files read
`review.py` `desk.py` `tickets.py` `main.py` `flightlog.py` `crew.py` `uplink.py` `missions.py` `house_dump.py` `ops.py` `protocol.py`(empty write) `hop.py`/`hop_factory.py`(no md write) `AGENTS.md` `PROTOCOL.md` `OPS.md` `BRIEF.md` `.grok/agents/{lars,wernher,gene}.md` `docs/crew/lars.md` `docs/{lessons,last-flight}.md` `docs/program/{ship,desk,plan,briefing,loop,note-tech,current}.md` `docs/missions/jebediah/{plan,briefing,loop}.md` `docs/crew/log/{jebediah,lars,wernher,gene,hank,gus,linus,mortimer,verena,walt,katherine,bill,bob,grok,valentina}.md`. `docs/archive/` **PARKED** (reviews dest + cutover hits).

===== CENSUS 6 =====
## Topic
Lars pulse vs Wernher catalog vs immortal `hop.py` — current house, AS-IS. No per-craft compose `.py` on disk.

## Counts (path:line or wc)
- `hop.py` **3300** lines, **127** `^def` (`hop.py:161`–`:3238`). Header parked water/splash (`hop.py:1`–`:31`). `run_on_vessel` (`hop.py:2260`) dispatches factory unless `wait_water`/`wait_splash` (`hop.py:2300`–`:2303`). `run_hop_to_water` `:3167`; `run_hop_splash` `:3238`.
- `hop_factory.py` **1052** lines, **11** `^def`. `run_factory_vessel` `:274`–`:1051` (~778-line loop). Imports pad-RF `:31`, warp `:33`–`:41`.
- `hop_factory_pad.py` **202** lines, **8** `^def` (`_pad_engines` `:20` … `_pad_hold` `:165`).
- `physics_warp.py` **429** lines, **27** `^def`. Catalog header `:1`–`:29`.
- `pad.py` **772** / **30** `^def`. `splash.py` **342** / **7**. `science.py` **1451** / **56**.
- `docs/program/blocks.md` **173** lines. Gene names `pad` `hop` `splash` `tech-unlock` (`blocks.md:1`). Hop row still names `hop.py` slew/water (`:11`); factory named `hop_factory.py` (`:11`, `:16`–`:17`).
- `tests/test_hop.py` **8803** lines, **231** `def test_` (godfile). `tests/test_hop_factory.py` **234** / **8** (pad-RF only, `:1`). `tests/test_physics_warp.py` **592** / **30** tests.
- Per-craft compose `.py`: **MISSING** (no `hop_t7*.py`). Cards allow a t7-only file (`.grok/agents/lars.md:33`; `PROTOCOL.md:140`; `CHARTER.md:116`). Inland compose on disk is `hop_factory.py`. Crafts are `crafts/*.craft` only.

## Who writes it
- **Lars:** `hop_factory.py` pulse, `hop_factory_pad.py` pad-RF, `pad.py`, `splash.py`, `science.py` sit-match, parked water/splash + shared helpers in `hop.py` (`.grok/agents/lars.md:19`–`:38`, `:54`–`:55`). Miss → `docs/lessons.md` heading (`:165`). `blocks.md` only if a new phase name (`:169`).
- **Wernher:** `physics_warp.py` sit/warp/timeout/leftover/chute blocks; extract what still lives in `hop.py` (`.grok/agents/wernher.md:27`–`:30`). Does not write the living pulse (`:33`–`:36`). XOR Lars on the same `.py` (`:37`–`:39`).
- **Gene:** no `.py` (`.grok/agents/gene.md:18`).

## Who is told to read it
- Lars packet third path = named helper (`PROTOCOL.md:356`–`:359`; `BRIEF.md:75`–`:78`; table `.grok/agents/lars.md:29`–`:38`).
- Wernher: `physics_warp.py`; `hop.py` only to extract (`wernher.md:27`–`:30`).
- Gene packet: desk + BRIEF; RF names `hop_factory_pad.py` / `hop_factory.py` (`gene.md:72`–`:73`). `gene.md` hits on `blocks.md`: **0**.
- `blocks.md:3` says owned by Lars. `test_hop.py` still imports hop + factory + pad helpers.

## Injected every hire? (job card / AGENTS.md / packet / PROTOCOL)
- Job cards `.grok/agents/lars.md` / `wernher.md`: **yes** (spawn). Both `agents_md: false` — **AGENTS.md not** child-injected (`lars.md:11`, `wernher.md:10`).
- Packet: `desk.md` + `tickets packet` + `BRIEF.md`. Not PROTOCOL, not CHARTER, not `blocks.md`, not `hop.py` on a factory miss, not `lessons.md` as a read (append-after-miss only, `lars.md:165`).
- Parent AGENTS.md reads CHARTER then PROTOCOL; “Miss physics: `docs/lessons.md`” is parent, not the child packet.

## Stale vs live (dated last write)
- Live: Lars `2026-08-25` T-469 `hop_factory_pad` (`docs/crew/log/lars.md:3`). Wernher warp T-450 same day (`docs/crew/log/wernher.md:9`). Last Lars named `hop.py` T-326 `2026-08-24` (`lars.md:26`). RSI paper `docs/program/lars-rsi.md` applied `2026-08-25` (pad extract; compose stays; `run_factory_vessel` `:273`–`:1051`; house `test_hop.py` 231; factory tests **6** at `lars-rsi.md:37` vs live **8**).
- `world-model.md:505`–`:508` (T-376): `hop.py` ~3298 / `hop_factory.py` ~779 / `test_hop.py` ~7417 — live **3300** / file **1052** (fn ~778) / **8803**. `wernher.md:32` still ~7417.
- `PROTOCOL.md:349` “Jeb / Lars **low**” vs AGENTS medium for Lars. `blocks.md:11`/`105`–`:165` still park water/splash law in the Gene hop row.
- Crew logs: lars **89** `^-` (newest `:3`; last 40 = `:52`–`:91`, 2026-08-21 hop-to-water). wernher **46** `^-` (newest `:3`; file ends `:80`).

## Files read
`CHARTER.md`, `PROTOCOL.md`, `hop.py`, `hop_factory.py`, `hop_factory_pad.py`, `physics_warp.py`, `pad.py`, `splash.py`, `science.py`, `blocks.md`, `.grok/agents/{lars,wernher,gene}.md`, `BRIEF.md`, `OPS.md`, `world-model.md`, `lars-rsi.md`, `tests/test_hop.py`, `tests/test_hop_factory.py`, `tests/test_physics_warp.py`, `docs/crew/log/{lars,wernher}.md`, `AGENTS.md`, repo root listing.

===== CENSUS 7 =====
## Topic
A cold child loads the job card (`.grok/agents/<desk>.md`, `agents_md: false` on all 16 cards) plus whatever the parent pastes as the PROTOCOL spawn packet. Parent Hank’s TUI session **does** get `AGENTS.md` (`AGENTS.md:7`–`:8`, `CHARTER.md:100`–`:101`). Children do not. Packet on disk is `desk.md` + `tickets packet` stdout + `BRIEF.md` (`PROTOCOL.md:340`–`:346`, `AGENTS.md:162`–`:163`). `read:` is desk + ≤2 role paths (`PROTOCOL.md:335`) and also `read` ≤3 (`AGENTS.md:181`); Lars’s third path is the named helper `.py` (`PROTOCOL.md:356`–`:360`). First command is inbox, then packet (`BRIEF.md:5`–`:7`). Jsonl is tape CLI, not `read_file` (`tickets.py:372`, `PROTOCOL.md:347`).

## Counts (`path:line`)
- `agents_md: false`: 16/16 cards (`.grok/agents/*.md` frontmatter). Spotter card still on disk (`.grok/agents/spotter.md:11`).
- Packet skim always: `desk.md` + `BRIEF.md` (`tickets.py:396`–`:397`). Type extras: fly `docs/missions/jebediah/briefing.md` (`:406`); science `science.md` (`:414`); vehicle `vab.md` (`:416`); control `blocks.md` (`:420`); org/rsi `OPS.md` (`:430`). systems skim: none (`agent-notes` is `--deep`, `:426`).
- `lessons.md` in job cards: write Lars/Wernher (`lars.md:165`, `wernher.md:92`); Verena forbidden (`verena.md:24`). Not in `infer_links`.
- Crew logs: 15 files under `docs/crew/log/`. Job cards say **write one line**: linus/gus/wernher/verena/katherine/mortimer. **Read**: Gus reviews (`gus.md:19`); Verena interviews (`verena.md:66`).
- `resume_from` tax: `PROTOCOL.md:365`–`:372`, `AGENTS.md:140`–`:141`, `hank.md:57`–`:59` (parent text; not in specialist First command).

## Who writes it
- `desk.md`: parent `python main.py desk` (`AGENTS.md:159`–`:160`).
- Packet stdout: `tickets.py` (`:507`–`:547`).
- `BOARD.md`: `tickets board` dump (`OPS.md:88`–`:90`).
- `science.md` dump: Linus (`PROTOCOL.md:478`, `:506`).
- `vab.md` / `.craft`: Gus (`PROTOCOL.md:505`, `gus.md:101`).
- `world-model.md` flight layers: Gene; Practice: Mortimer (`PROTOCOL.md:67`–`:70`, `:500`–`:504`).
- `lessons.md` headings: Lars **or** Wernher (`AGENTS.md:326`, `lars.md:165`).
- `note-tech.md`: Commander CLI (`uplink.py:8`; `pilot.md:64`).
- jsonl: control-writer `Telem.read` (`PROTOCOL.md:233`); Hank `attach-run` (`OPS.md:367`).
- Crew logs: each desk’s one line (job cards).

## Who is told to read it
- **Packet skim (child who runs First command):** desk + BRIEF + type extra above. Gene: **do not** read `BOARD.md` (`gene.md:38`). Gene: do not dispatch via world-model novels or `science.md` (`gene.md:20`).
- **`lessons.md`:** parent `AGENTS.md:9`; child **write** after miss (Lars/Wernher), not First command.
- **`world-model.md`:** parent CHARTER/PROTOCOL/AGENTS; Verena story layer (`verena.md:14`); Mortimer mutates Practice (`mortimer.md:5`–`:6`).
- **`note-tech.md`:** file header says Lars/Gus/Wernher/Gene between exits (`note-tech.md:3`–`:4`); desk **clips** it (`desk.md:27`). AGENTS: tape not bus (`AGENTS.md:127`).
- **jsonl:** query `telem` / `tickets landing`; do not eat rows (`PROTOCOL.md:347`, `lars.md:79`).
- Extra job-card reads (not packet): voice `docs/crew/<slug>.md`; `fingerprints.json`; `krpc.md` (Gene `gene.md:90`, Lars `lars.md:149`).
- PROTOCOL/CHARTER: **parent** (`AGENTS.md:3`). Child job cards do not open them except Mortimer *rewrites* PROTOCOL (`mortimer.md:39`).

## Injected every hire? (job card / AGENTS.md / packet / PROTOCOL)
- **Job card:** yes, full prompt (sit memory, reasoning line, First command).
- **AGENTS.md / CHARTER:** parent only. Children `agents_md: false`.
- **Packet:** parent must paste; child First command re-runs `tickets packet`. Skim, not `--deep` (`PROTOCOL.md:351`, `hank.md:56`–`:57`).
- **PROTOCOL.md file:** not auto-injected into children.
- **Reasoning floors (conflict on disk):** PROTOCOL+`hank.md`: Jeb/Lars **low**, Mortimer **medium** (`PROTOCOL.md:348`–`:350`, `hank.md:54`–`:56`). Job cards: Jeb/Lars **medium**, Mortimer **high** (`jebediah.md:12`–`:13`, `lars.md:14`–`:15`, `mortimer.md:17`). Kernel: `walt` low, `mortimer` high, else type rsi/org/ctt or S1 high, S4 low, else medium (`tickets.py:117`–`:120`, `:337`–`:354`). OPS matches kernel (`OPS.md:382`–`:383`). Never xhigh. `packet_cmd` ignores the reasoning arg (`tickets.py:556`–`:557`).

## Stale vs live (dated last write)
- `desk.md`: live sit lock free, craft t7-wheel-pbc, last hop exit 0; **note-tech clip 2026-08-22T23:18Z** (`desk.md:1`–`:27`).
- `note-tech.md`: last bullet **2026-08-22T23:18Z**.
- `lessons.md`: newest heading **2026-08-25T21-57-33Z** rf-ignition-ullage.
- `science.md` / `vab.md`: bank 2.2905 / t7-wheel-pbc (same sit as desk).
- Two briefings diverge: packet fly skim `docs/missions/jebediah/briefing.md` (t7-wheel-pbc, `hop`); parent AGENTS names `docs/program/briefing.md` (proc-long-pbc, hop_apo 50000).
- `BOARD.md`: open 74/471, T-471 inbox (render of `head.json`).
- Last RSI on disk: `docs/program/lars-rsi.md` 2026-08-25 (git ea7f60b per brief).
- `resume_from`: parent law 2026-08-23 floors / PROTOCOL hire-freshness; specialist cards never mention it.

## Files read
`AGENTS.md:1`–`:80`, `:112`–`:210`; `PROTOCOL.md:1`–`:15`, `:67`–`:104`, `:327`–`:372`, `:478`–`:509`; `tickets.py:117`–`:120`, `:337`–`:448`, `:500`–`:557`; `BRIEF.md:1`–`:80`; `desk.md:1`–`:40`; `CHARTER.md:95`–`:101`; `OPS.md:82`–`:90`, `:362`–`:386`; `.grok/agents/{lars,gene,linus,gus,wernher,hank,mortimer,jebediah,pilot,verena,spotter}.md` First command / miss; `science.md:1`–`:14`; `vab.md:1`–`:15`; `world-model.md:1`–`:15`, `:322`–`:359`; `BOARD.md:1`–`:15`; `lessons.md:1`–`:24`; `note-tech.md:1`–`:4` + last bullets; `docs/program/briefing.md:1`–`:8`; `docs/missions/jebediah/briefing.md:1`–`:8`; `docs_inventory.py:27`–`:32`, `:380`; `lars-rsi.md:1`–`:8`; `docs/crew/log/` listing.

===== CENSUS 8 =====
## Topic

Inventory leftover is **I-012..I-020 and F-001..F-015 item files**, not `feedback-plan` / `lars-rsi` / `learn-rsi` / `note-tech`. Those four still sit in live `docs/program/`. Classify treats three as **`live_kernel`** (fallthrough) and **`note-tech.md` as `live_tape`**. They are **not** in `_ORG_NOVEL_NAMES`. `_ORG_NOVEL_NAMES` (10 basenames) are **absent** from live `docs/program/` and **present** under PARKED cutover. Spawn cards: **`verena.md` still names a FORBIDDEN path.** AGENTS / PROTOCOL / BRIEF do not.

## Counts (path:line or wc)

- `docs_inventory.py` **425** lines. `DOC_CLASSES` `19:24`. `FORBIDDEN_DISPATCH` **4** needles `27:32`. `_ORG_NOVEL_NAMES` **10** `47:60`. `_IF_ITEM` leftover regex `43:45`. `classify` `307:346` (leftover **before** archive `310:314`; `note-tech.md`/`loop.md` tape `343:344`; else kernel `346`).
- Packet drop: `skim_mentions_forbidden` `380:387`; `tickets.py` `infer_links` `389:392`, desk+BRIEF skim `396:397`.
- Tests import: `tests/test_tickets.py` `1414`, `1435`, `1469`, `1483` only. Live lock: leftover must still contain `I-012.md`/`F-014.md` `1448:1450`; `docs/program/improve/README.md` and `docs/crew/niche/gene.md` **not files** `1453:1454`. Spawn-omit check is **AGENTS.md + BRIEF.md only** `1485:1491`, not job cards.
- Live `docs/program/`: **29** `*.md` including `feedback-plan.md`, `lars-rsi.md`, `learn-rsi.md`, `note-tech.md`, `loop.md`. **0** I-/F- item files. **0** `_ORG_NOVEL_NAMES` basenames.
- Leftover stems on disk: **9+15=24** files under PARKED `docs/archive/2026-08-23-md-cutover/program/{improve,feedback}/` (`I-012`..`I-020`, `F-001`..`F-015`). Those classify **`leftover_migrated`**, not `parked_archive`, because `_IF_ITEM` wins first. PARKED cutover also holds the 10 novel names (`NEXT-ORG.md`, `SPEED.md`, `ORG.md`, `ORG-INTERACTIONS.md`, `org-session-audit.md`, `rsi-jump.md`, `ticket-bus-cutover.md`, `rescue.md`, `tickets/RSI-JUMP.md`, `feedback.md`).
- `docs/lessons.md:4` names `docs/archive/kerbin-lessons.md` (a FORBIDDEN needle) from live kernel.
- Crew: `docs/crew/log/mortimer.md` **3** path cites (`:3` lars-rsi, `:20` feedback-plan, `:27` learn-rsi). `jebediah.md` note-tech **1** (`:3`).

## Who writes it

Kernel module; no desk in-file. Consumers: `tickets.infer_links`, `migrate_second_bus` (`tickets.py:1632:1634`). RSI papers: Mortimer log. `note-tech.md`: Commander CLI (`main.py:755:875`, `uplink.py:8:34`). `desk.py:44:624` clips it into `desk.md`.

## Who is told to read it

`docs_inventory.py`: tests + packet filter — **not** PROTOCOL/BRIEF/GLOSSARY. Leftover I/F: `migrate_second_bus` + live tests. `note-tech.md`: AGENTS `127:127`, GLOSSARY `31:31`, `pilot.md:64`, desk clip. `learn-rsi.md`: `world-model.md:464`. `feedback-plan.md` / `lars-rsi.md`: Mortimer log only among live program/AGENTS/PROTOCOL/BRIEF.

## Injected every hire? (job card / AGENTS.md / packet / PROTOCOL)

**No** for `docs_inventory.py`, leftover I/F files, `feedback-plan.md`, `lars-rsi.md`, `learn-rsi.md`. Packet skim **always** `desk.md` + `BRIEF.md`; `add()` drops FORBIDDEN paths. AGENTS/PROTOCOL/BRIEF: **0** `docs/archive/` / `docs/crew/niche/` / `docs/program/improve/`. Job cards `agents_md: false`. **Yes-adjacent:** AGENTS names `note-tech.md` as tape (`127`); Lars/Wernher cards append `docs/lessons.md`. Spawn prompt **does** name forbidden: `.grok/agents/verena.md:65` ``docs/archive/kerbin-lessons.md``. Workflows (not cards) still list `docs/program/improve/`, `docs/crew/niche/`, `docs/archive/` (`.grok/workflows/{org-session-audit,ticket-bus-cutover,learn-rsi,org-pristine}.rhai`).

## Stale vs live (dated last write)

- `note-tech.md` last line **2026-08-22T23:18Z**; `desk.md:27` still clips that line.
- `learn-rsi.md` applied **2026-08-24** (`mortimer.md:27`).
- `feedback-plan.md` compile-only **2026-08-24** (`:20`); header “no apply”.
- `lars-rsi.md` applied **2026-08-25** (`:3`).
- `docs_inventory.py`: **no dated heading** in file.
- `_ORG_NOVEL_NAMES` + I/F items: last tree home **2026-08-23** PARKED cutover, not live `docs/program/`.

## Files read

`docs_inventory.py`; `tests/test_tickets.py:1414:1504`; `tickets.py:371:448`, `1625:1638`; `docs/program/` listing; PARKED `docs/archive/2026-08-23-md-cutover/program/` names; `AGENTS.md:123:128`; `PROTOCOL.md:1:80`; `tickets/BRIEF.md:1:90`; `GLOSSARY.md:28:33`; `feedback-plan.md`, `lars-rsi.md`, `learn-rsi.md`, `note-tech.md` (head+tail); `lessons.md:1:14`; `.grok/agents/{verena,lars,pilot}.md`; `docs/crew/log/mortimer.md:1:30`; greps for `FORBIDDEN_DISPATCH`, leftover names, `docs_inventory`.

===== CENSUS 9 =====
Last RSI on disk is `ea7f60b` (`Apply Lars RSI`, 2026-08-25 21:42Z). HEAD is `21be09e` (`org-pristine`, 2026-08-26 05:38Z): six commits later, one morning commit after a same-night burst. Ticket bus last event is still 2026-08-25T22:10:10Z. No `2026-08-26` string under `docs/`. `git status --short` is MISSING (no shell). Os “two to three turns” matches two calendar bursts, not six commits; session-turn count is MISSING.

## Topic
Git + tickets since last RSI (`ea7f60b` / `docs/program/lars-rsi.md`).

## Counts (path:line or wc)
- After RSI (`.git/logs/refs/heads/main:82-88`): `8e13299` Gus restamp; `3c3853b` Gus stamps; `be33da8` PresMat keep; `4720e8e` MainThrottle 1; `3616e52` independent once; `21be09e` org-pristine (HEAD `.git/refs/heads/main:1`).
- Last 30 oneline (HEAD←): `21be09e` `3616e52` `4720e8e` `be33da8` `3c3853b` `8e13299` `ea7f60b` `80c87ad` `42ba421` `ab9525b` `22cd611` `50d9f58` `3853908` `3635da5` `74c225f` `364bb50` `6046d1e` `daf97a2` `f6367fd` `c76e25d` `77444eb` `925f188` `451409c` `4365bba` `4a79846` `e1fd93a` `d59e3a0` `62628e8` `7adf0ed` `2c03954`.
- Uncommitted: MISSING.
- `board.jsonl` ends L2068; last `at` 2026-08-25T22:10:10Z (`T-081` patch hank + `T-471` open os). 08-26 events: 0.
- `BOARD.md:3` open 74/471; no dated 08-25/26 rows. Top: `T-471` inbox lars, `T-081` inbox gene.
- T-081 (`head.json:3215-3619`): `go: yes` (`:3339`); `payload.campaign: uncrewed` `cli: python main.py hop` (`:3342-3343`); `learn:` pre_launch synth soft (`:3567`); `phase: hop`; `status: inbox`; `updated: 2026-08-25T22:10:10Z`. No `payload.go`.
- Crew 08-25 dated lines: mortimer 13, lars 12, wernher 10, jebediah 10 (`:202-211`), linus 8, gus 6, hank 6, verena 2; gene/katherine/walt/bill/bob/valentina/grok **0**. 08-26: **0**.
- `lessons.md` `## 2026-08-25`: **22** (`:24-383`); 08-26: **0** (not 80).
- `missions/jebediah/logs` 08-25 jsonl starts: **15 hop + 3 hangar**; 08-26: **0**. Jeb log lists 10 hops only (missing 08-20-54, 08-40-14, 08-48-18, 08-56-15, 09-01-24).
- `lars-rsi.md:52-54` §9: T-465 inbox, `test_hop.py` 231 godfile, inland still `run_factory_vessel`, git MISSING (letter).

## Who writes it
- Git: `os@noreply.invalid` (desks commit per BRIEF `:88`).
- Tickets: hank/lars/linus/gus/wernher/mortimer/os (`board.jsonl` `who`).
- Lessons: no byline. XOR Lars/Wernher (`AGENTS.md:326`). 08-25 When:T-ids → Lars rf-ignition/hold-ground/lid; Wernher thin-tape/telem-eyes/warp/ra-rate/Close/ctt (`wernher.md:3-21`).
- Mission tape: hop pid (`crew=` empty); uncrewed still `docs/missions/jebediah/logs/`. Reviews `docs/archive/reviews/` PARKED.

## Who is told to read it
- Parent: CHARTER/PROTOCOL; `lessons.md` miss physics (`AGENTS.md:9,19`). Children `agents_md: false`.
- Packet (`PROTOCOL.md:327-347`): desk + ticket packet + BRIEF; `read:` ≤2 role; jsonl via `telem`/`landing`; last-flight only `--deep`.
- Lars miss: named helper `.py` (BRIEF `:75`); heading names fingerprint (`:83`). Katherine: `telem --window`. Gene Learn: envelope, not jsonl. Verena: do not edit lessons (`.grok/agents/verena.md:24`).

## Injected every hire? (job card / AGENTS.md / packet / PROTOCOL)
- AGENTS parent: yes mention (`:9,:19`); write on miss (`:326,:345`). Not child AGENTS.
- Job cards: Lars after miss (`.grok/agents/lars.md:165`); Wernher on miss (`wernher.md:92`); other desks no.
- Packet: **no** default `lessons.md` (`PROTOCOL.md:340-347`; `:76` not every packet).
- PROTOCOL `:564`: lessons stay run headings.

## Stale vs live (dated last write)
- Live: `BOARD.md` undated table; `head.json` T-081 22:10Z; `board.jsonl` 22:10Z; lessons newest `21-57-33Z` (`:24`); crew newest 08-25; HEAD `21be09e` 08-26 05:38Z.
- Stale vs that HEAD: `lars-rsi.md:54` “Git commit MISSING”; Gene log last 08-24 (`gene.md:3`); Jeb first 15 are 08-20/21 (`jebediah.md:1-15`); Jeb 08-25 log vs 15 hop jsonl.
- 08-26 docs: **empty**. RSI letter same night as `T-466` harvest (`mortimer.md:3`).

## Files read
`.git/HEAD`, `.git/refs/heads/main`, `.git/logs/refs/heads/main`, `.git/COMMIT_EDITMSG`, `docs/program/tickets/{head.json,board.jsonl,BOARD.md,BRIEF.md}`, `docs/program/{lars-rsi.md,PROTOCOL.md}`, `docs/lessons.md`, `docs/crew/log/{mortimer,lars,wernher,jebediah,linus,gus,hank,verena,gene,katherine,walt}.md`, `.grok/agents/{lars,wernher,verena}.md`, `AGENTS.md`, `docs/missions/jebediah/logs/2026-08-25*.jsonl` (starts). `git status --short` MISSING.