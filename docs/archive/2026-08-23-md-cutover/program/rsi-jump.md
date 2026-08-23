# RSI jump (applied)

Loop shape stayed. Hire/packet/Learn moved onto tickets. Wernher now has inbox.

## 1 Sit

Lock free, leftover 0, hangar none, sci **1.47** after honest CTT ([desk.md:1-9](desk.md)). `survivability` paid; Mk16/RC_cone Available ([slate.md:2-17](slate.md)). T-013 `go: yes` `campaign: uncrewed` `cli: hop-to-water`; landing still **10-11-27Z hard 61 m/s** — **10-35-54Z not in evidence** ([head.json:370-410](tickets/head.json)). Mortimer inbox none (T-030/T-048 done). Pre-jump BOARD **10/50**, no systems/rsi/org ([BOARD.md:3-17](tickets/BOARD.md)).

## 2 What comms showed

Gene last-writes novels: log **98** bullets, **45** `go: yes` / **41** wait / **12** none, **10×** Batch Learn, **0** `tickets stamp` ([log/gene.md](../crew/log/gene.md)). **13** live `_Gene fills this.` (old tape, incl. 10-35-54Z). Packet tax: skim used to always add BOARD; Gene/P0/S2 always `--deep`. Wernher idle: no live systems; `needing_go` did not batch him. Lars T-005 still `inbox` though log says flea patched ([log/lars.md:7](../crew/log/lars.md)). Fingerprints: `heading-never-090` **2**, suicide family **1** each (novel strings) so RSI never ×3 ([fingerprints.json](tickets/fingerprints.json)).

## 3 Design

Five hypotheses **keep**. Dataflow = tickets + stamps + skim. No TYPE zoo. `protocol.fly_gate` plan fallback stays ([protocol.py:134-143](../../protocol.py)). Gene-only `go:`. Depth 1. Lars XOR Wernher on miss. Do not touch `hop.py`/`pad.py`/`splash.py`/`science.py`.

## 4 Files changed

Landed: [ops.py:211-249](../../ops.py) systems in `needing_go`; [tickets.py:245-259](../../tickets.py) skim no BOARD, Gene medium unless S1; [749-783](../../tickets.py) software RSI → wernher; [549-599](../../tickets.py) `payload.learn`; [review.py:222-256](../../review.py) hygiene skip; [desk.py:245-411](../../desk.py) clip/`bind:`/`hop_apo:`; job cards + BRIEF/PROTOCOL/AGENTS/OPS first-command. **Not:** [telem.py:307-320](../../telem.py) `format_landing` still no horiz/pitch; [main.py:76-86](../../main.py) hop-exit still `write_review` only. `STAMP_RULES` unused ([tickets.py:83](../../tickets.py)). `TYPES` 11 ([tickets.py:18-30](../../tickets.py)).

## 5 Tests

TESTS hire: `python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk tests.test_world -q` → **102 OK**. KERNEL slice: 85 OK. Asserts: no BOARD in skim ([test_tickets.py:475](../../tests/test_tickets.py)); `needing_go` hires wernher ([229-243](../../tests/test_tickets.py)); `needs_learn` vs uncrewed ([245-276](../../tests/test_tickets.py)); RSI software desk=wernher ([149-161](../../tests/test_tickets.py)); review bans `_Gene fills this` ([711,733](../../tests/test_tickets.py)). This sit did not re-run. Did not fly.

## 6 Skeptics

**real=false.** Jump stayed in RSI-JUMP walls. TYPE zoo false. Vehicle `.py` untouched. `fly_gate` fallback intact. No CHARTER/portrait/lessons tickets. One kRPC writer (no phase/pad). Leftover DESIGN rows (telem/main) are under-scope, not overscope.

## 7 Tickets opened

| id | type | desk | fp | why |
|---|---|---|---|---|
| T-051 | systems | wernher | `packet-skim-landing` | horiz+pitch skim; hop-exit `attach_run` |
| T-052 | ops | hank | `leftover-prelaunch-ghost` | refile T-005 to systems (hangar kernel) |
| T-053 | rsi | wernher | `leftover-prelaunch-ghost` ×3 | kernel `maybe_open_rsi`; `rsi_loop=software` |

Did not duplicate BOARD titles. Did not open ops-learn-hire / learn-stamp (already in kernel).

## 8 Still markdown and why

Gene log + `briefing.md` + world-model Meaning: cards patched, last-write habit is not code. `science.md:15` still “chute locked” vs desk unlocked. `desk.md:24` still a note-tech novel (clip exists; sit not re-desk). OPS §0 is 21-Aug audit tape ([OPS.md:15-24](OPS.md)). **13** old review placeholders remain; generator is envelope now. T-013 evidence ends 10-11-27Z.

## 9 Open risks

Suicide family still unique MET dumps → RSI never ×3 without stable keys. `protocol.fly_gate` still plan+card fallback (wall). T-013 is Gene **medium** (S1-only `--deep`); 10-35 stays off the ticket until attach-run. Hank must refile T-005, not burn `hop.py`. Pad occupancy still beats Gene; uncrewed `go: yes` still re-flies the Commander.
