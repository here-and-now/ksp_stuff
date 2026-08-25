# Lars RSI (applied)

Prefix is the **id**, not a TYPE. RF pad is **one sit**. T-466 harvest and kernel T-467 are done. Extract pad-RF only; compose stays. Did not rewrite RF-ullage law. Did not raise ignitions. Bank 2.29 does not pay `generalRocketry` 20.

## 1 Sit

Lock free, leftover 0, sci 2.2905 (`docs/program/desk.md:1`–`:8`). Capable t7-wheel-pbc (`:12`). Last-flight hop exit 0 recovered (`docs/last-flight.md:1`–`:13`) is the postcard, not rec. 20-36-06Z flameout is T-465 (`docs/lessons.md:24`). Pad sit is seven defs `hop_factory_pad.py:18`–`:169` (`_pad_engines`…`_pad_hold`); cluster `hop_factory.py:199`–`341` is **MISSING**. Compose imports (`hop_factory.py:30`); `_hold_or_cut(..., brake=False)` `:547`; `_pad_hold` `:600`; `run_factory_vessel` `:273`–`:1051`. Factory **0** `T-\d+`. Stem `rf-ignition-ullage` **7** (`docs/program/tickets/fingerprints.json:153`). T-466 `done` (`docs/program/tickets/head.json:17640`); T-467 `done` (`:17674`); T-465 `inbox` (`:17597`); T-081 `go: yes` (`:3337`). Crew `rf-ignition-ullage|_pad_|hop_factory_pad` in `docs/crew/log/*.md`: **9** (lars **5** rf-ignition `:3`–`:7`; mortimer harvest **2**).

## 2 Why slow
Cold-start, not the 20-line patch. Fresh spawn used to get the immortal factory as third path. Card now: many fps one hire (`.grok/agents/lars.md:83`); first pytest `-k pad` (`:74`) not house `test_hop.py` **231** (`docs/program/tickets/BRIEF.md:82`). Hire-clock minutes (T-457 9.7 / T-459 8.8 / T-462 6.9 / T-464 ~13): **MISSING** on disk.

## 3 Why unmaintainable
Voice “one helper, stop” (`.grok/agents/lars.md:16`) paid `_pad_*` per stamp until the pad-block rule (`:34`, `:48`, `:167`). T-459 `_pad_light`, T-462 `_pad_hold`, T-464 `_engine_throttle` stacked. T-376 forbade immortal factory (`docs/program/world-model.md:505`). Without this card: helper #8 + stem 8. Forest/Grasslands wrap **4** in the pad file (`hop_factory_pad.py:6`, `:49`, `:108`, `:154`).

## 4 Prefix map

| prefix | `type` (unchanged `tickets.py:19`) |
|---|---|
| S- | science |
| M- | fly |
| C- | vehicle |
| T- | control, systems, ops, rsi, org, ctt, recover, press |

Forward-only. `ID_PREFIX` `tickets.py:59`; `_next_id` `:328`; `open_ticket` `:769`; landing parse `:1874`. Do not rename T-081 / T-404 / T-387. Next science **S-468**.

## 5 Files

| file | change | owner |
|---|---|---|
| `BRIEF.md:75` `OPS.md:379` `PROTOCOL.md:356` | S/M/C id; third path = named helper | mortimer |
| `.grok/agents/lars.md` | one pad-RF; `-k pad`; no `_pad_*` per stamp | mortimer |
| `world-model.md:711` | T-466 last-write (prefix, pad sit, stem 7) | mortimer |
| `linus.md:22` `gene.md:31` `gus.md:42` | S-/M-/C- first-command | mortimer |
| `tickets.py` | prefix-by-type; landing S/M/C/T | wernher |
| `hop_factory_pad.py:18` | extract `_pad_engines`…`_pad_hold`; compose stays | lars |

## 6 Tests
Quoted **142** (pad-import + requested). Pad: `tests/test_hop_factory.py:72` (**6**). Prefix: `tests/test_tickets.py:199` (`S-001`/`M-002`/`C-003`; hist T-466 → `S-467`). House `test_hop.py` still **231**. Kernel 119. Did not fly.

## 7 Skeptics
**real=false.** TYPE zoo no. Pulse LAW (sit/warp/suicide), ignitions, Hangar, GameData, CHARTER creed, two-writers, Gene-merge: not this paper. `id-prefix` **1** (`docs/program/tickets/fingerprints.json:87`) — do not re-mint. T-465 inbox is the flameout, not this gap.

## 8 Tickets

| id | sit |
|---|---|
| T-466 | rsi `done` — harvest close |
| T-467 | systems `done` — do not re-mint `id-prefix` |
| T-465 | control `inbox` Lars S1; `_pad_hold` patched; extract legal |
| T-081 | fly `go: yes`; leftover 0 |

## 9 Open risks

T-465 still inbox after the pad-hold patch (`docs/program/tickets/head.json:17597`). `test_hop.py` 231 remains the house godfile. Inland compose still `run_factory_vessel` (`hop_factory.py:273`) — do not extract lid/chute; do not touch `hop.py` `_hold_or_cut`. Git commit **MISSING** (no shell this seat); parent commits house files, not gitignored tape. Last-flight 40 lines is still the postcard. An RSI letter does not empty the pad.
