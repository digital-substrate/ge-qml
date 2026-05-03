from dsviper import AttachmentMutating

from ge.data import Graph_GraphKey

from model import graph_integrity
from model import selection_integrity
from model import tools


def restore_by_respawning(attachment_mutating: AttachmentMutating,
                          graph_key: Graph_GraphKey) -> None:
    """Restore graph integrity by respawning missing vertices, then restore selection."""
    graph_integrity.restore_by_respawning(attachment_mutating, graph_key)
    selection_integrity.restore(attachment_mutating, graph_key)


def restore_by_deleting(attachment_mutating: AttachmentMutating,
                        graph_key: Graph_GraphKey) -> None:
    """Restore graph integrity by deleting orphaned edges, then restore selection."""
    graph_integrity.restore_by_deleting(attachment_mutating, graph_key)
    selection_integrity.restore(attachment_mutating, graph_key)


def restore_by_creating(attachment_mutating: AttachmentMutating,
                        graph_key: Graph_GraphKey) -> None:
    """Restore graph integrity by creating missing vertices, then restore selection."""
    value = tools.next_vertex_value(attachment_mutating, graph_key)
    graph_integrity.restore_by_creating(attachment_mutating, graph_key, value)
    selection_integrity.restore(attachment_mutating, graph_key)
