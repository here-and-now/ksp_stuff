# Tickets — spawn brief

Packet is `docs/program/desk.md` + `tickets packet T-NNN` stdout + this
page. Not BOARD.md. Not a jsonl novel. First command is inbox, then the
stamp or CLI on the packet.

```
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
python main.py tickets from-need --need need_stack --title "…"
```

**Categories:** `craft` `science_opportunity` `bug` `improvement`
`flight` `recover` `org` `control` `systems` `press` `ops`.

**Tags:** free lowercase (`hard-splash`, `heading-090`, `east-t3`).
`ops --tag ask|feedback|explore`. At most tag `learn` — no new TYPE.

One hire may open **many** tickets (Linus: leftover subjects; Gus:
alts; Lars: control fingerprints; Wernher: systems). Skim (envelope).
`--deep` is PNG/craft/tape CLI, not jsonl rows. Never xhigh. Desk
floors (Os 2026-08-23): Jeb/Lars **low**, Wernher **medium**, Mortimer
**medium**, Gene **medium**. Packet is skim. Jsonl stays on disk. Packet skim is the **envelope**
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
`payload.campaign` (`uncrewed`/`none`). Ask / itch / friction:
`tickets open --type ops --tag ask|explore|feedback`. Leftover `need_*`
→ `from-need` (shim). Never in a Return fence.
