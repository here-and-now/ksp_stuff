# Org interactions — analysis for the next program

Date: 2026-08-21. Tree: `letsgrok` gym (`KSP-rss`), before RO. Method:
six parallel **explore** children (protocol, knowledge, helm, specialist
desks, dual corpus, F-items) plus parent synthesis. Isolation `none`,
depth 1. This file is **design input**, not CHARTER. Campaign
postmortem of the pad sit remains `ORG.md`. Speed slice remains
`SPEED.md`. Handoffs remain `PROTOCOL.md`.

**Thesis.** Keep the **institution**. Throw out the **mission corpus**.
Do not clone dossiers, Flea crafts, or the three copies of Gene’s
walls into RO. The thing that hurt was not “agents cannot talk.” It
was **meaning without a shared sit object**, plus a **spawn tax** of
one full LLM hire per desk (measured ~2 min on this fan-out) after
every specialist, while every child re-read the bible and re-parsed
GameData.

---

## 1. How the room actually works

Os is Founder. Parent is the only `spawn_subagent` (depth 1). Children
do not spawn and do not see each other’s chats. Speech is **name +
title**. Machine slugs stay internal.

Three loops, never mixed in one process:

| Loop | Who | When | kRPC |
|---|---|---|---|
| **Helm** | seated Commander | `go: yes` + CLI | **one writer** |
| **Flight Director** | Gene | between exits, lock **free** | none (disk) |
| **R&D** | Lars XOR Wernher | miss / trap | none |

Ground conference (Gene, Linus, Gus, Lars, Wernher, Mortimer, Verena)
is **files**, lock free, **different last-write paths**. They address
each other by name. They do **not** spawn each other. Talk-by-name in
Os chat is **voice only — no spawn**. Legal `go:` / `capable:` /
`stack:` only from a **child return**.

```
Os ──talk──► anyone (parent voice, no hire)
Os ──go──► parent
              │
              ├─ desk (disk, not a hire)
              ├─ Gene draft          [optional if last Gene already named need_*]
              ├─ specialists ∥       [Linus opp ∥ Gus capable; not bind]
              ├─ Linus bind          [serial, after capable: yes]
              ├─ Gene merge          [only go:]
              ├─ Commander           [lock live; no Gene]
              └─ Learn Gene | Lars→Gene
```

Walls that are load-bearing (copy these):

- Missing `go:` = **wait**. Never auto-fly.
- One kRPC writer. `status` is a second Session — allowed only lock free.
- Parent does not patch `.py` in the fly turn.
- Crash UI is honest: leftover recover or next Hangar. No rewind UT.
- Helm `cli:` is Gene `recommended:` **verbatim**.
- Lars only on miss. Wernher only if Lars `stack: ok` **and** a kRPC trap.
- Linus ↛ helm. Gus ↛ Hangar. Gene ↛ stick while lock live.

---

## 2. Modes (do not conflate)

| Mode | Hire? | Artifact | Latency |
|---|---|---|---|
| **Os names someone** | no | parent loads `docs/crew/<slug>.md` | this turn |
| **Spawn packet** | yes | child LLM, return block | **~1–3 min** |
| **File conference** | yes, N desks | last-write on different boards | N hires + Gene merge |
| **`ask:`** | no extra hire | Open questions on `world-model.md` | **unbounded** (next real spawn of that desk) |
| **`feedback:`** | no | parent files `F-NNN` | zero hires |
| **Helm radio** | no | `uplink.md` last-write-wins; helm `take()` | next 1 Hz tick |
| **`loop.md` / `note`** | no | talk, not stick (L-032) | — |
| **Walt TUI** | no | phase start / end / unexpected only | — |
| **Retro** | parallel notes | `feedback/notes/<slug>.md` | lock free, 3+ open or chair |

Forbidden modes that kept happening:

- Spawn-to-chat (Gus question → hire Linus now).
- Spawn-to-complain (`feedback:` is a file).
- Gene as 15 s narrator / merge bus after every specialist.
- Two helms; Gene + helm; children during dwell.
- Parent swallowing 1 Hz heartbeats.

---

## 3. Latency

### 3.1 What a hire actually costs

This session’s six **read-only** explorers (no kRPC, no fly):

