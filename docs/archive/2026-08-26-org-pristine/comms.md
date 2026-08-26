

===== COMMS 0 =====
Hank is the in-between: parent TUI, not a child. `ops next` hires; leftover/tape stay on this process. Vessel is `ship.md` + ticket envelope, not BOARD/lessons/last-flight 40.

## Desk
Hank Grokman, COO. Parent *is* Hank (`OPS.md:44–47`, `AGENTS.md:53–56`). Owns ticket bus, who is hired, leftover/KSC, attach-run+landing, this-hop clock/`ship.md`. Never `go:`, Hangar, stick, Commander debrief (`.grok/agents/hank.md:41–44`). Isolated `subagent_type: hank` is ops writes only.

## Who they respond to (PROTOCOL vs actual log)
PROTOCOL: Os→Hank loop (`PROTOCOL.md:20`); Hank→desks via `ops next` (`:23`); desks return ticket patches. Os-by-name = voice, no spawn (`:22`).
Log: `docs/crew/log/hank.md` **15 lines total**; **6** dated 2026-08-25 (all Os/Mortie radio); **0** on 08-26. Gene log **0** hits `2026-08-25` (uncrewed; Gene not hired). Contrast 08-22: Gene still wrote “KSC Hank”.

## How Hank sits in between (ops next / packet / leftover / tape)
`ops.py:next_actions` (`:147`): leftover lock-free → Hank `leftover_cli` (`:198–217`); lock live → ground gus/linus/wernher/lars/verena/katherine, no Commander/Gene (`:219–229`); S1 recover → Hank (`:231`); `fly_ready` go=yes !waste → uncrewed parent starts `cli` else Jeb (`:243–281`) + Mortimer org + parallel ground; waste living +0 → Linus (`:283–311`); `needing_go` → Gene + batch Gus/Linus/Lars/Wernher (`:313–359`); else ground / pad-idle Hank (`:361–379`).
Tape after CLI: desk, `recover-probe --recover`, `attach-run`, `landing`, `ops next` (`hank.md:119–124`). Packet skim, never auto `--deep` (`tickets.py:550–557`). Lock-live: read `ship.md`, no jsonl (`hank.md:103–114`). Nag skipped findings = prose (`:150,180`); kernel harvests `close_why` / attach-run learn finding (`tickets.py:1394–1395`).

## Writes since 2026-08-25 (md vs tickets stamp vs tickets feedback)
md: 6 log bullets 08-25 (press/tape/clock/RA/Gus/git); portrait `docs/crew/hank.md` 23 lines, no 08-26. Job card last-writes are Os 08-25 tape/clock (`hank.md:15–33`).
stamp: `attach_run` overwrites `payload.learn` `who=hank` (`tickets.py:1359–1392`). Gene stamps `go`, not Hank.
feedback: 08-25 ~06:40Z `who=hank` findings patches (harvest dupes on T-386/391/392/394…) then Mortimer Practice closes (`board.jsonl` ~1610). 08-26 Hank md: empty.

## Card format (Return fence vs leftover keys vs first command)
First command: `desk` then `ops next` (`hank.md:46–51`). Return: `ops:` `hire:` `packet:` `pad:` `why:` `rsi:` (`:185–191`) then `tickets feedback --claim`. Leftover `need_*` = `from-need` shim, not Return (`:178–181`).

## Too long? (job-card lines, hire re-reads, pytest house)
Job card **194** lines; OPS/PROTOCOL grep-cap **≥199** each (files continue). Parent AGENTS still injects CHARTER + last-flight + lessons (`AGENTS.md:3–9`). Children `agents_md: false`; packet = desk+BRIEF+ticket, **no BOARD.md** (`AGENTS.md:162`). Token tax is this TUI (Hank) vs skim children; `resume_from` dumps transcript (`PROTOCOL.md:365–372`). BRIEF still house `test_hop.py` (`BRIEF.md:74`); OPS wants `test_hop_factory.py` not house 231 (`OPS.md:150`).

## In the loop? (S/M/C prefixes, named helper, findings, pad occupancy)
S/M/C on card (`hank.md:68–69`, `BRIEF.md:6–8`). Lars packet third path = named helper (`hank.md:64–65`). Findings cap 8 + copy-line on skim (`tickets.py:530–546`); nag is not a hire. Pad: leftover first, then fly_ready; idle sin / living +0 waste (`hank.md:80–86`). **Does not** read BOARD as vessel (packet forbids; human dump only `OPS.md:90`). last-flight 40 = abort/exit not vessel (`hank.md:24–29`) — AGENTS parent still “read last-flight before flying” (`AGENTS.md:4`) leftover tax. `lessons.md` not on Hank card; parent still injects it (`AGENTS.md:9`). Spotter row still “Do not spawn” (`AGENTS.md:106`).

## Files read
`.grok/agents/hank.md`; `docs/crew/hank.md`; `docs/crew/log/hank.md` (counts + last 40 = whole file); `docs/crew/log/gene.md` (08-25 = none); `ops.py:147–441`; `AGENTS.md` Supervisor + When to spawn; `docs/program/OPS.md`; `docs/program/PROTOCOL.md`; `docs/program/tickets/BRIEF.md`; `tickets.py:477–557,1359–1402`. `docs/archive/` not opened.

