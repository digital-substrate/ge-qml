# Copyright (c) Digital Substrate 2026, All rights reserved.
# Generated from GE.dsmb by kibo-1.2.0.jar

"""
Getters, setters and collaborative setters for attachments defined for ge.
"""

from __future__ import annotations
import dsviper
from . import path as mp
from . import value_type as mt
from .data import *

# Namespace Graph
# attachment<Edge, EdgeTopology> Graph::topology
def graph_edge_topology_keys(attachment_getting: dsviper.AttachmentGetting) -> Set_Graph_EdgeKey:
    a = mt.attachment_Graph_Edge_Topology()
    return Set_Graph_EdgeKey(attachment_getting.keys(a))

def graph_edge_topology_diff_keys(current: dsviper.AttachmentGetting, other: dsviper.AttachmentGetting) -> tuple[Set_Graph_EdgeKey,Set_Graph_EdgeKey,Set_Graph_EdgeKey,Set_Graph_EdgeKey]:
    a = mt.attachment_Graph_Edge_Topology()
    added_keys, removed_keys, different_keys, same_keys = dsviper.AttachmentGetting.diff_keys(current, other, a)
    return Set_Graph_EdgeKey(added_keys), Set_Graph_EdgeKey(removed_keys), Set_Graph_EdgeKey(different_keys), Set_Graph_EdgeKey(same_keys)

def graph_edge_topology_has(attachment_getting: dsviper.AttachmentGetting, key: Graph_EdgeKey) -> bool:
    a = mt.attachment_Graph_Edge_Topology()
    return attachment_getting.has(a, key.vpr_value)

def graph_edge_topology_get(attachment_getting: dsviper.AttachmentGetting, key: Graph_EdgeKey) -> Optional_Graph_EdgeTopology:
    a = mt.attachment_Graph_Edge_Topology()
    return Optional_Graph_EdgeTopology(attachment_getting.get(a, key.vpr_value))

def graph_edge_topology_set(attachment_mutating: dsviper.AttachmentMutating, key: Graph_EdgeKey, value: Graph_EdgeTopology) -> None:
    a = mt.attachment_Graph_Edge_Topology()
    attachment_mutating.set(a, key.vpr_value, value.vpr_value)

def graph_edge_topology_diff(attachment_mutating: dsviper.AttachmentMutating, key: Graph_EdgeKey, value: Graph_EdgeTopology, *, recursive: bool = False) -> None:
    a = mt.attachment_Graph_Edge_Topology()
    attachment_mutating.diff(a, key.vpr_value, value.vpr_value, recursive=recursive)

def graph_edge_topology_set_va_key(attachment_mutating: dsviper.AttachmentMutating, key: Graph_EdgeKey, value: Graph_VertexKey):
    a = mt.attachment_Graph_Edge_Topology()
    attachment_mutating.update(a, key.vpr_value, mp.Graph_Path_EdgeTopology.vaKey, value.vpr_value)


def graph_edge_topology_set_vb_key(attachment_mutating: dsviper.AttachmentMutating, key: Graph_EdgeKey, value: Graph_VertexKey):
    a = mt.attachment_Graph_Edge_Topology()
    attachment_mutating.update(a, key.vpr_value, mp.Graph_Path_EdgeTopology.vbKey, value.vpr_value)


class _Enumerator_graph_edge_topology:
    def __init__(self, attachment_getting: dsviper.AttachmentGetting):
        self.__getting = attachment_getting
        self.__iter = iter(graph_edge_topology_keys(attachment_getting))

    def __iter__(self):
        return self

    def __next__(self) -> tuple[Graph_EdgeKey, Graph_EdgeTopology]:
        i = next(self.__iter)
        d = graph_edge_topology_get(self.__getting, i).unwrap()
        return i, d


def graph_edge_topology_enumerate(attachment_getting: dsviper.AttachmentGetting) ->_Enumerator_graph_edge_topology:
    return _Enumerator_graph_edge_topology(attachment_getting)


# attachment<Graph, xarray<string>> Graph::comments
def graph_graph_comments_keys(attachment_getting: dsviper.AttachmentGetting) -> Set_Graph_GraphKey:
    a = mt.attachment_Graph_Graph_Comments()
    return Set_Graph_GraphKey(attachment_getting.keys(a))

