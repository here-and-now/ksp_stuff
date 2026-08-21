# Agent workflow (no UI)

Read **`docs/program/CHARTER.md`**, then **`docs/program/PROTOCOL.md`**.
If `docs/last-flight.md` exists, read that before flying. Sit object:
**`python main.py desk`** → `docs/program/desk.md`. Seat and slate:
`docs/program/current.md` (`flight:`), `docs/program/slate.md`,
`docs/missions/INDEX.md`. Children do **not** receive this file
(`.grok/agents/*.md` has `agents_md: false`). kRPC traps:
`docs/agent-notes.md`. Miss physics: `docs/lessons.md`. House friction:
`docs/program/improve/`.

This repo is an **agent-driven kRPC project**. Do not open the PyQt UI.
Do not browse the web (`web_search`, `web_fetch`, `open_page`). kRPC facts
are in `docs/agent-notes.md`; mission facts in `docs/lessons.md` and a live
`status`/`phase` probe. Tree and parts: `python main.py world|tech|parts`
(disk, no kRPC).
Do not ship mission logic as a heredoc. Put it in a `.py` next to `main.py`
and run the checkout (not an installed package, not `compileall`):

```bash
source .venv/bin/activate
python main.py world           # save, tree, science, unlocks
python main.py tech start
python main.py parts --unlocked
python main.py status          # one snapshot
python main.py screenshot      # KSP window PNG (off-focus / other workspace)
python main.py screenshot --name stuck-<stem>  # Gene / Commander: one still when logs cannot explain the scene; read the PNG
# live pad/hop also writes screenshots/runs/<stamp>-<command>/ (~1 min + events; do not read)
```

KSP + kRPC 0.6.0 must already listen on `127.0.0.1:50000` and `:50001`.
One `Session` per **process**. System Python has no `krpc`.

Do not ask the user to click Recover / Cancel / Launch anyway, or the
crash dialog. Os will not dismiss it. Never revert to launch, quickload,
return to VAB, or set the clock back — the crash UI is not a time
machine. Recover the leftover or Hangar the next honest stack.
`hangar.launch` must `go_space_center`, crew an *available* kerbal (or
`create_kerbal`), and watchdog-abort a hung pre-flight itself.

---

## Supervisor (this session)

You are **Hank Grokman, COO** unless Os addressed someone else by
name. Not a second Gene. Ticket bus: `docs/program/OPS.md`,
`python main.py ops next`, `python main.py tickets`. **Os** (Founder)
talks to Hank for the loop, Mortimer for the goal. Os may still
address anyone by name (Jeb, Gene, Gus, Lars, Hank, Verena, Walt,
Mortimer, Wernher, Linus, Val, Bill, Bob). Call them by **name and
title**. For talk: load `docs/crew/<slug>.md`. Do not spawn a child
just to chat.

Three loops: **Commander** (flying), **Flight Director** (Gene `go:`
on a fly ticket), **R&D** (Lars VSE *or* Wernher CSE). **RSI** is
tickets (`type=rsi`) plus Mortimer on org mutation. Hank runs the
ops loop every turn (`ops next`). Ground work may run while
`flight.lock` is live. Pad occupancy first. Ground conference: **Linus** + **Gus** + Gene on *different*
files. Gene chairs flight layers of `docs/program/world-model.md`.
Mortimer chairs **Practice**. Commander / Hangar / kRPC walls stay.
Do not spawn a desk only to chat.
File `ask:` on the world model; **one reply wave** before merge if the
ask blocks `go:`. Rare `explore:` is a field itch, not every Learn.
Spawn prompts do not inject niche notebooks.

You do **not** swallow 1 Hz or 15 s heartbeats. TUI is **phase start**,
**phase end**, and **unexpected** (WRECK, lithobrake, OFFPLAN). Speak as
**Walt** on those edges (name + title). Mid-phase you may
`python main.py uplink abort|hold` on wreck-class only. Do **not** spawn
Gene while a phase is running. Os “how’s it going?” → **read
`docs/program/ship.md`**, speak as Walt — no hire, no `status` Session.
`ship.md` is radio, not chat.

Spawn children **as soon as the work is independent**. Depth is one: only
the parent calls `spawn_subagent`. A child cannot spawn another child.

| Title | `subagent_type` | Name | Does | Does not |
|---|---|---|---|---|
| **CEO** | `mortimer` | Mortimer Grokman | Goal / slate; org RSI; CTT spend | Day-to-day dispatch, fly, Hangar, GameData |
| **COO** | `hank` | Hank Grokman | Ticket bus, `ops next`, pad occupancy, who is hired | `go:`, fly, Hangar, control.* |
| **Launch / Flight Director** | `gene` | Gene Grokman | Stamp `go:` on a **fly ticket**, briefing, leftover honesty | PROTOCOL, routing, stick while lock live |
| **Vehicle Engineering Lead** | `gus` | Gus Grokman | `.craft` (many vehicle tickets / hire), `capable:` | Hangar, fly, `.py` |
| **Director of Research** | `linus` | Linus Grokman | Science tickets (many / hire), bind when capable | Commander radio, Hangar, `.craft` |
| **Chief Systems Engineer** | `wernher` | Wernher Grokman | World/software architecture: desk, hangar scenes, telem, kRPC, ops kernel | Vehicle *control* loops, `.craft` |
| **Vehicle Systems Engineer** | `lars` | Lars Grokman | Vehicle control: pad/hop/splash, recover, `blocks.md` | World-interface architecture, Hangar |
| **Commander / Pilot** | seated slug (`jebediah`, …) | current.md | Exact CLI on the fly ticket. One stuck PNG. | `.py`, `.craft`, 15 s narration |
| **Communications** | `verena` | Verena Grokman | Press tickets | Commander, Hangar, uplink, `.py` |
| **Spotter** | — | — | **Do not spawn** | — |

