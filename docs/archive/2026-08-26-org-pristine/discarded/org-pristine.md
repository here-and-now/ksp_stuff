The bus already exists. The clusterfuck is a **second bus**: RSI novels, dual dumps, leftover mailboxes, and a 2872-line miss-physics file that a cold hire is still told to treat as law. This letter is the sit and the cut — not a new live `docs/program/*.md`. Pad stays hot. Do not idle it for the archive. Bank **2.2905** does not pay `generalRocketry` **20**.

# Org pristine — status quo and plan (2026-08-26)

## PART I — Status quo

### 1 Sit

Lock **free**, leftover **0**, sci **2.2905**, craft **`kspstuff-hop-valiant-t7-wheel-pbc`**, capable **yes**, seat **jebediah** (`docs/program/desk.md:1`–`:16`). Tree `start,engineering101,basicRocketry,survivability,stability`. Bound T-404 / T-460 / T-461 PresMat (`desk.md:26`). Last CTT spent is `stability`. Next node **20** does not pay (`docs/program/CHARTER.md:8`–`:11`; `docs/program/slate.md:4`–`:11` still says bank **2.09**).

Tape is a three-way lie. `docs/last-flight.md:1`–`:9` hop **exit 2 abort**. Desk last **exit=0 abort=none** (`desk.md:15`). T-081 `learn:` is **synth** `sit=pre_launch rec=yes sci=run=0 rem=0 bank=2.29 +0` with a **waste** latch (`docs/program/tickets/head.json:3567`–`:3596`). `docs/program/ship.md:5`–`:7` is the same hang `pre_launch` at `2026-08-25T22:09Z`. Last-flight 40 lines is not the vessel.

T-081 `go: yes` `campaign: uncrewed` `cli: python main.py hop` (`head.json:3338`–`:3343`). Living +0 is not clean-0 re-fly. T-471 control **inbox** (Os scrap, engine dead on pad, `rf-ignition-ullage`, `head.json:17881`–`:17900`). T-468 RSI **inbox** sci-unchanged ×19 desk **wernher**. T-470 RSI **inbox** rf-ignition ×8 desk **mortimer**. BOARD dump `open: 74 / 471` (`docs/program/tickets/BOARD.md:3`).

Last RSI on disk: **lars-rsi** 2026-08-25 (`docs/program/lars-rsi.md:1`; git `ea7f60b` “Apply Lars RSI: S/M/C prefixes, pad-RF one sit.”). The letter still claims T-465 **inbox** and git **MISSING** (`lars-rsi.md:49`–`:54`) — both stale. T-465 is **done** (`head.json:17716`). Os 2026-08-26: clusterfuck of documents; agents do not know where to write; ticket bus is the comms.

### 2 Communication graph

**Law:** Os → Hank (`docs/program/PROTOCOL.md:20`). Hank `ops next` then those hires (`:23`; `docs/program/OPS.md:15`–`:27`). Os-by-name = voice, no spawn (`PROTOCOL.md:22`). Gene stamps `go:` on the fly ticket only (`:24`). Mortimer org / RSI / CTT (`OPS.md:20`). Lars pulse / Wernher blocks (`OPS.md:25`–`:26`). Commander takes `uplink.md` (`CHARTER.md:191`). Walt speaks phase edges. Depth 1. One control writer (`AGENTS.md:111`).

**Ticket** = bind / `go` / `capable` / `learn` / finding. **MD** = creed, kernel how-to, Gene render, tape. Crew logs are voice tape, not dispatch.

**Actual:** Hank is the TUI parent (`OPS.md:44`–`:47`). His log is **16** lines; **6** dated 2026-08-25; **0** on 08-26 (`docs/crew/log/hank.md:3`–`:9`). Gene last log **08-24** T-081 Ad astra, Not Learn (`docs/crew/log/gene.md:3`); **0** on 08-25/26. Uncrewed Learn is Hank `attach-run` (`tickets.py:1359`–`:1392`) — hop-exit still calls it `who="wernher"` then `stamp_learn who="hank"` (`main.py:106`; `tickets.py:1392`). Packet skim is already `desk.md` + `BRIEF.md` (`tickets.py:396`–`:397`) — then **twins**: fly injects seated `jebediah/briefing.md` (`:406`); science injects program `science.md` (`:414`); vehicle `vab.md` (`:416`); control `blocks.md` (`:420`); org/rsi `OPS.md` (`:430`). BOARD is a human dump (`OPS.md:90`), forbidden in packet (`BRIEF.md:4`).

