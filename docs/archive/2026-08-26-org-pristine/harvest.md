

===== HARVEST 0 =====
## Jump
Applied 2026-08-25. Design caps: no TYPE zoo; prefix is the id; no sit/warp/suicide retune; pad-RF extract optional; no ignition raise (`.grok/workflows/lars-rsi.rhai:236`–`:239`). Report phase **writes** `docs/program/lars-rsi.md` (`:12`, `:356`). Git after the letter: `ea7f60b` “Apply Lars RSI: S/M/C prefixes, pad-RF one sit.” (`.git/logs/HEAD:82`).

## Claimed (quote the report)
“Prefix is the **id**, not a TYPE. RF pad is **one sit**.” Extract pad-RF; “compose stays.” T-466/T-467 done; “T-465 `inbox`”; next science **S-468**. Pad seven defs; factory `run_factory_vessel` `:273`–`:1051`. Packet third path named helper. Pad tests **6**; house `test_hop.py` **231**. “Git commit **MISSING**.” “T-465 still inbox after the pad-hold patch.” (`docs/program/lars-rsi.md:1`–`:54`)

## Still true (path:line)
- `ID_PREFIX` science/fly/vehicle S/M/C; else T (`tickets.py:59`–`:63`, `_next_id` `:328`). TYPES still 11 (`:19`). Landing accepts T/S/M/C (`:1873`). Tests `S-001`/`M-002` (`tests/test_tickets.py:199`–`:227`). **0** live `S-`/`M-`/`C-` ids in `head.json`.
- BRIEF/PROTOCOL third path = named helper (`docs/program/tickets/BRIEF.md:75`–`:83`; `docs/program/PROTOCOL.md:356`–`:360`).
- Lars card: one pad-RF, no `_pad_*` per stamp; first pytest `-k pad`; third path named helper (`.grok/agents/lars.md:34`–`:49`, `:72`–`:82`).
- `hop_factory_pad.py` exists; 8 defs (`:20`–`:165`); compose `from hop_factory_pad import _pad_hold, _pad_light` (`hop_factory.py:31`). `_pad_light` **not** in factory (`tests/test_hop_factory.py:88`–`:89`). Pad tests now **8** (`:85`–`:224`), not 6.
- `hop_factory.py` still **1052** lines; `run_factory_vessel` `:274`–`:1051`. `_hold_or_cut` `:548`; `_pad_hold` `:601`. `test_hop.py` still **231** `def test_`.
- T-466/T-467 `done` (`head.json:17759`, `:17793`). Stem `rf-ignition-ullage` now **10** (`fingerprints.json:153`), not 7.
- **Yes: jump added a live novel** `docs/program/lars-rsi.md` next to `learn-rsi.md`.

## Leftover (still poisoning hires)
- **T-465 inbox is stale** — `status: done` (`head.json:17716`). Live: **T-471 inbox** control (`:17897`); **T-470** RSI ×8 inbox (`:17875`); **T-468** sci-unchanged ×19 inbox (`:17817`).
- After-miss still `docs/lessons.md` (`.grok/agents/lars.md:165`).
- Git risk **stale**: `ea7f60b` landed; the letter could not see it.
- Card still “one helper, stop” (`lars.md:16`) vs 1052-line immortal inland compose.
- Crew `rf-ignition-ullage|_pad_|hop_factory_pad`: **11** (lars **6** `:3`–`:8`; mortimer harvest **2** `:3`–`:4`). Pad still flies.

## What the jump did NOT touch that Os named today
Per-rocket pulse from a Wernher catalog (Design: compose stays). `lessons.md` still injected. Spotter card still on disk (`.grok/agents/spotter.md:1`–`:11`). Uncrewed tape still `docs/missions/jebediah/logs/` (`tickets.py:424`). Doc clusterfuck: jump **added** `lars-rsi.md` instead of putting the harvest only on T-466. Inland factory still one `run_factory_vessel`. No live S/M/C opens.

## Files read
`docs/program/lars-rsi.md`; `.grok/workflows/lars-rsi.rhai`; `hop_factory.py`; `hop_factory_pad.py`; `tickets.py`; `.grok/agents/lars.md`; `docs/program/tickets/BRIEF.md`; `head.json` T-465–T-471; `fingerprints.json`; `world-model.md:711`; `PROTOCOL.md:350`; `OPS.md:26`; `tests/test_tickets.py:199`; `tests/test_hop_factory.py:84`; `docs/crew/log/{lars,mortimer}.md`; `.git/logs/HEAD`; `.grok/agents/spotter.md`; `docs/program/learn-rsi.md`.

