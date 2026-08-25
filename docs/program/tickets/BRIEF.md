# Tickets — spawn brief

Packet is `docs/program/desk.md` + `tickets packet T-NNN` stdout + this
page. Not BOARD.md. Not a jsonl novel. Not parked archive / niche /
gym queues. First command is inbox, then the stamp or CLI on the packet.

**Learn (uncrewed):** Hank `attach-run` overwrites `payload.learn` every
hop (`who=hank`) — one line from the landing envelope (`format_landing`
+ apo + biome + rec + sci bank/run). Packet skim prints **this hop**.
Do not hire Gene. `needs_learn` stays false. Gene Learn is campaign-stop
only (crewed / `campaign: none` / firsts): **one line** from
`tickets landing`, not a 15 min novel.

**Fingerprint:** lookup `docs/program/tickets/fingerprints.json`. Reuse
the class (`heading-never-090`, `sci-unchanged-recovered`,
`flyinghigh-lid`, `forest-splashed-thermo`, `hold-ground-card`,
`bigger-dv`, `far-shear`). Longer kebab aliases onto the shortest existing
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
python main.py tickets inbox --desk <you>
python main.py tickets packet T-NNN            # skim (envelope + this-hop learn)
python main.py tickets packet T-NNN --deep     # tape CLI / PNG / craft
python main.py tickets landing T-NNN           # envelope (pad/last/apo/hz)
python main.py telem <run.jsonl>               # same eyes; --window pad|airborne|apex|burnout|descent|impact
python main.py ship                            # live eyes from ship.md (no jsonl, no kRPC)
python main.py tickets open --type science --category science_opportunity \
  --title "…" --severity S3 --priority P1 --desk linus --tag splash --tag goo
python main.py tickets open --type control --category bug --title "…" \
  --severity S2 --priority P1 --desk lars --fingerprint heading-never-090
python main.py tickets open --type ops --tag feedback --title "…" \
  --fingerprint sci-unchanged-recovered
python main.py tickets stamp T-NNN --field go --value yes --who gene
python main.py tickets stamp T-NNN --field learn --value "…" --who gene
  # campaign-stop / crewed / firsts only — uncrewed is attach-run
python main.py tickets stamp T-NNN --field capable --value yes --who gus
python main.py tickets tag T-NNN --add hard-splash
python main.py tickets attach-run T-NNN --path docs/missions/jebediah/logs/<run>.jsonl
  # overwrites payload.learn (who=hank)
python main.py tickets feedback T-NNN --claim "…"
  # append payload.findings on the work ticket; close harvests --why if empty
```

**Categories:** `craft` `science_opportunity` `bug` `improvement`
`flight` `recover` `org` `control` `systems` `press` `ops`.

**Tags:** free lowercase (`hard-splash`, `heading-090`, `east-t3`).
`ops --tag ask|feedback|explore`. At most tag `learn` — no new TYPE.
Control/systems patches: `python -m pytest tests/test_physics_warp.py tests/test_hop.py tests/test_pad_science.py -q`.
Lars packet `read:` third path is the **named pulse file**
(`hop_factory.py` inland, or the living rocket's compose, `pad.py`
pad, `science.py` sit-match). Not `hop.py` for a factory miss. Warp /
sit / timeout / leftover-abort / chute-sit **blocks** are Wernher
(`physics_warp.py`). Tests lock those blocks, not dead-hang envelopes
in `test_hop.py`. Lars `lessons.md` heading **names** the reusable
fingerprint.

Katherine (Flight Dynamics) is disk tape only: `telem --window`, not jsonl.
Rare `ops --tag ask`. Stamp `verify` when waiting for more hops.

**Git (Os 2026-08-25):** after you change the checkout, `git add` those
paths and `git commit` a sentence. Do not wait for Hank. Do not commit
gitignored tape (`desk.md`, last-flight, jsonl).

**VAB helpers (Os 2026-08-25):** Gus does not default to hand-writing
`.craft`. He reviews his own spawns and files
`type=systems --desk wernher --fingerprint vab-helper`. Wernher writes
the helper (`craft.py` / CLI). Gus does not edit `.py`.

**RealAntennas (Os 2026-08-25):** `conn.real_antennas` is live. Do not
cheat a link. Discover targeting / rate when a hop goes deaf. Brief:
`docs/program/krpc.md`. Gene / Lars / Gus / Katherine / Hank.

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
