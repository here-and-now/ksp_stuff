# Claimed tech

Do not inventory parts here. Query the live save:

```bash
python main.py world
python main.py tech
python main.py tech start
python main.py parts --unlocked
python main.py parts --node basicRocketry
```

kRPC has no RD-node list. `world.py` reads GameData (post-MM ConfigCache +
the save's `TechTreeUrl`) and `saves/<save>/persistent.sfs` R&D.

Canonical install `~/Games/KSP-rss`, save `letsgrok` (`KSPSTUFF_KSP` /
`KSPSTUFF_SAVE`). Honor PBC: if `parts --unlocked` does not list a pod, it
is locked.