def graph_graph_comments_diff_keys(current: dsviper.AttachmentGetting, other: dsviper.AttachmentGetting) -> tuple[Set_Graph_GraphKey,Set_Graph_GraphKey,Set_Graph_GraphKey,Set_Graph_GraphKey]:
    a = mt.attachment_Graph_Graph_Comments()
    added_keys, removed_keys, different_keys, same_keys = dsviper.AttachmentGetting.diff_keys(current, other, a)
    return Set_Graph_GraphKey(added_keys), Set_Graph_GraphKey(removed_keys), Set_Graph_GraphKey(different_keys), Set_Graph_GraphKey(same_keys)

def graph_graph_comments_has(attachment_getting: dsviper.AttachmentGetting, key: Graph_GraphKey) -> bool:
    a = mt.attachment_Graph_Graph_Comments()
    return attachment_getting.has(a, key.vpr_value)

def graph_graph_comments_get(attachment_getting: dsviper.AttachmentGetting, key: Graph_GraphKey) -> Optional_XArray_string:
    a = mt.attachment_Graph_Graph_Comments()
    return Optional_XArray_string(attachment_getting.get(a, key.vpr_value))

def graph_graph_comments_set(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: XArray_string) -> None:
    a = mt.attachment_Graph_Graph_Comments()
    attachment_mutating.set(a, key.vpr_value, value.vpr_value)

def graph_graph_comments_diff(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: XArray_string, *, recursive: bool = False) -> None:
    a = mt.attachment_Graph_Graph_Comments()
    attachment_mutating.diff(a, key.vpr_value, value.vpr_value, recursive=recursive)

def graph_graph_comments_insert(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, before_position: dsviper.ValueUUId, new_position: dsviper.ValueUUId, value: str):
    a = mt.attachment_Graph_Graph_Comments()
    attachment_mutating.insert_in_xarray(a, key.vpr_value, mp.Path_Root, before_position, new_position, value)

def graph_graph_comments_update(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, position: dsviper.ValueUUId, value: str):
    a = mt.attachment_Graph_Graph_Comments()
    attachment_mutating.update_in_xarray(a, key.vpr_value, mp.Path_Root, position, value)

def graph_graph_comments_remove(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, position: dsviper.ValueUUId):
    a = mt.attachment_Graph_Graph_Comments()
    attachment_mutating.remove_in_xarray(a, key.vpr_value, mp.Path_Root, position)



class _Enumerator_graph_graph_comments:
    def __init__(self, attachment_getting: dsviper.AttachmentGetting):
        self.__getting = attachment_getting
        self.__iter = iter(graph_graph_comments_keys(attachment_getting))

    def __iter__(self):
        return self

    def __next__(self) -> tuple[Graph_GraphKey, XArray_string]:
        i = next(self.__iter)
        d = graph_graph_comments_get(self.__getting, i).unwrap()
        return i, d


def graph_graph_comments_enumerate(attachment_getting: dsviper.AttachmentGetting) ->_Enumerator_graph_graph_comments:
    return _Enumerator_graph_graph_comments(attachment_getting)


# attachment<Graph, GraphDescription> Graph::description
def graph_graph_description_keys(attachment_getting: dsviper.AttachmentGetting) -> Set_Graph_GraphKey:
    a = mt.attachment_Graph_Graph_Description()
    return Set_Graph_GraphKey(attachment_getting.keys(a))

def graph_graph_description_diff_keys(current: dsviper.AttachmentGetting, other: dsviper.AttachmentGetting) -> tuple[Set_Graph_GraphKey,Set_Graph_GraphKey,Set_Graph_GraphKey,Set_Graph_GraphKey]:
    a = mt.attachment_Graph_Graph_Description()
    added_keys, removed_keys, different_keys, same_keys = dsviper.AttachmentGetting.diff_keys(current, other, a)
    return Set_Graph_GraphKey(added_keys), Set_Graph_GraphKey(removed_keys), Set_Graph_GraphKey(different_keys), Set_Graph_GraphKey(same_keys)

def graph_graph_description_has(attachment_getting: dsviper.AttachmentGetting, key: Graph_GraphKey) -> bool:
    a = mt.attachment_Graph_Graph_Description()
    return attachment_getting.has(a, key.vpr_value)

