# Tickets — spawn brief

Packet is `docs/program/desk.md` + `tickets packet T-NNN` (also S-/M-/C-)
stdout + this page. Not BOARD.md. Not jsonl. Not parked lessons. Not
`science.md` / `vab.md` / `blocks.md`. Not parked archive / niche / gym
queues. First command is **`tickets packet <Hank-named id>`** (live T-
stay; new science/fly/vehicle mint S-/M-/C-), then the stamp or CLI on
the packet. **Id prefix is not a TYPE:** new science `S-`, fly `M-`,
vehicle `C-`; control / systems / ops / rsi / org / ctt / recover /
press stay `T-`. Global N. Live T- science/fly/vehicle ids stay.

**Learn (uncrewed):** Hank `attach-run` overwrites `payload.learn` every
hop (`who=hank`) — one line from the landing envelope (`format_landing`
+ apo + biome + rec + sci bank/run). Packet skim prints **this hop**.
Do not hire Gene. `needs_learn` stays false. Gene Learn is campaign-stop
only (crewed / `campaign: none` / firsts): **one line** from
`tickets landing`, not a 15 min novel.

**Fingerprint:** lookup `docs/program/tickets/fingerprints.json`. Reuse
the class (`heading-never-090`, `sci-unchanged-recovered`,
`flyinghigh-lid`, `forest-splashed-thermo`, `hold-ground-card`,
`hop-coast-phys-warp`, `bigger-dv`, `far-shear`). Longer kebab aliases onto the shortest existing
prefix (`flyinghigh-lid-18km-hop` → `flyinghigh-lid`). Do not invent a
stem per T-id, `hop-<digits>`, or a timestamp novel. Do not map inland
heading 299 → `heading-never-090` (Water-dead). `control` / `systems` /
`ops --tag feedback` **require** `--fingerprint` (empty is refused;
error prints `reuse (count):` plus a copy line). `legacy-twin` seed is
exempt. Stumble → that stem, not a log shrug. Do not tell another desk
in prose — `ops --tag ask` and `payload.to`. House friction *during*
work is `ops --tag feedback --fingerprint <existing>` (×3 → rsi).
After the hire, file on the **work ticket** (not Return keys):
`python main.py tickets feedback T-NNN --claim "…"`.
Kernel appends `payload.findings`. Close harvests `close_why` if empty.
No new TYPE. No `need_*` / `good:` as Return keys.

```
python main.py science-scan                      # Linus: live MM caps (not tweak cfg)
python main.py comms                             # Gus: RA + HD + ground last-write
python main.py tickets packet T-NNN            # first command; Hank-named id; also S-/M-/C-
python main.py tickets packet T-NNN --deep     # tape CLI / PNG / craft
python main.py tickets landing T-NNN           # envelope (pad/last/apo/hz)
python main.py telem <run.jsonl>               # same eyes; --window pad|airborne|apex|burnout|descent|impact
  # last-flight 40 lines is abort/exit, not the vessel. Do not Learn from it.
python main.py ship                            # live eyes from ship.md (no jsonl). Lock-live status is a GET reader (kspstuff-read); writer Telem.read still owns jsonl/ship.md.
python main.py tickets open --type science --category science_opportunity \
  --title "…" --severity S3 --priority P1 --desk linus --tag splash --tag goo
  # new science mints S-; live T- science ids stay
python main.py tickets open --type fly --title "…" --desk gene
  # new fly mints M-
python main.py tickets open --type vehicle --title "…" --desk gus
  # new vehicle mints C-
python main.py tickets open --type control --category bug --title "…" \
  --severity S2 --priority P1 --desk lars --fingerprint heading-never-090
python main.py tickets open --type ops --tag feedback --title "…" \
  --fingerprint sci-unchanged-recovered
python main.py tickets stamp T-NNN --field go --value yes --who gene
python main.py tickets stamp T-NNN --field learn --value "…" --who gene
  # campaign-stop / crewed / firsts only — uncrewed is attach-run
python main.py tickets stamp T-NNN --field capable --value yes --who gus
python main.py tickets tag T-NNN --add hard-splash
python main.py tickets attach-run T-NNN --path docs/missions/uncrewed/logs/<run>.jsonl
  # overwrites payload.learn (who=hank)
python main.py tickets feedback T-NNN --claim "…"
  # append payload.findings on the work ticket; close harvests --why if empty
```

**Categories:** `craft` `science_opportunity` `bug` `improvement`
`flight` `recover` `org` `control` `systems` `press` `ops`.

