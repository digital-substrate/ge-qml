from dsviper import AttachmentMutating

from ge import attachments
from ge.data import Graph_GraphKey

from model import graph_topology
from model import selection_edges


def delete_selection(attachment_mutating: AttachmentMutating,
                     graph_key: Graph_GraphKey) -> None:
    """Delete selected vertices and edges from the graph."""
    vertex_keys = set()
    edge_keys = set()

    opt = attachments.graph_graph_selection_get(attachment_mutating, graph_key)
    if opt:
        selection = opt.unwrap()
        vertex_keys = selection.vertex_keys
        edge_keys = selection.edge_keys

    graph_topology.remove(attachment_mutating, graph_key, vertex_keys, edge_keys)
    selection_edges.deselect_all(attachment_mutating, graph_key)


def delete_selection_bugged(attachment_mutating: AttachmentMutating,
                            graph_key: Graph_GraphKey) -> None:
    """Delete selected vertices (bugged version for testing)."""
    vertex_keys = set()

    opt = attachments.graph_graph_selection_get(attachment_mutating, graph_key)
    if opt:
        vertex_keys = opt.unwrap().vertex_keys

    graph_topology.remove_bugged(attachment_mutating, graph_key, vertex_keys)
    selection_edges.deselect_all(attachment_mutating, graph_key)
