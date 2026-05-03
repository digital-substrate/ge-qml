from dsviper import AttachmentMutating, AttachmentGetting

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_VertexKey,
    Graph_EdgeKey,
    Graph_Position,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey,
)

from model import random as model_random


def referenced_keys(attachment_getting: AttachmentGetting,
                    graph_key: Graph_GraphKey) -> Set_Graph_VertexKey:
    """Get all vertex keys referenced by the graph (including from edges)."""
    vertex_keys = Set_Graph_VertexKey()
    edge_keys = Set_Graph_EdgeKey()

    opt = attachments.graph_graph_topology_get(attachment_getting, graph_key)
    if opt:
        topology = opt.unwrap()
        vertex_keys = topology.vertex_keys
        edge_keys = topology.edge_keys

    for edge_key in edge_keys:
        opt_edge = attachments.graph_edge_topology_get(attachment_getting, edge_key)
        if opt_edge:
            edge_topo = opt_edge.unwrap()
            vertex_keys.add(edge_topo.va_key)
            vertex_keys.add(edge_topo.vb_key)

    return vertex_keys


def increment_value(attachment_mutating: AttachmentMutating,
                    vertex_keys: Set_Graph_VertexKey,
                    increment: int) -> None:
    """Increment the value of vertices."""
    color = model_random.make_color()
    for vertex_key in vertex_keys:
        opt = attachments.graph_vertex_visual_attributes_get(attachment_mutating, vertex_key)
        if opt:
            attrs = opt.unwrap()
            attachments.graph_vertex_visual_attributes_set_value(
                attachment_mutating, vertex_key, attrs.value + increment
            )
            attachments.graph_vertex_visual_attributes_set_color(
                attachment_mutating, vertex_key, color
            )


def move(attachment_mutating: AttachmentMutating,
         vertex_keys, offset: Graph_Position) -> None:
    """Move vertices by an offset."""
    for vertex_key in vertex_keys:
        opt = attachments.graph_vertex_render_2d_attributes_get(attachment_mutating, vertex_key)
        if opt:
            attrs = opt.unwrap()
            position = Graph_Position()
            position.x = attrs.position.x + offset.x
            position.y = attrs.position.y + offset.y
            attachments.graph_vertex_render_2d_attributes_set_position(
                attachment_mutating, vertex_key, position
            )
