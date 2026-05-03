from dsviper import AttachmentGetting

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_VertexKey,
    Graph_EdgeKey,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey)


def next_vertex_value(attachment_getting: AttachmentGetting, graph_key: Graph_GraphKey) -> int:
    """Get the next vertex value (max + 1) for a graph."""
    result = 0

    opt = attachments.graph_graph_topology_get(attachment_getting, graph_key)
    if not opt:
        return result + 1

    topology = opt.unwrap()
    for vertex_key in topology.vertex_keys:
        opt_attr = attachments.graph_vertex_visual_attributes_get(attachment_getting, vertex_key)
        if opt_attr:
            attrs = opt_attr.unwrap()
            result = max(result, attrs.value)

    return result + 1


def vertex_label(attachment_getting: AttachmentGetting, vertex_key: Graph_VertexKey) -> str:
    """Get the label for a vertex (its value as string)."""
    opt = attachments.graph_vertex_visual_attributes_get(attachment_getting, vertex_key)
    if opt:
        return str(opt.unwrap().value)
    return "?"


def edge_label_from_vertices(attachment_getting: AttachmentGetting,
                             va_key: Graph_VertexKey,
                             vb_key: Graph_VertexKey) -> str:
    """Get the label for an edge from its vertex keys."""
    va = vertex_label(attachment_getting, va_key)
    vb = vertex_label(attachment_getting, vb_key)
    return f"{va} - {vb}"


def edge_label(attachment_getting: AttachmentGetting, edge_key: Graph_EdgeKey) -> str:
    """Get the label for an edge."""
    opt = attachments.graph_edge_topology_get(attachment_getting, edge_key)
    if not opt:
        return "?-?"
    edge = opt.unwrap()
    return edge_label_from_vertices(attachment_getting, edge.va_key, edge.vb_key)


def safe_next_vertex_value(attachment_getting: AttachmentGetting, graph_key: Graph_GraphKey) -> int:
    """Safe version of next_vertex_value that returns 1 on error."""
    try:
        return next_vertex_value(attachment_getting, graph_key)
    except Exception:
        return 1


def safe_edge_label(attachment_getting: AttachmentGetting, edge_key: Graph_EdgeKey) -> str:
    """Safe version of edge_label that returns '?-?' on error."""
    try:
        return edge_label(attachment_getting, edge_key)
    except Exception:
        return "?-?"


def safe_edge_label_from_vertices(attachment_getting: AttachmentGetting,
                                  va_key: Graph_VertexKey,
                                  vb_key: Graph_VertexKey) -> str:
    """Safe version of edge_label_from_vertices that returns '?-?' on error."""
    try:
        return edge_label_from_vertices(attachment_getting, va_key, vb_key)
    except Exception:
        return "?-?"


def difference_vertex_keys(a: Set_Graph_VertexKey, b: Set_Graph_VertexKey) -> Set_Graph_VertexKey:
    """Return elements in a but not in b."""
    return a - b


def difference_edge_keys(a: Set_Graph_EdgeKey, b: Set_Graph_EdgeKey) -> Set_Graph_EdgeKey:
    """Return elements in a but not in b."""
    return a - b


def intersection_vertex_keys(a: Set_Graph_VertexKey, b: Set_Graph_VertexKey) -> Set_Graph_VertexKey:
    """Return elements in both a and b."""
    return a & b


def intersection_edge_keys(a: Set_Graph_EdgeKey, b: Set_Graph_EdgeKey) -> Set_Graph_EdgeKey:
    """Return elements in both a and b."""
    return a & b


def union_edge_keys(a: Set_Graph_EdgeKey, b: Set_Graph_EdgeKey) -> Set_Graph_EdgeKey:
    """Return elements in a or b."""
    return a | b