===== COMMS 1 =====
Gene still stamps `go:` on live **T-081** (`go: yes`, `campaign: uncrewed`). He has not last-written the bus since **2026-08-23T17:10Z**. Uncrewed Learn is Hank `attach-run`. Dual `plan.md` is live. **M-** is card-only; no `M-` id exists.

## Desk
**Gene Grokman, Launch / Flight Director.** Card: stamp `go:` on a fly ticket; never Control / `.py` / routing / spawn (`.grok/agents/gene.md:12–20`). Voice: `docs/crew/gene.md:3–7`. Chairs **flight** layers (`docs/program/world-model.md:3–9`). T-081 `desk: gene` `go: yes` `cli: hop` (`head.json:3221`, `:3339–3343`, `:3618`).

## Who they respond to (PROTOCOL vs actual log)
**PROTOCOL:** Os→Hank `ops next`; Gene→fly ticket only (`PROTOCOL.md:10–24`, `:445–467`). Ground: Linus bind, Gus `capable:` (`OPS.md:22`, `:170`). Not Commander radio; not stick (`PROTOCOL.md:44–46`, `:240–243`). Uncrewed: first `go:` then skip Gene (`:246–257`).
**Log:** 106 dated lines; **08-25=0, 08-26=0**; last entry **08-24** T-081 Ad astra, Not Learn (`docs/crew/log/gene.md:3`). Last 40 ≈ `:69–:108` (08-20, one 08-21). Talks Linus binds / Gus capable (`:3`, `:7–:10`). Jeb **1×** crash-UI wait, not radio (`:45`). `need_*` **24×**, last 08-21 (`:24`). `who=gene` board **86**; last **2026-08-23T17:10:37Z** (`board.jsonl:849–852`). **0** gene patches 08-24–26.

## How Hank sits in between (ops next / packet / leftover / tape)
Leftover first → Hank, not Gene (`ops.py:198–217`). Lock-live hires gus/linus/wernher/lars/verena/katherine — **not gene** (`:219–229`) vs AGENTS off-nominal Gene. `go==yes` uncrewed → `fly_ready` → **hank** parent hop (`:243–255`). Gene only `needing_go` (`go != yes`) or `needs_learn` (`:313–321`). `needs_learn` false if learn set **or** `campaign==uncrewed` (`tickets.py:937–943`). Packet: desk + `packet T-NNN` + BRIEF (`gene.md:35–37`). Tape: Hank `attach-run` / `landing` (`BRIEF.md:10–15`, `:63–64`).

## Writes since 2026-08-25 (md vs tickets stamp vs tickets feedback)
**Gene md:** 0 (log/briefing/world-model Meaning). Briefing still 08-24 Forest leftover (`briefing.md:1–11`; no 08-25 string). World-model 08-25 bullets are Practice/Os, not Gene Learn (`world-model.md:349–721`); “Gene last-wrote” is Kerbalism Patterns (`:276`).
**Stamp:** 0 gene. T-081 `updated` **2026-08-25T22:10:10Z** via Hank tape (`head.json:3619`; learn `:3567`).
**Feedback:** T-081 `findings[0]` `who=hank` 08-24 (`:3344–3351`). Gene findings **0**.

## Card format (Return fence vs leftover keys vs first command)
Fence `fly/go/cli/campaign/learn/f013` (`gene.md:146–162`; `PROTOCOL.md:445–461`). Forbid `need_*` (`PROTOCOL.md:430–443`). Log still used `need_stack|builder|science` (`gene.md` log `:24–:105`). First command **`tickets packet M-NNN` / `stamp M-NNN`** (`gene.md:29–37`) **and** “live T-081 stay”. **0** `"id": "M-"` in `head.json`.

## Too long?
Job card **170** lines (RA/git/tape/shelf lore `:43–100`). Voice **65**. PROTOCOL uncrewed block `:246–318`. Hire still re-reads PROTOCOL + world-model (~700) + BRIEF. Gene does not own pytest; house `test_hop.py` **231** is Lars (`BRIEF.md:74–83`, `OPS.md:150`).

## In the loop?
**Idle by design while T-081 `go: yes` uncrewed** — `ops next` will not hire him. Still the fly desk on BOARD (`BOARD.md:8`). Dual plan: `docs/program/plan.md:1–16` seated header, `expect_apo_max: 140000`, no `cli`/`science_ids`; `docs/missions/jebediah/plan.md:1–18` “Gene’s plan”, `400000`, `cli` + `science_ids` = ticket barometer/geiger/goo (`head.json:3569–3573`) **≠** briefing thermo+TELEMETRY (`briefing.md:9–10`). Ticket `craft` proc-long (`:3218`) vs `waste.craft` t7-wheel (`:3596`) vs slate t7-wheel (`slate.md:15–16`). Named helper: N/A (no `.py`). Pad: last envelope `sit=pre_launch` synth rec=yes sci_run=0 (`head.json:3557–3567`).

## Files read
`.grok/agents/gene.md`; `docs/crew/gene.md`; `docs/crew/log/gene.md` (counts + last 40); `docs/program/{plan,briefing,world-model,PROTOCOL,OPS,slate,current,desk}.md`; `docs/missions/jebediah/plan.md`; `docs/program/tickets/{BRIEF,BOARD.md,head.json,board.jsonl}`; `ops.py`; `tickets.py:927–943`. `docs/archive/`: not opened.

