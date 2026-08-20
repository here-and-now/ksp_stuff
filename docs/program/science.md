# Linus board — science program

Query first, then write opportunities. Do not copy Squad Start from memory.

```bash
python main.py world
python main.py parts --unlocked --module Experiment
python main.py parts --search goo
python main.py science
```

Kerbalism Default is on: experiments are `MODULE Experiment` + `HardDrive`
(time + EC), not stock `Experiment.run` until a live probe says otherwise.
Samples stay on the vessel — recover the HD. Do not transmit this program
yet (omni-only, no RA planner).

PBC: early science is unmanned. Mk1 / crew report are future nodes — check
`python main.py tech mk1` / `parts --search mk1`.

Pad craft `kspstuff-pad-pbc`: `mysteryGoo` on `GooExperiment`,
`temperatureScan` on `sensorThermometer`. Recover the HD. Do not transmit.

After Gus `capable: yes`, bind to **that** craft in seated `science.md`.
Each line needs `experiment_id`, `part`, `duration_s`, `ec_rate`. Card
`recover_banks: yes|no`. If the craft lacks the part: `need_builder`.
Gus sizes packs from `ec_rate × duration_s` before signing.