**Tags:** free lowercase (`hard-splash`, `heading-090`, `east-t3`).
`ops --tag ask|feedback|explore`. At most tag `learn` — no new TYPE.
Control/systems patches: `python -m pytest tests/test_physics_warp.py tests/test_hop.py tests/test_pad_science.py -q`.
Lars packet `read:` third path is the **named helper file**
(`hop_factory_pad.py` pad-RF, else `hop_factory.py` inland compose,
`pad.py` pad dwell, `science.py` sit-match). Not the immortal factory
for a pad miss. Not `hop.py` for a factory miss. RF pad is **one sit**
— no `_pad_*` per stamp. Warp / sit / timeout / leftover-abort /
chute-sit **blocks** are Wernher (`physics_warp.py`). Tests lock those
blocks, not dead-hang envelopes in `test_hop.py`. Lars first pytest is
`tests/test_hop_factory.py` (`-k pad` pad-RF), not house `test_hop.py`
(231). Miss physics lives on the helper docstring + `tickets feedback
--claim`. Warp law is Wernher.

Katherine (Flight Dynamics) is disk tape only: `telem --window`, not jsonl.
Rare `ops --tag ask`. Stamp `verify` when waiting for more hops.

**Git (Os 2026-08-25):** after you change the checkout, `git add` those
paths and `git commit` a sentence. Do not wait for Hank. Do not commit
gitignored tape (`desk.md`, last-flight, jsonl).

**VAB helpers (Os 2026-08-25 / T-481 / T-496):** Gus does not default to hand-writing
`.craft`. He reviews his own spawns and files
`type=systems --desk wernher --fingerprint vab-helper`. Wernher writes
the helper (`craft.py` / CLI). Gus does not edit `.py`. Pad flies a
**fed** hang — do not idle for helpers. A hang you cannot prove is
FED is not capable. `python main.py craft fuel <craft>` dumps attach
+ `fuelCrossFeed` (BLOCKED = starved). A helper that writes a hang
must leave the **engine in the first fire list** (`sqor=0`, not only
`istg=1`), the heatshield a **VAB dish** (`bottomDiameter=0`), not a
filled puck, and a **fed** engine (`insert_heatshield` refuses
`fuelCrossFeed=False`; T-495 dump / T-497 gate). Do not write
GameData.

**RealAntennas (Os 2026-08-25):** `conn.real_antennas` is live. Do not
cheat a link. T-427 prove **passed**: TL2 **64 bps is table and Cape
path** (`RateToHome`). Pre-clamp 31.5 kbps is not current. Packet:
`docs/program/ra-rate.md`. Do not plan dump hours from
`python main.py comms`. Brief: `docs/program/krpc.md`.

One hire may open **many** tickets (Linus: leftover subjects; Gus:
alts; Lars: control fingerprints; Wernher: systems). Skim (envelope).
`--deep` is PNG/craft/tape CLI, not jsonl rows. Never xhigh. **low**
Walt / S4; **high** Mortimer / rsi / org / S1; else **medium**. Packet is skim. Jsonl stays on disk. Packet skim is the **envelope**
(landing + pad/last heading/horiz/pitch + apo + hz + lat/lon/downrange + biome)
plus this-hop `learn:`. Do **not**
`read_file` a jsonl. Query `tape.Tape` / `python main.py telem` /
`tickets landing`. `--deep` may name the path as `tape: python main.py
telem …` — it must not dump rows. Default hire is skim (no `--deep`).
**Hank** (parent) runs `attach-run` + `landing` after Commander CLI
exit (that stamps `learn`). The Commander does not.

Bound science is `payload.experiment_id` + `situation` on a science
ticket. Vehicle `capable` is a stamp on a craft ticket. Gene `go` is a
stamp on a fly ticket. Uncrewed `learn` is kernel. Crewed / firsts /
`campaign: none`: Gene stamps a one-line `learn` from `tickets landing`.
Commander `cli` is fly `payload.cli` (not `recommended:`). `campaign:`
is fly `payload.campaign` (`uncrewed` → parent starts hop,
`commander: none`; `none` → abort officer). Factory cli is
`python main.py hop` — not `hop-to-water` / `hop-splash`. Ask / itch /
friction: `tickets open --type ops --tag ask|explore` or
`--tag feedback --fingerprint <stem>`. After the hire:
`tickets feedback T-NNN --claim "…"`. Do not emit `need_*` /
`recommended:` / `ask:` / `feedback:` / `good:` as Return keys. Gym `F-014` speech is the twin
ticket id (e.g. T-184).
