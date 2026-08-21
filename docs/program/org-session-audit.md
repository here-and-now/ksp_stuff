# House session and interaction audit (as-is)

Two days of letsgrok (2026-08-20–21) on save `letsgrok` / `~/Games/KSP-rss` ran as a depth-1 star: Os talks, the unnamed parent sequences packets, Gene Grokman owns `go:`, Jebediah Grokman is the only kRPC writer, and ground desks last-write different files. Tree on disk is **start, engineering101, basicRocketry**. Board bank in [`docs/program/science.md`](docs/program/science.md) is **10.96** (need **~4.04** of survivability 15). Live [`docs/program/desk.md`](docs/program/desk.md) is **sci 13.2632**. Last-flight is `hop-splash` / `exit: 2` / `abort: ec=0`. Dual plan files disagree: seated [`docs/missions/jebediah/plan.md`](docs/missions/jebediah/plan.md) `go: yes` / `campaign: uncrewed` / `python main.py hop-splash`; shim [`docs/program/plan.md`](docs/program/plan.md) `go: wait` / `campaign: none` / `need_stack: hop-splash`. Session counts below are from child desk notes of `/home/os/.grok/sessions/%2Fhome%2Fos%2Fgits%2Fksp_stuff/` unless marked **disk**. Where notes conflict, disk wins.

---

## 1 Executive as-is

The house is **Os (Founder) → parent sequencer → one child**. PROTOCOL: “Parent is the room sequencer (depth 1).” AGENTS: “not a second Gene.” Children do not spawn. Gene last-writes seated `plan.md` / `briefing.md` and flight layers of [`docs/program/world-model.md`](docs/program/world-model.md). Mortimer chairs Practice, slate, PROTOCOL on a friction trip, and honest CTT spend. Jebediah is seated (`flight: jebediah`); Valentina is named capcom and never sat.

What the files show as work: Cape pad harvest (1235Z goo+thermo, sci **2.22**) → Flea hops (FlyingLow TELEMETRY, recovery@EarthFlew, sci **8.90**) → two CTT spends (`engineering101` 9.93→4.93, `basicRocketry` 6.13→1.13) → Cape Surface geiger **capped** 4.93→6.13 → FAR Flea lithobrake crumbs → Valiant/t7 FlyingHigh shorts (13-49 **+3.31**, 13-58 **+1.30**, bank **10.96**) → hop-to-water 13/13 **+0** (heading never 090) → hop-splash 11/11 **+0** (science skip / `ec=0`). After **13-58-18Z** the bank and tree do not move on the Gene/Linus/slate boards. Desk now files leftover `geigerCounter@EarthFlyingLow` 0.316 and `kerbalism_TELEMETRY@EarthFlyingHighForest` 1.512.

Volume on disk vs spawn table:

| Desk | Crew-log dated bullets (disk) | Sessions (child notes) | PROTOCOL hire rule on the wall |
|---|---:|---:|---|
| Gene | **86** | **83** | max two hires/sit; only `go:` |
| Jebediah | **67** (61 CLI) | **≥67** | exact CLI; lock live |
| Lars | **37** | **≥30** | miss / `need_stack` |
| Linus | **33** | several bind/opportunities | bind after `capable: yes` |
| Gus | **24** | **19** | `capable:` / `.craft` |
| Mortimer | **10** | **8** | CTT / 3+ I- / Os org |
| Verena | **6** | **5** (all 20 Aug) | firsts / `need_pr` |
| Wernher | **2** | **1** Grokman | XOR Lars, kRPC trap |
| Walt | **1** | **0** | TUI voice, no hire |
| Val / Bill / Bob / Grok | **1** each | 3 / 0 / 0 / 6 (Val+Grok = 19 Aug Mun) | not seated |
| Spotter | none | **14** (19 Aug only) | “Do not spawn” |
| Parent | **MISSING** | sequencer, not a spawn type | depth 1 |

Gene log `go:`: **36 yes / 38 wait** (12 bullets have no `go:`). Jeb CLI exits: **23×0, 37×2, 1×4**. Helm `note-tech.md`: **44** dated lines, all Jebediah, 39→Lars / 4→Gus / 1→Wernher. `docs/lessons.md`: **52** `##` headings, newest **2026-08-21T18-15-08Z-hop-splash**. Fourteen reviews still `_Gene fills this.` including eight hop-splash after Gene’s last Learn. Live improve I-012–I-020: **5 accepted, 4 open**. Gym F-001–F-015: **8 accepted, 7 open**. Open questions: **20/20** stamped answered 21 Aug.

---

## 2 Per-desk session compile

### Gene Grokman, Flight Director

`subagent_type: gene`. Voice: “quiet chess player” ([`docs/crew/gene.md`](docs/crew/gene.md)). Thesis: “The log can lie. The still and the **jsonl envelope** (`heading` / `horiz` / pitch) have to agree before `go:`.” Niche still open: “Honest path to survivability 15. Bank 10.96. Need ~4.04. Water is dead on Stayputnik+Valiant+tank fins” ([`docs/crew/niche/gene.md`](docs/crew/niche/gene.md)).

Does: dossier, briefing, `go:` (max 2 hires/sit), chairs flight world-model, `need_stack` / `need_builder` / `need_science`, one stuck PNG. Does not: `control.*`, `.py`, `.craft`, PROTOCOL, poll, seat while lock live.

Sessions: **83** `agent_name: gene` (2026-08-20T15:21Z `01a01fc3` through 2026-08-21T18:26Z `01a02593`). Example merge packet (`01a02593`): `to: Gene Grokman, Flight Director` / `from: parent` / `live_run: none` / `lock: free` / `task: hop-splash already recovers leftover wreck/PRELAUNCH ghost then Hangars t7-splash; Lars starts TELEMETRY PAW + Goo at splash.` / `read: desk.md ; blocks.md ; science.md`. Same-hire multi-packet: `01a0216c` (20 Aug) took sequential packets in one session (Os go → Linus bind → 18-02 miss → SpaceCenter leftover → 18-22 miss → 18-32 clean → max Start harvest → pad-card → pad misses → Os “no Geiger part” → TELEMETRY hop → `engineering101`).

Crew log **86** dated bullets. Named `need_stack` (13 log lines): `hop`, `hop-jsonl`, `splash`, `pad-card`, `pad-geiger-hangar`, `tech-unlock`, `hop-hammer-hangar`, `hop-flyinghigh`, `hangar-flight-results`, `hop-splash`. `need_builder` 12 lines, `need_science` 13. No `need_mortimer` / `need_pr` token. CTT lines: “Call engineering101 (5). No buy CLI. need_stack tech-unlock.” “Mortimer bought engineering101.” Last log line is merge hop-splash PAW, `go: yes`, `python main.py hop-splash`. Gene log and seated `go: yes` stop at **18-15**; later hops have no new Gene Learn.

**20 Aug (pad / first hop / 72 m).** 1235Z pad dwell 740 s recovered, sci **2.22**; F-002, F-005; `go: wait`. Os continue hop; conference “hop does not Hangar the Flea”; `need_stack hop`. 15-58 leftover flying **73 m EC=0**; 16-24 no-science leftover; 16-36 crash UI; 17-02 leftover recover exit 0, sci still 3.20. F-006: disk empty vs live leftover. 72 m still is leftover wreck. Os drums **002423** / KER **2,380.7 m** (Verena log: Gene first read **002123** / **2,090.7**). `need_stack hop-jsonl`. 18-32 clean **3.20 → 3.70**. Sequential harvest pad geiger → Flea TELEMETRY → splash. Os “no Geiger part” killed pad-geiger. 20-55 hop **3.70 → 8.90**. Mortimer bought `engineering101`. 22-20 Cape geiger **4.93 → 6.13** capped. 22-56 Hammer OFFPLAN 18.8 km. 23-13 landed TELEMETRY **2.33 → 2.43**.

