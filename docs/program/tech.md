# Claimed tech

Do not inventory parts here. Query the live save:

```bash
python main.py world
python main.py tech
python main.py tech start
python main.py tech-unlock engineering101
python main.py parts --unlocked
python main.py parts --node basicRocketry
```

kRPC 0.6 has no RD-node list and no UnlockTech. `world.py` reads GameData
(post-MM ConfigCache + the save's `TechTreeUrl`) and
`saves/<save>/persistent.sfs` R&D. The buy CLI is `tech-unlock` (opens
R&D, spends if a purchase RPC exists). Query stays `python main.py tech`.

Canonical install `~/Games/KSP-rss`, save `letsgrok`. Honor PBC: if `parts --unlocked` does not list a pod, it
is locked.