| Child | Wall | Tool calls |
|---|---|---|
| Protocol | 109 s | 26 |
| Knowledge | 131 s | 66 |
| Helm | 162 s | 81 |
| Specialists | 105 s | 45 |
| Dual corpus | 133 s | 78 |
| F-items | 102 s | 42 |

**~2 minutes per child** is the unit of org latency, not the 9 s pad.
A “Gene, then Lars, then Gene” after a clean recover is **~6 minutes
of models** around a 9 s physics sit (`ORG.md`). `SPEED.md` target:
**5–7 Gene/sit → 1 draft + 1 merge**.

Every named `.grok/agents/*.md` is `prompt_mode: full` and
`agents_md: true`. The child therefore eats:

1. Job card (walls + return schema)
2. **Entire parent `AGENTS.md`** (switchboard — the child cannot spawn)
3. AGENTS line 1: CHARTER → `lessons.md` → `agent-notes.md` → last-flight
4. Portrait `docs/crew/<slug>.md` (voice **plus ops Log**)
5. Packet `read: ≤3` (often ignored; role files re-run `world`/`tech`/`parts`)

Helm is worse: type stub (`jebediah.md`) **plus** `pilot.md`.

### 3.2 Hop counts (parent → child → parent)

| Sit | Serial LLM layers | Typical child calls |
|---|---|---|
| Os go, last Gene already named `need_*` | 2 | N specialists + 1 Gene merge |
| Os go, no prior `need_*` | 3 | Gene draft + N + Gene merge |
| New pad (builder + science) | 3–4 | Gus ∥ Linus opp → bind → merge |
| Fly | 1 | Commander (Gene **not** spawned) |
| Clean Learn (exit 0, sci moved) | 1 | Gene only |
| Miss | 2–3 | Lars → (Wernher iff trap) → Gene |
| Paid CTT node | 6–7 | Mortimer + `load rd-<node>` + Gus + bind + Genes |
| `ask:` | unbounded | no hire until that desk is needed |

**Happy briefed pad:** conference 3–4 hops **before** fly + 1 helm + 1
Learn ≈ **5–6 child turns**. Bind cannot share a turn with `capable:`
— that extra serial hop is the F-013 honesty tax.

### 3.3 Wall-clock the parent must not poll

| Stage | Who | Cost |
|---|---|---|
| `python main.py desk` | parent, disk | one `load_world()` |
| Gene / specialist | LLM | **~2 min** each |
| Pilot `status` | 2nd Session | first connect **~30 s** schema |
| Hangar | kRPC | `go_space_center` ≤45 s; `launch_vessel` 25 s watchdog; `wait_vessel_ready` ≤30 s |
| Phase physics | helm | catalog `duration_s` (TELEMETRY tens of s; geiger 497 s if bound) |
| 1 Hz jsonl / stdout | Telem `pulse` | **parent IGNORE** |

The phase **moves** when UT ticks, not when the LLM finishes talking.
Named waits (`hangar ready`, `wait science … run= rem=`), never sleep
chunks. Stuck: **one** `screenshot --name stuck-<stem>`, then read the
PNG. Not a heartbeat. Not press.

### 3.4 GameData tax (on top of LLM)

`load_world()` reads `persistent.sfs` + tech tree +
`ModuleManager.ConfigCache`. Each extra `python main.py tech` /
`parts --unlocked` **re-does that parse**. A conference of Gene +
Linus + Gus + Lars following their **current** prompts is **four
catalog loads**, plus Gene’s post-exit `world`, plus helm
`parts --stack`. Desk was supposed to be **one**. `desk.json` stores
**only** `{"sci": …}`. SPEED’s `desk.md` **does not exist**. Role
prompts still issue the CLIs.

---

## 4. Packet and the sit object

Legal packet (`PROTOCOL.md`):

```
to: <Name, Title>
from: Os | parent
live_run: <UTC-seconds-command> | none
lock: free | live
task: one sentence
read: <≤3 paths>
cli: <exact command or none>
return: the named block
```

Intended `read:` = **desk stdout** + ≤2 role paths. Helm `cli:` =
Gene `recommended:` copied verbatim (F-004). Lars miss names the
**live** review path, not “newest file” (F-003). Parent copies
**F-013** (tree, instrument, unlocked, on_craft).

