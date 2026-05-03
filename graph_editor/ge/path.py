# Copyright (c) Digital Substrate 2026, All rights reserved.
# Generated from GE.dsmb by kibo-1.2.0.jar

import dsviper

Path_Root: dsviper.PathConst = dsviper.Path().const()

# Namespace Graph
class Graph_Path_Color:
    red: dsviper.PathConst = dsviper.Path.from_field("red").const()
    green: dsviper.PathConst = dsviper.Path.from_field("green").const()
    blue: dsviper.PathConst = dsviper.Path.from_field("blue").const()
    pass

class Graph_Path_EdgeTopology:
    vaKey: dsviper.PathConst = dsviper.Path.from_field("vaKey").const()
    vbKey: dsviper.PathConst = dsviper.Path.from_field("vbKey").const()
    pass

class Graph_Path_GraphDescription:
    name: dsviper.PathConst = dsviper.Path.from_field("name").const()
    author: dsviper.PathConst = dsviper.Path.from_field("author").const()
    createDate: dsviper.PathConst = dsviper.Path.from_field("createDate").const()
    pass

class Graph_Path_GraphSelection:
    vertexKeys: dsviper.PathConst = dsviper.Path.from_field("vertexKeys").const()
    edgeKeys: dsviper.PathConst = dsviper.Path.from_field("edgeKeys").const()
    pass

class Graph_Path_GraphTopology:
    vertexKeys: dsviper.PathConst = dsviper.Path.from_field("vertexKeys").const()
    edgeKeys: dsviper.PathConst = dsviper.Path.from_field("edgeKeys").const()
    pass

class Graph_Path_Position:
    x: dsviper.PathConst = dsviper.Path.from_field("x").const()
    y: dsviper.PathConst = dsviper.Path.from_field("y").const()
    pass

class Graph_Path_Rectangle:
    x: dsviper.PathConst = dsviper.Path.from_field("x").const()
    y: dsviper.PathConst = dsviper.Path.from_field("y").const()
    w: dsviper.PathConst = dsviper.Path.from_field("w").const()
    h: dsviper.PathConst = dsviper.Path.from_field("h").const()
    pass

class Graph_Path_Vertex2DAttributes:
    position: dsviper.PathConst = dsviper.Path.from_field("position").const()
    pass

class Graph_Path_VertexVisualAttributes:
    value: dsviper.PathConst = dsviper.Path.from_field("value").const()
    color: dsviper.PathConst = dsviper.Path.from_field("color").const()
    pass

