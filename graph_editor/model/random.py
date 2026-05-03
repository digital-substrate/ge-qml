import random
import string

from dsviper import AttachmentMutating, AttachmentGetting, ValueUUId

from ge import attachments
from ge.data import (
    Graph_GraphKey,
    Graph_VertexKey,
    Graph_EdgeKey,
    Graph_EdgeTopology,
    Graph_Rectangle,
    Graph_Position,
    Graph_Color,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey,
    Map_string_to_string)

from model import vertex as model_vertex
from model import edge as model_edge


def random_float(s: float = 1.0) -> float:
    return random.random() * s


def random_float_range(min_val: float, max_val: float) -> float:
    return min_val + random_float(max_val - min_val)


def random_int() -> int:
    return random.randint(0, 2**31 - 1)


def make_word(length: int) -> str:
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def make_color() -> Graph_Color:
    r = random_float_range(0.2, 0.4)
    g = random_float_range(0.2, 0.4)
    b = random_float_range(0.2, 0.4)

    color = Graph_Color()
    color.red = r
    color.green = g
    color.blue = b
    return color


def create_vertex(attachment_mutating: AttachmentMutating,
                  value: int,
                  rect: Graph_Rectangle) -> Graph_VertexKey:

    margin = min(rect.h, rect.w) / 8
    vx = random_float_range(rect.x + margin, rect.x + rect.w - margin)
    vy = random_float_range(rect.y + margin, rect.y + rect.h - margin)

    position = Graph_Position()
    position.x = vx
    position.y = vy

    return model_vertex.create(attachment_mutating, value, position, make_color())


def add_vertex(attachment_mutating: AttachmentMutating,
               graph_key: Graph_GraphKey,
               rect: Graph_Rectangle) -> Graph_VertexKey:

    value = next_vertex_value(attachment_mutating, graph_key)
    vertex_key = create_vertex(attachment_mutating, value, rect)

    vertex_keys = Set_Graph_VertexKey()
    vertex_keys.add(vertex_key)
    attachments.graph_graph_topology_union_vertex_keys(attachment_mutating, graph_key, vertex_keys)

    return vertex_key


def next_vertex_value(attachment_getting: AttachmentGetting, graph_key: Graph_GraphKey) -> int:
    """Get the next vertex value (max + 1) for a graph."""
    opt = attachments.graph_graph_topology_get(attachment_getting, graph_key)
    if not opt:
        return 1

    topology = opt.unwrap()
    max_value = 0

    for vertex_key in topology.vertex_keys:
        opt_attr = attachments.graph_vertex_visual_attributes_get(attachment_getting, vertex_key)
        if opt_attr:
            attrs = opt_attr.unwrap()
            max_value = max(max_value, attrs.value)

    return max_value + 1


def find_edge_topology(attachment_getting: AttachmentGetting,
                       graph_key: Graph_GraphKey) -> Graph_EdgeTopology | None:
    """Find a valid edge topology (two vertices not already connected)."""
    opt = attachments.graph_graph_topology_get(attachment_getting, graph_key)
    if not opt:
        return None

    topology = opt.unwrap()
    vertex_keys = list(topology.vertex_keys)
    edge_keys = topology.edge_keys

    vertex_count = len(vertex_keys)
    if vertex_count < 2:
        return None

    max_edges = vertex_count * (vertex_count - 1) // 2
    if len(edge_keys) >= max_edges:
        return None

    while True:
        ra = random_int() % len(vertex_keys)
        rb = random_int() % len(vertex_keys)
        if ra == rb:
            continue

        va_key = vertex_keys[ra]
        vb_key = vertex_keys[rb]

        if not has_edge(attachment_getting, graph_key, va_key, vb_key):
            result = Graph_EdgeTopology()
            result.va_key = va_key
            result.vb_key = vb_key
            return result


def has_edge(attachment_getting: AttachmentGetting,
             graph_key: Graph_GraphKey,
             va_key: Graph_VertexKey,
             vb_key: Graph_VertexKey) -> bool:
    """Check if an edge exists between two vertices."""
    opt = attachments.graph_graph_topology_get(attachment_getting, graph_key)
    if not opt:
        return False

    topology = opt.unwrap()

    for edge_key in topology.edge_keys:
        opt_edge = attachments.graph_edge_topology_get(attachment_getting, edge_key)
        if opt_edge:
            edge = opt_edge.unwrap()
            same_edge = ((edge.va_key == va_key and edge.vb_key == vb_key) or
                         (edge.va_key == vb_key and edge.vb_key == va_key))
            if same_edge:
                return True

    return False


def add_edge(attachment_mutating: AttachmentMutating,
             graph_key: Graph_GraphKey) -> Graph_EdgeKey | None:
    """Add a random edge to the graph."""
    topology = find_edge_topology(attachment_mutating, graph_key)
    if not topology:
        return None

    return model_edge.add(attachment_mutating, graph_key, topology.va_key, topology.vb_key)


def graph(attachment_mutating: AttachmentMutating,
          graph_key: Graph_GraphKey,
          vertex_count: int,
          edge_count: int,
          rect: Graph_Rectangle) -> None:
    """Generate a random graph with vertices and edges."""
    value = next_vertex_value(attachment_mutating, graph_key)

    vertex_keys = Set_Graph_VertexKey()
    vertex_list = []

    for i in range(vertex_count):
        vertex_key = create_vertex(attachment_mutating, value + i, rect)
        vertex_keys.add(vertex_key)
        vertex_list.append(vertex_key)

    edge_keys = add_edges(attachment_mutating, edge_count, vertex_list)

    attachments.graph_graph_topology_union_vertex_keys(attachment_mutating, graph_key, vertex_keys)
    attachments.graph_graph_topology_union_edge_keys(attachment_mutating, graph_key, edge_keys)


def add_edges(attachment_mutating: AttachmentMutating,
              edge_count: int,
              vertex_keys: list[Graph_VertexKey]) -> Set_Graph_EdgeKey:
    """Add multiple random edges between given vertices."""
    edges: list[tuple[Graph_VertexKey, Graph_VertexKey]] = []
    edge_keys = Set_Graph_EdgeKey()

    max_edges = len(vertex_keys) * (len(vertex_keys) - 1) // 2
    count = min(max_edges, edge_count)

    while len(edge_keys) < count:
        ra = random_int() % len(vertex_keys)
        rb = random_int() % len(vertex_keys)
        if ra == rb:
            continue

        va_key = vertex_keys[ra]
        vb_key = vertex_keys[rb]

        if not has_edge_in_list(va_key, vb_key, edges):
            edge_key = model_edge.create(attachment_mutating, va_key, vb_key)
            edges.append((va_key, vb_key))
            edge_keys.add(edge_key)

    return edge_keys


def has_edge_in_list(va_key: Graph_VertexKey,
                     vb_key: Graph_VertexKey,
                     edges: list[tuple[Graph_VertexKey, Graph_VertexKey]]) -> bool:
    """Check if an edge exists in a list of edges."""
    for edge in edges:
        same_edge = ((edge[0] == va_key and edge[1] == vb_key) or
                     (edge[0] == vb_key and edge[1] == va_key))
        if same_edge:
            return True
    return False


def tag(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Add a random tag to the graph."""
    key = make_word(3)
    value = make_word(5)
    tags = Map_string_to_string({key: value})
    attachments.graph_graph_tags_union(attachment_mutating, graph_key, tags)


def comment(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> None:
    """Add a random comment to the graph."""
    text = make_word(10)
    attachments.graph_graph_comments_insert(
        attachment_mutating,
        graph_key,
        ValueUUId.INVALID,
        ValueUUId.create(),
        text)