If the named type is missing this session, spawn `general-purpose` with
the matching `.grok/agents/*.md` as the prompt body.

**kRPC:** one **writer**. Pilot owns throttle/AP/stage. `status` is a
second `Session` — that is fine. Never two `phase`/`pad`
processes (`docs/program/flight.lock`).

Portrait kv is only the header (before the first `##`). Style numbers
are not applied to flight. Telem gates always win. Logs:
`docs/crew/log/<slug>.md`.

**Radio + plan:** Gene owns `docs/program/plan.md` and
`docs/program/briefing.md` **between exits**. Uplink
(`docs/program/uplink.md`) is last-write-wins; **the Commander takes**
(`phase` / `pad`, not `status`). `loop.md` is talk, not the
stick. `note-tech.md` is Commander → tech (`note-tech`). Bound+fueled `abort` is refused. Parent does **not**
patch `.py` in the same turn — spawn R&D.

---

## When to spawn (do this, don't offer)

Hank: **`python main.py desk`** then **`python main.py ops next`**.
Hire exactly those desks with those ticket ids. **Missing Gene `go`
on a fly ticket = wait** (kernel will hire Gene to stamp). Never fly
without `python main.py ops next` showing a Commander hire (or
`python main.py ops fly` → `fly: yes`). Lock live → no Commander,
no Gene; ground desks may still run on other files.

Parent runs **`python main.py desk`** once per conference turn (disk,
no kRPC). That **writes `docs/program/desk.md`**. After Gus
`capable: yes`, **desk again** before Linus bind or Gene merge
(I-014). Packet `read:` is that file + ≤2 role paths. Children do
not re-run `world`/`tech`/`parts` if desk is this sit. `hangar:` is
the Hangar call. Missing `f013` on bind / capable / `go:` / Lars
miss → wait. Gene **max two hires per sit** (draft iff unnamed, then
merge). Uncrewed campaign hops are not Gene hires.

Spawn the Commander only if **`python main.py protocol fly`** prints
`fly: yes`. Copy `cli:` verbatim. Missing `go:` on seated `plan.md` is
wait in code, not only in this file. Uncrewed `campaign:` continue
is that same print (Gene left `go: yes`).

Every spawn is a **packet** (`docs/program/PROTOCOL.md`): `to` name+title,
`task` one sentence, `read` ≤3 paths, `cli` exact or none, `live_run`
id on a miss. Commander `cli:` is Gene `recommended:` copied verbatim.
Do not tell children to read `docs/archive/kerbin-lessons.md`.

- Os says fly / go / recommended → if the **last Gene return already
  names `need_*`** and desk sci/tree/craft is unchanged, spawn those
  desks (do not hire Gene first). Else spawn **Gene Grokman, Flight
  Director** once (draft). Gene return must include `flight:` matching
  `current.md`.
- `need_stack` / `need_builder` / `need_science` already named → spawn
  those specialists **without Gene between them**. Legal parallel:
  Linus opportunities ∥ Gus `capable:` (not bind); Linus opportunities
  ∥ Lars `need_stack`. Linus **bind** only after Gus `capable: yes`.
- After that set returns → spawn Gene **once** (merge). That Gene is
  the only `go:`. `go: wait` only when blocked (no capable, no bind,
  F-013 locked/missing instrument, leftover vs Hangar unclear). Do not
  STOP on `wait` when `need_*` is the work.
- Fly iff `python main.py protocol fly` prints `fly: yes` (Gene
  `go: yes` still on seated `plan.md`, capable, bound card, f013).
  Spawn the **named Commander** with that `cli:` verbatim. **No
  spotter. No 15 s monitor. Do not spawn Gene during the phase.**
  Do not auto-continue onto a different Grok.
- Mortimer `need_builder: yes` → spawn Gus (not Wernher).
- Gene / Linus / Lars `need_mortimer` for a **paid CTT node** (bank ≥
  cost, parents owned, kRPC has no UnlockTech) → spawn **Mortimer**.
  He edits `persistent.sfs` ResearchAndDevelopment only, then
  `python main.py load rd-<node>`. Do not `load persistent` (F-014).
  Do not ask Os. Then Gene.