def graph_graph_description_get(attachment_getting: dsviper.AttachmentGetting, key: Graph_GraphKey) -> Optional_Graph_GraphDescription:
    a = mt.attachment_Graph_Graph_Description()
    return Optional_Graph_GraphDescription(attachment_getting.get(a, key.vpr_value))

def graph_graph_description_set(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Graph_GraphDescription) -> None:
    a = mt.attachment_Graph_Graph_Description()
    attachment_mutating.set(a, key.vpr_value, value.vpr_value)

def graph_graph_description_diff(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Graph_GraphDescription, *, recursive: bool = False) -> None:
    a = mt.attachment_Graph_Graph_Description()
    attachment_mutating.diff(a, key.vpr_value, value.vpr_value, recursive=recursive)

def graph_graph_description_set_name(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: str):
    a = mt.attachment_Graph_Graph_Description()
    attachment_mutating.update(a, key.vpr_value, mp.Graph_Path_GraphDescription.name, value)


def graph_graph_description_set_author(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: str):
    a = mt.attachment_Graph_Graph_Description()
    attachment_mutating.update(a, key.vpr_value, mp.Graph_Path_GraphDescription.author, value)


def graph_graph_description_set_create_date(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: str):
    a = mt.attachment_Graph_Graph_Description()
    attachment_mutating.update(a, key.vpr_value, mp.Graph_Path_GraphDescription.createDate, value)


class _Enumerator_graph_graph_description:
    def __init__(self, attachment_getting: dsviper.AttachmentGetting):
        self.__getting = attachment_getting
        self.__iter = iter(graph_graph_description_keys(attachment_getting))

    def __iter__(self):
        return self

    def __next__(self) -> tuple[Graph_GraphKey, Graph_GraphDescription]:
        i = next(self.__iter)
        d = graph_graph_description_get(self.__getting, i).unwrap()
        return i, d


def graph_graph_description_enumerate(attachment_getting: dsviper.AttachmentGetting) ->_Enumerator_graph_graph_description:
    return _Enumerator_graph_graph_description(attachment_getting)


# attachment<Graph, GraphSelection> Graph::selection
def graph_graph_selection_keys(attachment_getting: dsviper.AttachmentGetting) -> Set_Graph_GraphKey:
    a = mt.attachment_Graph_Graph_Selection()
    return Set_Graph_GraphKey(attachment_getting.keys(a))

def graph_graph_selection_diff_keys(current: dsviper.AttachmentGetting, other: dsviper.AttachmentGetting) -> tuple[Set_Graph_GraphKey,Set_Graph_GraphKey,Set_Graph_GraphKey,Set_Graph_GraphKey]:
    a = mt.attachment_Graph_Graph_Selection()
    added_keys, removed_keys, different_keys, same_keys = dsviper.AttachmentGetting.diff_keys(current, other, a)
    return Set_Graph_GraphKey(added_keys), Set_Graph_GraphKey(removed_keys), Set_Graph_GraphKey(different_keys), Set_Graph_GraphKey(same_keys)

def graph_graph_selection_has(attachment_getting: dsviper.AttachmentGetting, key: Graph_GraphKey) -> bool:
    a = mt.attachment_Graph_Graph_Selection()
    return attachment_getting.has(a, key.vpr_value)

def graph_graph_selection_get(attachment_getting: dsviper.AttachmentGetting, key: Graph_GraphKey) -> Optional_Graph_GraphSelection:
    a = mt.attachment_Graph_Graph_Selection()
    return Optional_Graph_GraphSelection(attachment_getting.get(a, key.vpr_value))

def graph_graph_selection_set(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Graph_GraphSelection) -> None:
    a = mt.attachment_Graph_Graph_Selection()
    attachment_mutating.set(a, key.vpr_value, value.vpr_value)

def graph_graph_selection_diff(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Graph_GraphSelection, *, recursive: bool = False) -> None:
    a = mt.attachment_Graph_Graph_Selection()
    attachment_mutating.diff(a, key.vpr_value, value.vpr_value, recursive=recursive)

def graph_graph_selection_set_vertex_keys(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_Graph_VertexKey):
    a = mt.attachment_Graph_Graph_Selection()
    attachment_mutating.update(a, key.vpr_value, mp.Graph_Path_GraphSelection.vertexKeys, value.vpr_value)