===== COMMS 2 =====
Lars still patches one immortal inland pulse after each RF miss, appends `lessons.md`, and never `ops --tag ask`s Wernher. Pad extract happened after four hires; compose did not. T-471 is still inbox.

## Desk
Lars Grokman, Vehicle Systems Engineer. Owns this-sit pulse composed from Wernher blocks — not leftover, Hangar, `.craft`, or warp law (`.grok/agents/lars.md:14–27`). Voice is forensic novelist (`docs/crew/lars.md:5`). T-376 forbids an immortal factory that remembers Flea/Hammer/4t/splash-090 (`world-model.md:504–507`).

## Who they respond to (PROTOCOL vs actual log)
PROTOCOL: Hank hires on a control **pulse** miss; Lars returns `lesson:` close (`PROTOCOL.md:32`). New sit/warp/timeout → `ops --tag ask --desk wernher --fingerprint control-blocks` (`.grok/agents/lars.md:39`, `world-model.md:510`). Voice: may ask Gene/Gus/Linus; not Wernher’s traps (`docs/crew/lars.md:23`).
Log since 08-25: **0** `ops --tag ask`. Wernher hits **3** total (T-357, T-335, T-082) — last compose talk is 08-24 T-335 calling Wernher sits (`docs/crew/log/lars.md:25`). Every RF close says not Wernher (`docs/lessons.md:40`). He talks to Wernher by **growing `hop_factory` then importing pad**, not by ask tickets.

## How Hank sits in between (ops next / packet / leftover / tape)
Miss → leftover/KSC first → open `type=control --fingerprint` → `ops next` hires Lars on the **named helper** (`PROTOCOL.md:270–274`). Packet = `desk.md` + `tickets packet` + BRIEF; third path is that helper, not `hop.py` (`PROTOCOL.md:356–360`, `BRIEF.md:75–78`). Pad waits the live `.py`. After CLI: Hank `attach-run` / `landing`; uncrewed re-flies if hang still capable. RSI ×3 on the same stem goes Mortimer (`T-463`/`T-466`/`T-470`), not Lars↔Wernher.

## Writes since 2026-08-25 (md vs tickets stamp vs tickets feedback)
Log: **12** bullets 08-25, **0** 08-26 (`docs/crew/log/lars.md:3–14`; file **89** bullets). `lessons.md`: **6** `rf-ignition-ullage` headings (`:24` `:43` `:65` `:83` `:99` `:115`) — append-after-miss still law (`.grok/agents/lars.md:165`). Control **done**: T-457, T-459, T-462, T-464, T-465, T-469. Open: **T-471** (`BOARD.md:7`). Findings: T-459/T-465/T-469 `who=lars`; T-457/T-462/T-464 `who=hank` (`head.json:17337` `:17596` `:17665`). No stamp `go:`. Four hires **then** extract: T-457/459/462/464 patched `hop_factory.py`; T-466 harvest made pad one sit (`world-model.md:711–717`). Then T-465/T-469 patched `hop_factory_pad.py`.

## Card format (Return fence vs leftover keys vs first command)
Fence only: `tickets:` `stack:` `lesson:` `f013:` `blocks:` (`.grok/agents/lars.md:176–182`). No `need_*` / `good:` / `ask:` in Return. After work: `tickets feedback --claim`. First command: inbox, packet, `pytest tests/test_hop_factory.py -k pad` (`:69–75`).

## Too long? (job-card lines, hire re-reads, pytest house)
Job card **193** lines vs voice **56**. Packet does **not** inject `lessons.md`; the miss path still **writes** it (`PROTOCOL.md:564`; file **156** `##` headings). First pytest is `-k pad`; house `test_hop.py` **231** is forbidden as first (`BRIEF.md:82`, `lars-rsi.md:10`). Hire clocks T-457 9.7 / T-459 8.8 / T-462 6.9 / T-464 ~13: **MISSING** on disk (`lars-rsi.md:10`). Reasoning conflict: PROTOCOL Lars **low** (`PROTOCOL.md:349`) vs OPS/card **medium** (`OPS.md:384–385`, `.grok/agents/lars.md:15`).

## In the loop? (S/M/C prefixes, named helper, findings, pad occupancy)
Yes — miss-first, control stays **T-**. Stem `rf-ignition-ullage` **10** (`fingerprints.json:153`). Open S1: T-471. Named helper **after** extract is `hop_factory_pad.py` (**203** lines, **8** defs); inland compose is still `run_factory_vessel` `hop_factory.py:274–1051` (**1051** lines, **11** defs) importing two pad fns (`:31`). **No** t7-only rocket file. Wernher catalog in use = `physics_warp` import (`hop_factory.py:33–41`), not a per-rocket compose. Pad occupancy: T-471 blocks the next light.

## Files read
`.grok/agents/lars.md`, `docs/crew/lars.md`, `docs/crew/log/lars.md` (counts + newest 40), `docs/lessons.md:1–130`, `hop_factory.py` / `hop_factory_pad.py`, `BOARD.md`, `fingerprints.json:153`, `head.json` T-457…T-471, `PROTOCOL.md`, `OPS.md`, `BRIEF.md`, `world-model.md:495–720`, `lars-rsi.md`, `.grok/agents/wernher.md:1–50`. `docs/archive/`: not opened.