### 3 What each desk still writes and reads (since 2026-08-25)

| Desk | Writes | Reads / told to read |
|---|---|---|
| **Hank** | leftover CLI, `attach-run`/`landing`, `desk.md` via CLI, 6 log bullets 08-25 | `OPS.md` kernel (`.grok/agents/hank.md:78`); first command `desk` then `ops next` (`:48`–`:51`). Parent `AGENTS.md:3`–`:9` still CHARTER + last-flight + lessons |
| **Gene** | **0** md / stamp / findings 08-25. T-081 `go: yes` last Gene log 08-24. Dual `plan.md` / `briefing.md` still his render (`PROTOCOL.md:500`–`:502`) | packet M-NNN + live T-081 (`.grok/agents/gene.md:29`–`:37`). Card already: do not dispatch via world-model / science.md (`:19`–`:20`) |
| **Lars** | pad-RF patches; lessons headings; 6 `rf-ignition-ullage` log lines (`docs/crew/log/lars.md:3`–`:8`) | named helper `.py` + **lessons append** (`.grok/agents/lars.md:165`); portrait still orders a lessons heading (`docs/crew/lars.md:32`–`:33`) |
| **Wernher** | T-467 prefix; T-449 eyes; VAB helpers | miss → lessons heading (`.grok/agents/wernher.md:92`); `agent-notes.md` still-true API |
| **Mortimer** | lars-rsi letter; Practice last-writes 08-25; log still “git MISSING” (`docs/crew/log/mortimer.md:3`) | PROTOCOL / job cards / Practice. This letter is not a live novel |
| **Linus** | science **dump** not bind (`PROTOCOL.md:478`; `.grok/agents/linus.md:16`) | packet S-NNN; live T- science stay |
| **Gus** | `vab.md` after stamp (`.grok/agents/gus.md:101`); `.craft` | packet C-NNN; live T- vehicle stay. BOARD vehicle = T-ids, **0 C-** |
| **Commander** | takes uplink; `note-tech` CLI still a mailbox (`uplink.py:8`–`:9`; `main.py:755`) | `current.md`, `note-tech` during hop (`.grok/agents/pilot.md:64` tape label) |
| **Katherine** | disk tape windows | card exists (`.grok/agents/katherine.md:1`); **no row** in `docs/program/roster.md:5`–`:20` |
| **Verena** | README / press | not spawn this letter |
| **Spotter** | — | **Do not spawn** (`AGENTS.md:106`) — card still on disk |

### 4 Injection (what a cold hire loads)

**Child (every job card `agents_md: false`):** packet = `desk.md` + `tickets packet` + `BRIEF.md` (`PROTOCOL.md:340`–`:345`). `read:` desk + ≤2. Control third path = named helper (`:356`–`:360`).

**Parent (Hank TUI):** `AGENTS.md:3`–`:9` CHARTER → PROTOCOL → last-flight → `desk` → `current.md` / `slate.md` / INDEX; **miss physics `docs/lessons.md`**. Feedback chain still “append `docs/lessons.md`” (`AGENTS.md:326`, `:345`).

**Not packet, still live next to kernel:** `lars-rsi.md`, `learn-rsi.md`, `feedback-plan.md`, `world-model.md` (800), `RO.md`, `org-flow/`, `sit-card.json`, `BOARD.md`, `lessons.md` (2872 / **156** `##`). `FORBIDDEN_DISPATCH` (`docs_inventory.py:27`–`:32`) lists archive / niche / improve / kerbin-lessons — **not** `docs/lessons.md`. Classify fallthrough stamps RSI novels as `live_kernel` (`docs_inventory.py:345`).

Floors clash: `PROTOCOL.md:349` Jeb / Lars **low** vs `AGENTS.md:137` everyone-else **medium** (Lars patches not cheap). Hank card copies **low** (`.grok/agents/hank.md:54`).

### 5 Dual stores and leftover mailboxes

