"""Spend banked science on a CTT node. Not a pad sit. Not GameData.

kRPC 0.6: ``GameScene.research_and_development`` opens the facility;
``SpaceCenter.science`` is ``ResearchAndDevelopment.Instance.Science``
(get). There is no UnlockTech RPC. This block validates the node on
disk, opens R&D, invokes a purchase RPC if one exists, and aborts
instead of editing GameData or the save. F-013: this is the unlock,
not a Geiger dwell.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

from hangar import game_scene, go_space_center
from telem import MissionAbort
from world import TechNode, World, WorldError, load_world

log = logging.getLogger("kspstuff")

# 0.6 has none of these. Probe so a later service can buy without a new block.
_PURCHASE_RPCS = (
    ("SpaceCenter", "UnlockTech"),
    ("SpaceCenter", "ResearchTech"),
    ("SpaceCenter", "PurchaseTech"),
    ("SpaceCenter", "UnlockNode"),
    ("SpaceCenter", "PurchaseNode"),
)
_ATTRS = ("unlock_tech", "research_tech", "purchase_tech")
_SCENE_RD = "research_and_development"
_EPS = 0.05


def _say(msg: str, on_log: Callable[[str], None] | None) -> None:
    log.info(msg)
    if on_log:
        on_log(msg)


def plan_node() -> str:
    from phases import _kv

    kv = _kv()
    return (kv.get("tech") or kv.get("unlock") or "").strip()


def resolve_node(node: str | None) -> str:
    nid = (node or plan_node() or "").strip()
    if not nid:
        raise MissionAbort(
            "tech-unlock needs a node (python main.py tech-unlock <id> or plan tech:)"
        )
    return nid


def assert_can_buy(world: World, node_id: str) -> TechNode:
    """Disk tree + save unlocks. Does not spend. Does not write the save."""
    node = world.tree.get(node_id)
    if node is None:
        raise MissionAbort(f"tech-unlock: unknown node {node_id}")
    owned = set(world.research.unlocked)
    if node_id in owned:
        return node
    missing = [p for p in node.parents if p and p not in owned]
    if missing:
        raise MissionAbort(
            f"tech-unlock: parent {','.join(missing)} locked (need before {node_id})"
        )
    return node


def _science(session: Any) -> float:
    try:
        return float(session.space_center.science)
    except Exception as exc:
        raise MissionAbort(f"tech-unlock: SpaceCenter.science unreadable ({exc})") from exc


def go_research(session: Any, *, timeout: float = 45.0) -> None:
    """Open the R&D pseudo-scene. No click. No Hangar."""
    scene = game_scene(session)
    if scene not in {_SCENE_RD, "space_center", "?"}:
        go_space_center(session, timeout=timeout)
    krpc = session.conn.krpc
    rd = getattr(krpc.GameScene, _SCENE_RD, None)
    if rd is None:
        raise MissionAbort("tech-unlock: kRPC has no GameScene.research_and_development")
    krpc.game_scene = rd
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if game_scene(session) == _SCENE_RD:
            try:
                session.space_center = session.conn.space_center
            except Exception:
                pass
            return
        time.sleep(0.1)
    raise MissionAbort(
        f"tech-unlock: timed out waiting for R&D (still {game_scene(session)})"
    )


def _invoke_purchase(session: Any, node_id: str) -> None:
    conn = getattr(session, "conn", None)
    if conn is None:
        raise MissionAbort(
            "tech-unlock: kRPC 0.6 has no UnlockTech (get_Science only; "
            "GameScene.research_and_development opens R&D). "
            "Do not edit GameData or the save."
        )
    types = getattr(conn, "_types", None)
    string_type = getattr(types, "string_type", None) if types is not None else None
    last = "no purchase RPC"
    for svc, proc in _PURCHASE_RPCS:
        try:
            if string_type is not None and hasattr(conn, "_invoke"):
                conn._invoke(svc, proc, [node_id], ["id"], [string_type], None)
            else:
                conn.krpc._invoke(svc, proc, node_id)
            return
        except MissionAbort:
            raise
        except Exception as exc:
            msg = str(exc)
            last = msg
            low = msg.lower()
            if "not found" in low or "does not exist" in low:
                continue
            raise MissionAbort(f"tech-unlock {proc}: {exc}") from exc
    raise MissionAbort(
        "tech-unlock: kRPC 0.6 has no UnlockTech (get_Science only; "
        "GameScene.research_and_development opens R&D). "
        f"Last: {last}. Do not edit GameData or the save."
    )


def spend(session: Any, node_id: str) -> None:
    """Honest purchase: SpaceCenter method if present, else kRPC RPC."""
    sc = session.space_center
    for name in _ATTRS:
        fn = getattr(sc, name, None)
        if callable(fn):
            fn(node_id)
            return
    _invoke_purchase(session, node_id)


def persist(session: Any) -> None:
    """Ask the game to save. Not a Python rewrite of the sfs."""
    sc = session.space_center
    try:
        sc.save("persistent")
    except Exception as exc:
        log.warning("tech-unlock save persistent: %s", exc)


def run_phase(
    session: Any,
    *,
    node: str | None = None,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    nid = resolve_node(node)
    try:
        world = load_world()
    except WorldError as exc:
        raise MissionAbort(f"tech-unlock: {exc}") from exc
    tech = assert_can_buy(world, nid)
    if nid in world.research.unlocked:
        _say(f"tech-unlock skip already {nid}", on_log)
        return f"tech-unlock skip {nid}"
    if abort is not None and abort():
        raise MissionAbort("tech-unlock timeout")
    sci = _science(session)
    if sci + _EPS < tech.cost:
        raise MissionAbort(
            f"tech-unlock: science {sci:.2f} < cost {tech.cost} ({nid})"
        )
    _say(f"tech-unlock {nid} cost={tech.cost} sci={sci:.2f}", on_log)
    go_research(session)
    if abort is not None and abort():
        raise MissionAbort("tech-unlock timeout")
    try:
        spend(session, nid)
        after = _science(session)
        if after > sci - tech.cost + _EPS:
            raise MissionAbort(
                f"tech-unlock did not spend science ({sci:.2f} -> {after:.2f}, "
                f"cost {tech.cost})"
            )
        _say(f"tech-unlock bought {nid} sci={after:.2f}", on_log)
        try:
            go_space_center(session)
        except Exception as exc:
            log.warning("tech-unlock leave R&D: %s", exc)
        persist(session)
        return f"tech-unlock {nid}"
    except Exception:
        try:
            go_space_center(session)
        except Exception:
            pass
        raise


def run_unlock(
    session: Any,
    node: str | None = None,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    return run_phase(session, node=node, on_log=on_log, abort=abort)