===== COMMS 3 =====
Sit/warp **catalog is `physics_warp.py`**, not `blocks.md`. Lars **imports** it into inland factory (one `apply_sit_warp` call); pad-RF does **not**. Standing open `type=systems` is two F-014/F-015 twins in `verify`, not that catalog. T-467 prefix kernel is **done**; no S-/M-/C- ids exist yet.

## Desk
Wernher CSE: kRPC/desk/hangar/telem/ops kernel **and** sit/warp/timeout/leftover/chute **blocks** (`.grok/agents/wernher.md:13–39`). Pulse is Lars. XOR same `.py`. Standing on open `type=systems` (`docs/program/OPS.md:294`). `physics_warp.py:1–5` — Wernher owner; Lars composes `hop_factory`. T-334 `done` (`head.json:12335–12352`).

## Who they respond to (PROTOCOL vs actual log)
PROTOCOL: Hank → Wernher on systems/blocks; return systems close (`PROTOCOL.md:33`). Os-by-name is voice only (`:22`). Log: Hank/Mortimer/Gus/Linus open; Wernher **self-opened** T-467 (`board.jsonl` 21:10:44Z, reporter Wernher) and closed 12s later. T-468 `type=rsi` desk=wernher, reporter Hank (`head.json:17799–17820`). 08-26 log **0**.

## How Hank sits in between (ops next / packet / leftover / tape)
`ops next` batches systems / `desk=wernher` even lock-live (`OPS.md:266`, `:294`). Packet = `desk.md` + `tickets packet` + BRIEF, no BOARD (`PROTOCOL.md:340–345`). Leftover **kernel** Wernher, **CLI** Hank (`wernher.md:95–96`). Tape: Hank `attach-run`/`landing`; Wernher owns jsonl helpers/reader (`wernher.md:99–107`). Parent does not patch `.py` same turn.

## Writes since 2026-08-25 (md vs tickets stamp vs tickets feedback)
Log `2026-08-25` **10**; `2026-08-26` **0**. No Gene-style `stamp`. Work is `tickets feedback --claim` then `close_why`+`done` (T-399/396/388/413–421/426/427/449/467). MD: one log line per batch; `lars-rsi.md` harvest names kernel T-467 (`:48`).

## Card format (Return fence vs leftover keys vs first command)
First command: `tickets inbox --desk wernher` then `packet T-NNN` (`wernher.md:61–66`). Fence: `tickets:` `ready_to_fly:` `files:` `blocker:` (`:135–140`). No `need_*` / `good:` / `feedback:` in Return; leftover `need_qol` → `from-need` never in fence (`:75`, `:142`). Findings = `tickets feedback --claim` (`:146`).

## Too long? (job-card lines, hire re-reads, pytest house)
Job card **147** lines; stamp lore (T-421/442/337/09-01Z) still on the card. Hire re-reads PROTOCOL packet + BRIEF + desk. BRIEF still `test_physics_warp.py` **+** `test_hop.py` (`BRIEF.md:74`); house `test_hop.py` **231** (`lars-rsi.md:38`).

## In the loop? (S/M/C prefixes, named helper, findings, pad occupancy)
**Prefix:** T-467 `_next_id` S/M/C else T-, global N, TYPES unchanged (`tickets.py:59–63`, `:328–334`). Live T-081/T-404/T-387 stay. Next rsi is T-468 not S-468 (`lars-rsi.md:25` stale). **No minted S-/M-/C-.** **Catalog vs tickets:** open systems = T-184/T-185 `verify` only (`BOARD.md:9`, `:44`). `control-blocks` fp **7**; no open catalog ticket. **Import not copy:** `hop_factory.py:33–41` import, `:671` call. `hop.py:52–64` import + thin wrap `:1532–1560`. `hop_factory_pad.py` **no** `physics_warp` import. `blocks.md:3` is Gene CLI (`pad`/`hop`/`splash`), **not** the sit catalog. Pad occupancy: idle-pad sin on Hank card; T-468 inbox unworked 08-26.

## Files read
`.grok/agents/wernher.md`, `lars.md:1–80`, `hank.md:1–97`; `docs/crew/log/wernher.md` (grep 08-25=10, 08-26=0; last 40 = lines 1–40); `docs/program/{krpc,blocks,PROTOCOL,OPS,BRIEF,lars-rsi,world-model}.md`; `physics_warp.py:1–30`; `hop_factory.py:1–80,:650–680`; `hop_factory_pad.py:1–50`; `hop.py:52–64,:1520–1560`; `tickets.py:50–77,:320–334`; `BOARD.md:1–80`; `head.json` T-184/185/334/467/468.

===== COMMS 4 =====
Gus and Linus are ground shelf desks: Hank hires them on ticket ids; they do not talk to the Commander. Since 08-25 they restamp/rebind on live **T-** vehicle/science tickets, while `vab.md` / dual `science.md` stay dumps. **08-26 logs: 0.** No **C-** / **S-** on disk.

## Desk
Gus = VAB + `capable:` on vehicle tickets; no Hangar / `.py` (`.grok/agents/gus.md:6-8`). Linus = science tickets + **bind after** Gus `capable:` (`PROTOCOL.md:31,134`; `linus.md:16,73`). `science.md` is dump, not bind (`linus.md:16`; `PROTOCOL.md:478,506`).

