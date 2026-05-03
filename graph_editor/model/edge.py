from dsviper import AttachmentMutating

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_VertexKey,
    Graph_EdgeKey,
    Graph_EdgeTopology,
    Set_Graph_EdgeKey)


def create(attachment_mutating: AttachmentMutating,
           va_key: Graph_VertexKey,
           vb_key: Graph_VertexKey) -> Graph_EdgeKey:

    edge_key = Graph_EdgeKey.create()

    topology = Graph_EdgeTopology()
    topology.va_key = va_key
    topology.vb_key = vb_key
    attachments.graph_edge_topology_set(attachment_mutating, edge_key, topology)

    return edge_key


def add(attachment_mutating: AttachmentMutating,
        graph_key: Graph_GraphKey,
        va_key: Graph_VertexKey,
        vb_key: Graph_VertexKey) -> Graph_EdgeKey:

    edge_key = create(attachment_mutating, va_key, vb_key)

    edge_keys = Set_Graph_EdgeKey()
    edge_keys.add(edge_key)
    attachments.graph_graph_topology_union_edge_keys(attachment_mutating, graph_key, edge_keys)

    return edge_key