`python main.py desk` already prints: lock, seat, sci, sci_delta,
unlocked nodes, Gus `capable`/`craft`, bound card ids, last-flight
command/exit/abort, newest review path, helm-tech, leftover **vessels**
(F-006), leftover science, catalog budgets, F-013, seated stack,
science-scan. Children are told not to re-run `world`/`tech`/`parts`
if desk is this sit. **Job cards fight that rule.**

**The quality leak:** `read: ≤3` cannot hold CHARTER + lessons +
science + vab + review + last-flight. F-013 failed because conference
passed `experiment_id`, not tree+instrument. If the three slots are
desk + review + `pad.py`, the hardware line **must live inside desk
text**, not as a fourth file.

Missing field = wait, never infer:

| Missing | Parent |
|---|---|
| no `go:` | wait (even if `recommended:` present) |
| `go: wait` with `need_*` | spawn those desks — do **not** STOP |
| `go: yes` without pad `capable: yes` | no helm |
| `go: yes` with `phase:` not in `blocks.md` | no helm |
| leftover vs Hangar unclear | `go: wait` |
| `feedback:` / `ask:` | file board / world-model; **no spawn** |

---

## 5. Data flow (producer → file → consumers)

| Producer | Artifact | Consumers |
|---|---|---|
| Parent `desk` | stdout snapshot; `desk.json` = sci float only | intended packet food |
| `world.load_world()` | stdout of `world`/`tech`/`parts` (no wiki) | anyone told to query |
| Helm `write_handoff` | gitignored `docs/last-flight.md` + seated `logs/*-review.md` | Learn, Lars miss |
| Helm 1 Hz | `docs/program/ship.md` (radio, **not** chat) | `python main.py radio` |
| Gene/parent | `uplink.md` (one verb) | **helm `take()` only** |
| Helm `note-tech` | `helm-tech.md` | tech desks **between exits** |
| Gene | seated `plan.md`/`briefing.md`; chairs `world-model.md` | helm; ground |
| Gus | `vab.md`, `crafts/*.craft`, seated `craft.md` | Hangar byte-copy |
| Linus | `science.md` opportunities; seated bind | Gene briefing; Gus EC |
| Lars | `blocks.md`; `lessons.md` run headings; named `.py` | Gene `phase:`; Wernher iff trap |
| Wernher | `lessons.md` XOR Lars; `agent-notes.md` API | cold start |
| Mortimer | `slate.md`; RD in `persistent.sfs` → `rd-<node>` | live tree |
| Parent | `feedback.md` / `F-NNN` | retro |
| Verena | README, `docs/press/` | story |
| `status` | stdout Snapshot (**kRPC**) | stuck; **must not** overwrite last-flight |

**Fresh vs stale (this save, as of the audit):**

- `ship.md` can be a frozen hop Snapshot while `last-flight.md` is a later pad. Heartbeat ≠ handoff.
- `docs/program/plan.md` / `briefing.md` / `loop.md` are **shims** of seated `docs/missions/<id>/`. Uplink must not fall through (L-038).
- `last-flight.md` is **gitignored**. A clone has no handoff.
- `preflight.md` can be a checked-off leftover while `vab.md` is `capable: no`.
- Disk `world` leftover vessels ≠ live window (F-006). Desk lists save vessels; it still cannot see a paused crash UI.

Nobody sits in the live VAB. `editor_vab` exists on the scene enum;
desks must not drive it. The “VAB” is `vab.md` + `crafts/`. Hangar is
the only path from paper rocket into Flight. `parts --stack` is a
**disk** parse of seated `craft.md` + hosted PAW, not live
`vessel.parts` unless helm.

---

## 6. Knowledge gathering

Three layers that never collapse:

1. **Query tools** — disk `world` / `desk` / `tech` / `parts` / `science-scan`
2. **Live kRPC** — `status`, helm `phase`/`pad`, career `science` (lock free)
3. **Prose boards** — Gene chairs world-model; Linus/Gus/Lars last-write

**Cold spawn today:** AGENTS.md → CHARTER → lessons (letsgrok novel) →
agent-notes (kRPC bible) → last-flight → current/slate → portrait Log
→ then the role’s CLI list. **Thousands of tokens before a number
from the save.** ORG.md called this “bible before the job.”