===== HARVEST 1 =====
## Jump
learn-rsi (applied). Kernel uncrewed Learn = hop-exit `attach_run` overwrite. rsi-jump had already skipped Gene; this jump filled the empty `payload.learn` writer. Design cap (`.grok/workflows/learn-rsi.rhai:505`): **Lars `lessons.md` heading MUST name the reusable fingerprint.** Report kept that file as markdown forensics and did not ticket it (`docs/program/learn-rsi.md:132`, `:154-159`). That is how lessons got worse.

## Claimed (quote the report)
“hop-exit `attach_run` overwrites `payload.learn` (`who=hank`) … Gene unhired. `needs_learn` stays false for uncrewed.” (`learn-rsi.md:67-73`)  
“Refuse empty on `control` / `systems` / `ops --tag feedback` … error prints `reuse (count):`” (`:78-80`)  
“CHARTER sit is `payload.learn` + packet skim. Lars `lessons.md` heading **names** the reusable fingerprint … that is not RSI.” (`:157-160`)  
“`docs/lessons.md` were not ticketed.” (`:132`)

## Still true (path:line)
- Uncrewed Learn runs: `attach_run` stamps `payload.learn` (`tickets.py:1359-1392`); hop-exit calls it (`main.py:101-106`). Packet prints `learn:` (`tickets.py:527-529`).
- `needs_learn` false for uncrewed (`tickets.py:937-943`). Gene Learn is campaign-stop only (`ops.py:313-321`; `.grok/agents/gene.md:104-108`). Review drops Stamp nag when `campaign=uncrewed` (`review.py:269-270`).
- Fingerprint reuse: alias prefix (`tickets.py:192-212`); empty/novel refused (`:182-189`, `:773-774`). Live counts: `sci-unchanged-recovered` 21, `flyinghigh-lid` 16 (`fingerprints.json:160`, `:40`).
- Feedback CLI is `tickets feedback --claim` (`PROTOCOL.md:542-551`; `tickets.py:661-699`).
- Gene log: **Not Learn ×2** (`docs/crew/log/gene.md:3-4`); **Batch Learn ×10** (old, `:12-39`). Newest still a go novel.

## Leftover (still poisoning hires)
**Yes — learn-rsi made `lessons.md` worse.** It dual-bused sit (`payload.learn`) and forensics (`lessons.md`) and **required** fingerprint-named appends. File is **156 `##`**. Same stem, new heading: `rf-ignition-ullage` ×6 (`docs/lessons.md:24-115`); `flyinghigh-lid` ×10 (`:326-751`). Packet skim does **not** list `lessons.md` (`tickets.py:396-430`) — parent still injects it (`AGENTS.md:9`, `:19`, `:326-345`). Cards still command the append (`.grok/agents/lars.md:165-166`; `wernher.md:92-93`; `BRIEF.md:83`). `migrate_second_bus` still twins those headings into `type=control` with `fingerprint=""` (`tickets.py:1666-1678`).
Also still true from §10: hop-exit `who="wernher"` (`main.py:106`); `from_need` fps `stack`/`builder` (`tickets.py:579`); `ops.py:317` still says “batch Learn”; abort-novel key still `fingerprints.json:2`; `payload-learn-attach` is **1** (report said 2).

## What the jump did NOT touch that Os named today
Clusterfuck / where-to-write (kept crew logs, Practice, portraits, lessons — `learn-rsi.md:154-158`). Rip stale. Ticket bus as **only** comms (MD still required on miss). **Do not inject `lessons.md` every hire.** Uncrewed tape still `docs/missions/jebediah/logs/` (228 jsonl; `hank.md:122`; `tickets.py:406`, `:424`). Spotter card still on disk (`.grok/agents/spotter.md:1-11`). Lars compose from a Wernher catalog: rhai forbade `hop_factory.py` retune (`learn-rsi.rhai:379`); `hop_factory.py` still owns sit helpers (`:46-274`); card still says “or the living compose” (`lars.md:19-33`). `hop_factory_pad.py` was not even in the walls.

## Files read
`docs/program/learn-rsi.md`; `.grok/workflows/learn-rsi.rhai`; `tickets.py`; `ops.py`; `main.py`; `review.py`; `.grok/agents/{gene,lars,hank,wernher,spotter}.md`; `AGENTS.md`; `docs/program/{PROTOCOL,OPS,tickets/BRIEF,tickets/fingerprints,feedback-plan}.md`; `docs/lessons.md` headings; `docs/crew/log/gene.md` (counts + newest); `docs/missions/jebediah/`; `hop_factory.py` defs; `docs_inventory.py`.