**21 Aug (FAR Flea → Valiant → Water → splash).** Merge Gus `kspstuff-hop-flea-pbc`, Linus FlyingLow geiger recover-HD, `go: yes` `python main.py hop`. 10-30 dismiss-lied recover; 10-42 living recover **+1.13**; lithobrake / crash UI string; campaign stamp `uncrewed`; “Os did not ask to continue” → `go: wait`. 13-31 t7 apo **88.8 km** splash **+0**; 13-49 **+3.31**; 13-58 **+1.30**. Bank **10.96**. Water merge then hop-to-water all **+0**. “Water dead on this hang.” Merge splash: Gus `t7-splash` vertical; Linus splash TELEMETRY then goo; `need_stack hop-splash`. Last Gene Learn 18-15: envelope **heading 228 horiz 62 pitch 13 biome Forest — not Water**.

World-model Open questions: 20 rows; Gene wrote or answered most on 21 Aug. Improve he filed: I-012 accepted, I-019 open. F-002, F-005, F-006 accepted from Gene. I-016 and I-020 describe Gene Learn idle and last-flight-as-heading.

### Gus Grokman, VP Build

Owns `.craft`, [`docs/program/vab.md`](docs/program/vab.md), `capable:`. Gene decides. Never fly, Hangar, uplink, `.py`. Thesis: “Batteries are a religion. Hang is not batteries. `capable: no` is a design.” kRPC: “kRPC has **no VAB placer.**”

Board now: `capable: yes`, `craft: kspstuff-hop-valiant-t7-splash-pbc`, 24×Z-100, 7×FL-T100, Valiant Boattail, 3× basicFin on engine, no chute, no RW. `crafts/` has **11** `kspstuff-*.craft`. `crafts/stock` **MISSING**. `kspstuff-pad-pbc` is a `craft.py` template, not a file under `crafts/`.

Sessions: **19** (`12` subagent, `7` resumes of one 20 Aug splash-craft chain). Crew log **24** dated (14 on 20 Aug, 10 on 21 Aug). Three explicit `capable: no` sign lines on 20 Aug (thermo hang / 0.5 MB tape, locked instrument F-013, 497 s FlyingLow). Every 21 Aug line is `capable: yes`.

Craft ladder signed: pad-pbc (template) → hop-flea-pbc → geiger-pbc → hop-hammer-pbc → hop-hammer-far-pbc (vab stayed flea) → hop-valiant-pbc → t7-pbc → east-pbc → east-bare → east-one → east-fin → t7-splash (then 24×Z-100 after 17-46 `ec=0`). F-010 accepted from Gus. I-013 open (`from: Gus`; hop Hangar substring `geiger-pbc`). Reviews: grep `Gus|gus|VP Build` → **0** matches. Jebediah → Gus `note-tech`: 4 lines (14:37–17:00Z).

### Linus Grokman, Director of Research

Owns [`docs/program/science.md`](docs/program/science.md) and seated [`docs/missions/jebediah/science.md`](docs/missions/jebediah/science.md). Horizon layer. Briefs Gene. Does not fly, Hangar, uplink, note, brief the Commander, or edit `.py` / `.craft`. Working goal on the job card: **15 sci**. Bind only after Gus `capable: yes`.

Crew log **33** dated (19 on 20 Aug, 14 on 21 Aug). First: “Earth/PBC. Kerbin hop card dead.” Last: bound t7-splash splash pair TELEMETRY 30/0.052/0.80 then goo 641/0.18/2.40, pair **3.20 — 0.84 short**. Horizon still matches that bind (bank 10.96). Live desk is **13.2632**. `science.md` still says “Live `sci = 10.9586` (desk).” Board and desk are not the same sit.

`need_builder` on Linus log **6** times (opportunities, no bind). Gus log: **0** “Linus”. Lars log: **0**. `note-tech.md`: **0**. Reviews: **0** Linus. Gene log names Linus on ~20 of 86 lines. World-model asks involving this desk: 4 rows, all **merged** 21 Aug.

### Lars Grokman, Vehicle Engineering and Wernher Grokman, Avionics

Lars owns block *code* and [`docs/program/blocks.md`](docs/program/blocks.md). Misses only, or Gene `need_stack`. Voice: “forensic novelist. Timeline, then one cause, one file, stop.” Catalog phases: `pad`, `hop`, `splash`, `hop-to-water`, `hop-splash`, `tech-unlock`. Crew log **37** dated (desk notes said 38; disk is 37). Last: hop-splash Hangar t7-splash vertical, leftover east-fin PRELAUNCH recover dark, Flea refused. Sessions: **≥30** child `system_prompt` “You are **Lars Grokman, Vehicle Engineering**.” `docs/lessons.md` **52** headings; modules named include `hop.py`, `pad.py`, `splash.py`, `science.py`, `telem.py`, `hangar.py`, `phases.py`, `main.py`, `catalog.py`, `craft.py`, `missions.py`, `flightlog.py`, `tech_unlock.py`, `recover_probe.py`, `blocks.md`. After 18-15: **0** further dated lesson headings. Jeb `note-tech` to Lars continues through 19:51Z.

Wernher: thesis “If it is not AttributeError / StreamError / protobuf / `get_services`, it is Lars.” Log **2** lines, both 20 Aug: disk briefing [`docs/program/krpc.md`](docs/program/krpc.md), `autoStartServers=False`, “No trap this pass.” / “letsgrok. No trap this campaign. Standing by.” One Grokman session `01a020cd`. Filed F-011 (open). Live `lessons.md`: **0** Wernher matches. Jebediah wrote him once (`note-tech` 10:28Z, kRPC ports refused); Wernher log has no 21 Aug line. Five older `You are **Wernher von Kerman**` sessions are Mun-era. XOR held: no dual lesson on one miss.

### Jebediah Grokman, Commander (and the rest of the fly roster)

[`docs/program/current.md`](docs/program/current.md): `flight: jebediah`, `pilot: Jebediah Grokman`, `capcom: Valentina Grokman`. INDEX lists one mission id `jebediah`, next **hop-to-water**. Seated plan phase **hop-splash**. Shared fly card `.grok/agents/pilot.md`. Early sessions: “You **are Jebediah Kerman**” + `ksp-pilot.md` (**7**); later “You **are Jebediah Grokman, Commander**” (**62**). Sessions `agent_name: jebediah` **≥67**. Latest sampled: `01a025d9` 19:43Z “KSC hop-splash hangar t7 vertical loft”.

Crew log **67** dated (desk said 69; disk 67). Six Os/seat narrative lines + **61** CLI: hop **25**, pad **7**, load **3**, ksc **2**, hop-to-water **13**, hop-splash **11**. Exits **23×0, 37×2, 1×4**. Abort strings on the 37+1: not recoverable 13; Hangar waits / Flight Results `can_revert` 4; not splashed 5; no science (wanted kerbalism_TELEMETRY…) 5; `ec=0` 2; abort/abort_pad 4; timeout 1; MET frozen, empty HD 2; recover 1; OFFPLAN apo 18858 > 18000 1.

