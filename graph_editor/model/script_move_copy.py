from dsviper import AttachmentMutating

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_VertexVisualAttributes,
    Graph_Vertex2DAttributes,
    Graph_EdgeTopology,
    Graph_Position,
    Graph_Color,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey,
)

from render.graph import MoveCopyData


def run(attachment_mutating: AttachmentMutating,
        graph_key: Graph_GraphKey,
        move_copy_data: MoveCopyData,
        offset: Graph_Position) -> None:

    vertex_keys = Set_Graph_VertexKey()
    for vertex_key, render_vertex in move_copy_data.vertices.items():
        color = Graph_Color()
        color.red = render_vertex.color.redF()
        color.green = render_vertex.color.greenF()
        color.blue = render_vertex.color.blueF()

        visual_attributes = Graph_VertexVisualAttributes()
        visual_attributes.value = render_vertex.value
        visual_attributes.color = color
        attachments.graph_vertex_visual_attributes_set(attachment_mutating, vertex_key, visual_attributes)

        position = Graph_Position()
        position.x = render_vertex.position.x() + offset.x
        position.y = render_vertex.position.y() + offset.y
        render_attributes = Graph_Vertex2DAttributes()
        render_attributes.position = position
        attachments.graph_vertex_render_2d_attributes_set(attachment_mutating, vertex_key, render_attributes)

        vertex_keys.add(vertex_key)

    edge_keys = Set_Graph_EdgeKey()
    for edge_key, render_edge in move_copy_data.edges.items():
        topology = Graph_EdgeTopology()
        topology.va_key = render_edge.va.vertex_key
        topology.vb_key = render_edge.vb.vertex_key
        attachments.graph_edge_topology_set(attachment_mutating, edge_key, topology)

        edge_keys.add(edge_key)

    attachments.graph_graph_topology_union_vertex_keys(attachment_mutating, graph_key, vertex_keys)
    attachments.graph_graph_topology_union_edge_keys(attachment_mutating, graph_key, edge_keys)
