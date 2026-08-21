# Tickets — spawn brief

The board is the bus. Not `need_*`. Not science.md cards. Not I-NNN
as live work. Open tickets. Packet is how you read them.

```
python main.py tickets inbox --desk <you>
python main.py tickets packet T-NNN            # skim (no jsonl)
python main.py tickets packet T-NNN --deep     # jsonl / PNG / craft
python main.py tickets open --type science --category science_opportunity \
  --title "…" --severity S3 --priority P1 --desk linus --tag splash --tag goo
python main.py tickets tag T-NNN --add hard-splash
python main.py tickets attach-run T-NNN --path docs/missions/jebediah/logs/<run>.jsonl
python main.py tickets landing T-NNN           # one-line impact class
```

**Categories:** `craft` `science_opportunity` `bug` `improvement`
`flight` `recover` `org` `control` `systems` `press` `ops`.

**Tags:** free lowercase (`hard-splash`, `heading-090`, `east-t3`).

One hire may open **many** tickets (Linus: leftover subjects; Gus:
alts; Lars: control fingerprints). Skim unless reasoning is **high**.
Never xhigh. Mortimer is always high. Jsonl stays `--deep`. Landing
class is a skim line on the fly ticket after `attach-run`.

Bound science is `payload.experiment_id` + `situation` on a science
ticket. Vehicle `capable` is a stamp on a craft ticket. Gene `go` is
a stamp on a fly ticket.
