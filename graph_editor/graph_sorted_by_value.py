from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from dsviper import AttachmentGetting

from ge import attachments
from ge.data import Graph_GraphKey, Graph_VertexKey, Graph_EdgeKey

if TYPE_CHECKING:
    pass


@dataclass
class SortedEdge:
    """An edge in the sorted graph."""
    edge_key: Graph_EdgeKey
    vertex_key: Graph_VertexKey


@dataclass
class SortedVertex:
    """A vertex in the sorted graph."""
    vertex_key: Graph_VertexKey
    value: int
    edges: list[SortedEdge] = field(default_factory=list)


class GraphSortedByValue:
    """A graph structure sorted by vertex value."""

    def __init__(self):
        self.vertices: dict[Graph_VertexKey, SortedVertex] = {}

    def sorted_vertices(self) -> list[SortedVertex]:
        """Get vertices sorted by value."""
        result = list(self.vertices.values())
        result.sort(key=lambda v: (v.value, v.vertex_key.instance_id()))
        return result

    @staticmethod
    def build(getting: AttachmentGetting, graph_key: Graph_GraphKey) -> GraphSortedByValue:
        """Build a sorted graph from attachments."""
        result = GraphSortedByValue()

        vertex_keys = set()
        edge_keys = set()

        opt_topology = attachments.graph_graph_topology_get(getting, graph_key)
        if opt_topology:
            topology = opt_topology.unwrap()
            vertex_keys = set(topology.vertex_keys)
            edge_keys = set(topology.edge_keys)

        # Add vertices from edge topologies (in case they're not in graph topology)
        for edge_key in edge_keys:
            opt_edge_topo = attachments.graph_edge_topology_get(getting, edge_key)
            if opt_edge_topo:
                edge_topo = opt_edge_topo.unwrap()
                vertex_keys.add(edge_topo.va_key)
                vertex_keys.add(edge_topo.vb_key)

        # Build vertex entries
        for vertex_key in vertex_keys:
            opt_attrs = attachments.graph_vertex_visual_attributes_get(getting, vertex_key)
            value = -1
            if opt_attrs:
                value = opt_attrs.unwrap().value
            result.vertices[vertex_key] = SortedVertex(vertex_key, value)

        # Build edge entries
        for edge_key in edge_keys:
            opt_edge_topo = attachments.graph_edge_topology_get(getting, edge_key)
            if not opt_edge_topo:
                continue

            edge_topo = opt_edge_topo.unwrap()
            va_key = edge_topo.va_key
            vb_key = edge_topo.vb_key

            s_va = result.vertices.get(va_key)
            s_vb = result.vertices.get(vb_key)

            if s_va is None or s_vb is None:
                continue

            # Add edge to the vertex with lower value
            if s_va.value < s_vb.value:
                s_va.edges.append(SortedEdge(edge_key, vb_key))
            else:
                s_vb.edges.append(SortedEdge(edge_key, va_key))

        # Sort edges within each vertex
        for vertex in result.vertices.values():
            vertex.edges.sort(key=lambda e: result.vertices[e.vertex_key].value)

        return result