def graph_graph_selection_union_vertex_keys(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_Graph_VertexKey):
    a = mt.attachment_Graph_Graph_Selection()
    attachment_mutating.union_in_set(a, key.vpr_value, mp.Graph_Path_GraphSelection.vertexKeys, value.vpr_value)

def graph_graph_selection_subtract_vertex_keys(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_Graph_VertexKey):
    a = mt.attachment_Graph_Graph_Selection()
    attachment_mutating.subtract_in_set(a, key.vpr_value, mp.Graph_Path_GraphSelection.vertexKeys, value.vpr_value)


def graph_graph_selection_set_edge_keys(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_Graph_EdgeKey):
    a = mt.attachment_Graph_Graph_Selection()
    attachment_mutating.update(a, key.vpr_value, mp.Graph_Path_GraphSelection.edgeKeys, value.vpr_value)

def graph_graph_selection_union_edge_keys(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_Graph_EdgeKey):
    a = mt.attachment_Graph_Graph_Selection()
    attachment_mutating.union_in_set(a, key.vpr_value, mp.Graph_Path_GraphSelection.edgeKeys, value.vpr_value)

def graph_graph_selection_subtract_edge_keys(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_Graph_EdgeKey):
    a = mt.attachment_Graph_Graph_Selection()
    attachment_mutating.subtract_in_set(a, key.vpr_value, mp.Graph_Path_GraphSelection.edgeKeys, value.vpr_value)


class _Enumerator_graph_graph_selection:
    def __init__(self, attachment_getting: dsviper.AttachmentGetting):
        self.__getting = attachment_getting
        self.__iter = iter(graph_graph_selection_keys(attachment_getting))

    def __iter__(self):
        return self

    def __next__(self) -> tuple[Graph_GraphKey, Graph_GraphSelection]:
        i = next(self.__iter)
        d = graph_graph_selection_get(self.__getting, i).unwrap()
        return i, d


def graph_graph_selection_enumerate(attachment_getting: dsviper.AttachmentGetting) ->_Enumerator_graph_graph_selection:
    return _Enumerator_graph_graph_selection(attachment_getting)


# attachment<Graph, map<string, string>> Graph::tags
def graph_graph_tags_keys(attachment_getting: dsviper.AttachmentGetting) -> Set_Graph_GraphKey:
    a = mt.attachment_Graph_Graph_Tags()
    return Set_Graph_GraphKey(attachment_getting.keys(a))

def graph_graph_tags_diff_keys(current: dsviper.AttachmentGetting, other: dsviper.AttachmentGetting) -> tuple[Set_Graph_GraphKey,Set_Graph_GraphKey,Set_Graph_GraphKey,Set_Graph_GraphKey]:
    a = mt.attachment_Graph_Graph_Tags()
    added_keys, removed_keys, different_keys, same_keys = dsviper.AttachmentGetting.diff_keys(current, other, a)
    return Set_Graph_GraphKey(added_keys), Set_Graph_GraphKey(removed_keys), Set_Graph_GraphKey(different_keys), Set_Graph_GraphKey(same_keys)

def graph_graph_tags_has(attachment_getting: dsviper.AttachmentGetting, key: Graph_GraphKey) -> bool:
    a = mt.attachment_Graph_Graph_Tags()
    return attachment_getting.has(a, key.vpr_value)

def graph_graph_tags_get(attachment_getting: dsviper.AttachmentGetting, key: Graph_GraphKey) -> Optional_Map_string_to_string:
    a = mt.attachment_Graph_Graph_Tags()
    return Optional_Map_string_to_string(attachment_getting.get(a, key.vpr_value))

def graph_graph_tags_set(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Map_string_to_string) -> None:
    a = mt.attachment_Graph_Graph_Tags()
    attachment_mutating.set(a, key.vpr_value, value.vpr_value)

def graph_graph_tags_diff(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Map_string_to_string, *, recursive: bool = False) -> None:
    a = mt.attachment_Graph_Graph_Tags()
    attachment_mutating.diff(a, key.vpr_value, value.vpr_value, recursive=recursive)

def graph_graph_tags_union(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Map_string_to_string):
    a = mt.attachment_Graph_Graph_Tags()
    attachment_mutating.union_in_map(a, key.vpr_value, mp.Path_Root, value.vpr_value)