Flight tape: **66** `*-review.md`, same six sections (`Envelope`, `First / last`, `Flag changes`, `Events`, `Handoff`, `Learn`). **14** still `_Gene fills this.` Compact-stamp pads `1101Z`/`1119Z`/`1136Z` exist as reviews and are not in the dated crew-log CLI list. Seven jsonl files have no matching review (desk note): `18-15-04Z-hop`, `20-02-16Z-pad`, `20-27-04Z-pad`, `11-55-40Z-hop`, `18-56-58Z-hop-splash`, `19-14-03Z-hop-splash`, `19-16-34Z-hop-splash`.

Valentina log: “letsgrok. Not seated. Ready when Gene names her.” Three sessions **19 Aug** Mun. Grok: “No flights.” Six sessions **19 Aug** `mun --from-orbit`. Bill / Bob: “Not seated. PBC: probes first.” Zero `agent_name: bill|bob` summaries.

### Mortimer Grokman, CEO

Owns goal / slate, Practice, PROTOCOL and job cards on a friction trip, honest CTT spend (`persistent.sfs` ResearchAndDevelopment only → `rd-<node>.sfs` → `python main.py load rd-<node>`; never `load persistent`). Does not fly, Hangar, write GameData, rewind UT, or patch `.py` (`need_qol` → Lars). Gene owns `go:`. CHARTER (Os 20 Aug): “Mortimer Grokman, CEO may edit `persistent.sfs` **only** to spend banked science… **Os is not asked.**”

Crew log **10** dated (desk slot 5 said 12; disk 10). Sessions **8**: `01a0210f`, `01a02116`, `01a0211d`, `01a02152` (CTT + asteroid `ksc`); `01a02350` (RSI I-001–I-011, **no org return** in transcript); `01a0242a` (I-014/I-016, `org: patched`); `01a02451` (15-sci slate, closed I-015); `01a02579` (I-020). Two CTT spends: engineering101 sci **9.92548084→4.92548084**; basicRocketry **6.12557697→1.12557697**. Both named loads reseated **Ast. XRL-564** (F-015); `ksc` both times. `load persistent` once wiped the spend (F-014). Live Open questions: **no Mortimer row**. `note-tech.md`: **0**. Reviews: **0**.

### Verena, Walt, Spotter, parent

Verena: log **6** lines, all 20 Aug. Five sessions. Four press stories (INDEX: potato 4.93, five-in-bank 8.90, two kilometers 3.20, Cape Goo 2.22) and README hangar front. Drums **002423** / KER **2,380.7 m**. **0** Verena sessions 21 Aug. Walt: one log line “CAPCOM on phase edges.” **0** sessions. No `.grok/agents/walt.md`. Spotter: job card still on disk, “DEPRECATED. Do not spawn.” Fourteen `ksp-spotter` sessions **19 Aug only**. Parent: no crew portrait, no spawn type, no `docs/crew/log/parent.md`. Files packets, `I-NNN`, Open questions, F-comments; copies Gene `recommended:` as Commander `cli:` (F-004); re-desks after Gus capable (I-014); speaks as Walt on phase edges. One review mentions parent wall-clock (`2026-08-21T12-22-36Z-hop-review.md`: “90 s (parent ~165 s) vs 12-04 ~329 s.”).

---

## 3 Pain and recurrence

### Quoted pain (path → line)

**Log vs still vs leftover.** Gene: “The log can lie” / “72 m was a leftover, not a hop” ([`docs/crew/gene.md`](docs/crew/gene.md), niche). F-006: “world disk said empty KSC / sci 3.20 while live leftover hop still flying 73 m EC=0.” I-019 (open): “leftover hop-flea vs seated valiant — python main.py hop still enters the flea.” 14-52 Gene: “stuck still: Flight Results still up, Tracking no vessels. Hangar waits. Do not Hangar from Gene.” I-017 (open): “desk leftover FLYING debris while Tracking search is empty.”

**Recover is not dismiss.** 10-30 lesson: “Dismiss is not a living recover.” 11-09: `recover()` in Flight, not after dismiss. 12-04: “Catastrophic never lands.” F-007 (open): “dwell hung. Catastrophic Flight Results paused physics; recoverable never true; HD not recovered.” Os F-007 comment: “Escape hid the crash UI by accident. Next stuck: no Os click.” PROTOCOL: “Disk cannot see crash UI (`scene: unknown (disk)`).” `recover-sit` / `recover-pad-again`: `recover()` then Space Center is a launch-save reload (`pre_launch` MET 0 `can_revert_to_launch=True`). “Not `revert_to_launch` (never called).”

**F-013 Stayputnik-as-Geiger.** Os F-013: “Linus bound Stayputnik PAW `geigerCounter`. Gus signed it as hardware. Gene `go: yes` pad geiger. Lars spent the miss chain on MET/dry-launch for a Geiger Counter we have not unlocked (`engineering101`).” Linus: “I bound PAW geigerCounter without saying the Geiger part is engineering101 LOCKED.” Gus: “I knew PAW ≠ part (F-010) and still let a geiger sit fly. capable: no when the instrument is LOCKED. Lars never got the tree.” F-010: “vab/science signed ‘the ship has a geiger’ — Os saw no Geiger Counter part.” 22-11 helm Toggled Stayputnik PAW, skipped the Geiger Counter part. 18-15 inverted it: “science skip (no Experiment modules)” then ABORT wanted `kerbalism_TELEMETRY`.

**Card vs hang vs bank.** F-005: “another identical Cape pad will sit 12 min for science we may already have”; later “run_pad ignores seated card.” F-009 (open): “leftover thermo is hang not EC… Do not brief 75 s as finished leftover thermo.” Gus: “Do not sign a 75 s hop as 497 s.” / “Hang is the wall: 50 km lid ~202 s… Flea 75 s, Hammer 15 s.” Gene: “Gus no: 497 s FlyingLow vs 50 km lid. Linus unbound.” I-012: “Linus board sci 2.43 vs desk 2.9559 on the same sit.” I-018 (open): leftover-science hides unstarted REACH. Linus: “Scan hid other biomes behind Shores capped.” F-001: “Gus signed one Z-100; goo dwell needed ~310 EC.”

**Heading never 090 / jsonl vessel frame.** 14:37 Jeb→Lars: “jsonl has no biome/lat/lon/heading; speed=0 all samples.” Lesson 16-14Z: “jsonl speed=0 is the vessel frame.” 16-33 / 16-57: heading never holds 090. I-020: “Gene Learn / bind / miss from last-flight prose; heading never 090 looked like skill.” Gene 16-57: “Wheel stability LOCKED. leftover PRELAUNCH after Close is a ghost.” Jeb→Gus 16:36: “Need fins or a wheel.” 17:00: “Need a reaction wheel.”

**Splash EC=0.** 17-46 Gus: “ABORT ec=0 before science… 10× emptied in loft (~1.9/s).” 19:51 Jeb→Lars: “Briefing said dwell may start EC=0; gate still abort.” Last-flight: `science start kerbalism_TELEMETRY` then `sit=splashed` then `ABORT ec=0`. No lesson heading after 18-15.

**House serial / spawn tax.** I-016: “pad stands still between hops while Gene Learn / Lars / merge run.” F-002: “parent still hired Vehicle Engineering after exit 0.” I-014: “desk.md still capable: no / craft none / f013 none after Gus signed.” F-004: “Commander guessed phase pad vs python main.py pad.” ORG.md: “Spawn tax… Clean 1235Z still hired Lars.” ORG-INTERACTIONS: “spawn tax of one full LLM hire per desk (measured ~2 min).” SPEED: “The loop works. It is slow because Gene is hired as a **merge bus** after every specialist.” PROTOCOL: “Gene **max two hires per sit**” next to **83** gene sessions / **86** log lines in two days.