| Pair | Live lie |
|---|---|
| **plan** | Shim `docs/program/plan.md:12`–`:15` `expect_apo_max: 140000` craft **proc-long** `go: yes`, **no** `cli`/`campaign`/`science_ids`. Seated `docs/missions/jebediah/plan.md:12`–`:18` `expect_apo_max: 400000` same proc-long + `cli: hop` `campaign: uncrewed` `science_ids: barometerScan,geigerCounter,mysteryGoo`. `sync_shim` copies seated→shim (`missions.py:192`–`:209`) — **not last-run**. `protocol fly` still `ff.get("go") or plan.get("go")` (`protocol.py:132`–`:135`) |
| **briefing** | Program `docs/program/briefing.md:3`–`:17` **proc-long**, bank **8.7721**, T-077/T-287 Forest land. Seated `docs/missions/jebediah/briefing.md:3`–`:10` **t7-wheel**, T-404/460/461, landing `10-57-36Z`. Fly skim injects **seated** (`tickets.py:406`) |
| **science** | Program dump 87 lines, bound T-404/460/461 + catalog (`docs/program/science.md:6`–`:24`, `:87`). Seated dump 37 lines, same three (`docs/missions/jebediah/science.md:1`–`:36`). Bind = ticket payload (`PROTOCOL.md:526`–`:530`). Hop/pad still **parse seated science.md** if tickets empty (`hop.py:316`–`:335`; `pad.py:65`–`:81`) |
| **vab vs C-** | `vab.md:2`–`:4` hang **t7-wheel** + alt novel. **0** live `"id": "S-`/`M-`/`C-` in `head.json`. Prefix law exists (`tickets.py:59`–`:63`); mint has not |
| **note-tech** | 65-line 08-22 mailbox; last `note-tech.md:65` T-081 stiff-pbc. Desk **clips it into every packet** (`desk.py:624`; `desk.md:27`). Test pins the clip (`tests/test_desk.py:281`–`:285`). CLI still “Commander → Lars/Gus/Wernher” (`uplink.py:8`–`:9`; `main.py:755`) |
| **loop** | Program 1-line stub (`docs/program/loop.md:1`). Seated abort/`no_warp` tape (`docs/missions/jebediah/loop.md:1`–`:22`). `main.py:751` help still says program loop |
| **world-model** | Chair `world-model.md:1`–`:16`. Meaning still T-013 hop-to-water 10-11-27Z (`:29`–`:47`). Open questions last Gene **08-22** (`:799`). Practice dump to `:800`. Claims `hop_factory.py` **~779** (`:506`) vs disk **1052** |
| **BOARD / sit-card** | `BOARD.md` 80-line dump, open 74/471. `sit-card.json:2` craft **east-t3-pbc**. `GLOSSARY.md:37` **Retired** — sit is `desk.md` |
| **slate / CHARTER / learn-rsi** | slate bank **2.09** (`slate.md:5`); CHARTER **2.29** (`CHARTER.md:10`); desk **2.2905**; learn-rsi sit sci **8.7721** (`learn-rsi.md:13`) |

### 6 Mission identity

CHARTER already `docs/missions/<id>/logs/` (`CHARTER.md:163`). `current.md:1` `flight: jebediah` on an **uncrewed** Stayputnik sit (`docs/crew/log/jebediah.md:8`). Tree: `docs/missions/` = `INDEX.md` + `jebediah/` only (`INDEX.md:7`). Logs **442** files (228 jsonl, 214 md). Jeb crew log **209** `-` lines; last `:211` `2026-08-25T22-06-37Z hop exit=2 abort=abort`. **0** `crew=Jeb` / `crew=[A-Za-z]` on tape. `command: phase` in logs: **0**. 2026-08-26 tape: **0**.

**Hop writer** is `seated_logs_dir(seated_id())` (`flightlog.py:246`–`:249`; `missions.py:103`–`:104`). Exception fallback `docs/flights/` (`flightlog.py:27`, `:253`). Kernel **hardcodes** `jebediah` in packet/envelope (`tickets.py:406`, `:424`, `:458`) and dump paths (`house_dump.py:20`–`:22`). How-to is mixed: `BRIEF.md:63` and `tickets/README.md:26` still `docs/missions/jebediah/logs/`; `OPS.md:100` evidence path jebediah; `.grok/agents/hank.md:122` and `docs/flights/README.md:15` already `<seat>`. `main.py:761` review help still jebediah. `GLOSSARY.md:10` “mission = seated folder `jebediah/`”.

### 7 Lars vs Wernher catalog

Law already: Lars composes **one living rocket** from Wernher blocks (`PROTOCOL.md:138`–`:141`; `OPS.md:26`). T-376 **done** `control-blocks` (`head.json:13664`–`:13681`).

**Disk:** `hop_factory.py` **1052** lines; `run_factory_vessel` still immortal (`:1051`–`:1052`). Compose imports pad-RF (`hop_factory.py:31`). `hop_factory_pad.py` **8** defs (`:20` `_pad_engines` … `:165` `_pad_hold`); docstring is the live RF law (`:1`–`:8`, `:173`–`:180`). Pad tests **8** (`tests/test_hop_factory.py:85`–`:224`) — lars-rsi claimed **6**. `hop.py` **3300** (parked water/splash + shared). Wernher catalog = `physics_warp.py` + sit predicates. `blocks.md` is a **174-line hop-law novel** (`blocks.md:3` “Vehicle Engineering”); packet injects it on every control ticket (`tickets.py:420`).