**Intended:** packet = desk stdout + ≤2 paths. Desk timestamp = this
sit → no `world`/`tech`/`parts`.

**Actual:** `agents_md: true` re-loads the switchboard **and** the
bible. Linus: desk **then** science-scan **then** parts. Gus: tech
then parts. Lars: desk **and** tech. Verena: world. Gene after clean
exit: `python main.py world` for sci. The snapshot is flavor.

Niche pages (`docs/crew/niche/<slug>.md`) are private **by manners**,
not by walls (isolation `none`). Thesis is copy-pasted into portrait
**and** niche **and** world-model. `ask:` answers wait in three
places and niches are not back-updated.

`docs/archive/kerbin-lessons.md` is forbidden — correct — but every
prompt still *names* the path.

---

## 7. Dual corpus (three, really)

| Surface | Job | Path |
|---|---|---|
| Spawn prompt | walls, CLI, return schema | `.grok/agents/<slug>.md` |
| Portrait | voice, Inner, Style kv, **ops Log** | `docs/crew/<slug>.md` |
| Niche | private itch | `docs/crew/niche/<slug>.md` |

Os-says-Gene loads **only** the portrait. Spawned Gene loads job card
+ AGENTS.md + portrait. In-session Gene **must not** mint a legal
`go:`.

**Roster holes:** `roster.md` omits **Lars and Verena**. Walt has crew
+ niche, **no** agent (correct — CAPCOM is parent TUI).
`spotter.md` still exists, DEPRECATED. `builder.md` is a pointer to Gus.

**Drift (real):**

- Linus portrait still says `parts --unlocked --module Experiment` (the PAW lie). Agent + F-013 forbid it.
- Wernher agent: “newest `docs/flights/*-review.md`”. PROTOCOL: **named** `live_run`.
- `grok.md` agent still mentions `mun --from-orbit`. Helm CLI is verbatim `recommended:`.
- GLOSSARY `tech-unlock` still says `load persistent`. CHARTER / F-014: `load rd-<node>`.
- CHARTER: voices “half a page.” Gene’s portrait is a fly diary. Jeb’s Log is every `append_log` from `cmd_phase`.
- Verena agent: packet ≤3 **plus these if missing** — cap already a lie.

**Style knobs are mostly dead.** AGENTS.md claims `docs/crew/*.md`
changes ascent through `crew.py` then clamps. `apply_ascent` is
**never called** from pad/hop/phases. `_parse_kv` walks the **whole**
portrait, including Log lines with `go: wait`. Personality numbers
are fiction. FlightWatch / Telem gates always win — that part is true.

`append_log` writes flight lines **into the voice file** the next
spawn must read. Telemetry inbox = character sheet.

---

## 8. Specialist contracts

Last-write is the conference. Parallel only on **different files**.

| Desk | Writes | Returns (parent keys) |
|---|---|---|
| Gus | `vab.md`, `.craft`, seated `craft.md` | `capable:` `craft:` `blocker:` |
| Linus | `science.md` (opp); seated bind **after** capable | `science:` `need_builder:` `card:` |
| Lars | `blocks.md`, named `.py`, lessons | `stack: ok\|patched` `lesson:` |
| Wernher | kRPC trap `.py`, agent-notes; lesson **iff Lars did not** | `ready_to_fly:` (not a go) |
| Mortimer | slate; RD only then `load rd-<node>` | `unlocked:` `need_builder:` `need_os:` |
| Verena | README, press | `story:` `shot:` `readme:` |
| Gene | plan, briefing, Learn, world-model | `go:` `need_*` `recommended:` `phase:` |

Legal parallel: Linus **opportunities** ∥ Gus `capable:` (not bind);
Linus opp ∥ Lars `need_stack`; Verena from disk; retro notes; parent
screenshot (no kRPC).

Illegal: bind before capable; Gus+Linus+Gene on one file; Lars **and**
Wernher both patch; Lars after clean 0; two helms; Gene+helm.

Linus has **no radio** to the Commander. Gene copies the card into
the briefing. That copy is where F-013 has to survive.

---

## 9. Pain catalog (comms, not aero)

