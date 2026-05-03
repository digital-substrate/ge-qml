from dsviper import AttachmentMutating

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_VertexKey,
    Graph_VertexVisualAttributes,
    Graph_Vertex2DAttributes,
    Graph_Position,
    Graph_Color,
    Set_Graph_VertexKey)


def create(attachment_mutating: AttachmentMutating,
           value: int,
           position: Graph_Position,
           color: Graph_Color) -> Graph_VertexKey:

    vertex_key = Graph_VertexKey.create()

    visual_attributes = Graph_VertexVisualAttributes()
    visual_attributes.value = value
    visual_attributes.color = color
    attachments.graph_vertex_visual_attributes_set(attachment_mutating, vertex_key, visual_attributes)

    render_attributes = Graph_Vertex2DAttributes()
    render_attributes.position = position
    attachments.graph_vertex_render_2d_attributes_set(attachment_mutating, vertex_key, render_attributes)

    return vertex_key


def add(attachment_mutating: AttachmentMutating,
        graph_key: Graph_GraphKey,
        value: int,
        position: Graph_Position,
        color: Graph_Color) -> Graph_VertexKey:

    vertex_key = create(attachment_mutating, value, position, color)

    vertex_keys = Set_Graph_VertexKey()
    vertex_keys.add(vertex_key)
    attachments.graph_graph_topology_union_vertex_keys(attachment_mutating, graph_key, vertex_keys)

    return vertex_key