Lars still appends `docs/lessons.md` (`.grok/agents/lars.md:165`). Stem `rf-ignition-ullage` **10** (`fingerprints.json:153`); lessons has **6** dated rf headings (`docs/lessons.md:24`–`:115`) plus MM cfg `:131`. T-471 is the same stem again. Compose is **after** the docs cut (pulse-law). Do not retune pad-RF this slice.

### 8 Stale cards and out-of-loop desks

- **Spotter** card `.grok/agents/spotter.md:1`–`:13` DEPRECATED / do not spawn. Still spawnable if someone ignores the table.
- **builder.md** pointer (`docs/crew/builder.md:1`–`:3`) so old prompts resolve.
- **Gene** first command `packet M-NNN` (`.grok/agents/gene.md:31`) with **0** live M- ids. Live fly is T-081.
- **Linus / Gus** first command S-/C- same mint gap.
- **Hank** card **194** lines; still 09-01Z / T-449 essays; warp sentence mixed; Return fence `ops/hire/packet/pad/why/rsi` vs CHARTER “not Return keys” (`CHARTER.md:19`–`:21`).
- **Lars** card **192**; “one helper, stop” vs 1052-line inland compose.
- **Wernher** still lessons-on-miss.
- **Pilot** relabels note-tech tape; CLI mailbox remains.
- **Roster** missing Katherine; card + portrait exist.
- **Job-card floors:** Lars low vs medium (above).

### 9 Poison live docs

`docs/program/`: **26** `*.md` + `sit-card.json` + `org-flow/` (html+6 svg, 0 md) + `overlay.last` / `uplink.last` / `unrecoverable.last`. `docs/archive/` is **PARKED** (2026-08-23-md-cutover already holds rsi-jump / ticket-bus-cutover / I/F twins).

| path | lines | class | why |
|---|---|---|---|
| `docs/lessons.md` | **2872** / 156 `##` | NUKE→stub | miss-physics bus; tests pin `Forest is 270` (`tests/test_protocol.py:145`–`:147`) and `## ` (`:197`–`:200`); kernel twins headings (`tickets.py:1666`–`:1692`) |
| `docs/program/world-model.md` | **800** | ARCHIVE dump; 20-line chair stub | Practice novel; Meaning 08-22; hop_factory size lie |
| `docs/program/PROTOCOL.md` | **566** | KEEP-MD | Hank kernel; **patch** inject / Lars floor |
| `docs/program/OPS.md` | **437** | KEEP-MD | **patch `:369`** drop lessons row |
| `docs/program/krpc.md` | **259** | KEEP-MD | role extra, not packet |
| `docs/program/CHARTER.md` | **200** | KEEP-MD | creed; do not rewrite |
| `docs/program/learn-rsi.md` | **186** | ARCHIVE | applied paper; sit sci 8.77 stale |
| `docs/program/blocks.md` | **174** | KEEP stub | CLI names only; body is hop-law |
| `docs/program/tickets/BRIEF.md` | **132** | KEEP-MD | **patch `:63` dest, `:83` lessons** |
| `docs/program/ra-rate.md` | **88** | KEEP-MD | disk fact, not spawn |
| `docs/program/science.md` | **87** | MOVE/TICKET | dump; skim still injects |
| `docs/program/tickets/BOARD.md` | **80** | NUKE-LIVE | forbid packet; PRINT dump |
| `docs/program/mods.md` | **78** | KEEP-MD | disk, not spawn |
| `docs/program/note-tech.md` | **65** | TAPE | mailbox law still live |
| `docs/program/RO.md` | **59** | ARCHIVE | parked 08-21, still live path |
| `docs/program/desk.md` | **57** | KEEP-MD | sit snapshot (gitignored) |
| `docs/program/lars-rsi.md` | **54** | ARCHIVE | applied; T-465 inbox lie |
| `docs/program/feedback-plan.md` | **48** | ARCHIVE | compile, no apply |
| `docs/program/slate.md` | **47** | KEEP-MD | goal; bank 2.09 stale vs desk |
| `docs/program/GLOSSARY.md` | **44** | KEEP-MD | **patch `:10` dest, `:31` tape-only** |
| `docs/program/tickets/README.md` | **44** | KEEP-MD | **patch `:26` dest** |
| `docs/program/vab.md` | **40** | MOVE/TICKET | Gus novel; skim injects |
| `docs/program/ship.md` | **24** | TAPE | radio, not spawn |
| `docs/crew/builder.md` | **24** | NUKE-LIVE | old-prompt pointer |
| `docs/program/roster.md` | **23** | KEEP-MD | names; add Katherine later if creed/roster |
| `docs/program/briefing.md` | **20** | TICKET/shim | stale proc-long / bank 8.77 |
| `docs/missions/jebediah/plan.md` | **20** | KEEP render | Gene; craft proc-long vs hang t7-wheel |
| `docs/program/tech.md` | **20** | KEEP-MD | query |
| `docs/program/plan.md` | **17** | TICKET/shim | `sync_shim` leftover |
| `.grok/agents/spotter.md` | **13** | NUKE-LIVE | retired, still a card |
| `docs/missions/jebediah/briefing.md` | **13** | KEEP (fly skim) | t7-wheel; hardcoded jebediah path |
| `docs/program/sit-card.json` | **24** | NUKE-LIVE | retired east-t3 |
| `docs/program/current.md` | **3** | KEEP-MD | seat |
| `docs/program/loop.md` | **1** | TAPE/shim | empty |
| `docs/program/uplink.md` | **1** | KEEP-MD | Commander takes; cleared |
| `docs/agent-notes.md` | **791** | KEEP (API only) | still-true kRPC; 2HOT sci 2.43 lie at `:786` |
| `hop_factory.py` | **1052** | pulse (later) | immortal compose |
| `hop.py` | **3300** | parked+shared | not this slice |
| `docs/program/tickets/head.json` | **17904** | TAPE | bus |
| `docs/program/tickets/fingerprints.json` | **212** | TAPE | lookup |
| `docs/program/org-flow/` | html+6 svg | ARCHIVE | 0 md |