**CTT / load.** F-014 (open): “`SpaceCenter.load(\"persistent\")` writes the in-memory game onto persistent.sfs before reading disk — the RD spend vanished until a named file was loaded.” F-015 (open): “`SpaceCenter.load(\"rd-engineering101\")` restored Flight on **Ast. XRL-564** around the Sun.” Repeated on basicRocketry. After `ksc`: “`status` died at KSC (`vessel.flight()`).” F-011 (open): disk `autoStartServers = False`; notes had True.

**I-013 substring.** Gus: “hop Hangar refuses any name containing geiger-pbc, so the part rides hop-flea.”

### Recurring patterns the files already name

- **Packet loop:** miss → Lars patch → parent hires Gene Learn → `need_*` → specialists without Gene → Gene **merge** is the only `go:`. Uncrewed `campaign: uncrewed` left on for re-fly; stop flips `campaign: none` and often `go: wait`.
- **Leftover vs Hangar is Gene’s gate:** matching PRELAUNCH → light, do not Hangar; unmatched / ghost Close-reload → recover without lighting, then Hangar seated craft; flying wreck / crash UI → do not Hangar from Gene; dead GUID / empty Tracking is not leftover.
- **Envelope over prose:** Learn cites jsonl `heading`/`horiz`/pitch after I-020. “Heading never 090 is Water-dead, not ‘flew poorly.’”
- **Do-not list on every Gene return:** Do not pad / hop / hop-to-water / Hangar / revert / fly Flea / Toggle Cape geiger — then the next sit names the one CLI.
- **Sign, fly, re-sign.** Parent hires Gus after `need_builder` or Jeb `note-tech`; Gus writes a new `kspstuff-*-pbc.craft`, last-writes `vab.md` `capable: yes`. Next abort produces the next named variant.
- **Two-pass science:** opportunities + `need_builder`; bind only after `capable: yes`; unbind when hang/tree/heading cannot finish (86 s thermo, PAW geiger, 497 s lid, Water 090).
- **One Toggle per id; do not co-run geiger with TELEMETRY;** splash TELEMETRY first then goo.
- **Recover voodoo:** each lesson heading patched one fingerprint; the next sit grew a new one (MET vs wall-clock; dismiss vs `recover()`; crash UI Close vs Space Center reload; Flight Results vs KSC; jsonl vessel-frame zeros; EC=0 as abort before science start).
- **f013** copied into briefing (instrument + tech + unlocked + on_craft). Missing f013 = wait.
- **Cape spent (F-005):** after 1235Z, no re-pad of landed goo+thermo.
- **Crumbs vs node:** leftover geiger 0.32, thermo 0.045, recovery crumbs skipped. Working gap ~4.04 toward 15. “Flea lithobrake is not a node.”
- **Hire is mutation, not chat** (Mortimer). Four completed org returns `org: patched`. First RSI spawn `01a02350` tasked I-001–I-011 and left no return.
- **Verena on firsts only** (pad Goo, first hop, first 5-sci, first unlock), then correction when the still contradicted the 72 m headline; not after every pad; not on 21 Aug.
- **Ground conference on different files.** Gus: `vab.md` + `crafts/` + log. Linus: `science.md`. Gene: `plan.md` / `briefing.md` / Meaning. Parent re-desks (I-014). Children `agents_md: false`.

---

## 4 Interaction graph and chain of command

The house is a **depth-1 star**. Only the parent calls `spawn_subagent`. Job cards: “You do not spawn.” PROTOCOL: “They do not spawn each other.” Ground desks are parent hires, not Gene’s children.

```
Os ──talk-by-name──► named desk          (voice; no spawn)
Os ──go / fly / science──► parent ──► Gene
Os ──PR / README──► parent ──► Verena
Os ──org / RSI / 3+ I-──► parent ──► Mortimer

Gene return
  need_science  ──► parent ──► Linus
  need_builder  ──► parent ──► Gus
  need_stack    ──► parent ──► Lars
  need_mortimer ──► parent ──► Mortimer   (CTT or org)
  need_pr       ──► parent ──► Verena
  go: yes + capable + phase in blocks.md
                ──► parent ── protocol fly: yes ──► Commander
specialists return ──► parent ──► Gene merge (only go:)

Commander clean 0 + campaign: uncrewed ──► parent re-spawns Commander (no Gene)
Commander miss (nonzero / ABORT / science none / sci unchanged)
                ──► parent ──► Lars ── (stack: ok AND kRPC trap) ──► Wernher
                ──► parent ──► Gene
Mortimer need_qol     ──► parent ──► Lars
Mortimer need_builder ──► parent ──► Gus
Mortimer / Gene need_os ──► Os (ratify; not a spawn)
```

Packet fields (PROTOCOL Spawn packet): `to` name+title, `from: Os | parent`, `live_run`, `lock`, `task` one sentence, `read: desk.md + ≤2 role paths`, `cli` exact or none, `return` the named block. Helm `cli:` is Gene `recommended:` copied verbatim (F-004). Missing `go:` = wait. `go: wait` with `need_*` = spawn those desks. Missing `f013` on bind / capable / `go:` / Lars miss = wait.

CHARTER conference (serial, different files): Linus opportunities → Gene draft (`go: wait`) → Gus `capable:` → parent **re-desks** (I-014) → Linus **bind** → Gene briefing + `go:`. Legal parallel: Linus opportunities ∥ Gus `capable:` (not bind); Linus opportunities ∥ Lars `need_stack`. Not parallel: two Commanders; Gene + flight; Lars on a clean 0.

**What actually fired (20–21 Aug, logs + packets):**

1. Os go → Gene draft → specialists without Gene → Gene merge → `protocol fly` → Jeb. Hop conference: hop in catalog, Gus capable, Linus bound, then `need_stack hop` (`go: wait` until Lars wrote the block).
2. Gene `need_stack: <name>` → parent → Lars → Gene again. Ten named blocks listed in §2.
3. Gene `need_builder` + `need_science` together on harvest / Water / geiger-part sits → Gus sign + Linus bind (bind after capable), then Gene merge.
4. Miss loop: Jeb abort → parent → Lars (one `lessons.md` heading + `.py`) → Gene Learn/`go:`. Wernher never took a trap handoff.
5. Uncrewed campaign (I-016): Gene first `go: yes` + `campaign: uncrewed`; parent re-flies last `recommended:` on clean 0 **without Gene**. Stop flips `campaign: none`. After 18-15 that stop did not happen: hop-splash kept flying with Gene’s last `go: yes` still on the seated plan.
6. CTT: Gene wrote “Call engineering101” / `need_stack tech-unlock`; parent spawned **Mortimer** (Os-ratified RD edit), not a Gene `need_mortimer` token. Same for `basicRocketry`.
7. Commander → tech is a file, not a spawn: `note-tech.md` (44 lines, all Jebediah). Parent files / Gene reads between exits.
8. `ask:` is a table, not a spawn: parent files Open questions; one reply hire only if the ask **blocks `go:`**.

Forbidden edges written on the wall: Linus ↛ Commander. Gus ↛ Hangar. Commander ↛ `.py`/`.craft`. Gene ↛ stick while lock live. Parent ↛ patch `.py` in the fly turn. Children ↛ spawn. Spotter ↛ spawn. Walt TUI | no hire. Mortimer ↛ GameData / flight/UT in the save. Never revert.

