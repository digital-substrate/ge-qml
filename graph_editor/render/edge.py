from __future__ import annotations

from dataclasses import dataclass

from ge.data import Graph_EdgeKey
from .vertex import RenderVertex


@dataclass
class RenderEdge:
    """An edge for rendering."""
    edge_key: Graph_EdgeKey
    va: RenderVertex
    vb: RenderVertex

    def is_valid(self) -> bool:
        return self.va.is_valid and self.vb.is_valid

    @staticmethod
    def make(edge_key: Graph_EdgeKey, va: RenderVertex, vb: RenderVertex) -> RenderEdge:
        return RenderEdge(edge_key, va, vb)

    def __lt__(self, other: RenderEdge) -> bool:
        return str(self.edge_key.instance_id()) < str(other.edge_key.instance_id())
