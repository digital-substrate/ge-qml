from dsviper import AttachmentMutating

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_VertexKey,
    Graph_GraphTopology,
    Graph_GraphSelection,
    Graph_Position,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey)

from model import vertex as model_vertex
from model import edge as model_edge
from model import random as model_random


def create_with_missing_vertex(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Create a graph with missing vertices (intentionally buggy for testing)."""
    pos0 = Graph_Position()
    pos0.x, pos0.y = 100, 100
    pos1 = Graph_Position()
    pos1.x, pos1.y = 200, 100
    pos2 = Graph_Position()
    pos2.x, pos2.y = 200, 200
    pos3 = Graph_Position()
    pos3.x, pos3.y = 100, 200

    v0 = model_vertex.create(attachment_mutating, 1, pos0, model_random.make_color())
    v1 = model_vertex.create(attachment_mutating, 2, pos1, model_random.make_color())
    v2 = model_vertex.create(attachment_mutating, 3, pos2, model_random.make_color())
    v3 = model_vertex.create(attachment_mutating, 4, pos3, model_random.make_color())

    e0 = model_edge.create(attachment_mutating, v0, v1)
    e1 = model_edge.create(attachment_mutating, v1, v2)
    e2 = model_edge.create(attachment_mutating, v2, v3)
    e3 = model_edge.create(attachment_mutating, v3, v0)

    # Introduce the bug: only include v0 and v1 in topology, but all edges
    topology = Graph_GraphTopology()
    topology.vertex_keys = Set_Graph_VertexKey()
    topology.vertex_keys.add(v0)
    topology.vertex_keys.add(v1)
    topology.edge_keys = Set_Graph_EdgeKey()
    topology.edge_keys.add(e0)
    topology.edge_keys.add(e1)
    topology.edge_keys.add(e2)
    topology.edge_keys.add(e3)

    attachments.graph_graph_topology_set(attachment_mutating, graph_key, topology)
    attachments.graph_graph_selection_set(attachment_mutating, graph_key, Graph_GraphSelection())


def create_with_missing_vertex_properties(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Create a graph with vertices missing their properties (intentionally buggy)."""
    # Create vertices without properties (just keys)
    v0 = Graph_VertexKey.create()
    v1 = Graph_VertexKey.create()
    v2 = Graph_VertexKey.create()
    v3 = Graph_VertexKey.create()

    e0 = model_edge.create(attachment_mutating, v0, v1)
    e1 = model_edge.create(attachment_mutating, v1, v2)
    e2 = model_edge.create(attachment_mutating, v2, v3)
    e3 = model_edge.create(attachment_mutating, v3, v0)

    # Create some valid vertices
    pos4 = Graph_Position()
    pos4.x, pos4.y = 100, 100
    pos5 = Graph_Position()
    pos5.x, pos5.y = 200, 100
    pos6 = Graph_Position()
    pos6.x, pos6.y = 300, 150

    v4 = model_vertex.create(attachment_mutating, 1, pos4, model_random.make_color())
    v5 = model_vertex.create(attachment_mutating, 2, pos5, model_random.make_color())
    v6 = model_vertex.create(attachment_mutating, 3, pos6, model_random.make_color())

    e4 = model_edge.create(attachment_mutating, v4, v5)
    e5 = model_edge.create(attachment_mutating, v5, v6)

    # Mix valid and invalid vertices/edges in topology
    topology = Graph_GraphTopology()
    topology.vertex_keys = Set_Graph_VertexKey()
    topology.vertex_keys.add(v0)
    topology.vertex_keys.add(v1)
    topology.vertex_keys.add(v4)
    topology.vertex_keys.add(v5)
    topology.edge_keys = Set_Graph_EdgeKey()
    topology.edge_keys.add(e0)
    topology.edge_keys.add(e1)
    topology.edge_keys.add(e2)
    topology.edge_keys.add(e3)
    topology.edge_keys.add(e4)
    topology.edge_keys.add(e5)

    attachments.graph_graph_topology_set(attachment_mutating, graph_key, topology)
    attachments.graph_graph_selection_set(attachment_mutating, graph_key, Graph_GraphSelection())


def create_with_error(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Create a graph and then raise an error (for testing error handling)."""
    pos0 = Graph_Position()
    pos0.x, pos0.y = 100, 100
    pos1 = Graph_Position()
    pos1.x, pos1.y = 200, 100

    v0 = model_vertex.add(attachment_mutating, graph_key, 1, pos0, model_random.make_color())
    v1 = model_vertex.add(attachment_mutating, graph_key, 2, pos1, model_random.make_color())
    model_edge.add(attachment_mutating, graph_key, v0, v1)

    raise RuntimeError("This is a voluntary crash but without any consequence.")