### `need_*` on disk vs PROTOCOL table

| Key | PROTOCOL From → To | Crew-log hits (letsgrok) |
|---|---|---|
| `need_science` | Gene → Linus | **13** (all Gene) |
| `need_builder` | Gene → Gus | **18** (Gene 12, Linus 6). Gus/Lars/Mortimer/Jeb **0** as the token |
| `need_stack` | Gene → Lars | **13** (all Gene) |
| `need_gene` | — (not in PROTOCOL table; job-card return) | **0** |
| `need_mortimer` | Gene → Mortimer (CTT); any desk → Mortimer (`org`) | **0** |
| `need_qol` | Mortimer → Lars | **0** in crew logs (15-sci hire returned `need_qol: hop.py` in session notes) |
| `need_os` | Mortimer / Gene → Os | **0** in crew logs |
| `need_pr` | Gene → Verena | **0** |

### Open questions `from` | `to` (20/20 answered 2026-08-21)

| from | n | to | n |
|---|---:|---|---:|
| Gene | 6 | Gene | **10** |
| parent | 3 | Gus | 6 |
| Gus | 3 | Linus | 2 |
| Linus | 3 | Lars | 2 |
| Lars | 2 | | |
| Jebediah | 2 | | |
| Os / Lars | 1 | | |

Zero rows to or from Mortimer, Verena, Walt, Wernher, Bill, Bob, Valentina, Grok, Spotter. Parent is `from` on 3, never `to`. Commander PROTOCOL: “The Commander never `ask:`s” — Jebediah still has **2** table rows (recover line → Lars **done**; heading never 090 → Gene “**fins failed.** … Water dead.”).

Dual disk plan: PROTOCOL “Gene last-writes plan/briefing”; job card owns **seated** plan. Shim [`docs/program/plan.md`](docs/program/plan.md) still `go: wait` / `need_stack: hop-splash`. Seated plan `go: yes` / `need_stack: none`. `protocol.py` `fly_gate` reads the **seated** file.

---

## 5 Bottlenecks and waits

The pad sat still more often than it flew. CHARTER / PROTOCOL / SPEED / NEXT-ORG name the same conference: Linus opportunities → Gene draft (`go: wait`) → Gus `capable:` ∥ Linus tree (not bind) → parent re-desk (I-014) → Linus bind (serial) → Gene merge (only `go:`) → `python main.py protocol fly` → Commander with `flight.lock` live.

**Spawn tax (files).** ORG.md: “Spawn tax. Stack-after-every-0 plus Gene-after-every-exit turns a 9 s pad into two multi-minute hires. Clean 1235Z still hired Lars.” ORG-INTERACTIONS: “spawn tax of one full LLM hire per desk (measured **~2 min**)”; six explorers 102–162 s; “Gene, then Lars, then Gene after a clean recover is **~6 minutes of models** around a 9 s physics sit.” SPEED target on the wall: “5–7 Gene/sit → 1 draft + 1 merge.” PROTOCOL: “Gene **max two hires per sit**.” Gene 86 log lines / 83 sessions in two days.

**Serial hop table (ORG-INTERACTIONS 3.2).** Os go with prior `need_*`: 2 layers. No prior: 3. New pad builder+science: 3–4. Fly: 1 (no Gene). Clean Learn: 1 Gene. Miss: 2–3. Paid CTT: **6–7**. `ask:`: unbounded until that desk’s next real hire. ORG-INTERACTIONS: “`ask:` without receipt — world-model answers not copied onto the addressee’s next packet.”

**I-016 pad idle.** Os: “pad stands still between hops while Gene Learn / Lars / merge run.” Accepted: uncrewed campaign — first Gene `go: yes` + `campaign: uncrewed`; parent re-flies last recommended on clean 0; batch Learn at stop. `protocol fly` still gates. Pre-rule ORG.md pad loop: Os go → Gene → Jeb pad → **Lars after every exit (even 0)** → Gene again. F-002 records that hire after 1235Z exit 0.

**Lock live.** [`docs/program/flight.lock`](docs/program/flight.lock) is the writer wall. While live: no Gus / Linus / Gene; no `status` / `python main.py science` (second Session); parent does not swallow 1 Hz. Commander owns throttle/AP/stage. 19:22Z note-tech: “stale lock took leftover flying MET~428.” Desk now `lock: free`. Mid-phase Os “how’s it going?” is `ship.md` as Walt — no hire.

**`protocol fly` wait reasons (code, in order):** missing `go: yes`; lock live; hangar `blocked`; hangar `recover …` leftover; `phase` not in `blocks.md`; `capable` not yes (**pad/hop only**); no bound card (**pad/hop/splash only**); f013 `unlocked=no` or `on_craft!=yes`. `hop-splash` is in `NAMES` but not `_HANGAR_PHASES` and not in the card-id set, so capable/empty-card are not those waits. Last abort is not a gate field. Gate reads seated plan, not the shim. Current last-flight abort `ec=0` is not a fly-gate field.

**CTT spend wait.** kRPC 0.6 has no UnlockTech. Gene `need_stack tech-unlock` then Mortimer RD edit → `load rd-<node>` (never `load persistent`, F-014) → asteroid seated (F-015) → `ksc` → Gene “Wait Os reload letsgrok. Then Gus + Linus. `go: wait`.” Two spends, 6–7 child layers each.

**Leftover vs Hangar waits.** Matching PRELAUNCH → light. Unmatched / ghost → recover dark then Hangar. Flying wreck / crash UI → Hangar waits. 14-52 Flight Results over Tracking: Hangar raises `Hangar waits`, Close until KSC and `can_revert` false (~53 s timeouts in note-tech). 19-24 leftover LANDED Forest: Jeb waited **~17 min** sit=landed then uplink recover. I-019 still open: leftover flea vs seated valiant.

**Bind-after-capable.** SPEED: “Linus bind after `capable: yes`.” NEXT-ORG: “that extra serial hop is the F-013 honesty tax.” I-014: desk stayed `capable: no` after Gus signed until parent re-desked.

**Physics / Hangar / Session waits quoted:**

- 1235Z pad dwell **740 s**; I-016 friction is the gap *between* those hops.
- Catalog: geiger **497 s**, goo **641 s**, TELEMETRY **30 s**.
- 10-47-59Z: “Frozen-MET unpause only after **600s** timeout”; recover() never.
- 12-04-13Z: “Logged wait landed … then still flying recoverable=no **~250s**.”
- Hangar: `go_space_center` ≤45 s; `launch_vessel` 25 s watchdog; `wait_vessel_ready` ≤30 s (ORG-INTERACTIONS 3.3).
- 15:20Z: “Close timed out **~53s**, no `launch_vessel`.”
- First `status` connect **~30 s** schema; `status` died at KSC (`vessel.flight()`).
- 10:28Z: kRPC 50000/50001 **refused** (SESSION).
- 18-02 leftover Flea at SpaceCenter: SESSION until Lars scene-enter.
- Gene 20 Aug: “Wait Os reload letsgrok.” “go: wait until Os says fly.” 11-47: “Os did not ask to continue. go: wait.”
- Missing `go:` = wait. Missing `f013` = wait. Disagreement → Gene `go: wait`.

**Reviews after last Gene Learn.** 14 `_Gene fills this.` including hop-splash **18-08, 18-28, 18-38, 18-45, 19-04, 19-21, 19-24, 19-43** (last abort `ec=0`, sit splashed). Seated `go: yes` / `campaign: uncrewed` still on that CLI. `docs/lessons.md` stops at 18-15. Jeb `note-tech` continues through 19:51Z.

