from __future__ import annotations
from dsviper import *
from ge import *
import ge.attachments as gea
import random
import traceback

def random_word(size: int):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    l = len(letters) - 1
    result = ""
    for _ in range(size):
        result += letters[random.randint(0, l)]
    return result


def random_comment(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey):
    v = random_word(10)
    gea.graph_graph_comments_insert(attachment_mutating, graph_key, ValueUUId.INVALID, ValueUUId.create(), v)


def random_tag(attachment_mutating: AttachmentMutating, graph_key: Key):
    m = Map_string_to_string()
    m[random_word(3)] = random_word(5)
    gea.graph_graph_tags_union(attachment_mutating, graph_key, m)


def random_position(min: int, max: int) -> Graph_Position:
    result = Graph_Position()
    result.x = random.randint(min, max)
    result.y = random.randint(min, max)
    return result


def random_color(min: int, max: int) -> Graph_Color:
    result = Graph_Color()
    result.red = random.randint(min, max) / 255
    result.green = random.randint(min, max) / 255
    result.blue = random.randint(min, max) / 255
    return result


def create_vertex(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey, value: int, position: Graph_Position, color: Graph_Color) -> Graph_VertexKey:
    va = Graph_VertexVisualAttributes()
    va.value = value
    va.color = color    

    vr = Graph_Vertex2DAttributes()
    vr.position = position

    vertex_key = Graph_VertexKey.create()
    gea.graph_vertex_visual_attributes_set(attachment_mutating, vertex_key, va)
    gea.graph_vertex_render_2d_attributes_set(attachment_mutating, vertex_key, vr)

    return vertex_key
    

def add_vertex(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey, value: int, position: Graph_Position, color: Graph_Color) -> Graph_VertexKey:
    vertex_key = create_vertex(attachment_mutating, graph_key, value, position, color)
    keys = Set_Graph_VertexKey()
    keys.add(vertex_key)
    gea.graph_graph_topology_union_vertex_keys(attachment_mutating, graph_key, keys)
    return vertex_key


def random_vertex(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey):
    value = random.randint(1, 1000)
    position = random_position(40, 400)
    color = random_color(40, 100)
    add_vertex(attachment_mutating, graph_key, random.randint(1, 100), position, color) 


def create_edge(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey, va_key: Graph_VertexKey, vb_key: Graph_VertexKey) -> Graph_EdgeKey:
    topology = Graph_EdgeTopology()
    topology.va_key = va_key
    topology.vb_key = vb_key

    edge_key = Graph_EdgeKey.create()
    keys = Set_Graph_EdgeKey()
    keys.add(edge_key)

    gea.graph_edge_topology_set(attachment_mutating, edge_key, topology)
    gea.graph_graph_topology_union_edge_keys(attachment_mutating, graph_key, keys)
    return edge_key


def has_edge(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey, va_key: Graph_VertexKey, vb_key: Graph_VertexKey) -> Optional[Graph_EdgeKey]:
    topology = gea.graph_graph_topology_get(attachment_mutating, graph_key).unwrap()
    edge_keys = topology.edge_keys
    for edge_key in edge_keys:
        e_topology = gea.graph_edge_topology_get(attachment_mutating, edge_key)
        if not e_topology:
            continue
        
        e_va_key = e_topology.unwrap().va_key
        e_vb_key = e_topology.unwrap().vb_key
        if (e_va_key == va_key and e_vb_key == vb_key) or (e_va_key == vb_key and e_vb_key == va_key):
            return edge_key;
    
    return None

def random_edge(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey) -> Graph_EdgeKey:
    topology = gea.graph_graph_topology_get(attachment_mutating, graph_key).unwrap()
    vertex_keys = topology.vertex_keys
    edge_keys = topology.edge_keys

    vertex_count = len(vertex_keys)
    max_edge = (vertex_count * (vertex_count - 1)) / 2
    assert len(vertex_keys)
    assert len(edge_keys) < max_edge
    
    v_keys: list[VertexKey] = list()
    for vertex_key in vertex_keys:
        v_keys.append(vertex_key)

    while True:
        ra = random.randint(0, len(v_keys) - 1)
        rb = random.randint(0, len(v_keys) - 1)
        if ra == rb:
             continue
        
        va_key = v_keys[ra]
        vb_key = v_keys[rb]
        if not has_edge(attachment_mutating, graph_key, va_key, vb_key):
            return create_edge(attachment_mutating, graph_key, va_key, vb_key)

