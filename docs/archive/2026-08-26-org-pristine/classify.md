

===== CLASS 0 =====
Live `docs/program` is a mixed kernel: packet skim is only `desk.md` + `BRIEF.md` (`tickets.py:396-397`). RSI novels and `world-model` Practice still sit as `live_kernel`. `_ORG_NOVEL_NAMES` are already PARKED. No `leftover_migrated` I/F files remain live.

## Shard
`docs/program/*.md` (26) + `sit-card.json` + `tickets/` md/json/jsonl. `org-flow/` = `index.html` + 6 svg, **0** md/json. `overlay.last` / `uplink.last` / `unrecoverable.last` not md/json. `improve/` `feedback/` **MISSING** live.

## Table
path | class | lines | last writer | injected? | evidence
---|---|---|---|---|---
CHARTER.md | KEEP-MD | 200 | Os/Mortimer | parent AGENTS only | creed `CHARTER.md:1`
PROTOCOL.md | KEEP-MD | 566 | Mortimer | no packet | handoffs `PROTOCOL.md:16`
OPS.md | KEEP-MD | 437 | Hank | no packet | kernel `OPS.md:1`
GLOSSARY.md | KEEP-MD | 42 | house | no | speech `GLOSSARY.md:1`
krpc.md | KEEP-MD | 259 | Wernher | job-card Brief | `.grok/agents/{hank,gene,lars,gus,katherine}.md`
slate.md | KEEP-MD | 47 | Mortimer/dump | Gene fence | `gene.md:161`
desk.md | KEEP-MD | 57 | desk.py | **yes skim** | `tickets.py:396`
tickets/BRIEF.md | KEEP-MD | 132 | Hank | **yes skim** | `tickets.py:397`
tickets/README.md | KEEP-MD | 44 | Hank | no | points at OPS
current.md | KEEP-MD | 3 | desk | no | seat
roster.md | KEEP-MD | 23 | house | no | names
uplink.md | KEEP-MD | 1 | Gene | Commander takes | `uplink.md:1`
ship.md | TAPE | 23 | hop pid | radio not spawn | `ship.md:1`
ra-rate.md | KEEP-MD | 88 | Os 08-25 | no | Cape 64 bps
tech.md | KEEP-MD | 20 | house | no | query only
mods.md | KEEP-MD | 78 | disk 08-23 | no | not GameData
blocks.md | KEEP-MD | 174 | Lars/Gene | no packet | CLI names; body hop-law novel `blocks.md:11`
plan.md | TICKET | 17 | Gene render | no | stale proc-long `plan.md:13` vs desk t7-wheel
briefing.md | TICKET | 20 | Gene | no (fly uses missions/briefing) | stale `briefing.md:3`
science.md | TICKET | 87 | dump/Linus | no | “not dispatch” `science.md:3`
vab.md | TICKET | 40 | Gus | Gus card | `gus.md:5`
tickets/BOARD.md | TICKET | 80 | dump | **forbid** | BRIEF `BRIEF.md:4`
note-tech.md | TAPE | 65 | Jeb 08-22 | no | inv `live_tape` `:343`
loop.md | TAPE | 1 | shim empty | no | same
tickets/board.jsonl | TAPE | 2068 | kernel | no | inv jsonl exception
tickets/head.json | TAPE | 17904 | kernel 22:10Z | no | inv **unclassed** (.json)
tickets/fingerprints.json | TAPE | 212 | kernel | lookup | `BRIEF.md:17`
sit-card.json | TAPE | 24 | kernel | no | stale east-t3 `sit-card.json:2`
RO.md | ARCHIVE | 59 | Os 08-21 | no | “Parked” `RO.md:3` still live
lars-rsi.md | NUKE-LIVE | 54 | Mortimer 08-25 | no | RSI novel `lars-rsi.md:1`
learn-rsi.md | NUKE-LIVE | 186 | Mortimer 08-24 | no | same
feedback-plan.md | NUKE-LIVE | 45 | Mortimer 08-24 | no | compile-only `feedback-plan.md:1`
world-model.md | NUKE-LIVE | 800 | Mortimer T-466 | no packet | chair `world-model.md:1-16`; Practice dump `:322-800`
org-flow/* | ARCHIVE | html+6 svg | poster | no | 0 md/json

## Inventory mismatch
`docs_inventory.py:47-59` `_ORG_NOVEL_NAMES` **not live** — PARKED `docs/archive/2026-08-23-md-cutover/program/` (NEXT-ORG, SPEED, ORG*, rsi-jump, ticket-bus-cutover, rescue, feedback.md). `leftover_migrated` I/F **not live** (same archive). Inv still stamps **live_kernel** on lars-rsi/learn-rsi/feedback-plan/world-model/RO/science/vab/briefing/plan/BOARD (`classify` fallthrough `:345`). note-tech/loop match `live_tape`. `.json` + org-flow **not walked** (`iter_docs` only md/jsonl `:362`). `docs/program/improve/` `feedback/` claimed `parked_archive` `:317-320` — dirs **MISSING** live.

## Files read
`docs_inventory.py:1-60,307-345`; all 26 program `*.md` headers + tails; `sit-card.json`; `tickets/{BRIEF,BOARD,README,head.json,fingerprints.json,board.jsonl}`; `org-flow/index.html`; `tickets.py:396-397`; crew `mortimer.md` (RSI cites 3); `.grok/agents/{gene,gus}.md` inject bits. `docs/archive/` PARKED, not dispatch.

===== CLASS 1 =====
## Shard

`docs/missions` + `docs/crew` + `docs/flights`: **481** md/json. Only Commander folder is `jebediah` (`INDEX.md:7`; `current.md:1` `flight: jebediah`). Uncrewed tape still lands here — the structural bug. Dropped from the table: **442** `logs/` files + **15** portraits + **15** crew logs (grouped). `docs/archive/**` is **PARKED**. `docs/crew/niche` **MISSING**. Spotter is **not** this shard (`.grok/agents/spotter.md` still on disk).

## Table

| path | class | lines | last writer | inj? | evidence |
|---|---|---|---|---|---|
| `docs/missions/INDEX.md` | KEEP-MD | 8 | kernel | no | `INDEX.md:3` one seat |
| `…/jebediah/plan.md` | KEEP-MD | 20 | Gene | no | sit render `plan.md:15` `go:`; **stale** `craft:` proc-long `plan.md:13` vs t7-wheel |
| `…/jebediah/briefing.md` | KEEP-MD | 13 | Gene | **yes** | fly skim `tickets.py:406`; t7-wheel `briefing.md:4` |
| `…/jebediah/science.md` | TICKET | 36 | Linus | no | `science.md:3` `science: tickets`; T-404/460/461 |
| `…/jebediah/craft.md` | TICKET | 22 | Gus | no | `craft.md:13` T-400 capable |
| `…/jebediah/loop.md` | ARCHIVE | 23 | uplink | no | ack dump `loop.md:1`; inv `parked_archive` `docs_inventory.py:327` **still live** |
| `…/logs/*.jsonl` | TAPE | n=228 | kernel | no | inv `live_tape` `:339`; do not inject |
| `…/logs/*.md` | TAPE | n=214 | kernel | no | last-40 handoff `22-06-37Z-hop.md:1`; **0** live `*-review.md` |
| `docs/crew/{15 portraits}.md` | KEEP-MD | ~20–64 | desks | talk | `AGENTS.md:61`; roster |
| `docs/crew/builder.md` | NUKE-LIVE | 24 | stale | **yes if old prompt** | pointer `builder.md:1` |
| `docs/crew/log/*.md` | TAPE | see counts | desks | no | voice TAPE not dispatch |
| `docs/flights/README.md` | KEEP-MD | 23 | kernel | no | attach-run `README.md:14` |
| `docs/flights/index.jsonl` | TAPE | 141 | `flightlog.py` | no | inv `live_tape` `:337` |

Crew-log `^-` counts (newest at top): gene **106**, jebediah **≥209** (file ends `:211` `22-06-37Z` abort), lars **89**, linus **77**, gus **53**, mortimer **52**, wernher **46**, verena **21**, hank **12**, katherine **2**, walt/bill/bob/grok/valentina **1**. Jeb log `:9–:109` still cites live `logs/*-review.md` (**MISSING**; reviews PARKED `docs/archive/reviews/` after `16-37-14Z`).

## Inventory mismatch

No `leftover_migrated` in this shard (I/F items PARKED under `docs/archive/2026-08-23-md-cutover/`). **`loop.md` is `parked_archive` in `classify()` (`docs_inventory.py:327`) but still live.** `craft.md` inv=`live_tape` vs TICKET here. `plan.md`/`science.md` inv=`live_kernel` (asserted `tests/test_tickets.py:1445–1446`) vs KEEP/TICKET. `builder.md` inv=`live_kernel` vs NUKE-LIVE. `*-review.md` would be `parked_archive` (`:323`) — none live in `logs/` (grep 0).

## Files read

`current.md`; `INDEX.md`; seated plan/science/craft/briefing/loop headers; `flights/README.md` + `index.jsonl:1–5,:141`; crew portraits (headers) + `builder.md`; crew logs via `^-` counts + jebediah `:200–:211`; `docs_inventory.py:307–346`; `tickets.py:405–424`; `flightlog.py:1–8`; `main.py:78–85`; `tests/test_tickets.py:1441–1454`. PARKED opened only as listing: `docs/archive/` (reviews + cutover twins). Not dumped: jsonl bodies, gene/lars/linus novels.

===== CLASS 2 =====
Live shard is 19 md files. Parent AGENTS plus Lars/Wernher cards still inject `docs/lessons.md` (2872 lines, 156 `##`). Packet skim does not. Inventory never walks `.grok/agents` or `AGENTS.md`.

## Shard
`.grok/agents/*.md` (16) + `AGENTS.md` + `docs/lessons.md` + `docs/agent-notes.md`. No json in shard. `docs/archive/` not opened (PARKED). Crew `lessons.md` hits in `docs/crew/log/`: **0**. `2026-08-25` hits: ≥65.

## Table
| path | class | lines | last writer | injected? | evidence |
|---|---|---|---|---|---|
| `AGENTS.md` | KEEP-MD | 360 | org/Hank (parent) | parent yes; children no (`:8`) | injects lessons `:9` `:19` `:326` |
| `.grok/agents/hank.md` | KEEP-MD | 195 | Os/Mortie T-448 | spawn yes | NUKE paras: hop clock, T-448 |
| `.grok/agents/lars.md` | KEEP-MD | 192 | Mortie RSI / Lars T-469 | spawn yes | NUKE: T-376, `lessons` append `:165` |
| `.grok/agents/gene.md` | KEEP-MD | 169 | Mortie fence | spawn yes | long Return; no lessons |
| `.grok/agents/wernher.md` | KEEP-MD | 147 | Os/Wernher T-454 | spawn yes | NUKE: T-413–420, T-448, `lessons` `:92` |
| `.grok/agents/gus.md` | KEEP-MD | 127 | Os vab-helper | spawn yes | |
| `.grok/agents/linus.md` | KEEP-MD | 115 | fence | spawn yes | |
| `.grok/agents/mortimer.md` | KEEP-MD | 97 | RSI 2026-08-25 | spawn yes | |
| `.grok/agents/verena.md` | KEEP-MD | 94 | Os STYLE | spawn yes | forbids lessons `:24` |
| `.grok/agents/pilot.md` | KEEP-MD | 87 | Commander fence | spawn yes | shared fly card |
| `.grok/agents/katherine.md` | KEEP-MD | 85 | dynamics | spawn yes | |
| `.grok/agents/jebediah.md` | KEEP-MD | 23 | identity | spawn yes | points at `pilot.md` |
| `.grok/agents/grok.md` | KEEP-MD | 18 | identity | spawn yes | |
| `.grok/agents/spotter.md` | NUKE-LIVE | 14 | retired | spawn **exists** | `DEPRECATED` `:3`; AGENTS `:206` |
| `.grok/agents/{bill,bob,valentina}.md` | KEEP-MD | 13×3 | identity | spawn yes | |
| `docs/lessons.md` | NUKE-LIVE | 2872 | Lars T-469 (`log/lars.md:3`) | **parent+R&D yes**; packet skim **no** | 156 `##`; newest `:24`; twins `tickets.py:1666` |
| `docs/agent-notes.md` | KEEP-MD | 791 | Wernher T-454 (`:564`) | parent + systems **deep** | API `:13`–`:546`; `## Log` is TAPE |

## Inventory mismatch
`docs_inventory.classify` (`:307`–`:345`) walks **`docs/` only**. `AGENTS.md` and `.grok/agents/*` are **unclassed**. `docs/lessons.md` and `docs/agent-notes.md` fall through to **`live_kernel`** (`:345`) — not `leftover_migrated`. Headings are already **done** twins (`tickets.py:1682` “forensics”) while the file stays live and AGENTS still injects it. Kernel still **requires** the path: `lesson_headings()` (`docs_inventory.py:291`), migrate (`tickets.py:1633`), `tests/test_protocol.py:145` `:197`. **0** shard files are `leftover_migrated`. `_IF_ITEM` would reclassify archive `I-012`/`F-001` **before** `docs/archive/` (`:310` then `:313`) — those are PARKED, not this shard.

## Files read
`AGENTS.md:1–40` `:347–360`; `docs/lessons.md:1–80` `:2858–2872`; `docs/agent-notes.md:1–80` `:546–575` `:752–791`; all 16 `.grok/agents/*.md` headers+tails; `docs_inventory.py:1–120` `:291–345`; `tickets.py:400–448` `:1632–1693`; `PROTOCOL.md:550–565`; `BRIEF.md:70–83`; `OPS.md:360–370`; `tests/test_protocol.py:40–54` `:145` `:197`; crew logs `lars.md:1–40` (newest T-469) + tail 08-21; `wernher.md:1–20`; grep counts above.

===== CLASS 3 =====
## Shard

Archive is **PARKED**. Live md/json here: nine `docs/press/*.md` + `README.md`. README also points `docs/lessons.md` (poison), plus CHARTER/PROTOCOL/slate/science/missions/mods (not tabled). PROTOCOL/CHARTER/AGENTS do not name `docs/archive/`. `.grok/agents/verena.md:65` still names `kerbin-lessons.md`. Four press pieces href parked reviews. No live json in this shard.

## Table

| path | class | lines | last writer | injected? | evidence |
|---|---|---|---|---|---|
| `README.md` | KEEP-MD | 270 | Verena T-435 | yes | `README.md:270` → lessons |
| `docs/press/INDEX.md` | KEEP-MD | 28 | Verena | Verena | `INDEX.md:3` |
| `docs/press/STYLE.md` | KEEP-MD | 220 | Os/Verena 08-25 | yes | `STYLE.md:1`; `verena.md:24` |
| `docs/press/first-space.md` | KEEP-MD | 157 | Verena | Verena | `first-space.md:149` archive hrefs |
| `docs/press/forest-for-the-trees.md` | KEEP-MD | 114 | Verena | Verena | `:107` cutover href |
| `docs/press/first-fifteen-sci.md` | KEEP-MD | 113 | Verena | Verena | `:108` cutover href |
| `docs/press/asteroid-xrl-564.md` | KEEP-MD | 77 | Verena | Verena | no archive href |
| `docs/press/first-five-sci.md` | KEEP-MD | 71 | Verena | Verena | `:68` cutover href |
| `docs/press/first-hop.md` | KEEP-MD | 83 | Verena | Verena | `:79` live mission logs |
| `docs/press/pad-goo.md` | KEEP-MD | 60 | Verena | Verena | `:58` live pad log |
| `docs/lessons.md` | TAPE | 2872 | Lars/Wernher | **YES** | `AGENTS.md:9`; `README.md:270`; `lessons.md:3` names PARKED kerbin |
| `docs/program/RO.md` | ARCHIVE | 58 | Os 08-21 | no | `RO.md:3` Parked; inv `live_kernel` |
| `docs/archive/README.md` | ARCHIVE | 12 | — | no | `docs/archive/README.md:9` PARKED |
| `docs/archive/kerbin-lessons.md` | ARCHIVE | — | — | poison | `docs_inventory.py:31`; `lessons.md:3` |
| `docs/archive/reviews/*` | TAPE | ~108 md | `write_review` | no | `reviews/README.md:1-4` PARKED |
| `docs/archive/2026-08-23-md-cutover/**` | ARCHIVE | I-012–I-020, F-001–F-015, niche, org | — | no | cutover `README.md:3-4` PARKED |
| `docs/archive/letsgrok-2026-08-21/**` | ARCHIVE | I-001–I-011, 53 log md, 29 jsonl | — | no | letsgrok `README.md:4` PARKED |

Drop: cutover 106 jeb log md, feedback notes, org novels, letsgrok program snapshots, mun `tar.gz` (`archive/README.md:3`).

## Inventory mismatch

`classify` hits `_IF_ITEM` **before** `docs/archive/` (`docs_inventory.py:310-314`), so parked `I-012.md`/`F-014.md` are `leftover_migrated`, not `parked_archive`. They are **not still live**. Live `docs/program/improve/` and `docs/crew/niche/` are **MISSING** (`test_tickets.py:1448-1454`). Press + `RO.md` + `lessons.md` all default `live_kernel` (`:345`); press fits KEEP-MD; RO is parked-but-live; lessons is tape that AGENTS injects. Archive jsonl is `parked_archive` (`:313` before tape `:331`). No `NUKE-LIVE` file; poison is **pointers** (README/AGENTS → lessons; press/`verena` agent → archive).

## Files read

PARKED: `docs/archive/README.md`, `2026-08-23-md-cutover/README.md`, `reviews/README.md`, `kerbin-lessons.md` hdr, `letsgrok-2026-08-21/README.md`, cutover `I-012.md` hdr. Live: press INDEX/STYLE + 7 articles hdrs, `README.md`, `RO.md`, `docs_inventory.py`, `lessons.md` hdr+end, `docs/crew/verena.md`, `tests/test_tickets.py:1448`. Crew: `docs/crew/log/verena.md` **21** bullets / **23** lines (whole file); `press/` grep **0**; last writer T-435 `verena.md` log `:3`.

===== CLASS 4 =====
Live tickets dir is six files. Gym I/F leftovers are **not** live (`docs/program/improve` and `docs/program/feedback` MISSING); inventory still labels the parked copies `leftover_migrated` because the I/F regex wins before `docs/archive/`. BOARD is a dump; BRIEF is the only spawn-injected prose. `tests/test_protocol.py` still **requires** `docs/lessons.md`, so NUKE of lessons is blocked.

## Shard
`docs/program/tickets/` (6 live md/json/jsonl) + `docs_inventory.classify` leftovers (`I-012`–`I-020`, `F-001`–`F-015`). Archive trees PARKED.

## Table
path | class | lines | last writer | injected? | evidence
---|---|---|---|---|---
`docs/program/tickets/BRIEF.md` | KEEP-MD | 132 | Os notes in-file (`BRIEF.md:88`) | **yes** | spawn how-to; “Not BOARD.md” (`BRIEF.md:4`); `PROTOCOL.md:345`
`docs/program/tickets/README.md` | KEEP-MD | 44 | same sit as BRIEF | no | dir index → OPS/BRIEF (`README.md:1-8`); not packet `read:`
`docs/program/tickets/BOARD.md` | TAPE | 80 | `tickets.py:719-744` Hank `2026-08-25T22:10:10Z` | no | open dump 74/471 (`BOARD.md:3`); inventory `live_kernel`
`docs/program/tickets/board.jsonl` | TAPE | 2068 | Hank kernel, last `op=open` T-471 (`board.jsonl:2068`) | no | event log; inventory special-cases `live_kernel` (`docs_inventory.py:331`)
`docs/program/tickets/head.json` | TAPE | 17905 | kernel `updated` (`head.json:17904`) | no | **not walked** (`.json`); user TAPE/kernel
`docs/program/tickets/fingerprints.json` | KEEP-MD | 212 | kernel rewrite (`tickets.py:302`) | no | **not walked**; BRIEF lookup (`BRIEF.md:17`); KEEP kernel
PARKED `…/improve/I-012.md`–`I-020.md` (9) | ARCHIVE | ~7–20 ea | 2026-08-23 cutover | no | inventory **leftover_migrated** (`docs_inventory.py:310-311`); live path MISSING
PARKED `…/feedback/F-001.md`–`F-015.md` (15) | ARCHIVE | ~10–20 ea | same | no | same leftover class; F-014 still `status: open` (`F-014.md:8`) vs twin T-184 `verify` (`head.json:6922-6928`)
PARKED `…/tickets/RSI-JUMP.md` | ARCHIVE | — | cutover | no | `_ORG_NOVEL_NAMES`; not leftover regex

## Inventory mismatch
- **No live leftover_migrated.** `docs/program/improve` MISSING; `docs/program/feedback` MISSING; tests assert that (`test_tickets.py:1453`, `test_protocol.py:45,180`).
- Inventory still reports leftover because `_IF_ITEM` runs **before** `docs/archive/` (`docs_inventory.py:310-314`). Tests **require** archive `I-012.md` / `F-014.md` in leftover (`test_tickets.py:1448-1450`).
- `.json` (`fingerprints.json`, `head.json`) are invisible to `iter_docs` (md/jsonl only, `docs_inventory.py:362-363`).
- `board.jsonl` + `BOARD.md` + `BRIEF.md` = inventory `live_kernel`. This shard: BRIEF KEEP-MD; BOARD/jsonl TAPE (do not inject).
- Twins **are** tickets (`head.json:6469+`); gym MD must not be spawn-read. `GLOSSARY.md:23`: speech is T-id (F-014 → T-184).
- **NUKE blocker:** `tests/test_protocol.py:145-147` reads `docs/lessons.md` (`latitude`, `Forest is 270`); `:197-200` requires `## ` and forbids `L-NNN`.

## Files read
`docs/program/tickets/{BRIEF,README,BOARD}.md` headers; `fingerprints.json:1`, `head.json:1`+`:17904`; `board.jsonl:1`+`:2068` (no dump); `docs_inventory.py:1-40,307-345`; `tickets.py:14-17,300-303,719-744`; `tests/test_protocol.py:10-55,145-180,197-200`; `tests/test_tickets.py:1431-1504`; PARKED `I-012.md`, `I-020.md`, `F-001.md`, `F-014.md`, `RSI-JUMP.md` headers; `GLOSSARY.md:23`.