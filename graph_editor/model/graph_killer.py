from dsviper import AttachmentMutating

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_Position,
    Graph_GraphTopology,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey)

from model import vertex as model_vertex
from model import random as model_random


def shoot(attachment_mutating: AttachmentMutating,
          graph_key: Graph_GraphKey,
          vertex_count: int) -> None:
    """Create many vertices and then keep only the last one (kills all previous work)."""
    position = Graph_Position()
    position.x = 100
    position.y = 100
    color = model_random.make_color()

    for _ in range(vertex_count):
        model_vertex.add(attachment_mutating, graph_key, 42, position, color)

    killer = model_vertex.add(attachment_mutating, graph_key, 42, position, color)

    attachments.graph_graph_description_set_name(attachment_mutating, graph_key, "They have killed Commit!")

    topology = Graph_GraphTopology()
    topology.vertex_keys = Set_Graph_VertexKey()
    topology.vertex_keys.add(killer)
    topology.edge_keys = Set_Graph_EdgeKey()
    attachments.graph_graph_topology_set(attachment_mutating, graph_key, topology)