`ORG.md`: *“Data that never made the next desk.”* `SPEED.md`: Gene as
merge bus; every child re-runs `world`/`tech`/`parts`.

| Id | Symptom | Interaction bug |
|---|---|---|
| F-001 acc. | EC=0 mid-dwell | Linus card lacked `duration_s`/`ec_rate`; Gus signed anyway |
| F-002 acc. | Lars after clean 0 | parent treated every live exit as a miss |
| F-003 acc. | newest last-flight was unittest | tests forged the live bus |
| F-004 acc. | Jeb guessed `phase pad` | packet did not copy `recommended:` |
| F-005 open | same Cape goo+thermo | `run_pad` ignored seated card (`PAD_EXPERIMENTS`) |
| F-006 open | world empty vs leftover flying 73 m | disk ≠ window; leftover vs Hangar is a vibe |
| F-007 open | hop hung on crash UI | recover waited on `recoverable`; Os Escape hid modal |
| F-008 open | Hangar recovered empty HD | leftover-HD skip leaked onto a **new** Flea |
| F-009 open | 75 s Flea as leftover thermo | hang vs EC vs node — sit identity disagreed |
| F-010 open | “ship has a geiger” | PAW host sold as hardware |
| F-011 open | `autoStartServers` False vs notes True | environment memory was prose |
| F-012 open | UT moved, MET=0, ABORT | helm and Lars used different clocks |
| F-013 open | tree never reached Lars or a `go:` | packet passed `experiment_id` |
| F-014 open | `load persistent` wiped RD spend | kRPC autosaves RAM first |
| F-015 open | RD load seated asteroid | scene after load not in the packet |

**Recurring patterns:**

1. **Leftover vs Hangar** — Gene comments oscillate; desk now lists save vessels; still cannot see paused Flight Results.
2. **Instrument ≠ experiment_id** — Stayputnik PAW `geigerCounter` vs locked `kerbalism-geigercounter` at engineering101.
3. **Card vs compose vs craft** — Linus `science.md`, Gus `.craft`, Lars `pad.py` without a bind contract.
4. **Wrong clock** — MET vs UT vs `run=`/`rem=`/`file=recording`.
5. **Rewind temptation** — crash UI, `load persistent`, recover the asteroid. Protocol already forbids it.
6. **`ask:` without receipt** — world-model answers not copied onto the addressee’s next packet. Retro `notes/` mostly empty headers.
7. **Late / wrong desk** — Linus not spawned when sci stayed 0; Gus after EC=0.

`log.md` is a **wait tape**: each line a serial Gene hire for a fact
another desk already had. Honest waits (`capable: no`, hang-limited)
are fine. Packet-hole waits are the tax.

---

## 10. Accessibility

| Need | How they get it | Hole |
|---|---|---|
| Live sci / tree / stack | desk / world / parts | children re-query anyway |
| Live vessel list | desk leftover vessels from **save** | F-006 window |
| Scene (crash UI, leftover vs KSC) | **one** stuck PNG, then read it | used as heartbeat |
| Helm CLI | `recommended:` → packet `cli:` | F-004 guess |
| Hardware honesty | F-013 line on desk | still not in every packet |
| kRPC API | `agent-notes.md` | 500 lines every spawn |
| Voice | `docs/crew/<slug>.md` | Log pollution |
| Private itch | niche | isolation `none` |
| Live VAB | **does not exist** | files only |
| Mid-phase Gene | **forbidden** | uplink wreck-class only |

Helm mid-phase: parent silent except wreck `uplink abort|hold`.
`ship.md` is radio. Bound+fueled abort refused (L-033). Lithobrake
keeps throttle 1.

---

## 11. What survives RO vs what poisons it

**Copy (institution + kRPC 0.6):**

- Depth-1 switchboard. Gene-only `go:`. One writer.
- File-split conference. `ask:` / `feedback:` not spawn-to-chat.
- Desk snapshot as **the** sit object (persist stdout, not `desk.json` sci).
- F-013 as **schema** on every bind / capable / go / miss.
- Leftover-or-Hangar honesty, with leftover as a **desk field**.
- last-flight + named review + jsonl; tests must not write last-flight.
- FlightWatch / Telem gates over personality.
- `rd-<node>` then `ksc`; never `load persistent`; never rewind UT.
- `agent-notes.md` connection/stream/`engaged`/protobuf/`get_services`/warp-in-atmo.
- Hangar watchdog, `wait_vessel_ready`, grim screenshots.
- Voices as **half a page**. Titles. Os = Founder.

