from dsviper import AttachmentMutating, AttachmentGetting

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_VertexKey,
    Graph_EdgeKey,
    Graph_GraphTopology,
    Graph_GraphSelection,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey,
    Map_string_to_string,
    XArray_string)

from model import tools


def clear(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Clear all topology, selection, comments, and tags from a graph."""
    attachments.graph_graph_topology_set(attachment_mutating, graph_key, Graph_GraphTopology())
    attachments.graph_graph_selection_set(attachment_mutating, graph_key, Graph_GraphSelection())
    attachments.graph_graph_comments_set(attachment_mutating, graph_key, XArray_string())
    attachments.graph_graph_tags_set(attachment_mutating, graph_key, Map_string_to_string())


def remove(attachment_mutating: AttachmentMutating,
           graph_key: Graph_GraphKey,
           vertex_keys: Set_Graph_VertexKey,
           edge_keys: Set_Graph_EdgeKey) -> None:
    """Remove vertices and edges from the graph, including connected edges."""
    topology_edge_keys = Set_Graph_EdgeKey()
    opt = attachments.graph_graph_topology_get(attachment_mutating, graph_key)
    if opt:
        topology_edge_keys = opt.unwrap().edge_keys

    # Find edges connected to removed vertices
    connected_edge_keys = Set_Graph_EdgeKey()
    for vertex_key in vertex_keys:
        for edge_key in topology_edge_keys:
            opt_edge = attachments.graph_edge_topology_get(attachment_mutating, edge_key)
            if not opt_edge:
                continue
            edge = opt_edge.unwrap()
            if edge.va_key == vertex_key or edge.vb_key == vertex_key:
                connected_edge_keys.add(edge_key)

    attachments.graph_graph_topology_subtract_vertex_keys(attachment_mutating, graph_key, vertex_keys)
    all_edges_to_remove = tools.union_edge_keys(edge_keys, connected_edge_keys)
    attachments.graph_graph_topology_subtract_edge_keys(attachment_mutating, graph_key, all_edges_to_remove)


def remove_bugged(attachment_mutating: AttachmentMutating,
                  graph_key: Graph_GraphKey,
                  vertex_keys: Set_Graph_VertexKey) -> None:
    """Remove vertices without removing connected edges (intentionally buggy)."""
    attachments.graph_graph_topology_subtract_vertex_keys(attachment_mutating, graph_key, vertex_keys)


def has_edge(attachment_getting: AttachmentGetting,
             graph_key: Graph_GraphKey,
             va_key: Graph_VertexKey,
             vb_key: Graph_VertexKey) -> Graph_EdgeKey | None:
    """Check if an edge exists between two vertices, return the edge key if found."""
    opt = attachments.graph_graph_topology_get(attachment_getting, graph_key)
    if not opt:
        return None

    topology = opt.unwrap()
    for edge_key in topology.edge_keys:
        opt_edge = attachments.graph_edge_topology_get(attachment_getting, edge_key)
        if not opt_edge:
            continue
        edge = opt_edge.unwrap()

        if ((edge.va_key == va_key and edge.vb_key == vb_key) or
            (edge.va_key == vb_key and edge.vb_key == va_key)):
            return edge_key

    return None


def has_vertices(attachment_getting: AttachmentGetting, graph_key: Graph_GraphKey) -> bool:
    """Check if the graph has any vertices."""
    opt = attachments.graph_graph_topology_get(attachment_getting, graph_key)
    if opt:
        return len(opt.unwrap().vertex_keys) > 0
    return False


def has_edges(attachment_getting: AttachmentGetting, graph_key: Graph_GraphKey) -> bool:
    """Check if the graph has any edges."""
    opt = attachments.graph_graph_topology_get(attachment_getting, graph_key)
    if opt:
        return len(opt.unwrap().edge_keys) > 0
    return False


def has_remaining_edges(attachment_getting: AttachmentGetting, graph_key: Graph_GraphKey) -> bool:
    """Check if there are remaining edges that can be added to the graph."""
    vertex_keys = Set_Graph_VertexKey()
    edge_keys = Set_Graph_EdgeKey()

    opt = attachments.graph_graph_topology_get(attachment_getting, graph_key)
    if opt:
        topology = opt.unwrap()
        vertex_keys = topology.vertex_keys
        edge_keys = topology.edge_keys

    vertex_count = len(vertex_keys)
    max_edges = vertex_count * (vertex_count - 1) // 2
    return vertex_count > 1 and len(edge_keys) < max_edges
