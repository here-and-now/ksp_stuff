# RSI jump — standing brief

Reusable house capability jump. **Not a fly.** Fired when comms
and issues pile up: Gene writes markdown instead of stamps, Learn is
not on the bus, Wernher is idle, Lars owns too much vehicle *and*
world-stack, packet/token tax is the wait.

Predecessor workflows: `.grok/workflows/org-session-audit.rhai`
(as-is only) and `ticket-bus-cutover.rhai` (cards → tickets). This
one **reviews comms, then patches dataflow**. Loop shape stays.
Hire graph, packet, Learn, and who owns `.py` move.

## Walls

No kRPC. No `phase` / `pad` / `hop` / `ksc` / `recover-probe` / Hangar /
`load`. No GameData. No `persistent.sfs`. No CHARTER creed. No
`hop.py` / `pad.py` / `splash.py` / `science.py` (Lars, vehicle).
No second Commander. Depth 1. Gene only stamps `go`. One kRPC
writer stays a wall even though this run does not fly.

## Token tax (the hidden cost)

A hire that re-reads world/tech/parts, the whole gene log, a jsonl,
or BOARD.md as a novel is a miss. Packet is `desk.md` + this ticket
+ BRIEF (one page). Jsonl is `--deep` only. Crew logs: grep counts
+ last page. Empty answer is valid only after a search.

Agents must **know the first command** from the packet. If they
still dig, that dig is a systems ticket (Wernher) or a job-card
cut (Mortimer), not more prose.

## Who owns what on this jump

| Desk | Owns | Does not |
|---|---|---|
| **Wernher** | World-stack: `desk.py`, `tickets.py`, `ops.py`, `protocol.py`, `review.py`, leftover/hangar *kernel*, packet skim, telem schema, kRPC traps | Vehicle burns, `.craft` |
| **Lars** | Vehicle control: `hop.py` `pad.py` `splash.py` `phases.py` `blocks.md` | Desk/ops/ticket kernel |
| **Gene** | `go:` stamp, short Learn on the fly ticket, seated plan **render** | Ticket routing, `.py`, world-model novels |
| **Hank** | `ops next`, leftover CLI, who is hired | `go:`, Hangar |
| **Mortimer** | PROTOCOL / job cards / Practice, this workflow | `.py` (files `type=systems`) |
| **Linus** | Science ticket payload | `science.md` as bind source |
| **Gus** | `.craft` / `capable:` | Hangar, `.py` |

## Allowlist if `apply=true`

`.py`: `tickets.py` `ops.py` `protocol.py` `desk.py` `review.py`
(plus their tests). Job cards: `.grok/agents/*.md`. Docs:
`PROTOCOL.md` spawn/return, `AGENTS.md` When-to-spawn, `OPS.md`
hire table, `BRIEF.md`. **At most one new ops tag** (prefer
`learn`). No new `TYPES` zoo.

## Success

Wernher has inbox work and `ops next` can hire him. Learn is a
stamp / attach-run / short Learn block, not fourteen `_Gene fills
this.` Gene’s last-writes shrink. Recurring fingerprints become
code or a ticket, not another markdown file. Token tax per hire
drops. Pad occupancy does not wait on a novel.