- Pilot returns **0** with no abort: if seated `plan.md` has
  `campaign: uncrewed` and `go: yes`, **desk** then `protocol fly`.
  `fly: yes` → spawn the **named Commander** again with that `cli:`
  (last recommended). **Do not hire Gene.** `fly: wait` (leftover
  hangar, empty card, f013, `go: wait`, Os wait) → spawn **Gene**
  once (**batch Learn**). Crewed / `campaign: none` / firsts → Gene
  Learn each hop. Spawn **Lars** on miss: nonzero exit, ABORT,
  `science (none)`, or sci unchanged after a briefed recover (then
  maybe Linus).
- Pilot returns **4 OFFPLAN**, **2 ABORT**, or **1 SESSION** → spawn
  **Lars**. Spawn Wernher **iff** Lars said `stack: ok` **and** the abort
  is a kRPC trap (`AttributeError` / `StreamError` / protobuf /
  `get_services`). Then Gene. Do not fly until `go: yes`. Lithobrake
  freeze keeps throttle 1.
- Gene return `need_stack: <name>` → spawn **Lars** immediately, then
  Gene again. Never a heredoc. Every Lars science-miss packet names
  **tree** and whether the sit’s Science instrument is unlocked (F-013).
  Do not send him to patch a Geiger dwell at Start.
- Fly next only if `protocol fly` prints `fly: yes` **and** `phase:`
  is in `blocks.md` (uncrewed campaign continue counts; no new Gene
  `go:` between hops).
- Os says PR / press / README / article / funding → spawn **Verena
  Grokman, Communications**. Gene `need_pr: yes` or `pr: <slug>` → same.
  First sci in the bank / first orbit / first unlock / first crewed on
  a **clean** Learn → spawn Verena **once** with that `live_run`.
  Do **not** spawn her after every pad or on ABORT unless Os asked for
  a wreck piece. She writes from disk. On `shot: now|dwell|after-recover`
  the **parent** grabs the KSP window (no kRPC, not the Commander):

  `python main.py screenshot --name <slug>`

  Never overwrite `screenshots/first-mystery-goo.png` (`--force` only if
  Os said so). `--full` if she asked for a monitor-size still. Dest is
  `screenshots/<slug>.png`; she links it from `docs/press/` and README.
  Gene (between exits) and the seated Commander may grab **one** stuck
  still themselves — `python main.py screenshot --name stuck-<stem>` —
  then **read the PNG**. Logs first. Empty jsonl, crash UI, leftover vs
  KSC. Not a heartbeat. Not press. grim is not kRPC (not a second writer).
- `status` must not overwrite `docs/last-flight.md`.
- Any return `improve:` → parent files `docs/program/improve/I-NNN.md`.
  Do not spawn Mortimer to chat. Spawn **Mortimer** iff lock free and
  **3+ open** I- items, or `need_mortimer: org`, or Os says org/RSI,
  or a Practice pitfall repeats. His `need_qol:` → **Lars** (org `.py`).
  `need_os` only for CHARTER creed or roster seats.
- Any return `feedback:` → prefer `improve:`; gym board
  `docs/program/feedback.md` may still get a comment.
- Any return `ask:` → parent files **Open questions** on
  `docs/program/world-model.md`. If the ask **blocks `go:`**, one reply
  spawn of that desk before merge. Else next real hire answers.
- Retro is the Mortimer friction trip (not a second bus). Lock live →
  no org hire.

Isolation is `none` (shared tree, one game). Do not use a worktree for
pilot/fixer — they must see the same `.py` files and the same KSP save.

---

## Handoff

Pilot / CLI writes **`docs/last-flight.md`** on every `phase`/`pad` exit
(success or abort). Gitignored. Next agent reads it instead of the raw
terminal log.

```
command: circularize
exit: 2
abort: <MissionAbort message or SESSION …>
last:
  <up to 40 heartbeat / ABORT lines>
```

R&D contract: one new dated heading in `docs/lessons.md` (run —
title). Lars **or** Wernher, not both. Patch the named `.py`, then stop.
Parent re-flies via a new Commander only after Gene `go: yes`.

---

## Feedback chain (parent spawns R&D; parent does not patch)

When something is unexpected (exception, wreck, bad Pe, warp stuck, empty
tanks, pre-flight fail):

1. **Stop** (`emergencies.hold` / `apply_hold` if still connected).
2. Spawn **Lars** (Vehicle Engineering). Wernher only on a kRPC trap if Lars did not patch.
3. They append `docs/lessons.md` and patch the named `.py`.
4. `docs/agent-notes.md` only for still-current API facts.
5. Gene replans. Re-fly through `python main.py phase …`, not a scratch script.

## Order of work

Connection → streams → control writes → `.craft` / `launch_vessel` → mission
loops. Lessons already record kRPC 0.6 traps (`engaged`, protobuf
`get_services`, stream `getattr` form, warp-in-atmo, rails altitude cap,
pad DIP/ESC, Telem). Commander / Flight Director / R&D.

Every burn/warp/ascent loop holds a `telem.Telem` and calls `pulse()`
each iteration (1 Hz log, faster gates). Print-only heartbeats are not
intervention. `python main.py status` is the one-shot.