def graph_graph_tags_subtract(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_string):
    a = mt.attachment_Graph_Graph_Tags()
    attachment_mutating.subtract_in_map(a, key.vpr_value, mp.Path_Root, value.vpr_value)

def graph_graph_tags_update(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Map_string_to_string):
    a = mt.attachment_Graph_Graph_Tags()
    attachment_mutating.update_in_map(a, key.vpr_value, mp.Path_Root, value.vpr_value)



class _Enumerator_graph_graph_tags:
    def __init__(self, attachment_getting: dsviper.AttachmentGetting):
        self.__getting = attachment_getting
        self.__iter = iter(graph_graph_tags_keys(attachment_getting))

    def __iter__(self):
        return self

    def __next__(self) -> tuple[Graph_GraphKey, Map_string_to_string]:
        i = next(self.__iter)
        d = graph_graph_tags_get(self.__getting, i).unwrap()
        return i, d


def graph_graph_tags_enumerate(attachment_getting: dsviper.AttachmentGetting) ->_Enumerator_graph_graph_tags:
    return _Enumerator_graph_graph_tags(attachment_getting)


# attachment<Graph, GraphTopology> Graph::topology
def graph_graph_topology_keys(attachment_getting: dsviper.AttachmentGetting) -> Set_Graph_GraphKey:
    a = mt.attachment_Graph_Graph_Topology()
    return Set_Graph_GraphKey(attachment_getting.keys(a))

def graph_graph_topology_diff_keys(current: dsviper.AttachmentGetting, other: dsviper.AttachmentGetting) -> tuple[Set_Graph_GraphKey,Set_Graph_GraphKey,Set_Graph_GraphKey,Set_Graph_GraphKey]:
    a = mt.attachment_Graph_Graph_Topology()
    added_keys, removed_keys, different_keys, same_keys = dsviper.AttachmentGetting.diff_keys(current, other, a)
    return Set_Graph_GraphKey(added_keys), Set_Graph_GraphKey(removed_keys), Set_Graph_GraphKey(different_keys), Set_Graph_GraphKey(same_keys)

def graph_graph_topology_has(attachment_getting: dsviper.AttachmentGetting, key: Graph_GraphKey) -> bool:
    a = mt.attachment_Graph_Graph_Topology()
    return attachment_getting.has(a, key.vpr_value)

def graph_graph_topology_get(attachment_getting: dsviper.AttachmentGetting, key: Graph_GraphKey) -> Optional_Graph_GraphTopology:
    a = mt.attachment_Graph_Graph_Topology()
    return Optional_Graph_GraphTopology(attachment_getting.get(a, key.vpr_value))

def graph_graph_topology_set(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Graph_GraphTopology) -> None:
    a = mt.attachment_Graph_Graph_Topology()
    attachment_mutating.set(a, key.vpr_value, value.vpr_value)

def graph_graph_topology_diff(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Graph_GraphTopology, *, recursive: bool = False) -> None:
    a = mt.attachment_Graph_Graph_Topology()
    attachment_mutating.diff(a, key.vpr_value, value.vpr_value, recursive=recursive)

def graph_graph_topology_set_vertex_keys(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_Graph_VertexKey):
    a = mt.attachment_Graph_Graph_Topology()
    attachment_mutating.update(a, key.vpr_value, mp.Graph_Path_GraphTopology.vertexKeys, value.vpr_value)

def graph_graph_topology_union_vertex_keys(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_Graph_VertexKey):
    a = mt.attachment_Graph_Graph_Topology()
    attachment_mutating.union_in_set(a, key.vpr_value, mp.Graph_Path_GraphTopology.vertexKeys, value.vpr_value)

def graph_graph_topology_subtract_vertex_keys(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_Graph_VertexKey):
    a = mt.attachment_Graph_Graph_Topology()
    attachment_mutating.subtract_in_set(a, key.vpr_value, mp.Graph_Path_GraphTopology.vertexKeys, value.vpr_value)


def graph_graph_topology_set_edge_keys(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_Graph_EdgeKey):
    a = mt.attachment_Graph_Graph_Topology()
    attachment_mutating.update(a, key.vpr_value, mp.Graph_Path_GraphTopology.edgeKeys, value.vpr_value)

def graph_graph_topology_union_edge_keys(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_Graph_EdgeKey):
    a = mt.attachment_Graph_Graph_Topology()
    attachment_mutating.union_in_set(a, key.vpr_value, mp.Graph_Path_GraphTopology.edgeKeys, value.vpr_value)