---

## 6 Absences and frequency

### Talk frequency (disk)

| Slug | Dated bullets | 20 Aug | 21 Aug | Last line |
|---|---:|---:|---:|---|
| gene | **86** | ~50 | ~36 | Merge hop-splash PAW, `go: yes` |
| jebediah | **67** | 24 | 43 | 19-43-18Z hop-splash `ec=0` |
| lars | **37** | 22 | 15 | hop-splash Hangar t7-splash |
| linus | **33** | 21 | 12 | Bound t7-splash splash pair |
| gus | **24** | 14 | 10 | 24×Z-100, `capable: yes` |
| mortimer | **10** | 6 | 4 | I-020 jsonl envelope |
| verena | **6** | 6 | **0** | Cape story sci 2.22 |
| wernher | **2** | 2 | **0** | “No trap this campaign. Standing by.” |
| walt | **1** | 1 | 0 | “CAPCOM on phase edges.” |
| valentina / bill / bob / grok | **1** each | 1 | 0 | not seated / no flights |
| parent | **MISSING** | — | — | no `docs/crew/log/parent.md` |

The fly loop on letsgrok is **Gene–Jeb–Lars**, with **Gus** and **Linus** on other files between exits. Mortimer chairs Practice and two CTT spends, not `go:`. Linus never talks to helm (CHARTER: “Linus has **no** `uplink` / `loop` / `note` to the Commander.”). Gus 24 log lines, 0 review hits; Jeb’s four east notes are the only Commander→Build path.

**note-tech addressees:** Lars 39, Gus 4, Wernher 1. **Never** Gene, Linus, Mortimer, Verena, Walt, Val, Bill, Bob, Grok.

**Reviews:** 66 files. Sampled headings never name Gus, Linus, Mortimer, Walt, Wernher. Verena appears in Gene Learn on 15-58 and 17-02 only. **14** Learn stubs.

**I-012–I-020 `from:`:** Gene 2, Linus 2, Gus 1, Lars 1, Jeb 1, Os 1, Mortimer (Os: more data-driven) 1. Open now: I-013, I-017, I-018, I-019 (count **4**; Mortimer trip threshold is **3+**). Mortimer log: “I-013/I-017 hop.py → Lars.”

**F-001–F-015 From:** Jeb 4, Gene 3, Lars 2, Mortimer 2, Linus 1, Gus 1, Wernher 1, Os 1. Retro `notes/` exist for gene (6 bullets), jebediah (2), and empty headers for gus/lars/linus/mortimer/verena. **MISSING** notes for walt, wernher, bill, bob, valentina, grok, parent, spotter.

### Never spawned this program (20–21 Aug)

Bill, Bob, Walt: no `agent_name` sessions, no Open-questions row, no note-tech, no I-/F- from them. Walt has **no** agent card. Spotter: zero 20/21 Aug summaries.

### Rostered, not letsgrok

Valentina and Grok: 19 Aug Mun sessions and one 20 Aug “not seated / no flights” line. `current.md` still prints `capcom: Valentina Grokman`. No `docs/missions/valentina/` or `grok/`. No grok niche file.

### Spawned once, then idle

Wernher — disk `krpc.md`, F-011 open, XOR with Lars held (`docs/lessons.md` has **0** Wernher headings). The 10:28Z kRPC-refused note produced no Wernher lesson. Verena — four press stories + README on 20 Aug firsts; **0** 21 Aug sessions while bank went 2.43 → 10.96 (board) and Water died.

### Tokens that exist on cards and never appear in crew logs

`need_gene`, `need_mortimer`, `need_pr`, `need_qol`, `need_os`. Two CTT spends were **parent (Os ratified)** packets. Verena hires were firsts / Os, not `need_pr:`.

### After 18-15

Gene log stops at hop-splash PAW merge `go: yes`. Lars log last line is hop-splash catalog. Lessons stop. Eight hop-splash reviews stay `_Gene fills this.` Jeb `note-tech` continues: airborne TELEMETRY vs wait-splash, `Part.get_Name` NRE ~T+288, leftover LANDED Forest dry fire **19-24**, splash EC=0 **19-43**. I-016 uncrewed re-fly ran those hops without a new Gene Learn. That is silence from the `go:` desk, not from helm.

### Files that are empty or missing

- `docs/crew/log/parent.md` **MISSING**
- `.grok/agents/walt.md` **MISSING**
- `crafts/stock` **MISSING**
- `docs/program/improve/I-001.md` … `I-011.md` live **MISSING** (archive copies all `status: open`)
- `feedback/notes/{gus,lars,linus,mortimer,verena}.md` header only
- `feedback/notes/{walt,wernher,spotter}.md` **MISSING**
- Live Open questions: **0** Mortimer / Verena / Walt / Wernher rows
- Reviews: **0** Gus / Linus / Mortimer name hits

ORG.md interviews Gene, Jeb, Gus, Linus, Lars — not Verena, Walt, Wernher, Spotter, parent.

---

## 7 Patterns that repeated without moving sci/tree

Board and slate last sci move on a hop: **13-58-18Z** `9.66 → 10.96, +1.30` ([`docs/program/world-model.md`](docs/program/world-model.md) Facts; [`docs/program/slate.md`](docs/program/slate.md)). Tree after 22-39: **start, engineering101, basicRocketry** — no later node. survivability still **LOCKED**. RW `stability` still **LOCKED**. No chute on any signed craft. From 13-58 through last-flight **19-43-18Z**, every `hop-to-water` (13) and `hop-splash` (11) logged **+0** on that board. Live desk now **13.2632** with leftover FlyingLow geiger 0.316 and FlyingHigh Forest TELEMETRY 1.512; `science.md` still prints bank **10.96**. Conference still ran Gene merge → Gus re-sign → Linus re-point → Lars `need_stack` → Jeb CLI.

Craft ladder on disk (did not buy 15): pad-pbc → geiger-pbc → hop-flea-pbc → hammer → valiant-pbc → t7 → east-pbc → east-bare → east-one → east-fin → t7-splash (24×Z-100).

### hop-to-water, heading never 090 (13/13 **+0**)

CLI `python main.py hop-to-water` 14-33 through 16-57. Pitch program changed (7.5° → 25° command → AP hold → slew 0.4 → east-bare → east-one → east-fin). Water pair stayed **3.50 / 0.54 short**. jsonl heading is tape-live only on **16-33-22Z** and **16-57-24Z**; both **never hold 090**. Gene then `go: wait`, `need_stack: hop-splash`.

| Stamp | What the review/log says | sci |
|---|---|---|
| 14-33-29Z | Pitch 7.5° stayed Shores, lithobrake 74.5 m, never splash | +0 |
| 14-45-33Z | leftover lit; abort `not splashed` MET 0.6 pad landed | +0 |
| 14-52-25Z | leftover already flying; Crash UI T+13; Flight Results up | +0 |
| 15-14 / 15-19 | Hangar waits `can_revert` | +0 |
| 15-26-18Z | 25° **commanded** not flown; HDG 304; lithobrake Shores | +0 |
| 15-50-45Z | AP held; fins weathercock HDG **290**; lithobrake Shores MET 148 | +0 |
| 16-06 / 16-08 | Hangar waits Flight Results | +0 |
| 16-11-58Z | east-bare shear; lithobrake Shores MET 54 | +0 |
| 16-25-47Z | east-one throttle slam; apo 1.84 km Shores | +0 |
| **16-33-22Z** | jsonl **heading never 090** (299 tumble); lithobrake Shores | +0 |
| **16-57-24Z** | heading **never holds 090**; five ±15° fly-throughs; impact 299 | +0 |