===== HARVEST 2 =====
Live jump reports are gone. Kernel still prefers the fly ticket, then falls back to plan/science markdown. KEEP dumps are still in the hire path.

## Jump
`docs/program/ticket-bus-cutover.md` **MISSING**. `docs/program/rsi-jump.md` **MISSING**. PARKED: `docs/archive/2026-08-23-md-cutover/program/{ticket-bus-cutover,rsi-jump,tickets/RSI-JUMP}.md`. SPEED/NEXT-ORG: **no live copies** under `docs/program/`. PARKED org novels (`archive/…/README.md:12`). Classifier only: `docs_inventory.py:47-56`.

## Claimed (quote the report)
Cutover: ``protocol fly` prefers the seated fly ticket and **falls back** to `plan.md` + `science.md`` (`ticket-bus-cutover.md:7-8`). MOVE leftover `need_*` onto types; KEEP-MD: `lessons.md`, dual `plan.md` render, `science.md` dump, packet “kernel may add BOARD.md” (`:247-285`, `:514-522`). Dual compile by design (`:542-548`). RSI-jump: “skim no BOARD”; `needing_go` hires wernher; `fly_gate` fallback stays; Gene-only `go:`; Learn on ticket (`rsi-jump.md:13-19`). “Linus bind … is ticket payload” (`RSI-JUMP.md:41`).

## Still true (path:line)
- Ticket-then-plan: `protocol.py:130-135`; science-card fallback `protocol.py:107-118,262-268`.
- `ops.fly_gate` tickets-only: `ops.py:414-419`. `needing_go` batches Wernher: `ops.py:313-350`.
- Packet skim = desk+BRIEF, **no BOARD**: `tickets.py:396-397`; AGENTS `AGENTS.md:162-163`. Science type still skims the dump: `tickets.py:413-414`.
- Gene not merge: `AGENTS.md:171,198`; `PROTOCOL.md:409`.
- `NEED_MAP` shim still live: `tickets.py:121-129`. `need_builder` in agents: `.grok/agents/gus.md:63`, `hank.md:178`.
- Seated `need_*` kv **scrubbed** (plan/science dumps no longer carry `need_builder:`).

## Leftover (still poisoning hires)
- Dual gates: `protocol fly` vs `ops fly` (`protocol.py:244-271`, `ops.py:457-462`). Gene `SCHEMAS` still `recommended` (`protocol.py:13`).
- Dual boards: generated `tickets/BOARD.md:3` (open 74/471) **and** Linus dump `docs/program/science.md:1-28` on science packets.
- Dual plans: `docs/program/plan.md:8-16` vs `docs/missions/jebediah/plan.md:8-19` both hold `go`/`cli`/`campaign`.
- KEEP now poison: `science.md` dump (`tickets.py:414`); `plan.md` as fly fallback (`protocol.py:132-135`); `lessons.md` forensics twinned onto the bus (`tickets.py:1633,1686`) and injected in AGENTS (`AGENTS.md:9,19,326`) + Lars (`lars.md:165`).
- `desk.md:14` still `card:`. World-model still answers `need_stack` (`world-model.md:772,791`).
- Gene log: **0** `tickets stamp`; last-write is still `go: yes` novels (`docs/crew/log/gene.md:3-10`).
- Spotter card live: `.grok/agents/spotter.md:1-11`.
- Uncrewed tape path unchanged: `tickets.py:424,458`.
- `hop_factory.py` has **0** `compose`; imports `hop as H` + pad helpers (`hop_factory.py:29-31`). Card still says “one living rocket” (`lars.md:19-20`).

## What the jump did NOT touch that Os named today
Where-to-write (reports themselves parked; live novels `feedback-plan.md` / `learn-rsi.md` / `lars-rsi.md` / `world-model.md`). Rip stale KEEP dumps. Ticket-bus-as-comms vs MD-only-if-needed. `lessons.md` scale / every-hire inject. Uncrewed jsonl under `docs/missions/jebediah/`. Spotter card. Lars composing one rocket from a Wernher catalog.

