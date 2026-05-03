from dsviper import AttachmentMutating

from ge.data import Graph_GraphKey, Graph_Rectangle

from model import random as model_random
from model import selection_random


def random_graph(attachment_mutating: AttachmentMutating,
                 graph_key: Graph_GraphKey,
                 vertex_count: int,
                 edge_count: int,
                 rect: Graph_Rectangle) -> None:
    """Create a random graph and randomly select some elements."""
    model_random.graph(attachment_mutating, graph_key, vertex_count, edge_count, rect)
    selection_random.mixed(attachment_mutating, graph_key)