Quote (16-57 Learn): “Heading **never holds 090** (pad 299, tumble… impact 299)… Water is **dead** on this hang.” Linus: “Unbound Water shorts (unflyable, no wheel).”

### Lithobrake Shores / Flea hops

FAR Flea envelope apo ~7.4–7.7 km, down ~74–79 m, repeated 10-30 through 12-30. hop-to-water east hops lithobraked Shores and **never splashed**. 13-58 t7 lofted ~90 km then lithobraked Shores landed recoverable=no. World-model: “Same lithobrake Flea is **not** a 15-sci campaign.” Flea hops that moved sci vs not (21 Aug morning): moved 10-42 **+1.13**, 11-23 **+0.30**, 11-40 **+0.54**, 11-47 **+0.32**, 11-52 **+0.40**, 12-04 **+0.30** (in-flight). Unchanged: 10-30, 11-09 (false recover), 11-28, 12-22, 12-30. Leftover geiger after the string: **0.32**. After 6.35 Gene: “Do not fly the Flea.” hop-to-water / hop-splash logs: **Flea refused**. I-019 still open.

### Science skip no Experiment modules (hop-splash **+0**)

Review Events hits: 16-24-37Z-hop; hop-splash **18-08, 18-15, 18-28, 18-38, 19-43**. note-tech **4** lines (18:08–18:44) all Jebediah → Lars, abort wanted `kerbalism_TELEMETRY`. 18-15 Learn: “Science **skip**: Kerbalism **Experiment modules=0** at splash… **+0** (10.96).” Stayputnik still hosted TELEMETRY PAW.

### Leftover PRELAUNCH after Close

Crash UI Close reloads the pad. Matching PRELAUNCH is a **ghost** (`can_revert` true). Gene log names leftover PRELAUNCH on ≥12 dated lines. 11-40 lit leftover flea. 14-52 disk PRELAUNCH was already flying wreck. 19-24 lit leftover LANDED Forest dry. 18-56 recovered PRELAUNCH ghost then Hangar. 16-57: “leftover PRELAUNCH east-fin after Close is a **ghost pad reload**.”

### 497 s FlyingLow never finished

Bound as Cape pad geiger and as FlyingLow geiger 2.80. Gus `capable: no` once on that hang. Lid ~202 s. Recover-HD on the part instead. Cape Surface geiger 22-20 **capped** (4.93 → 6.13), not FlyingLow 497. World-model Patterns: “A 75 s Flea does not buy 497 s FlyingLow.” Linus log mentions 497 on ≥10 lines.

### Splash EC=0 after loft (hop-splash **+0**)

17-46 Water T+532, TELEMETRY/goo never, ABORT `ec=0`. Gus 24×Z-100. Lesson 17-46: skip EC=0 abort until splash card started. **19-43-18Z** last-flight still `gate ec=0` / `ABORT ec=0` after `science start kerbalism_TELEMETRY` and `sit=splashed`. No lesson heading after 18-15. Pair **3.20** still **0.84 short** of ~4.04.

### Pairs vs 15 that never closed

Splash 3.20 is 0.84 short of ~4.04. Water pair 3.50 is 0.54 short. FlyingHigh shorts ~4.50 still ~4.15 short of 8.65. TELEMETRY-only Water 4.00 is 0.04 short. “Flea lithobrake is not a node.” Two CTT spends are the only tree moves on disk.

World-model Meaning last-write is **16-57-24Z** (`go: wait`, `need_stack: hop-splash`). Commander `note-tech` continues through **19:51Z**. Seated plan still `go: yes` `campaign: uncrewed` `python main.py hop-splash`.

---

## 8 Source map (paths)

### Protocol / spawn / chairs

- [`/home/os/gits/ksp_stuff/AGENTS.md`](/home/os/gits/ksp_stuff/AGENTS.md) — spawn table; depth 1; when-to-spawn; Gene max 2; I-014 re-desk; I-016 campaign; parent not a second Gene
- [`/home/os/gits/ksp_stuff/docs/program/PROTOCOL.md`](/home/os/gits/ksp_stuff/docs/program/PROTOCOL.md) — Gene owns `go:`; spawn packet; handoffs; I-016; `ask:`; F-013; Lars XOR Wernher; Gus ↛ Hangar; Linus ↛ Commander
- [`/home/os/gits/ksp_stuff/docs/program/CHARTER.md`](/home/os/gits/ksp_stuff/docs/program/CHARTER.md) — conference order; parent `read:` desk; Os 20 Aug RD exception
- [`/home/os/gits/ksp_stuff/.grok/agents/{gene,gus,linus,lars,wernher,mortimer,pilot,verena,spotter}.md`](/home/os/gits/ksp_stuff/.grok/agents/gene.md) — return blocks; “You do not spawn”; spotter DEPRECATED; Walt agent **MISSING**
- [`/home/os/gits/ksp_stuff/docs/program/{ORG,ORG-INTERACTIONS,NEXT-ORG,SPEED,log,roster,GLOSSARY}.md`](/home/os/gits/ksp_stuff/docs/program/ORG.md)

### Sit object / boards (this sit)

- [`/home/os/gits/ksp_stuff/docs/program/desk.md`](/home/os/gits/ksp_stuff/docs/program/desk.md) — lock free; sci **13.2632**; capable yes; t7-splash; last hop-splash abort `ec=0`
- [`/home/os/gits/ksp_stuff/docs/program/current.md`](/home/os/gits/ksp_stuff/docs/program/current.md) — `flight: jebediah`; capcom Valentina
- [`/home/os/gits/ksp_stuff/docs/program/plan.md`](/home/os/gits/ksp_stuff/docs/program/plan.md) — `go: wait` / `need_stack: hop-splash`
- [`/home/os/gits/ksp_stuff/docs/missions/jebediah/plan.md`](/home/os/gits/ksp_stuff/docs/missions/jebediah/plan.md) — `go: yes` / `campaign: uncrewed` / `python main.py hop-splash`
- [`/home/os/gits/ksp_stuff/docs/missions/jebediah/briefing.md`](/home/os/gits/ksp_stuff/docs/missions/jebediah/briefing.md) — splash sit, f013, leftover ghost
- [`/home/os/gits/ksp_stuff/docs/program/slate.md`](/home/os/gits/ksp_stuff/docs/program/slate.md) — 15 sci; recommended hop-splash; `go: yes`; bank 10.96
- [`/home/os/gits/ksp_stuff/docs/program/science.md`](/home/os/gits/ksp_stuff/docs/program/science.md) — bound t7-splash; bank **10.96**
- [`/home/os/gits/ksp_stuff/docs/missions/jebediah/science.md`](/home/os/gits/ksp_stuff/docs/missions/jebediah/science.md) — splash TELEMETRY then goo; pair 3.20
- [`/home/os/gits/ksp_stuff/docs/program/vab.md`](/home/os/gits/ksp_stuff/docs/program/vab.md) — `capable: yes` / t7-splash / 24×Z-100
- [`/home/os/gits/ksp_stuff/docs/program/world-model.md`](/home/os/gits/ksp_stuff/docs/program/world-model.md) — Facts 10.96; Meaning 16-57; Horizon Linus; Practice Mortimer; Open questions **20 rows**
- [`/home/os/gits/ksp_stuff/docs/program/blocks.md`](/home/os/gits/ksp_stuff/docs/program/blocks.md) — owned by Lars; 6 phases
- [`/home/os/gits/ksp_stuff/docs/program/krpc.md`](/home/os/gits/ksp_stuff/docs/program/krpc.md) — no VAB placer; Stayputnik PAW vs Geiger part
- [`/home/os/gits/ksp_stuff/docs/last-flight.md`](/home/os/gits/ksp_stuff/docs/last-flight.md) — `hop-splash` / `exit: 2` / `abort: ec=0`
- [`/home/os/gits/ksp_stuff/docs/missions/INDEX.md`](/home/os/gits/ksp_stuff/docs/missions/INDEX.md) — next **hop-to-water**
- [`/home/os/gits/ksp_stuff/docs/missions/jebediah/craft.md`](/home/os/gits/ksp_stuff/docs/missions/jebediah/craft.md)