## Who they respond to (PROTOCOL vs actual log)
PROTOCOL: Hank → ids; `Linus ↛ Commander`; `Gus ↛ Hangar`; Return no other desk (`PROTOCOL.md:30-31,46,119`). Voice still “may ask Gene / Linus / Lars” (`docs/crew/gus.md:20`; `linus.md:21`). **08-25:** Gus log Commander/Jeb/Gene hits **0**; Linus 08-25 **0** Gus/Jeb; Gene-hangar only **08-21** (`linus.md:47-55`). They meet on desk/tickets. Gus → Wernher via `vab-helper` T-413–T-420 (`gus.md` log:7).

## How Hank sits in between (ops next / packet / leftover / tape)
`ops next`: unsigned vehicle → Gus batch; unbound science → Linus; bind blocked until `capable` (`OPS.md:263-269`). Packet = `desk.md` + inbox + `packet` + BRIEF (`PROTOCOL.md:340-345`). Leftover/KSC before pad (`OPS.md:233-238`). Tape = Hank `attach-run` / `landing`, not them (`OPS.md:287`; `PROTOCOL.md:9-10`). I-014 re-desk after `capable: yes` (`PROTOCOL.md:309`). Leftover `need_*` → Hank `from-need` (`PROTOCOL.md:105-107`). 08-25 capable restamps often `who=hank` (`head.json` T-400:14719).

## Writes since 2026-08-25 (md vs tickets stamp vs tickets feedback)
Logs: Gus **6** / Linus **8** on 08-25; **0** on 08-26 (Gus 53 bullets; Linus 77). MD: `vab.md` capable dump (T- ids, not C-); `science.md` + seated `science.md` from `house_dump.py:152-254`. Stamp: `capable: yes` T-387/T-400/…; T-404 `payload.bound=yes` (`head.json:14980`). Feedback: findings on those tickets (`who=gus` 20 / `who=linus` 32 in `head.json`). T-405 closed; helpers T-413–T-420. **No C-/S- minted.**

## Card format (Return fence vs leftover keys vs first command)
Gus fence `capable/craft/f013/tickets/blocker` (`gus.md:116-122`). Linus `science/tickets/f013` (`linus.md:105-108`). First cmd: inbox + packet + Gus `stamp --field capable` (`gus.md:40-43`; `linus.md:20-22`). Leftover keys `need_*` banned (`PROTOCOL.md:80-82`); Linus log `need_builder` **6× 08-20/21**, **0** on 08-25.

## Too long? (job-card lines, hire re-reads, pytest house)
Job cards **128** / **115** lines. Hire re-reads desk + BRIEF + `vab.md` 40-line blob + `science.md` catalog **~54** unbound rows. Gus restamped the same hang **5×** 08-25. Pytest is Lars house (`BRIEF.md:74-83`); Gus/Linus cards **0** pytest.

## In the loop? (S/M/C prefixes, named helper, findings, pad occupancy)
Kernel mints S/M/C (`tickets.py:59-62`); **0 C- / 0 S-** on disk; live T- stay (`BRIEF.md:6-8`). Bind = payload (`T-404` `head.json:14979-14985`); dumps lag: desk bind still lists Water T-025/026/028 (`desk.md:26`); T-081 `science_ids` still goo/geiger (`head.json:3569-3572`) vs bound PresMat trio T-404/T-460/T-461 (`science.md:22-24`). Named helper: Gus files Wernher `vab-helper`, does not write `craft.py` (`gus.md:21-32`). Findings: yes on work tickets. Pad: leftover **0**, hangar **none** (`desk.md:4-5`); 08-25 “Did not Hangar.”

## Files read
`.grok/agents/gus.md`, `.grok/agents/linus.md`, `docs/crew/{gus,linus}.md`, `docs/crew/log/{gus,linus}.md` (counts + last 40), `docs/program/{PROTOCOL,OPS,vab,science,desk,current}.md`, `docs/program/tickets/BRIEF.md`, `docs/missions/jebediah/science.md`, `house_dump.py`, `card.py`, `tickets.py:59-64,324`, `head.json` T-081/T-387/T-400/T-404 (ids/findings only).

===== COMMS 5 =====
Seat is still `jebediah`; uncrewed `commander: none` so Hank/parent flies. Last Commander bus write is 08-22. 08-25 tape is kernel hops in his folder; 08-26 is empty.

## Desk
Jebediah Grokman, Commander — abort officer, not hop pid. Overlay `.grok/agents/jebediah.md` (23) follows `.grok/agents/pilot.md`. `current.md:1` `flight: jebediah`; `desk.md:6` `seat: jebediah`; INDEX one mission. Plan `campaign: uncrewed` / `cli: python main.py hop` (`plan.md:16-17`). Gate: `commander_for(uncrewed)→none` (`tickets.py:927-934`). Val capcom never sat; Bill/Bob logs 1 line each (`docs/crew/log/{valentina,bill,bob}.md:3`). Spotter card still on disk, deprecated (`.grok/agents/spotter.md:2-11`).

