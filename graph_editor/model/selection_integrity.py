from dsviper import AttachmentMutating

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey,
)

from model import tools


def restore(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Restore selection to only include vertices and edges that exist in topology."""
    vertex_keys = Set_Graph_VertexKey()
    edge_keys = Set_Graph_EdgeKey()

    opt = attachments.graph_graph_topology_get(attachment_mutating, graph_key)
    if opt:
        topology = opt.unwrap()
        vertex_keys = topology.vertex_keys
        edge_keys = topology.edge_keys

    selected_vertex_keys = Set_Graph_VertexKey()
    selected_edge_keys = Set_Graph_EdgeKey()

    opt = attachments.graph_graph_selection_get(attachment_mutating, graph_key)
    if opt:
        selection = opt.unwrap()
        selected_vertex_keys = selection.vertex_keys
        selected_edge_keys = selection.edge_keys

    restored_vertex_keys = tools.intersection_vertex_keys(selected_vertex_keys, vertex_keys)
    restored_edge_keys = tools.intersection_edge_keys(selected_edge_keys, edge_keys)

    attachments.graph_graph_selection_subtract_vertex_keys(attachment_mutating, graph_key, selected_vertex_keys)
    attachments.graph_graph_selection_union_vertex_keys(attachment_mutating, graph_key, restored_vertex_keys)
    attachments.graph_graph_selection_subtract_edge_keys(attachment_mutating, graph_key, selected_edge_keys)
    attachments.graph_graph_selection_union_edge_keys(attachment_mutating, graph_key, restored_edge_keys)