### 10 Prior RSI: what stuck, what failed, what the jumps added to the pile

**rsi-jump (PARKED `docs/archive/2026-08-23-md-cutover/program/rsi-jump.md`):** skipped Gene between uncrewed hops. Also skipped the only `payload.learn` writer.

**learn-rsi (live `docs/program/learn-rsi.md`, applied):** filled Learn as hop-exit `attach_run`. `needs_learn` false for uncrewed (`tickets.py:937`–`:943`). Fingerprint reuse / empty refused. **Kept** `lessons.md` run headings as forensics (`learn-rsi.md:156`–`:159`) — that is how the novel got worse. Sit block still sci **8.7721**. Leftover already named hop-exit `who=wernher` (`learn-rsi.md:151`, `:177`). **Added a live novel.**

**ticket-bus-cutover (PARKED):** I/F twins migrated; `migrate_second_bus` still mints `done` control tickets per lessons heading (`tickets.py:1632`–`:1692`).

**lars-rsi (live, git `ea7f60b` then RF follow-ups):** `ID_PREFIX` S/M/C (`tickets.py:59`–`:63`) **stuck**. Pad-RF extract **stuck** (`hop_factory_pad.py`, 8 tests). Packet third path named helper **stuck**. **Failed:** compose still immortal; **0** live S/M/C; lessons still injected; spotter still on disk; uncrewed tape still `jebediah/logs`; letter **added** `lars-rsi.md` next to `learn-rsi.md`. Claimed T-465 inbox / git MISSING / pad tests 6 / stem 7 — disk is T-465 **done**, git **landed**, tests **8**, stem **10**.

**feedback-plan (live, compile only):** Os rejected `--good --self --them`. Door is `tickets feedback --claim`. **Added a live novel.** Findings door **stuck**; this paper must not land as another.

**Each jump wrote a harvest MD into live kernel.** That is the pile.

### 11 Wrong access

| Who | Wrong read | Law |
|---|---|---|
| Parent Hank | `AGENTS.md:3`–`:9` CHARTER + **last-flight before fly** + **lessons** + INDEX | After cutover: `desk.md` + `ops next` + packet + BRIEF |
| Cold Lars | After a miss, `read_file` `docs/lessons.md` (default 1000 = newest contradictions) | named helper docstring + packet `finding:`/`close_why` (`tickets.py:530`–`:546`; `hop_factory_pad.py:1`–`:8`) |
| Fly packet | seated `jebediah/briefing.md` + deep last-flight (`tickets.py:406`–`:412`) | ticket payload + landing envelope |
| Science packet | program `science.md` dump (`:414`) | science payload |
| Vehicle packet | `vab.md` (`:416`) | vehicle `capable:` |
| Control packet | `blocks.md` novel (`:420`) + deep last-flight + hardcoded `jebediah/logs/{live}` (`:424`) | named helper `.py` |
| Desk every sit | clips 08-22 `note-tech` (`desk.py:624`) | stop clip; retire CLI mailbox |
| Anyone | BOARD as vessel; jsonl in prompt; archive as dispatch | BOARD PRINT only; `telem` / `tickets landing`; archive **PARKED** |
| Gene | world-model Open questions 08-22 | card already forbids; `ops --tag ask` |
| Learn | last-flight 40 / desk last / synth `rec=yes` | envelope jsonl via `attach-run` |