def random_graph(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey, vertex_count: int, edge_count: int):

    def r_next_value(attachment_getting: attachmentGetting) -> int:
        value = -1
        for key in gea.graph_vertex_visual_attributes_keys(attachment_mutating):
            v = gea.graph_vertex_visual_attributes_get(attachment_mutating, key)
            if v:
                value = max(value, v.unwrap().value)
        return value + 1

    def r_vertex(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey, value) -> Graph_VertexKey:
        position = random_position(40, 400)
        color = random_color(40, 100)
        return create_vertex(attachment_mutating, graph_key, value, position, color)

    def r_has_edge(va_key: Graph_VertexKey, vb_key: Graph_VertexKey, edges: list[Graph_EdgeKey]):
        for edge in edges:
          if (edge.va_key == va_key and edge.vb_key == vb_key) or (edge.va_key == vb_key and edge.vb_key == va_key):
               return True 
        return False

    def r_add_edge(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey, va_key: Graph_VertexKey, vb_key: Graph_VertexKey, edges: list[Graph_EdgeKey], edge_keys: Set_Graph_EdgeKey):
        edge_key = Graph_EdgeKey.create()
        edge = Graph_EdgeTopology()
        edge.va_key = va_key
        edge.vb_key = vb_key
        gea.graph_edge_topology_set(attachment_mutating, edge_key, edge)
        edges.append(edge)
        edge_keys.add(edge_key)

    def r_add_edges(attachment_mutating: AttachmentMutating, graph_key: Graph_GraphKey, edge_count: int, vertex_keys: Set_Graph_VertexKey):
        candidate_keys: list[Graph_VertexKey] = list()
        for key in vertex_keys:
            candidate_keys.append(key)

        edges: list[Graph_EdgeTopology] = list()
        edge_keys = Set_Graph_EdgeKey()
    
        max_edge = len(vertex_keys) * (len(vertex_keys) - 1) / 2
        count = min(max_edge, edge_count)
    
        while len(edge_keys) < count:
            va_key = random.choice(candidate_keys)
            vb_key = random.choice(candidate_keys)
            if va_key == vb_key:
                continue
                
            if len(edges) == 0:
                r_add_edge(attachment_mutating, graph_key, va_key, vb_key, edges, edge_keys)
            elif not r_has_edge(va_key, vb_key, edges):
                r_add_edge(attachment_mutating, graph_key, va_key, vb_key, edges, edge_keys)
        
        return edge_keys

    value = r_next_value(attachment_mutating)
    vertex_keys = Set_Graph_VertexKey()
    for _ in range(vertex_count):
        vertex_keys.add(r_vertex(attachment_mutating, graph_key, value))
        value += 1

    edge_keys = r_add_edges(attachment_mutating, graph_key, edge_count, vertex_keys)
    gea.graph_graph_topology_union_vertex_keys(attachment_mutating, graph_key, vertex_keys)
    gea.graph_graph_topology_union_edge_keys(attachment_mutating, graph_key, edge_keys)

#ctx.reset()
#ctx.dispatch("random_vertex", random_vertex, ge_graph_key()) # eval me two times
#ctx.dispatch("random edge", random_edge, ge_graph_key())
#ctx.dispatch("random tags", random_tag, ge_graph_key())
#ctx.dispatch("random comment", random_comment, ge_graph_key())
#ctx.dispatch("random graph", random_graph, ge_graph_key(), 6, 8)
#ctx.undo()
#ctx.redo()

#for r in range(100):
#    ctx.dispatch("random_vertex", random_vertex, ge_graph_key()) # eval me two times

