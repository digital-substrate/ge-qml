from dsviper import AttachmentMutating, AttachmentGetting

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_EdgeKey,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey)

from model import tools


def select(attachment_mutating: AttachmentMutating,
           graph_key: Graph_GraphKey,
           edge_key: Graph_EdgeKey) -> None:
    """Select a single edge, deselecting all others."""
    vertex_keys = Set_Graph_VertexKey()
    edge_keys = Set_Graph_EdgeKey()

    opt = attachments.graph_graph_selection_get(attachment_mutating, graph_key)
    if opt:
        selection = opt.unwrap()
        vertex_keys = selection.vertex_keys
        edge_keys = selection.edge_keys

    attachments.graph_graph_selection_subtract_edge_keys(attachment_mutating, graph_key, edge_keys)

    new_selection = Set_Graph_EdgeKey()
    new_selection.add(edge_key)
    attachments.graph_graph_selection_union_edge_keys(attachment_mutating, graph_key, new_selection)
    attachments.graph_graph_selection_subtract_vertex_keys(attachment_mutating, graph_key, vertex_keys)


def combine(attachment_mutating: AttachmentMutating,
            graph_key: Graph_GraphKey,
            edge_key: Graph_EdgeKey,
            selected: bool) -> None:
    """Add or remove an edge from the selection."""
    edge_keys = Set_Graph_EdgeKey()
    edge_keys.add(edge_key)

    if selected:
        attachments.graph_graph_selection_union_edge_keys(attachment_mutating, graph_key, edge_keys)
    else:
        attachments.graph_graph_selection_subtract_edge_keys(attachment_mutating, graph_key, edge_keys)


def select_all(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Select all edges in the graph."""
    edge_keys = Set_Graph_EdgeKey()
    opt = attachments.graph_graph_topology_get(attachment_mutating, graph_key)
    if opt:
        edge_keys = opt.unwrap().edge_keys

    attachments.graph_graph_selection_union_edge_keys(attachment_mutating, graph_key, edge_keys)


def deselect_all(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Deselect all edges in the graph."""
    edge_keys = Set_Graph_EdgeKey()
    opt = attachments.graph_graph_selection_get(attachment_mutating, graph_key)
    if opt:
        edge_keys = opt.unwrap().edge_keys

    attachments.graph_graph_selection_subtract_edge_keys(attachment_mutating, graph_key, edge_keys)


def invert(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Invert the edge selection."""
    edge_keys = Set_Graph_EdgeKey()
    opt = attachments.graph_graph_topology_get(attachment_mutating, graph_key)
    if opt:
        edge_keys = opt.unwrap().edge_keys

    selected_edge_keys = Set_Graph_EdgeKey()
    opt = attachments.graph_graph_selection_get(attachment_mutating, graph_key)
    if opt:
        selected_edge_keys = opt.unwrap().edge_keys

    attachments.graph_graph_selection_subtract_edge_keys(attachment_mutating, graph_key, selected_edge_keys)
    attachments.graph_graph_selection_union_edge_keys(
        attachment_mutating, graph_key, tools.difference_edge_keys(edge_keys, selected_edge_keys))


def selected(attachment_getting: AttachmentGetting, graph_key: Graph_GraphKey) -> Set_Graph_EdgeKey:
    """Get the set of selected edges."""
    opt = attachments.graph_graph_selection_get(attachment_getting, graph_key)
    if opt:
        return opt.unwrap().edge_keys
    return Set_Graph_EdgeKey()


def has_selected(attachment_getting: AttachmentGetting, graph_key: Graph_GraphKey) -> bool:
    """Check if any edges are selected."""
    return len(selected(attachment_getting, graph_key)) > 0