Crew logs (voice tape, newest-first): hank **16**-line file; lars rf-ignition **6** (`:3`–`:8`); mortimer lars-rsi applied / pad still flies (`:3`); wernher T-467 prefix / T-449 (`docs/crew/log/wernher.md:3`–`:5`); gene **0** on 08-25; jebediah hop-exit tape ends 22-06-37Z abort (`:211`). Do not inject logs.

---

## PART II — Tightened plan

The bus already exists. First slice still archives the second bus — and now names the three writers a cold hire still gets after that archive.

## Summary

Packet skim is `desk.md`+`BRIEF.md` (`tickets.py:396-397`). Poison is a **second bus**. First slice: archive, unpin tests, stop twins, strip inject, **kill leftover writers** (`OPS.md:369`, hop dest, note-tech CLI). Pad stays hot. Do not undo learn-rsi `attach-run` or lars-rsi S/M/C + pad-RF (`tickets.py:59-63`). Do not retune pulse. Do not rewrite CHARTER creed. This letter is **not** a new `docs/program/*.md`.

## Comms law

Os→Hank (`PROTOCOL.md:20`); Hank `ops next` then those hires (`OPS.md:15-27`). Os-by-name = voice, no spawn (`PROTOCOL.md:22`). Hank leftover + `attach-run`/`landing` (`PROTOCOL.md:8-9,:28`). Gene `go:` on the fly ticket only (`:24`). Mortimer org/RSI/CTT (`OPS.md:20`). Lars pulse / Wernher blocks (`OPS.md:25-26`). **Ticket** = bind/`go`/`capable`/`learn`/finding. **MD** = creed, kernel how-to, Gene render, tape. Crew logs are voice TAPE, not dispatch.

## Injection law

Cold child: job card (`agents_md: false`) + `desk.md` + `tickets packet` + `BRIEF.md` (`PROTOCOL.md:340-345`). `read:` desk+≤2. Control third path = named helper `.py` (`:356-360`). **Forbidden in spawn:** CHARTER, PROTOCOL, OPS, world-model, BOARD, lessons, last-flight, jsonl, archive, `lars-rsi.md`/`learn-rsi.md`/`feedback-plan.md`, sit-card, note-tech, spotter, org-flow. Parent after cutover: `desk.md` + `ops next` + packet + BRIEF — not `AGENTS.md:3-9`. `FORBIDDEN_DISPATCH` (`docs_inventory.py:27-32`) **adds** `docs/lessons.md`.

## KEEP-MD

`desk.md` sit; `tickets/BRIEF.md` how; `CHARTER.md` parent creed; `PROTOCOL.md`/`OPS.md` Hank kernel (**patch** `OPS.md:369` drop lessons row); `current.md` seat; `slate.md` goal; `GLOSSARY.md` speech (**patch** `:31` tape-only, `:10` dest); `roster.md` names; `krpc.md` role extra (not packet); `uplink.md` Commander takes; seated `plan.md` Gene render (`protocol fly` fallback one release, `OPS.md:6-8`); seated `briefing.md` Gene→pilot until ticket holds prose; `mods.md`/`tech.md`/`ra-rate.md` disk facts, not spawn.

## TAPE

jsonl, `last-flight.md`, `ship.md`, `docs/crew/log/*`, `docs/flights/index.jsonl`, `note-tech.md`, program `loop.md`, `tickets/{head.json,board.jsonl,fingerprints.json}`. Never inject. Query `telem` / `tickets landing`. `note-tech` is tape; the CLI is not a desk mailbox.

## ARCHIVE

This sit → `docs/archive/2026-08-26-docs-cutover/`: `lars-rsi.md`, `learn-rsi.md`, `feedback-plan.md`, `RO.md`, `org-flow/`, `world-model.md` 800-line dump (leave a 20-line chair stub), `docs/lessons.md`, seated `loop.md`. Not a new live novel.

