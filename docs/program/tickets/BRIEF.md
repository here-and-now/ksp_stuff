# Tickets — spawn brief

Packet is `docs/program/desk.md` + `tickets packet T-NNN` stdout + this
page. Not BOARD.md. Not a jsonl novel. Not parked archive / niche /
gym queues. First command is inbox, then the stamp or CLI on the packet.
Stumble: `tickets open` with a **short** `--fingerprint` stem. Do not
tell another desk in prose — `ops --tag ask` and `payload.to`. Landing
wins `learn`. `ops --tag feedback` is the friction door (×3 → rsi).

```
python main.py science-scan                      # Linus: live MM caps (not tweak cfg)
python main.py comms                             # Gus: RA + HD
python main.py tickets inbox --desk <you>
python main.py tickets packet T-NNN            # skim (envelope; no jsonl)
python main.py tickets packet T-NNN --deep     # tape CLI / PNG / craft
python main.py tickets landing T-NNN           # envelope (pad/last/apo/hz)
python main.py telem <run.jsonl>               # same eyes; --window pad|airborne|apex|burnout|descent|impact
python main.py ship                            # live eyes from ship.md (no jsonl, no kRPC)
python main.py tickets open --type science --category science_opportunity \
  --title "…" --severity S3 --priority P1 --desk linus --tag splash --tag goo
python main.py tickets stamp T-NNN --field go --value yes --who gene
python main.py tickets stamp T-NNN --field learn --value "…" --who gene
python main.py tickets stamp T-NNN --field capable --value yes --who gus
python main.py tickets tag T-NNN --add hard-splash
python main.py tickets attach-run T-NNN --path docs/missions/jebediah/logs/<run>.jsonl
```

**Categories:** `craft` `science_opportunity` `bug` `improvement`
`flight` `recover` `org` `control` `systems` `press` `ops`.

**Tags:** free lowercase (`hard-splash`, `heading-090`, `east-t3`).
`ops --tag ask|feedback|explore`. At most tag `learn` — no new TYPE.
Control/systems patches: `python -m pytest tests/test_physics_warp.py tests/test_hop.py tests/test_pad_science.py -q`.
Lars packet `read:` third path is the **named file** (`hop_factory.py`
inland, `physics_warp.py` warp, `pad.py` pad, `science.py` sit-match).
Not `hop.py` for a factory miss.

Katherine (Flight Dynamics) is disk tape only: `telem --window`, not jsonl.
Rare `ops --tag ask`. Stamp `verify` when waiting for more hops.

One hire may open **many** tickets (Linus: leftover subjects; Gus:
alts; Lars: control fingerprints; Wernher: systems). Skim (envelope).
`--deep` is PNG/craft/tape CLI, not jsonl rows. Never xhigh. **low**
Walt / S4; **high** Mortimer / rsi / org / S1; else **medium**. Packet is skim. Jsonl stays on disk. Packet skim is the **envelope**
(landing + pad/last heading/horiz/pitch + apo + hz + lat/lon/downrange + biome). Do **not**
`read_file` a jsonl. Query `tape.Tape` / `python main.py telem` /
`tickets landing`. `--deep` may name the path as `tape: python main.py
telem …` — it must not dump rows. Default hire is skim (no `--deep`).
**Hank** (parent) runs `attach-run` + `landing` after Commander CLI
exit. The Commander does not.

Bound science is `payload.experiment_id` + `situation` on a science
ticket. Vehicle `capable` is a stamp on a craft ticket. Gene `go` /
`learn` are stamps on a fly ticket. Commander `cli` is fly
`payload.cli` (not `recommended:`). `campaign:` is fly
`payload.campaign` (`uncrewed` → parent starts hop, `commander: none`;
`none` → abort officer). Factory cli is `python main.py hop` — not
`hop-to-water` / `hop-splash`. Ask / itch / friction:
`tickets open --type ops --tag ask|explore|feedback`. Do not emit
`need_*` / `recommended:` / `ask:` as Return keys. Gym `F-014` speech
is the twin ticket id (e.g. T-184).