## Files read
Live: `protocol.py`, `ops.py`, `tickets.py:115-448`, `AGENTS.md`, `PROTOCOL.md:320-409`, `docs_inventory.py`, `desk.md`, `plan.md`×2, `science.md`, `BOARD.md`, `BRIEF.md`, `lessons.md:1-14`, `lars-rsi.md:1-7`, `.grok/agents/{hank,gus,lars,spotter}.md`, `hop_factory.py:1-43`, `docs/crew/log/gene.md` (counts + last 40 = lines 1-40). PARKED: archive cutover first 40 + KEEP/risks, `rsi-jump.md:1-45`, `RSI-JUMP.md:1-58`, archive README. MISSING: live `docs/program/{ticket-bus-cutover,rsi-jump,SPEED,NEXT-ORG}.md`.

===== HARVEST 3 =====
## Jump

`feedback-plan` (`.grok/workflows/feedback-plan.rhai:2–11`): compile only, **no code**. Report `docs/program/feedback-plan.md`. §10 “Later patches (**do not apply**)”. Kernel apply is a later 08-24 hire, not this jump.

## Claimed (quote the report)

`feedback-plan.md:3`: drop `--good --self --them`; findings on the work T-id; harvest **writes**; “No apply. No new TYPE.”
`feedback-plan.md:35`: store `payload.findings[]` `{who,claim,evidence,owner,real,at}`; CLI `--claim`; mandatory ≥1; close harvests `close_why`; `attach-run` one `learn`; packet copy-line; inbox any-owner.
`feedback-plan.md:43`: later `tickets.py` + cards + CHARTER door sentence only.

## Still true (path:line)

Door **is** on disk (post-plan 08-24, not the jump): `tickets.py:1749–1754` `--claim` required; no trio CLI. `add_feedback` `:661–699`. Close harvest `:702–712`. `attach-run` harvest `:1394–1395`. Packet copy-line `:546`. Inbox any-owner `:1405–1423`. `TYPES` still 11 (`tickets.py:19–31`). `protocol.py:12–22` SCHEMAS: **no** finding key.
CHARTER quotes `--claim` (`CHARTER.md:19`, `:183`), not the trio. PROTOCOL Feedback (`PROTOCOL.md:534–554`) same CLI; still forbids Return `good:`/`self:`/`them:` (`:81`, `:558`).
`BOARD.md:3`: **74 / 471**. `"findings":` **100** tickets. `"payload": {}` **≥199**. `"real":` **≥199** rows; `"real": true` **5**. `"good":` **4** (legacy `payload.feedback` only: T-375 `:13640` + two more). `"at": "2026-08-25` **169**; `"2026-08-26` **0**.
`who=` findings: hank **87**, linus **32**, wernher **29**, mortimer **25**, gus **20**, lars **12**, verena **4**, **gene 0**, jeb/pilot **0**. Crew `--claim` strings: mortimer 1, wernher 1, **lars/gene/gus/linus 0**. Flying desks **did** write kernel `--claim` 08-25 (`who=linus|lars|gus`); Gene/Commander did not. T-081 has one Hank harvest landing (`head.json:3344–3352`), not the §8 Gene `go=yes` vs rec=no line. Live T-471 `payload: {}` (`:17890`).

## Leftover (still poisoning hires)

`learn-rsi.md:92` still quotes `--good --self --them`. Four live trio rows (T-375 `:13640`). Harvest novels (hank 87) vs cheap findings. T-471 empty. `lars.md:165` still “Append … `docs/lessons.md`”. AGENTS injects lessons (`AGENTS.md:9`, `:326`). PROTOCOL keeps run headings (`PROTOCOL.md:564`). Tape path still `docs/missions/jebediah/logs/` (`tickets.py:424`). `.grok/agents/spotter.md:1–11` still on disk (DEPRECATED). `hop_factory.py:1–21` sit-ifs, **0** `catalog|compose`.

## What the jump did NOT touch that Os named today

MD clusterfuck / where to write; rip stale RSI reports (`learn-rsi.md` trio); `lessons.md` scale + hire inject; uncrewed tape in `docs/missions/jebediah/` (442 files); spotter card; Lars one living rocket from a Wernher catalog. Ticket bus **is** the comms for findings — not for those.

## Files read

`docs/program/feedback-plan.md`, `.grok/workflows/feedback-plan.rhai`, `CHARTER.md`, `PROTOCOL.md`, `tickets.py`, `protocol.py`, `tests/test_tickets.py`, `docs/program/tickets/head.json` (sample), `BOARD.md`, `learn-rsi.md`, `lars-rsi.md`, `.grok/agents/{spotter,lars,gene}.md`, `hop_factory.py`, `docs/crew/log/{mortimer,wernher,lars,gene,gus,linus}.md` (grep), `docs/missions/jebediah/` (list).