## Who they respond to (PROTOCOL vs actual log)
PROTOCOL: Hank hires him only if `commander: jebediah`; Gene stamps `go:`; he copies `cli:`; leftover → Hank (`PROTOCOL.md:25-29`, `246-252`). Voice: copy Gene, note Lars/Gus/Wernher (`docs/crew/jebediah.md:37-45`). Actual: `note-tech` last **08-22T23:18Z Jebediah → Lars** (`note-tech.md:65`). `loop.md` is Gene/Hank abort talk, not stick (`loop.md:1-22`). Board `who: jebediah` **6**, last **08-22T23:18Z T-081** (`board.jsonl:336`). Crew log is kernel hop lines, not hire returns.

## How Hank sits in between (ops next / packet / leftover / tape)
`ops next` uncrewed: hire desk `hank` + `cli`, `commander: none` (`test_tickets.py:595-626`; `OPS.md:252-255`). Packet skim: desk + BRIEF + fly ticket. After CLI: leftover `recover()`+Close, `attach-run`/`landing` (`PROTOCOL.md:28-29,258-259`). Pad now clean: `lock: free` leftover 0 hangar none (`desk.md:1-5`). Last hop abort `ksc leftover` is a Hank handoff (`pilot.md:36-37`).

## Writes since 2026-08-25 (md vs tickets stamp vs tickets feedback)
**Hire writes: none.** No `who: jebediah` 08-25/26. No `tickets feedback` from him. **Kernel tape 08-25:** crew log 10 hops (`jebediah.md:202-211`); T-081 evidence 15 jsonl including 5 **not** in the crew log (`08-20-54`…`09-01-24`, `head.json:3326-3330`). `last-flight.md` == `…22-06-37Z-hop.md` (exit 2 abort). T-081 `learn`/`telem_run` Hank attach-run (`head.json:3567-3574`), `updated: 2026-08-25T22:10:10Z`. **08-26: MISSING** under `docs/missions/jebediah/`. `desk.md:15` still `exit=0` vs last-flight exit 2. Reviews → `docs/archive/reviews/` **PARKED**. `note-tech` frozen 08-22.

## Card format (Return fence vs leftover keys vs first command)
First command: `tickets inbox --desk <slug>` then packet `cli:` (`pilot.md:24-32`). Return: `result:` `exit:` `handoff:` `abort:` `last:` (`pilot.md:71-79`; `PROTOCOL.md:496`). Then `tickets feedback T-NNN --claim`. Drop `envelope:`/`need_*`/`improve:`/`good:`. Miss-during-hop: `tickets open --type control --fingerprint`. After exit: stop.

## Too long? (job-card lines, hire re-reads, pytest house)
Thin overlay 23 + pilot 87 + voice 53. Hire also re-reads desk + BRIEF (~132) + ticket. pytest house: uncrewed must **not** hire jebediah (`test_tickets.py:595-621`); crewed pad-occupancy **does** (`:569-593`); `test_telem.py:947` uses `09-01-24Z` jsonl missing from crew log.

## In the loop? (S/M/C prefixes, named helper, findings, pad occupancy)
Seat yes, **hire no**. Fly still **T-081** (no `M-`/`S-`/`C-` in `head.json`). He does not patch named helpers. Findings on T-081 `who: hank` (`head.json:3344-3352`). Pad empty; last abort pre_launch apo 85 (`ship.md:5-7`, `last-flight.md:1-9`). Uncrewed tape still lands in `docs/missions/jebediah/` (442 files).

## Files read
`.grok/agents/{jebediah,pilot,valentina,bill,bob,spotter}.md`; `docs/crew/jebediah.md`; `docs/crew/log/{jebediah,valentina,bill,bob}.md` (jeb: hop-exit 127, ksc-exit 25, pad/load/h2w 34, last 40 = `:173-211`); `docs/missions/jebediah/{loop,plan}.md`; `docs/program/{current,note-tech,PROTOCOL,OPS,desk,ship,tickets/BRIEF}.md`; `docs/last-flight.md`; `docs/missions/INDEX.md`; `tickets.py:927`; `protocol.py:40`; `head.json` T-081; `board.jsonl` who=jebediah; `tests/test_tickets.py:569-626`. PARKED: `docs/archive/reviews/*`, `docs/archive/2026-08-23-md-cutover/program/org-session-audit.md`.

===== COMMS 6 =====
Mortimer is the house-RSI desk, not the pad. 08-25 he harvested rsi/org into Practice, PROTOCOL, and cards, then left **live novels** (`lars-rsi.md`, `learn-rsi.md`, `feedback-plan.md`). 08-26 log **0**. T-470 rsi still **inbox**. Practice is last-write from **tickets** (rsi stems + Os org letters), not hop jsonl.

## Desk
**Mortimer Grokman, CEO.** Goal/slate, org RSI, CTT, PROTOCOL / `.grok/agents/*.md` / Practice. Never fly / Hangar / `.py` / GameData. `.grok/agents/mortimer.md:13-17`. CTT exception CHARTER `:83-86`. Reasoning fights itself: card **high** (`mortimer.md:17`), PROTOCOL **medium** (`PROTOCOL.md:349`), OPS **high** (`OPS.md:383`), portrait **medium** (`docs/crew/mortimer.md:27`).