def graph_graph_topology_subtract_edge_keys(attachment_mutating: dsviper.AttachmentMutating, key: Graph_GraphKey, value: Set_Graph_EdgeKey):
    a = mt.attachment_Graph_Graph_Topology()
    attachment_mutating.subtract_in_set(a, key.vpr_value, mp.Graph_Path_GraphTopology.edgeKeys, value.vpr_value)


class _Enumerator_graph_graph_topology:
    def __init__(self, attachment_getting: dsviper.AttachmentGetting):
        self.__getting = attachment_getting
        self.__iter = iter(graph_graph_topology_keys(attachment_getting))

    def __iter__(self):
        return self

    def __next__(self) -> tuple[Graph_GraphKey, Graph_GraphTopology]:
        i = next(self.__iter)
        d = graph_graph_topology_get(self.__getting, i).unwrap()
        return i, d


def graph_graph_topology_enumerate(attachment_getting: dsviper.AttachmentGetting) ->_Enumerator_graph_graph_topology:
    return _Enumerator_graph_graph_topology(attachment_getting)


# attachment<Vertex, Vertex2DAttributes> Graph::render2DAttributes
def graph_vertex_render_2d_attributes_keys(attachment_getting: dsviper.AttachmentGetting) -> Set_Graph_VertexKey:
    a = mt.attachment_Graph_Vertex_Render2DAttributes()
    return Set_Graph_VertexKey(attachment_getting.keys(a))

def graph_vertex_render_2d_attributes_diff_keys(current: dsviper.AttachmentGetting, other: dsviper.AttachmentGetting) -> tuple[Set_Graph_VertexKey,Set_Graph_VertexKey,Set_Graph_VertexKey,Set_Graph_VertexKey]:
    a = mt.attachment_Graph_Vertex_Render2DAttributes()
    added_keys, removed_keys, different_keys, same_keys = dsviper.AttachmentGetting.diff_keys(current, other, a)
    return Set_Graph_VertexKey(added_keys), Set_Graph_VertexKey(removed_keys), Set_Graph_VertexKey(different_keys), Set_Graph_VertexKey(same_keys)

def graph_vertex_render_2d_attributes_has(attachment_getting: dsviper.AttachmentGetting, key: Graph_VertexKey) -> bool:
    a = mt.attachment_Graph_Vertex_Render2DAttributes()
    return attachment_getting.has(a, key.vpr_value)

def graph_vertex_render_2d_attributes_get(attachment_getting: dsviper.AttachmentGetting, key: Graph_VertexKey) -> Optional_Graph_Vertex2DAttributes:
    a = mt.attachment_Graph_Vertex_Render2DAttributes()
    return Optional_Graph_Vertex2DAttributes(attachment_getting.get(a, key.vpr_value))

def graph_vertex_render_2d_attributes_set(attachment_mutating: dsviper.AttachmentMutating, key: Graph_VertexKey, value: Graph_Vertex2DAttributes) -> None:
    a = mt.attachment_Graph_Vertex_Render2DAttributes()
    attachment_mutating.set(a, key.vpr_value, value.vpr_value)

def graph_vertex_render_2d_attributes_diff(attachment_mutating: dsviper.AttachmentMutating, key: Graph_VertexKey, value: Graph_Vertex2DAttributes, *, recursive: bool = False) -> None:
    a = mt.attachment_Graph_Vertex_Render2DAttributes()
    attachment_mutating.diff(a, key.vpr_value, value.vpr_value, recursive=recursive)

def graph_vertex_render_2d_attributes_set_position(attachment_mutating: dsviper.AttachmentMutating, key: Graph_VertexKey, value: Graph_Position):
    a = mt.attachment_Graph_Vertex_Render2DAttributes()
    attachment_mutating.update(a, key.vpr_value, mp.Graph_Path_Vertex2DAttributes.position, value.vpr_value)


class _Enumerator_graph_vertex_render_2d_attributes:
    def __init__(self, attachment_getting: dsviper.AttachmentGetting):
        self.__getting = attachment_getting
        self.__iter = iter(graph_vertex_render_2d_attributes_keys(attachment_getting))

    def __iter__(self):
        return self

    def __next__(self) -> tuple[Graph_VertexKey, Graph_Vertex2DAttributes]:
        i = next(self.__iter)
        d = graph_vertex_render_2d_attributes_get(self.__getting, i).unwrap()
        return i, d


