# Protocol — who hands to whom

Os is Founder. Parent is the room sequencer (depth 1). Speech is
**name + title**. Machine slugs stay internal. Postmortem: `ORG.md`.
RSI house: `improve/README.md`. Next-house notes: `NEXT-ORG.md`.

**Mortimer Grokman, CEO** owns how the house works when friction
trips. **Gene Grokman, Flight Director** owns `go:`. Mortimer never
flies. Gene never rewrites PROTOCOL.

## Handoffs

| From | To | When | Hands | Returns |
|---|---|---|---|---|
| Os | Gene, Flight Director | go / fly / science | slate item | `go:` `phase:` `need_*` `recommended:` (exact CLI) |
| Os | named desk | talk by name | — | voice only — **no spawn** |
| Gene | Linus, Director of Research | `need_science` or first conference | ask | card: `experiment_id`, **part** (host), **instrument** (Science part + tech + unlocked), **duration_s**, **ec_rate**, `recover_banks` |
| Gene | Gus, VP Build | `need_builder` or after draft | plan + Linus board | `capable:` `craft:` — **no** if the sit needs a locked/missing Science part |
| Gene | Lars, Vehicle Engineering | `need_stack: <name>` | missing block **+ tree/unlocked parts** | `stack:` `lesson:` |
| Gene | seated Commander | `go: yes` + `capable: yes` + phase in `blocks.md` | briefing + **exact CLI** | `result:` `exit:` `handoff:` |
| Commander | parent | uncrewed `campaign:` **clean 0** | last `recommended:` | re-fly — **no Gene** |
| Commander | Gene | campaign **stop**, crewed, firsts, or `campaign: none` | reviews since last Learn | batch Learn |
| Commander | Lars / Gus / Wernher | during or after a sit | `python main.py note-tech <desk> …` → `note-tech.md` | parent files / Gene reads between exits |
| Commander | Lars | **miss only** (nonzero, ABORT, `science (none)`, sci unchanged) | last-flight + **live** run path | `stack:` then Gene |
| Lars | Wernher, Avionics | `stack: ok` **and** kRPC trap | traceback | one dated lesson in `docs/lessons.md` |
| Any spawned desk | improve queue | `improve:` on return | friction / suggest / code | parent files `I-NNN`; Mortimer on trip |
| Any spawned desk | feedback board | `feedback:` on return | good / bad / suggest | prefer `improve:`; gym F- table remains |
| Parent | named desks | retro (3+ open, or Os/Gene/Mortimer ask) | open F- items | `notes/<slug>.md` in **parallel** |
| Gene | Mortimer | `need_mortimer: yes` | paid CTT node | RD spend + `load rd-<node>` |
| Any spawned desk | Mortimer | friction trip (`improve/` 3+ open, `need_mortimer: org`, Os org/RSI) | `I-NNN` queue | `org:` `changed:` `need_qol:` `need_os` |
| Mortimer | Lars | `need_qol: <file>` | org/QOL `.py` | `stack:` (desk/wait/tests, not pad physics unless the miss was a fly) |
| Gene / Linus / Lars | Mortimer | bank pays a node and kRPC cannot buy | node id, cost, parents, sci | save: `Tech` owned, `sci` spent, copy `rd-<node>.sfs`, `python main.py load rd-<node>` |
| Mortimer / Gene | Os | `need_os: yes` | charter / roster / slate | Os ratifies |
| Walt, CAPCOM | Os | phase start / end / unexpected | one line, name+title | — |
| Os | Verena, Communications | PR / README / funding story | slate or live_run | `story:` `shot:` `readme:` |
| Gene | Verena | `need_pr: yes` after Learn | live_run, why it is a first | same |
| Verena | Gene | next fly needs a window | proposed `shot:` | Gene copies into briefing or `go: wait` |
| Parent | KSP window | Verena `shot: now` (or Gene `shot:` at dwell / after-recover) | `python main.py screenshot --name <slug>` | `screenshots/<slug>.png` |
| Gene or seated Commander | KSP window | stuck: last-flight / review / jsonl cannot explain the scene | `python main.py screenshot --name stuck-<stem>` then **read the PNG** | what the window shows |

Linus ↛ Commander. Gus ↛ Hangar. Commander ↛ `.py`/`.craft`. Gene ↛ stick while lock live. Parent ↛ patch `.py` in the fly turn.
Mortimer ↛ GameData. Mortimer ↛ flight/UT in the save. Mortimer **may**
edit `persistent.sfs` ResearchAndDevelopment (`sci`, `Tech` node) when
Linus/Lars/Gene brief a paid unlock.
Commander ↛ revert / quickload / return to VAB / rewind UT. Crash UI is
honest: recover the leftover or Hangar the next stack. Os will not
click it. Screenshot when stuck; do not wait for a founder click.