## NUKE-LIVE

Tests first: `.grok/agents/spotter.md` (`AGENTS.md:106`); `sit-card.json` (`GLOSSARY.md:37`); `tickets/BOARD.md`; `docs/crew/builder.md`; program `plan.md`/`briefing.md`/`science.md` shim writers (`missions.py:192-209`); `desk.py:624` note-tech clip. Stub `blocks.md` to CLI names. Stub `lessons.md` “parked; do not append” — that path is not miss-physics (`README.md:270` drop).

## MOVE to tickets

`go`/`cli`/`campaign`/`learn` → fly payload; bind → science payload (`PROTOCOL.md:526`); `capable:` → vehicle; open questions → `ops --tag ask`; Practice pitfall → rsi `findings` (stem+count); lessons heading → helper docstring + `close_why`; note-tech mailbox → `type=control --fingerprint` (**writer** `uplink.py:8-9` / `main.py:755`, not only desk clip); vab novel → vehicle `C-` (live T- stay). No `need_*`.

## lessons.md replacement

Stop append (`.grok/agents/lars.md:165`, `wernher.md:92`, `AGENTS.md:326,:345`, `PROTOCOL.md:564`, **`OPS.md:369`**, **`docs/crew/lars.md:33`**, `BRIEF.md:83`, `README.md:270`). Next Lars: named helper + packet `finding:`/`close_why` (`tickets.py:530-546`) + docstring (`hop_factory_pad.py:1-8`). Archive the novel. Drop `Forest is 270` (`test_protocol.py:145-147`) and `## ` requirement (`:197-200`). Stop heading twins (`tickets.py:1666-1692`). `agent-notes.md` = still-true kRPC only.

## Mission identity

CHARTER already `docs/missions/<id>/logs/` (`CHARTER.md:163`) — creed stays. Kernel hardcodes `jebediah` (`tickets.py:406,:424,:458`, `house_dump.py:20-22`) while `current.md:1` seats jebediah on uncrewed. **Hop writer** is `seated_logs_dir(seated_id())` (`flightlog.py:246-249`, `missions.py:103-104`, `main.py:99-106`); `docs/flights/` is the exception fallback (`flightlog.py:27,:253`). Crewed: `seated_id()`. Uncrewed `commander: none`: `docs/flights/`. How-to follows dest: `BRIEF.md:63`, `.grok/agents/hank.md:122`, `OPS.md:100`, `tickets/README.md:26`, `docs/flights/README.md:15`. Keep Jeb dossier for `commander: jebediah`. Do not ticket jsonl schema. Fix `GLOSSARY.md:10`.

## Lars compose

Later, not first slice (pulse-law). Law already (`PROTOCOL.md:139`, `OPS.md:26`). `hop_factory.py` still immortal `:1051`. Pad-RF stays `hop_factory_pad.py`. Reuse `control-blocks` (T-376 done, `head.json:13673`). Wernher catalog = `physics_warp.py` + sit predicates; `blocks.md` stub.

## Job-card cuts

`spotter.md` delete. `hank.md` drop 09-01Z/T-449/session-until essays; keep `desk`+`ops next`; attach-run recipe follows dest. `lars.md`/`wernher.md` drop lessons append. **Portrait dispatch** `docs/crew/lars.md:33` (voice stays). `gene.md` drop world-model dispatch; packet T- and M-. `linus.md` dump not bind. `gus.md` `vab.md` not capable. `pilot.md` note-tech is tape. Floors: Lars **medium** (`AGENTS.md:137`) — fix `PROTOCOL.md:349` low.

## Hank in-between after cutover

`ops next` still. Die: BOARD, lessons-as-facts (`OPS.md:369`), last-flight-before-fly, dual program dumps, desk note-tech clip, RSI novels, **note-tech mailbox**, **`jebediah` attach-run recipe**. Live: leftover → desk → attach-run → landing → `ops next`. Uncrewed parent `cli:`. Gene only `needing_go` / off-nominal plan. Depth 1. One control writer.

## Sequence