def graph_vertex_render_2d_attributes_enumerate(attachment_getting: dsviper.AttachmentGetting) ->_Enumerator_graph_vertex_render_2d_attributes:
    return _Enumerator_graph_vertex_render_2d_attributes(attachment_getting)


# attachment<Vertex, VertexVisualAttributes> Graph::visualAttributes
def graph_vertex_visual_attributes_keys(attachment_getting: dsviper.AttachmentGetting) -> Set_Graph_VertexKey:
    a = mt.attachment_Graph_Vertex_VisualAttributes()
    return Set_Graph_VertexKey(attachment_getting.keys(a))

def graph_vertex_visual_attributes_diff_keys(current: dsviper.AttachmentGetting, other: dsviper.AttachmentGetting) -> tuple[Set_Graph_VertexKey,Set_Graph_VertexKey,Set_Graph_VertexKey,Set_Graph_VertexKey]:
    a = mt.attachment_Graph_Vertex_VisualAttributes()
    added_keys, removed_keys, different_keys, same_keys = dsviper.AttachmentGetting.diff_keys(current, other, a)
    return Set_Graph_VertexKey(added_keys), Set_Graph_VertexKey(removed_keys), Set_Graph_VertexKey(different_keys), Set_Graph_VertexKey(same_keys)

def graph_vertex_visual_attributes_has(attachment_getting: dsviper.AttachmentGetting, key: Graph_VertexKey) -> bool:
    a = mt.attachment_Graph_Vertex_VisualAttributes()
    return attachment_getting.has(a, key.vpr_value)

def graph_vertex_visual_attributes_get(attachment_getting: dsviper.AttachmentGetting, key: Graph_VertexKey) -> Optional_Graph_VertexVisualAttributes:
    a = mt.attachment_Graph_Vertex_VisualAttributes()
    return Optional_Graph_VertexVisualAttributes(attachment_getting.get(a, key.vpr_value))

def graph_vertex_visual_attributes_set(attachment_mutating: dsviper.AttachmentMutating, key: Graph_VertexKey, value: Graph_VertexVisualAttributes) -> None:
    a = mt.attachment_Graph_Vertex_VisualAttributes()
    attachment_mutating.set(a, key.vpr_value, value.vpr_value)

def graph_vertex_visual_attributes_diff(attachment_mutating: dsviper.AttachmentMutating, key: Graph_VertexKey, value: Graph_VertexVisualAttributes, *, recursive: bool = False) -> None:
    a = mt.attachment_Graph_Vertex_VisualAttributes()
    attachment_mutating.diff(a, key.vpr_value, value.vpr_value, recursive=recursive)

def graph_vertex_visual_attributes_set_value(attachment_mutating: dsviper.AttachmentMutating, key: Graph_VertexKey, value: int):
    a = mt.attachment_Graph_Vertex_VisualAttributes()
    attachment_mutating.update(a, key.vpr_value, mp.Graph_Path_VertexVisualAttributes.value, value)


def graph_vertex_visual_attributes_set_color(attachment_mutating: dsviper.AttachmentMutating, key: Graph_VertexKey, value: Graph_Color):
    a = mt.attachment_Graph_Vertex_VisualAttributes()
    attachment_mutating.update(a, key.vpr_value, mp.Graph_Path_VertexVisualAttributes.color, value.vpr_value)


class _Enumerator_graph_vertex_visual_attributes:
    def __init__(self, attachment_getting: dsviper.AttachmentGetting):
        self.__getting = attachment_getting
        self.__iter = iter(graph_vertex_visual_attributes_keys(attachment_getting))

    def __iter__(self):
        return self

    def __next__(self) -> tuple[Graph_VertexKey, Graph_VertexVisualAttributes]:
        i = next(self.__iter)
        d = graph_vertex_visual_attributes_get(self.__getting, i).unwrap()
        return i, d


def graph_vertex_visual_attributes_enumerate(attachment_getting: dsviper.AttachmentGetting) ->_Enumerator_graph_vertex_visual_attributes:
    return _Enumerator_graph_vertex_visual_attributes(attachment_getting)