## Who they respond to (PROTOCOL vs actual log)
PROTOCOL: **Os** → objective/CHARTER (`PROTOCOL.md:21`); **Hank** → `type=ctt|org|rsi×3` (`:38`); software rsi → Wernher not him (`OPS.md:74-77`). Log 08-25 **13** bullets (`docs/crew/log/mortimer.md:3-15`); **0** on 08-26. Mix: Hank-opened rsi (T-407…T-466) + Os org letters (T-444, T-448, T-452, T-456). He never talks to Gene/Lars on the stick. Ground talk legal (`PROTOCOL.md:59-60`) unused in the log.

## How Hank sits in between (ops next / packet / leftover / tape)
`ops next` hires him **lock-free**; lock live **skips org**; fly_ready still hires without emptying the pad (`OPS.md:76-77`, `PROTOCOL.md:117-119`). Packet = `desk.md` + inbox + ticket + BRIEF (`mortimer.md:22-27`). Leftover/tape is **Hank** (`PROTOCOL.md:7-10`). Kernel opens rsi (`OPS.md:297`). Several Mortimer-desk rsi closes are **`who: hank`** (T-425/429/432/434/439/441; T-456/T-463 findings) while the log still says “Practice last-write.” T-458 software rsi went to **Wernher** (`head.json:17358-17378`).

## Writes since 2026-08-25 (md vs tickets stamp vs tickets feedback)
**MD:** Practice bullets `world-model.md:465-726`; CHARTER RSI `:16-33`; slate still dated **08-24** (`slate.md:3-11`); job cards + portraits; **live novels** `lars-rsi.md` (applied, git **MISSING**, `:3` / `:54`), `learn-rsi.md`, `feedback-plan.md` (compile, no apply). **Stamp:** none (`who: mortimer` + `op: stamp` empty). **Feedback CLI `op: feedback`:** empty. Door is **`op: patch`** `payload.findings` + `close_why` (`board.jsonl:1710-2019`). T-466/T-467 **done**; **T-470 inbox** (`head.json:17875-17878`). Board **0** events dated 08-26.

## Card format (Return fence vs leftover keys vs first command)
First command: `tickets inbox --desk mortimer` then `packet` (`mortimer.md:19-24`). Return: `goal:` `org:` `tickets:` `unlocked:` `need_os: none|charter|roster` (`:84-90`, `PROTOCOL.md:492`). Drop `need_builder`/`need_qol`/`need_gene`. After hire: `tickets feedback --claim` — not Return keys (`:92-94`).

## Too long?
CHARTER **200** vs OPS **437** vs PROTOCOL **565**. Practice **322–767** (~445 lines) **> CHARTER**. Job card **97**; portrait Notes dump the same law (`docs/crew/mortimer.md:27-67`). Gene/Hank/Lars cards ~170–194. Packet re-reads desk+BRIEF+ticket; **no** `lessons.md` on the Mortimer card. House pytest still `test_hop.py` **231** (`BRIEF.md:74-83`; `lars-rsi.md:38`). Spotter card still on disk (`.grok/agents/spotter.md:1-11`, DEPRECATED). CHARTER table lists Mortimer **twice** (`:111`, `:118`).

## In the loop?
Yes for **rsi/org/ctt**, not S/M/C flying. He **wrote** S/M/C prefix law (T-466, `world-model.md:711-720`, `BRIEF.md:5-8`) then left T-470 on **T-**. Named helper is Lars’s (`hop_factory_pad.py`), not his. Findings `real: false` harvests. Pad occupancy is the refrain “Pad still flies” — he does not sit occupancy. Practice from **rsi tickets + Os letters**, citing 09-01Z via T-448/T-452 — **not** jsonl (`mortimer.md:41-42`, `:72-80`).

## Files read
`.grok/agents/mortimer.md`, `gene.md`/`hank.md`/`lars.md`/`wernher.md` tails, `spotter.md`; `docs/crew/mortimer.md`; `docs/crew/log/mortimer.md` (13×08-25, 0×08-26); `CHARTER.md`; `PROTOCOL.md`; `OPS.md`; `world-model.md` Practice; `slate.md`; `lars-rsi.md`; `learn-rsi.md`; `feedback-plan.md`; `tickets/BRIEF.md`; `tickets/head.json` T-456/458/463/466/467/470; `tickets/board.jsonl` mortimer patches (no dump).

===== COMMS 7 =====
Comms desks since 2026-08-25: Verena rewrote press; Katherine/Walt/unused pilots did not fire. Spawn table still names them.

## Desk
Katherine: `.grok/agents/katherine.md` (86), `docs/crew/katherine.md` (~27). Verena: `.grok/agents/verena.md` (95), `docs/crew/verena.md` (~49), law `docs/press/STYLE.md` (219). Walt: `docs/crew/walt.md` (27); **`.grok/agents/walt.md` MISSING**. Spotter: `.grok/agents/spotter.md` (13) DEPRECATED. Stubs: `bill.md`/`bob.md`/`valentina.md` (12), `grok.md` (18) + shared `pilot.md` (87). `docs/program/roster.md` lists Walt/Verena/pilots, **not Katherine**. `crew.py:23–37` slug map: pilots+Walt+Verena, **not Katherine**.