1. Wernher — unpin `test_protocol.py:145-200`; stop `tickets.py:1666` twins. Pad flies.
2. Wernher — `docs_inventory.py:345` classify; `FORBIDDEN_DISPATCH` + `docs/lessons.md`; git-mv ARCHIVE set. Pad flies.
3. Mortimer — PROTOCOL/BRIEF/AGENTS inject + 8 cards + `OPS.md:369` + portrait `lars.md:33` + `README.md:270`. No pulse `.py`.
4. Wernher — `infer_links` drop science/vab/blocks novel; kill `sync_shim` (`missions.py:192`); drop skim `jebediah` (`tickets.py:406`).
5. Mortimer+Wernher — NUKE spotter/sit-card/BOARD/builder. Pad flies.
6. Wernher — `desk.py:624` stop clip; unpin `test_desk.py:281`; retire mailbox `uplink.py:8-9` `main.py:755`; `GLOSSARY.md:31` tape-only.
7. Wernher — dest: `flightlog.py:246-249` `missions.py:103-104` `main.py:99-106`; how-to `BRIEF.md:63` `hank.md:122` `OPS.md:100` `tickets/README.md:26` `docs/flights/README.md:15`; `tickets.py:406,:424,:458` `house_dump.py:20-22`. Schema untouched.
8. Lars — compose ticket after 1–7. Not this first slice.

## Tickets to open later

1. `type=org` desk=mortimer — apply archive/card cuts (no new `docs/program` novel).
2. `type=systems` desk=wernher fingerprint `control-blocks` — inventory + packet skim + twins + **uncrewed dest writers**.
3. `type=control` desk=lars fingerprint `control-blocks` — one living rocket compose (after 1–7).
4. `type=systems` desk=wernher fingerprint `fly-science-ids-stale` — hop/pad stop parsing seated `science.md`.
5. `type=systems` desk=wernher fingerprint `desk-leftover-vs-krpc` — desk stop clipping `note-tech` **and** retire CLI mailbox.
6. `type=ops` desk=hank `--tag feedback` fingerprint `feedback-return` — parent inject vs CHARTER not-Return-keys.

## Do not touch

CHARTER creed, slate goal, portrait **voice**, jsonl schema, `desk.md` snapshot, learn-rsi `attach-run`, `ID_PREFIX` S/M/C, `hop_factory_pad.py`, pulse law this slice, GameData, `persistent.sfs`, TYPE zoo, restore spotter/Gene-merge/Batch Learn/`need_*`/Return keys, pad occupancy, depth 1, one control writer, `protocol fly` plan fallback this release (`OPS.md:6-8`; `protocol.py:132-135`), this plan as live `docs/program/*.md`.

### 12 How the next hire is cheaper

Cold child already skips AGENTS. After this slice the parent does too: **`desk.md` + `ops next` stdout + packet + BRIEF**. No 2872-line lessons. No BOARD. No last-flight-before-fly. No RSI papers. No 08-22 note-tech clip in the sit object. No `blocks.md` novel on a control packet — the third path is the helper file whose docstring is the law. Uncrewed dest matches `commander: none`. Lars **medium** so a pulse patch is not a cheap shrug. Fresh spawn; no `resume_from` of a 200k transcript. One finding on the work T-id. Pad occupancy continues on T-081 **only** when waste is not latched — living +0 still hires Linus, not last `cli:`.

### 13 Open risks

- **T-471 inbox** is pulse (`rf-ignition-ullage`), not this letter. Do not retune `hop_factory_pad.py` in the docs cut. Do not idle the pad for archive either — leftover is 0; waste latch is the occupancy gate.
- **T-468 / T-470** already RSI inbox (wernher / mortimer). This cutover is a **new** `type=org` apply ticket, not a hijack of rf-ignition ×8.
- Hop-exit `attach_run(..., who="wernher")` (`main.py:106`) still contradicts Learn `who=hank`. learn-rsi leftover; dest work (seq 7) must not forget it.
- `protocol fly` plan fallback stays one release. Dual plan craft **proc-long** vs hang **t7-wheel** can still lie if ticket `go` is empty.
- T-376 done; inland factory still **1052**. Compose is seq 8. Do not extract lid/chute “while we are in the files.”
- **0** live S/M/C. Cards already say M-NNN. Do not rename T-081.
- Roster missing Katherine is **not** `need_os` until Os adds a seat. Creed untouched.
- Tests pin poison (`Forest is 270`, lessons `## `, note-tech clip). Seq 1 before git-mv or the tree goes red and the pad waits a novel.

### 14 This workflow did not apply

Plan only. No file under `docs/` or `.grok/agents/` written. No tickets opened. No Hangar. No kRPC. No `persistent.sfs`. No CHARTER creed rewrite. No pulse `.py` retune. No `tickets.py` kernel patch. No job-card rewrite. No tests edit. Scratch is the host’s. The pad is still the product.

```
goal: bigger rockets, more Δv, farther out; bank 2.29 does not pay generalRocketry 20
org: hold
tickets: none
unlocked: none
need_os: none
```