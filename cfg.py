"""KSP ConfigNode text (``.craft``, ``part.cfg``). Order-preserving, duplicate keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CfgNode:
    name: str = ""
    values: list[tuple[str, str]] = field(default_factory=list)
    children: list[CfgNode] = field(default_factory=list)

    def get(self, key: str, default: str | None = None) -> str | None:
        for k, v in self.values:
            if k == key:
                return v
        return default

    def get_all(self, key: str) -> list[str]:
        return [v for k, v in self.values if k == key]

    def set(self, key: str, value: str) -> None:
        for i, (k, _v) in enumerate(self.values):
            if k == key:
                self.values[i] = (key, value)
                return
        self.values.append((key, value))

    def add(self, key: str, value: str) -> None:
        self.values.append((key, value))

    def of(self, name: str) -> list[CfgNode]:
        return [c for c in self.children if c.name == name]

    def dumps(self, *, root: bool = False) -> str:
        lines: list[str] = []
        self._write(lines, indent=0, wrapped=not root)
        return "\n".join(lines) + "\n"

    def _write(self, lines: list[str], indent: int, wrapped: bool) -> None:
        pad = "\t" * indent
        if wrapped:
            lines.append(f"{pad}{self.name}")
            lines.append(f"{pad}{{")
            inner = indent + 1
        else:
            inner = indent
        ipad = "\t" * inner
        for key, value in self.values:
            lines.append(f"{ipad}{key} = {value}")
        for child in self.children:
            child._write(lines, inner, wrapped=True)
        if wrapped:
            lines.append(f"{pad}}}")


def loads(text: str) -> CfgNode:
    text = text.lstrip("\ufeff")
    raw = text.splitlines()
    i = 0

    def skip_empty() -> None:
        nonlocal i
        while i < len(raw):
            s = raw[i].strip()
            if not s or s.startswith("//"):
                i += 1
                continue
            break

    def parse_block(name: str) -> CfgNode:
        nonlocal i
        node = CfgNode(name=name)
        while i < len(raw):
            skip_empty()
            if i >= len(raw):
                break
            line = raw[i].strip()
            if line.startswith("}"):
                i += 1
                return node
            if line.endswith("{") and "=" not in line.split("{")[0]:
                header = line[: line.index("{")].strip()
                i += 1
                node.children.append(parse_block(header))
                continue
            if "=" in line:
                key, _, rest = line.partition("=")
                node.values.append((key.strip(), rest.strip()))
                i += 1
                continue
            # node name, brace on the next line
            child_name = line
            i += 1
            skip_empty()
            if i >= len(raw) or not raw[i].strip().startswith("{"):
                raise ValueError(f"Expected '{{' after {child_name!r} (line {i + 1})")
            i += 1
            node.children.append(parse_block(child_name))
        return node

    root = CfgNode(name="")
    while i < len(raw):
        skip_empty()
        if i >= len(raw):
            break
        line = raw[i].strip()
        if line.startswith("}"):
            raise ValueError(f"Unexpected '}}' at line {i + 1}")
        if line.endswith("{") and "=" not in line.split("{")[0]:
            header = line[: line.index("{")].strip()
            i += 1
            root.children.append(parse_block(header))
            continue
        if "=" in line:
            key, _, rest = line.partition("=")
            root.values.append((key.strip(), rest.strip()))
            i += 1
            continue
        child_name = line
        i += 1
        skip_empty()
        if i >= len(raw) or not raw[i].strip().startswith("{"):
            raise ValueError(f"Expected '{{' after {child_name!r} (line {i + 1})")
        i += 1
        root.children.append(parse_block(child_name))
    return root


def load(path: str | Path) -> CfgNode:
    return loads(Path(path).read_text(encoding="utf-8", errors="replace"))


def dump(node: CfgNode, path: str | Path, *, root: bool = True) -> None:
    Path(path).write_text(node.dumps(root=root), encoding="utf-8")
