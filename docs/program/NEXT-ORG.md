# Next house — decided 2026-08-21

Os answers + parent calls on the leftover “not sure.” This becomes
CHARTER / PROTOCOL / crew at **RO cutover**. Until then the gym
(`KSP-rss`, this `docs/program/`) still flies. Audit:
`ORG-INTERACTIONS.md`.

**Program:** totally fresh **RO science sandbox** on `~/Games/KSP-RO`.
No RP-1. No Flea dossiers. At cutover: **archive gym docs, blank
`docs/program/`**, new lessons from L-001, empty `docs/missions/`.

---

## You locked

| Topic | Call |
|---|---|
| Pains | Spawn tax, F-013 packet holes, bible before the job, re-query GameData, sit identity fights, **mid-phase too quiet** |
| Personalities | Keep *some*; do not pay ~2 min/hire to re-read fly diaries |
| Child prompt | **`agents_md: false`** |
| Leftover vs Hangar | **Desk field** (save vessels + scene + activeVessel) |
| Specialists | **Legal parallel, different files** |
| Trees | **Archive gym, blank program/** |
| First sit | **Fresh RO science sandbox** (not ported pad/hop) |
| Deferred to parent | Gene budget, prompt surfaces, sit object, F-013 home, `ask:`, helm live, bind tax, Lars/Wernher |

Agentic workflow over ritual. Recursive self-improvement over spawn-to-chat.

---

## Parent calls (the “not sure”)

### Personalities vs latency

**Keep the voices. Starve the bible.**

- Job card (`.grok/agents/<slug>.md`) is the **only spawn inject**: walls, return schema, “you do not spawn,” “desk.md is this sit.”
- Portrait (`docs/crew/<slug>.md`) is **≤25 lines**: voice, Inner, title. **No Log.** `append_log` → seated `docs/missions/<id>/logs/` only.
- **Niche dropped** (or a scratch file the job card never names).
- `crew.py` Style kv **deleted** until something actually calls `apply_ascent`.
- In-session “Gene” is still **voice only** — not a legal `go:`.

That is how Jeb stays Jeb without eating last week’s geiger tape every hire.

### Gene budget — max 2 per sit

Spawn tax was a pain. So was a blind dwell. Those are **different knobs**.

- **Draft Gene** only if the last return did not already name `need_*` / the sit.
- Specialists (parallel) → **one Gene merge** (`go:` only).
- Clean exit 0 + sci moved → **Learn Gene only** (that is the second hire, or the only one).
- Miss → Lars (then Wernher iff trap) → **one** Gene. Not Gene-after-Lars-after-Gene-after-Gus.

Mid-phase quiet is **not** fixed by hiring Gene. See helm live below.

### Sit object — `docs/program/desk.md`

Agents read markdown. `desk.json` as `{sci}` failed them.

Parent runs `python main.py desk` **once** per conference turn and
**writes the stdout** to `desk.md`. Packet `read:` is that file + ≤2
role paths. Children **do not** run `world` / `tech` / `parts` if
`desk.md` timestamp is this sit. If they still do, that is a **job-card
bug**, not a missing CLI.

Desk **fields** (schema, not prose):

```
lock: free|live
scene: space_center|flight|tracking|editor|crash_ui|unknown
active_vessel: <name|none>
leftover: none|recover <name>|hangar-blocked
seat: <id>
sci: <n>  sci_delta: <n>
capable: yes|no  craft: <file|none>
card: <ids or none>
last: command= exit= abort=
review: <path or none>
f013:
  instrument: <part>
  tech: <node>
  unlocked: yes|no
  on_craft: yes|no
  host: <paw part or none>
stack: <names>
```

`leftover:` is the Hangar decision. Gene does not vibe it.

### F-013 — desk field + return contract

Every Linus bind, Gus `capable:`, Gene `go:`, Lars miss **repeats**
`f013`. Missing line → parent **waits** (same as missing `go:`).
Locked / not on craft → Linus does not bind, Gus `capable: no`,
Gene `go: wait`, Lars does not sequence a ghost. No `parts --search`
pilgrimage.

### `ask:` — one reply wave (RSI, bounded)

Spawn-to-chat explodes hops. Pure mailbox never improves the same sit.

**Bounded mail round**, lock free, before Gene merge:

1. Specialists return (parallel). Parent files `ask:` on world-model.
2. If any `ask:` is needed for an honest `go:` (hardware, leftover,
   hang, EC), parent hires **those addressees once**, packet = `desk.md`
   + the question. No second round in the same sit.
3. Gene merge sees answers. Leftover asks wait until the next real hire.

Learn Gene may write **one** pattern on world-model. `feedback:` still
does **not** spawn. That is recursive self-improvement with a cap of
**+N hires once**, not a chat room.

### Helm while lock live — Walt + tape, not Gene

You wanted less quiet without the 15 s narrator.

- **No Gene spawn. No `status` Session** (second writer).
- Helm keeps writing `ship.md` (last Snapshot) and jsonl.
- **Os “how’s it going?”** → parent **reads `ship.md` / last jsonl line**
  and speaks as Walt. Disk. No hire.
- Phase **start / end / unexpected** (WRECK, lithobrake, OFFPLAN, crash
  UI) → Walt one line. Stuck → **one** `screenshot --name stuck-<stem>`,
  read the PNG.
- Wreck-class `uplink abort|hold` only. Bound+fueled abort still refused.

Quiet = no merge bus in the dwell. Not silent when you ask, not silent
on wreck.

### Bind after capable — keep, no extra Gene

Packet holes hurt more than one Linus hop.

Same conference: Gus `capable` ∥ Linus **opportunities** → if
`capable: yes`, **Linus bind** (serial) → Gene merge. Do not hire Gene
between capable and bind. Do not bind before capable.

### Lars / Wernher — miss only, XOR

Clean 0 + sci moved → Gene Learn, **no Lars** (F-002). Nonzero, ABORT,
`science (none)`, sci unchanged after briefed recover → Lars.
Wernher **iff** `stack: ok` **and** AttributeError / StreamError /
protobuf / `get_services`. Parent still does not patch `.py` on the
fly turn.

---

## Data flow (RO)

```
Os go
  parent: python main.py desk  →  docs/program/desk.md
  [Gene draft iff sit unnamed]
  Linus opp  ∥  Gus capable     (different files)
  [ask: reply wave, once, blockers only]
  Linus bind                    (if capable: yes)
  Gene merge                    go: / wait / recommended:
  Commander                     lock live; cli: verbatim
  exit 0 + sci moved            Gene Learn
  miss                          Lars → (Wernher?) → Gene
```

| Path | Writer | Readers |
|---|---|---|
| `desk.md` | parent, once per conference | **every** ground spawn |
| `vab.md` + `crafts/` | Gus | Hangar, desk, Gene |
| `science.md` (opp / bind) | Linus | Gene briefing, Gus EC |
| `blocks.md` | Lars | Gene `phase:` |
| `world-model.md` | Gene chairs; parent files `ask:` | ground |
| `uplink.md` | Gene/parent write; **helm take** | helm only |
| `ship.md` | helm 1 Hz | parent/Walt when Os asks; not Gene chat |
| `last-flight.md` | helm exit | Learn / Lars (gitignored) |
| `lessons.md` | Lars XOR Wernher | **not** cold-start bible; last 3 on miss packet |
| `agent-notes.md` | Wernher, API facts only | job cards point at traps; children do not ingest the novel unless the packet says so |

**Cold start for a child:** job card + `desk.md` + ≤2 paths. Not CHARTER
+ 27 lessons + agent-notes + portrait Log.

---

## Cutover (when Express has a save on KSP-RO)

1. Archive gym program docs (`docs/archive/letsgrok-program/` or a
   dated tree). `ORG.md` / `ORG-INTERACTIONS.md` / this file go with
   them. `agent-notes.md` **kRPC 0.6 traps** stay in the library.
2. Blank `docs/program/`. New CHARTER one-liner: Earth, **RO +
   Kerbalism-RO**, science sandbox, no RP-1. First honest stack is a
   sounding rocket.
3. Empty `docs/missions/`. New `blocks.md` **after** first boot, from
   parts that exist. Hangar names ROEngines/ROTanks, not `*-pbc`.
4. Rewrite `.grok/agents/*.md` with `agents_md: false`. Strip crew
   Logs. Roster includes Lars + Verena. Delete `spotter.md`.
5. Point `KSPSTUFF_KSP` at `~/Games/KSP-RO`. Gym tree stays on disk,
   not seated.
6. First conference: desk → Gus capable (whatever actually hangs) ∥
   Linus opportunities from Kerbalism-RO → bind → Gene `go:` or wait.

Do **not** merge jebediah’s geiger dossier. Do **not** port `pad.py`
recipes until a craft exists.

---

## Explicitly not this house

- RP-1 career
- Gene as 15 s monitor or merge bus after every specialist
- `agents_md: true`
- Children re-query GameData when `desk.md` is this sit
- Spawn-to-chat / unbounded `ask:` loops
- `load persistent` / rewind UT / Os clicks crash UI
- Two helms; Gene + helm; parent patches `.py` while flying
- Portrait fly diaries as personality