**Ground talk (between exits, lock free):** Gene, Linus, Gus, Lars,
Wernher, Mortimer, Verena may address each other by name. Still not
the stick. Still not mid-phase. Still different files in one turn. They
do not spawn each other.

## World model

`docs/program/world-model.md` — Gene chairs **flight** layers: facts
(disk / `desk.md`), meaning (Learn), horizon (Linus), story (Verena).
**Practice** (pitfalls, house changes, QOL) is **Mortimer**. Patterns
that are still true as *ops* stay Practice; flight clocks stay Gene.
Spawn prompts do not inject niche notebooks.

Wonder is inner. Moments, not a desk. Rare field exploration
(`explore:`), some Learns, firsts. Not every packet. Kardashev creed
in the model; joke in the TUI.

## Questions (`ask:`)

Between exits a spawned ground desk may return:

```
ask:
  to: <Name, Title>
  q: <one sentence>
explore: none|<one sentence itch>
```

Parent files `ask:` onto **Open questions** in the world model. Do
not spawn a desk only to chat. **RSI add-on:** if an `ask:` **blocks
an honest `go:`** (hardware, leftover, hang, EC), parent hires those
addressees **once** before Gene merge (`desk.md` + the question). No
second round in the same sit. Leftover asks wait until the next real
hire. `explore:` is rare — parent may keep them on `.craft` / stack
after Learn if lock is free and Os is not mid-go. The Commander never
`ask:`s the model. Ask Os almost never (`need_os`).

**Tree + hardware (F-013):** experiment_id is not a part. Every bind /
capable / `go:` / Lars science-miss packet must say **tree node** and
whether the **Science-category instrument** is unlocked and on the
craft. Stayputnik PAW is a host, not a Geiger Counter. Desk `f013` is
that line — do not send `tech` / `parts --search` if desk is this sit.
If the instrument is LOCKED: Linus does not bind it as hardware; Gus
`capable: no`; Gene `go: wait`; Lars does not patch a sit for a part we
do not have. Parent copies that line into Lars’s packet so he is not
sequencing a ghost instrument.

**Serial:** `go: yes` (Gene only — first of the sit, or after a stop); Linus **bind** after Gus `capable:`; one kRPC writer; Lars XOR Wernher.

**Uncrewed campaign (I-016):** Gene writes `campaign: uncrewed` with the first `go: yes` of a cheap probe sit (`pad`/`hop`, leftover science). He leaves `go: yes` on the plan. Parent, lock free, after clean exit **0** + abort none: `python main.py desk` then `protocol fly`. `fly: yes` → spawn the Commander with that `cli:` (last recommended). **Do not hire Gene between hops.** Pad does not idle. Stop the string (no re-fly; Gene **batch Learn**, or Lars on miss): nonzero / ABORT / `science (none)` / sci unchanged after a briefed recover; `hangar:` leftover unclear (`recover` / `blocked`); empty card; f013 fail; `go: wait`; Os wait; new craft or new card; crewed; **remaining subjects cannot finish on this hang/craft** (do not string lithobrake Flea hops to a 15-sci node). `campaign: none` is Learn each hop. `python main.py protocol fly` still owns the gate — missing `go: yes` is wait.

## Parallel (same parent turn, still depth 1)

| Together | Wait for |
|---|---|
| Linus opportunities + Gene world/tech | Gene draft `go: wait` |
| Gus `capable` + Linus tree re-read (not bind) | Linus bind to named craft |
| Parent **re-desk** after Gus `capable: yes` (I-014) | Linus bind / Gene merge on stale capable/f013 |
| Disk `python main.py world` anytime | never a second writer |
| Verena writing `docs/press/` + README from disk | Gene `shot:` before a grab |
| Parent `python main.py screenshot --name <slug>` | Verena `shot: now` (or Gene `shot:` at dwell / after-recover). No kRPC. |
| Gene / Commander `python main.py screenshot --name stuck-<stem>` | logs first; one still; read the PNG. No kRPC. |
| Retro comments on open F- items | Gene chairs ops; Mortimer if org/goal |
| Ground `ask:` filed on world-model | addressee’s next spawn (lock free) |
| Gene merge of world-model after Learn | never mid-phase |

Not parallel: two Commanders; Gene + flight; Lars on a clean 0. Uncrewed campaign hops are **serial** re-flies after lock free, not two writers. During dwell: no children; Walt silent unless unexpected. No retro while lock live.

## Spawn packet