## Who they respond to (PROTOCOL vs actual log)
PROTOCOL handoffs: Hank→Verena `type=press` firsts (`PROTOCOL.md:39`); Walt→Os phase edges (`:40`). Katherine **absent** from that table; only Return schema (`:489`). OPS 4.2 hires Verena on firsts (`OPS.md:296`); Walt “Never Hire” (`:28`); Katherine **not in 4.2** (`:280–297`) but in split (`:30`). AGENTS: Katherine if `desk=katherine` / `--tag dynamics` (`AGENTS.md:214–218`); Verena `type=press` / leftover `need_pr` (`:272–275`); Walt speech, no spawn (`:79–89`, `:136`); Commander seated slug (`:103`); Spotter “Do not spawn” (`:106`, `:206`). Talk-by-name lists Val/Bill/Bob, **not Katherine** (`:59–60`). Log: Katherine 08-23 Mortimer T-283 → Lars T-285 (`docs/crew/log/katherine.md:3–4`; `head.json:9987–10007`, `:10034–10059`). Verena Os/Hank press. Walt 08-20 only. `current.md:1–3` seat Jeb, **capcom Valentina** vs Walt CAPCOM.

## How Hank sits in between (ops next / packet / leftover / tape)
`ops next` leftover first (`ops.py:209`), lock-live ground includes verena+katherine (`:220`), fly_ready parallel **katherine not verena** (`:266`), idle DESKS skip walt (`:361–362`). `_desk_ground` only inbox/triage/ready/assigned (`:94–114`) → T-283 `verify` not hired. Packet: desk+BRIEF+id (`katherine.md:26–32`). After CLI: Hank leftover + `attach-run` + `landing` (`AGENTS.md:225–228`); Katherine eyes those windows (`katherine.md:20–21`). Verena `shot:` → parent screenshot (`PROTOCOL.md:313`). T-435: Os open, **Hank** finding+close (`board.jsonl` 1773/1782/1789), not Verena. Parent **speaks** as Walt (`PROTOCOL.md:40`).

## Writes since 2026-08-25 (md vs tickets stamp vs tickets feedback)
Katherine log count **3** (header+2); last 08-23; **0** this window. Verena log **22** lines; 08-25: T-435 corpus + T-397 close (`docs/crew/log/verena.md:3–4`). INDEX newest story still **2026-08-24** (`docs/press/INDEX.md:18`). Stamp: T-397 `done` who=verena 08-25; T-435 `done` who=**hank**. Findings: T-397 `who=verena` `real=true`; T-435 `who=hank` `real=false`. Walt/bill/bob/valentina/grok logs **2** each, last 08-20. Open press on BOARD: **0**. T-283 still `verify` (`BOARD.md:45`).

## Card format (Return fence vs leftover keys vs first command)
Katherine fence `tickets:` `model:` `ask:` (`katherine.md:76–80`) vs PROTOCOL “do not return `ask:` as the bus” (`PROTOCOL.md:80–82`). Verena `tickets:` `story:` `shot:` `readme:` (`verena.md:85–90`). Pilot `result:` `exit:` `handoff:` (`pilot.md:73–79`). Walt: no fence. Leftover `need_*` forbidden on Return; AGENTS still routes leftover `need_pr` (`:273`). First command: Katherine inbox+packet; Verena inbox; pilots exact `cli:`; Walt none; spotter do not spawn.

## Too long? (job-card lines, hire re-reads, pytest house)
Cards: Katherine 86, Verena 95, Gene 170, Lars 192, spotter 13, unused pilots 12–18. Verena hire re-reads STYLE 219 + INDEX + README beyond packet ≤3 (`verena.md:58–63`). Katherine `verify` is the anti-rehire. Pytest: `tests/test_protocol.py:80–89` file existence + README names — **not** hop house (`BRIEF.md:74`). No pytest on Katherine pulse.

## In the loop? (S/M/C prefixes, named helper, findings, pad occupancy)
**In (thin):** Verena on firsts only; press stays `T-`; helper = `docs/press/` + parent grim. **Parked-open:** Katherine T-283 `type=ops` (not S/M/C), empty `payload`, helper `telem --window` / `tickets landing`, not pad occupancy. **Out:** Walt (speech, `REASONING` low, skip-hire). Spotter file + spawn-table row still exist (`AGENTS.md:106`). **Unused:** `commander_for` returns only `none`|`jebediah` (`tickets.py:927–934`); DESKS has `jebediah` only (`:87`); bill/bob/valentina/grok never seated. Parent table **still lists** Verena, Katherine, Spotter, Commander slug. PARKED: `docs/archive/2026-08-23-md-cutover/program/org-session-audit.md` already said no `walt.md`, kill spotter.

## Files read
`.grok/agents/{katherine,verena,spotter,bill,bob,valentina,grok,pilot}.md`; `docs/crew/{katherine,verena,walt,bill,bob,valentina,grok}.md`; `docs/crew/log/{katherine,verena,walt,bill,bob,valentina,grok}.md`; `AGENTS.md`; `docs/program/{PROTOCOL,OPS,roster,current}.md`; `docs/press/{INDEX,STYLE}.md`; `docs/program/tickets/{BRIEF,BOARD,head}.json*` (grep only); `ops.py`; `tickets.py`; `protocol.py`; `crew.py`; `tests/test_protocol.py`. `.grok/agents/walt.md` **MISSING**.