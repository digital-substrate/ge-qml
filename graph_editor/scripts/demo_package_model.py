"""Demo script — exercises the model package (application business logic).

Unlike demo_ge_package.py which uses the ge generated code directly,
this script uses the higher-level model functions provided with the application.
These are the same functions used by the menus and toolbar buttons.

"""

# --- Random operations ---
#ctx.dispatch("Random Vertex", model_random.add_vertex, ge_graph_key(), ge_render_rect())
#ctx.dispatch("Random Edge", model_random.add_edge, ge_graph_key())
#ctx.dispatch("Random Tag", model_random.tag, ge_graph_key())
#ctx.dispatch("Random Comment", model_random.comment, ge_graph_key())
#ctx.undo()
#ctx.redo()
#ctx.reset()

# --- Random graph (vertex_count, edge_count, rect) ---
#ctx.dispatch("Random Graph", model_random.graph, ge_graph_key(), 6, 8, ge_render_rect())

# --- Batch ---
#for _ in range(10):
#    ctx.dispatch("Random Vertex", model_random.add_vertex, ge_graph_key(), ge_render_rect())

# --- Selection ---
#ctx.dispatch("Select All Vertices", selection_vertices.select_all, ge_graph_key())
#ctx.dispatch("Deselect All Vertices", selection_vertices.deselect_all, ge_graph_key())
#ctx.dispatch("Invert Vertex Selection", selection_vertices.invert, ge_graph_key())
#ctx.dispatch("Increment Value", selection_vertices.increment_value, ge_graph_key(), 100)
#ctx.dispatch("Select All Edges", selection_edges.select_all, ge_graph_key())
#ctx.dispatch("Deselect All Edges", selection_edges.deselect_all, ge_graph_key())

# --- Topology ---
#ctx.dispatch("Clear Graph", graph_topology.clear, ge_graph_key())

# --- Undo / Redo / Reset ---
#ctx.undo()
#ctx.redo()
#ctx.reset()

# --- Queries (read-only, no dispatch needed) ---
#ag = ctx.store.attachment_getting()
#print("Has vertices:", graph_topology.has_vertices(ag, ge_graph_key()))
#print("Has edges:", graph_topology.has_edges(ag, ge_graph_key()))
#print("Has remaining edges:", graph_topology.has_remaining_edges(ag, ge_graph_key()))
#print("Selected vertices:", selection_vertices.has_selected(ag, ge_graph_key()))
