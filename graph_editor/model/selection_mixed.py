from dsviper import AttachmentMutating, AttachmentGetting

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey)

from model import tools


def select_all(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Select all vertices and edges in the graph."""
    vertex_keys = Set_Graph_VertexKey()
    edge_keys = Set_Graph_EdgeKey()

    opt = attachments.graph_graph_topology_get(attachment_mutating, graph_key)
    if opt:
        topology = opt.unwrap()
        vertex_keys = topology.vertex_keys
        edge_keys = topology.edge_keys

    attachments.graph_graph_selection_union_vertex_keys(attachment_mutating, graph_key, vertex_keys)
    attachments.graph_graph_selection_union_edge_keys(attachment_mutating, graph_key, edge_keys)


def deselect_all(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Deselect all vertices and edges in the graph."""
    vertex_keys = Set_Graph_VertexKey()
    edge_keys = Set_Graph_EdgeKey()

    opt = attachments.graph_graph_topology_get(attachment_mutating, graph_key)
    if opt:
        topology = opt.unwrap()
        vertex_keys = topology.vertex_keys
        edge_keys = topology.edge_keys

    attachments.graph_graph_selection_subtract_vertex_keys(attachment_mutating, graph_key, vertex_keys)
    attachments.graph_graph_selection_subtract_edge_keys(attachment_mutating, graph_key, edge_keys)


def invert(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Invert the selection of all vertices and edges."""
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

    attachments.graph_graph_selection_subtract_vertex_keys(attachment_mutating, graph_key, selected_vertex_keys)
    attachments.graph_graph_selection_union_vertex_keys(
        attachment_mutating, graph_key, tools.difference_vertex_keys(vertex_keys, selected_vertex_keys))
    attachments.graph_graph_selection_subtract_edge_keys(attachment_mutating, graph_key, selected_edge_keys)
    attachments.graph_graph_selection_union_edge_keys(
        attachment_mutating, graph_key, tools.difference_edge_keys(edge_keys, selected_edge_keys))


def set_selection(attachment_mutating: AttachmentMutating,
                  graph_key: Graph_GraphKey,
                  vertex_keys: Set_Graph_VertexKey,
                  edge_keys: Set_Graph_EdgeKey) -> None:
    """Set the selection to specific vertices and edges."""
    selected_vertex_keys = Set_Graph_VertexKey()
    selected_edge_keys = Set_Graph_EdgeKey()

    opt = attachments.graph_graph_selection_get(attachment_mutating, graph_key)
    if opt:
        selection = opt.unwrap()
        selected_vertex_keys = selection.vertex_keys
        selected_edge_keys = selection.edge_keys

    attachments.graph_graph_selection_subtract_vertex_keys(attachment_mutating, graph_key, selected_vertex_keys)
    attachments.graph_graph_selection_union_vertex_keys(attachment_mutating, graph_key, vertex_keys)
    attachments.graph_graph_selection_subtract_edge_keys(attachment_mutating, graph_key, selected_edge_keys)
    attachments.graph_graph_selection_union_edge_keys(attachment_mutating, graph_key, edge_keys)


def has_selected(attachment_getting: AttachmentGetting, graph_key: Graph_GraphKey) -> bool:
    """Check if any vertices or edges are selected."""
    opt = attachments.graph_graph_selection_get(attachment_getting, graph_key)
    if opt:
        selection = opt.unwrap()
        return len(selection.vertex_keys) > 0 or len(selection.edge_keys) > 0
    return False