**Do not copy (mission corpus):**

- `docs/lessons.md` pad/hop/geiger/Flea/Hammer/Cape Shores as gospel
- `PAD_EXPERIMENTS` / `HOP_EXPERIMENTS` / FlyingLow 50 km lid
- `blocks.md` pad/hop/splash/hop-to-water
- crafts `kspstuff-*-pbc`; Stayputnik PAW as the science bus
- CTT / PBC / survivability-15 chute / science-sandbox Recover as R&D
- world-model Facts (XRL-564, 497 s geiger, 2.43 sci)
- seated jebediah dossier; `slate.md` hang-limited FlyingLow
- `docs/archive/kerbin-lessons.md` (already quarantined)
- Kerbalism Toggle-as-the-only-science-model (RO config differs)
- `crew.py` Style fiction; portrait Logs; triple Thesis
- `spotter`; Gene-after-every-0; `agents_md: true` on children

RO will **multiply** leftover vessels, locked instruments, and scene
traps. FAR/RealChute/RealHeat make stock Q/chute-15/Flea envelopes
false. Named-part Hangar will not speak ROEngines. The protocol that
failed here was meaning without a shared sit. The protocol that
worked was Gene-only `go:`, one writer, file-split conference,
leftover-or-Hangar.

---

## 12. Recommendations for the RO house

Keep **two artifacts max** per person:

**A. Job card (only spawn inject).** Walls, return schema, “you do not
spawn,” exact CLI. **`agents_md: false`** — children must not receive
the parent switchboard. One line: packet `read:` includes desk; do
not run `world`/`tech`/`parts` if desk timestamp is this sit. Pilots:
one file (`pilot.md` + 5-line identity). Kill spotter. Walt is not a
type.

**B. Portrait as data, not bible.** Half a page: voice, Inner (once),
Style kv **iff** `apply_ascent` is wired and tested. **Logs do not
live here** — `append_log` → `docs/missions/<id>/logs/` or
`docs/crew/log/<slug>.md`. `_parse_kv` stops at the Style section.
Roster is the **only** people index (put Lars and Verena on it).

**Niche:** drop, or a scratch file the spawn prompt **never mentions**.
`ask:` + world-model Open questions is enough.

**Sit object:** persist desk **stdout** (the missing `desk.md`). F-013
and leftover (scene + save vessels + activeVessel) are desk fields,
not prose in four agents. If a child still runs `tech`, that is a
prompt bug.

**Hire budget:** Gene twice per sit max (draft if `need_*` unnamed,
then one merge). Learn-only Gene on clean 0. Lars only on miss.
Specialists in parallel on different files. Do not spawn Gene during
lock live. Do not swallow heartbeats.

**Talk vs spawn:** keep PROTOCOL’s split. In-session “Gene” is voice.
Legal `go:` only from a child return. That dual earns its keep; the
rest is the same house copied until it drifted.

**New CHARTER one-liner:** Earth + RO + Kerbalism-RO, sandbox (no
RP-1), first honest stack is a sounding rocket, not a Flea. Empty
missions, new `blocks.md`, new hangar catalog **after first boot**.
Gym (`KSP-rss` + this org) keeps flying until RO has a save. Two
programs, two trees. Do not merge dossiers.

---

## 13. Pointers

| File | Role |
|---|---|
| `PROTOCOL.md` | handoffs, packet, parallel table |
| `ORG.md` | pad-campaign postmortem (spawn tax, fake bus) |
| `SPEED.md` | desk + fewer Gene hires (first slice shipped) |
| `CHARTER.md` | creed, query tools, desk table |
| `feedback.md` | F-001–F-015 |
| `world-model.md` | facts / meaning / horizon / story + Open questions |
| `krpc.md` | who may touch what |
| `GLOSSARY.md` | words (some stale vs F-014) |
| `.grok/agents/*.md` | spawn inject (too much switchboard) |
| `docs/crew/*.md` | voice + polluted Log |
| `desk.py` | sit snapshot (stdout is the packet; json is not) |