### Crew logs / portraits / niches

- [`/home/os/gits/ksp_stuff/docs/crew/log/{gene,gus,linus,lars,jebediah,mortimer,verena,wernher,walt,valentina,bill,bob,grok}.md`](/home/os/gits/ksp_stuff/docs/crew/log/gene.md) — dated bullets as counted in §2/§6
- [`/home/os/gits/ksp_stuff/docs/crew/{gene,gus,linus,lars,wernher,jebediah,valentina,bill,bob,grok,mortimer,verena,walt}.md`](/home/os/gits/ksp_stuff/docs/crew/gene.md)
- [`/home/os/gits/ksp_stuff/docs/crew/niche/{gene,gus,linus,lars,wernher,jebediah,mortimer,verena,walt}.md`](/home/os/gits/ksp_stuff/docs/crew/niche/gene.md)
- [`/home/os/gits/ksp_stuff/docs/crew/builder.md`](/home/os/gits/ksp_stuff/docs/crew/builder.md) — historical pointer
- parent log **MISSING**

### Fly tape / lessons / note-tech

- [`/home/os/gits/ksp_stuff/docs/lessons.md`](/home/os/gits/ksp_stuff/docs/lessons.md) — **52** `##`; newest 18-15-08Z
- [`/home/os/gits/ksp_stuff/docs/program/note-tech.md`](/home/os/gits/ksp_stuff/docs/program/note-tech.md) — **44** Jebediah lines 10:28Z–19:51Z
- [`/home/os/gits/ksp_stuff/docs/missions/jebediah/logs/`](/home/os/gits/ksp_stuff/docs/missions/jebediah/logs/) — **66** reviews; 14 `_Gene fills this.`
- [`/home/os/gits/ksp_stuff/protocol.py`](/home/os/gits/ksp_stuff/protocol.py) — `fly_gate`
- [`/home/os/gits/ksp_stuff/flightlog.py`](/home/os/gits/ksp_stuff/flightlog.py) — `flight.lock`
- [`/home/os/gits/ksp_stuff/phases.py`](/home/os/gits/ksp_stuff/phases.py) `NAMES`
- [`/home/os/gits/ksp_stuff/missions.py`](/home/os/gits/ksp_stuff/missions.py) `seated_plan_path`
- [`/home/os/gits/ksp_stuff/crafts/`](/home/os/gits/ksp_stuff/crafts/) — 11 `kspstuff-*.craft`; `stock` **MISSING**

### Improve / feedback / press

- [`/home/os/gits/ksp_stuff/docs/program/improve/README.md`](/home/os/gits/ksp_stuff/docs/program/improve/README.md) + [`I-012.md` … `I-020.md`](/home/os/gits/ksp_stuff/docs/program/improve/I-012.md) — 5 accepted, 4 open
- [`/home/os/gits/ksp_stuff/docs/archive/letsgrok-2026-08-21/improve/I-001.md`](/home/os/gits/ksp_stuff/docs/archive/letsgrok-2026-08-21/improve/I-001.md) … `I-011.md` — all `status: open` there
- [`/home/os/gits/ksp_stuff/docs/program/feedback.md`](/home/os/gits/ksp_stuff/docs/program/feedback.md) + [`F-001.md` … `F-015.md`](/home/os/gits/ksp_stuff/docs/program/feedback/F-001.md) — 8 accepted, 7 open
- [`/home/os/gits/ksp_stuff/docs/program/feedback/notes/{gene,gus,jebediah,lars,linus,mortimer,verena}.md`](/home/os/gits/ksp_stuff/docs/program/feedback/notes/gene.md)
- [`/home/os/gits/ksp_stuff/docs/press/`](/home/os/gits/ksp_stuff/docs/press/) INDEX + four stories; [`docs/press/asteroid-xrl-564.md`](/home/os/gits/ksp_stuff/docs/press/asteroid-xrl-564.md)
- [`/home/os/gits/ksp_stuff/README.md`](/home/os/gits/ksp_stuff/README.md)

### Sessions (child notes; not re-tallied here)

`/home/os/.grok/sessions/%2Fhome%2Fos%2Fgits%2Fksp_stuff/` — gene **83** (`01a01fc3`…`01a02593`; multi-packet `01a0216c`); jebediah **≥67** (latest `01a025d9`); lars **≥30** (`01a0255e`, `01a0217b` explore); gus **19** (`01a01fc8`…`01a02579`); linus packets e.g. `01a01fbb`, `01a01fd0`, `01a02089` (+ rewind copies), `01a0251f`, `01a0253d`, `01a0254f`, `01a02557`; mortimer **8** (`01a0210f`, `01a02116`, `01a0211d`, `01a02152`, `01a02350` no return, `01a0242a`, `01a02451`, `01a02579`); verena **5** (`01a02027`, `01a02037`/`01a0203c`, `01a020f9`, `01a02122`); wernher Grokman **1** (`01a020cd`); valentina **3** and grok **6** (19 Aug Mun); ksp-spotter **14** (19 Aug); bill **0**; bob **0**; walt **0**; parent `grok-build-plan` `01a01f2c`; Os 10.96 log write `01a02300`.

### Count conflicts resolved on disk

| Claim in child notes | Disk |
|---|---|
| Jebediah 69 bullets | **67** dated (`docs/crew/log/jebediah.md`) |
| Lars 38 bullets | **37** (`docs/crew/log/lars.md`) |
| Mortimer 12 bullets | **10** (`docs/crew/log/mortimer.md`) |
| note-tech 45 lines / Lars 40 | **44** dated; Lars **39**, Gus 4, Wernher 1 |
| Open questions `to` Gene 11 | **10** (`world-model.md` table) |
| Gene 86 / go 36 yes 38 wait | **confirmed** |
| I-012–I-020 status | 5 accepted, **4 open** (I-013, I-017, I-018, I-019) |
| F-001–F-015 | 8 accepted, **7 open** (007–009, 011–012, 014–015) |
| `_Gene fills this.` | **14** reviews |
| `lessons.md` headings | **52**; newest 18-15-08Z |
| Jeb CLI 61 / exits 23×0 37×2 1×4 | **confirmed** |
| crafts/ | **11** files; `stock` **MISSING** |

Unknown: exact Linus session count (desk notes: “several”); whether live desk sci **13.2632** is a later recover the board did not last-write (desk leftover-science lists FlyingLow geiger 0.316 and FlyingHigh Forest TELEMETRY 1.512; `science.md` still prints **10.96**); Wernher von Kerman Mun-era session contents beyond the child note that they are not this letsgrok sit.