```
to: <Name, Title>
from: Os | parent
live_run: 2026-08-20T12-35-42Z-pad | none
lock: free | live
task: one sentence
read: <desk.md + ≤2 role paths>
cli: <exact command or none>
return: the named block
```

Packet `read:` is **`docs/program/desk.md`** (parent just wrote it) plus
at most two role paths. Commander `cli:` is Gene `recommended:` **copied
verbatim** (F-004) from `python main.py protocol fly`. Lars miss packet
names the **live** review path, not “newest file”. Parent copies
**f013** from desk. Do not send `docs/archive/kerbin-lessons.md`.
Children do not re-run `world`/`tech`/`parts` if desk is this sit.

`hangar:` on desk **is** the Hangar decision (`none` |
`phase <name> sit=<SIT>` | `recover <name> sit=<SIT>` | `blocked`).
Disk cannot see crash UI (`scene: unknown (disk)`). Gene does not vibe
it. Missing `f013` on bind / capable / `go:` / Lars miss → wait.
Parent flies only if `python main.py protocol fly` prints `fly: yes`.
Uncrewed campaign continue uses that same print — plan still has
Gene’s `go: yes`. Do not vibe a hop because the last exit was 0.

Every ground return and Learn (Commander exit) may include:

```
improve:
  friction: none | <one line>
  suggest: none | <one line>
  code: none | <path>
need_mortimer: none | org
```

Parent files `docs/program/improve/I-NNN.md`. Spawn Mortimer only on
the trip in `improve/README.md`. Commander `improve:` on **exit**, not
mid-lock.

Gene merge is the only `go:`. Gene **max two hires per sit** (draft iff
the sit is unnamed, then merge). Uncrewed campaign: that merge is the
**first** `go:` (`campaign: uncrewed`); hops between are not Gene;
**batch Learn** at stop is the second. Crewed / `campaign: none` /
firsts: Learn each hop. Do not hire Gene as a merge bus after every
specialist. Do not hire Gene after every clean 0 on an uncrewed string.

A **run** is one Commander command. Filename Earth UTC with seconds
(`2026-08-20T12-35-42Z-pad`). Review also has Kerbal UT + MET. Verena
dates stories from those lines. Logs: `docs/missions/<id>/logs/`.

## Files

Gene last-writes plan/briefing/Learn (`campaign:` on seated `plan.md`)
and chairs **flight** layers of `world-model.md`. Mortimer last-writes
**Practice**, PROTOCOL, and job cards on an org hire. Gus last-writes `vab.md`/`.craft`. Linus
last-writes science boards. Verena last-writes `README.md` (portrait)
and `docs/press/` (story layer). The Commander takes `uplink.md`. `loop.md` is
talk, not stick. Disagreement → Gene `go: wait`. Missing `go:` = wait.

Milestone stills (no kRPC). Press: Verena `shot:` → parent grab. **Stuck:** Gene (between exits) or the seated Commander may grab **one** still when last-flight, the review, and the jsonl cannot explain the scene (empty events, crash UI, leftover vs KSC). Read the PNG. Not a heartbeat. Not press.

Flight cadence (capture only — do not read): `screenshots/runs/<stamp>-<command>/` about every 60 s of a live `pad`/`hop`, plus sit/stage/light/science/recover/wreck. Library for Verena or a stuck debug. Never clobber press heroes.

```bash
python main.py screenshot --name <slug>         # screenshots/<slug>.png
python main.py screenshot --name stuck-<stem>   # Gene / Commander, stuck only
python main.py screenshot --full                # monitor-size, then restore tile
```

Refuses `screenshots/first-mystery-goo.png` unless `--force`. `--full` only if the still is unreadable.

## Linus card

```
experiment_id / part / duration_s / ec_rate / recover_banks: yes|no
```

Gus sizes EC from `ec_rate × duration_s` **before** `capable: yes`. If `world` sci does not move after a briefed recover → Linus, then Gene.

## Feedback

Process lives in `docs/program/improve/` (`I-NNN`) for the RSI house.
Gym record remains `docs/program/feedback.md` (`F-NNN`). Flight bugs stay in
`docs/lessons.md` as **run — title** headings (the filename stem, not letter-codes).

Every return may include:

```
feedback:
  - F-005 comment: <one line>
  - new: <good / bad / suggest>
need_retro: none|yes
```

Gene also `need_mortimer: none|yes`. Mortimer `need_os: none|yes`.
Parent files `feedback:` onto the board. Retro only if Os asks, a chair
flags it, or 3+ items are `open` and lock is free. Consensus: chair
writes `decided:` + `status: accepted|wont`. Parent edits the named org
file. Os ratifies CHARTER / PROTOCOL / roster.
