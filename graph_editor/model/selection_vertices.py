from dsviper import AttachmentMutating, AttachmentGetting

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_VertexKey,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey)

from model import tools


def select(attachment_mutating: AttachmentMutating,
           graph_key: Graph_GraphKey,
           vertex_key: Graph_VertexKey) -> None:
    """Select a single vertex, deselecting all others."""
    selected_vertex_keys = Set_Graph_VertexKey()
    selected_edge_keys = Set_Graph_EdgeKey()

    opt = attachments.graph_graph_selection_get(attachment_mutating, graph_key)
    if opt:
        selection = opt.unwrap()
        selected_vertex_keys = selection.vertex_keys
        selected_edge_keys = selection.edge_keys

    attachments.graph_graph_selection_subtract_vertex_keys(attachment_mutating, graph_key, selected_vertex_keys)

    new_selection = Set_Graph_VertexKey()
    new_selection.add(vertex_key)
    attachments.graph_graph_selection_union_vertex_keys(attachment_mutating, graph_key, new_selection)
    attachments.graph_graph_selection_subtract_edge_keys(attachment_mutating, graph_key, selected_edge_keys)


def select_multiple(attachment_mutating: AttachmentMutating,
                    graph_key: Graph_GraphKey,
                    vertex_keys: Set_Graph_VertexKey) -> None:
    """Select multiple vertices, deselecting all others."""
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


def combine(attachment_mutating: AttachmentMutating,
            graph_key: Graph_GraphKey,
            vertex_key: Graph_VertexKey,
            selected: bool) -> None:
    """Add or remove a vertex from the selection."""
    vertex_keys = Set_Graph_VertexKey()
    vertex_keys.add(vertex_key)

    if selected:
        attachments.graph_graph_selection_union_vertex_keys(attachment_mutating, graph_key, vertex_keys)
    else:
        attachments.graph_graph_selection_subtract_vertex_keys(attachment_mutating, graph_key, vertex_keys)


def select_all(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Select all vertices in the graph."""
    vertex_keys = Set_Graph_VertexKey()
    opt = attachments.graph_graph_topology_get(attachment_mutating, graph_key)
    if opt:
        vertex_keys = opt.unwrap().vertex_keys

    attachments.graph_graph_selection_union_vertex_keys(attachment_mutating, graph_key, vertex_keys)


def deselect_all(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Deselect all vertices in the graph."""
    vertex_keys = Set_Graph_VertexKey()
    opt = attachments.graph_graph_topology_get(attachment_mutating, graph_key)
    if opt:
        vertex_keys = opt.unwrap().vertex_keys

    attachments.graph_graph_selection_subtract_vertex_keys(attachment_mutating, graph_key, vertex_keys)


def invert(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Invert the vertex selection."""
    vertex_keys = Set_Graph_VertexKey()
    opt = attachments.graph_graph_topology_get(attachment_mutating, graph_key)
    if opt:
        vertex_keys = opt.unwrap().vertex_keys

    selected_vertex_keys = Set_Graph_VertexKey()
    opt = attachments.graph_graph_selection_get(attachment_mutating, graph_key)
    if opt:
        selected_vertex_keys = opt.unwrap().vertex_keys

    attachments.graph_graph_selection_subtract_vertex_keys(attachment_mutating, graph_key, vertex_keys)
    attachments.graph_graph_selection_union_vertex_keys(
        attachment_mutating, graph_key, tools.difference_vertex_keys(vertex_keys, selected_vertex_keys))


def restore(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Restore selected vertices to the topology."""
    selected_vertex_keys = Set_Graph_VertexKey()
    opt = attachments.graph_graph_selection_get(attachment_mutating, graph_key)
    if opt:
        selected_vertex_keys = opt.unwrap().vertex_keys

    attachments.graph_graph_topology_union_vertex_keys(attachment_mutating, graph_key, selected_vertex_keys)


def increment_value(attachment_mutating: AttachmentMutating,
                    graph_key: Graph_GraphKey,
                    increment: int) -> None:
    """Increment the value of all selected vertices."""
    from model import random as model_random

    selected_vertex_keys = Set_Graph_VertexKey()
    opt = attachments.graph_graph_selection_get(attachment_mutating, graph_key)
    if opt:
        selected_vertex_keys = opt.unwrap().vertex_keys

    color = model_random.make_color()
    for vertex_key in selected_vertex_keys:
        opt_attr = attachments.graph_vertex_visual_attributes_get(attachment_mutating, vertex_key)
        if opt_attr:
            attrs = opt_attr.unwrap()
            attachments.graph_vertex_visual_attributes_set_value(attachment_mutating, vertex_key, attrs.value + increment)
            attachments.graph_vertex_visual_attributes_set_color(attachment_mutating, vertex_key, color)


def has_selected(attachment_getting: AttachmentGetting, graph_key: Graph_GraphKey) -> bool:
    """Check if any vertices are selected."""
    return len(selected(attachment_getting, graph_key)) > 0


def selected(attachment_getting: AttachmentGetting, graph_key: Graph_GraphKey) -> Set_Graph_VertexKey:
    """Get the set of selected vertices."""
    opt = attachments.graph_graph_selection_get(attachment_getting, graph_key)
    if opt:
        return opt.unwrap().vertex_keys
    return Set_Graph_VertexKey()
