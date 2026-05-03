from dsviper import AttachmentMutating

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_GraphDescription,
    Graph_GraphTopology,
    Graph_GraphSelection,
    Map_string_to_string,
    XArray_string)


def create(attachment_mutating: AttachmentMutating, name: str) -> Graph_GraphKey:
    graph_key = Graph_GraphKey.create()

    description = Graph_GraphDescription()
    description.name = name

    attachments.graph_graph_description_set(attachment_mutating, graph_key, description)
    attachments.graph_graph_topology_set(attachment_mutating, graph_key, Graph_GraphTopology())
    attachments.graph_graph_tags_set(attachment_mutating, graph_key, Map_string_to_string())
    attachments.graph_graph_comments_set(attachment_mutating, graph_key, XArray_string())
    attachments.graph_graph_selection_set(attachment_mutating, graph_key, Graph_GraphSelection())

    return graph_key
