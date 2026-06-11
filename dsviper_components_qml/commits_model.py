"""Commits model — exposes DAG commits to QML.

Flat list of commits ordered by grid row, with current/marked selection.
"""
from __future__ import annotations

from PySide6.QtCore import (
    QAbstractListModel, QModelIndex, QDateTime, Qt,
    Property, Signal, Slot,
)
from enum import IntEnum

from dsviper import CommitStore, CommitStateBuilder, CommitNode, CommitNodeGrid, CommitNodeGridBuilder, ValueCommitId


NODE_SIZE = 17
NODE_SPACING_X = NODE_SIZE + 4
NODE_SPACING_Y = NODE_SIZE + 2
MARGIN = 4

NODE_COLORS = {
    "Enable": "#6bd460",
    "Disable": "#ec5545",
    "Merge": "#b360ea",
    "Mutations": "#3b81f7",
}
GRAY = "#808080"


class CommitsModel(QAbstractListModel):

    class Roles(IntEnum):
        CommitIdStr = Qt.ItemDataRole.UserRole + 1
        CommitType = Qt.ItemDataRole.UserRole + 2
        Label = Qt.ItemDataRole.UserRole + 3
        Date = Qt.ItemDataRole.UserRole + 4
        ParentIdStr = Qt.ItemDataRole.UserRole + 5
        TargetIdStr = Qt.ItemDataRole.UserRole + 6
        IsEnabled = Qt.ItemDataRole.UserRole + 7
        IsCurrent = Qt.ItemDataRole.UserRole + 8
        IsMarked = Qt.ItemDataRole.UserRole + 9
        IsHead = Qt.ItemDataRole.UserRole + 10
        Column = Qt.ItemDataRole.UserRole + 11

    # Signals
    currentInfoChanged = Signal()
    markedInfoChanged = Signal()
    canMergeMarkedChanged = Signal()
    buttonStateChanged = Signal()
    graphChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._store = None
        self._rows: list[dict] = []
        self._commit_ids_list: list[ValueCommitId] = []  # parallel to _rows
        self._marked_commit_id: ValueCommitId | None = None
        self._grid_nodes: dict = {}  # dict[ValueCommitId, CommitNodeGrid] — kept for keyboard nav

        # Graph data for Canvas rendering
        self._graph_nodes: list[dict] = []  # {x, y, color, is_current, is_marked, order, commit_id}
        self._graph_edges: list[dict] = []  # {x1, y1, x2, y2, parent_color, child_color}
        self._graph_merges: list[dict] = []  # {x1, y1, x2, y2, color}
        self._graph_width = 0
        self._graph_height = 0
        self._viewport_height = 0  # set by QML, used for bottom-anchoring
        self._current_node_x = 0
        self._current_node_y = 0
        # Cached parameters for rebuild on viewport resize
        self._last_grid_builder = None
        self._last_enabled_map = {}
        self._last_current_cid = None

        # Current commit info (for header display)
        self._current_label = ""
        self._current_date = ""
        self._current_type = ""
        self._current_id = ""
        self._current_parent_id = ""
        self._current_target_id = ""

        # Marked commit info
        self._marked_label = ""
        self._marked_date = ""
        self._marked_type = ""
        self._marked_id = ""
        self._marked_parent_id = ""
        self._marked_target_id = ""
        self._can_merge_marked = False

    def set_store(self, store, notifier):
        self._store = store
        self._notifier = notifier
        notifier.state_did_change.connect(self.refresh)
        notifier.database_did_open.connect(self.refresh)
        notifier.database_did_close.connect(self.clear)

    # --- Current commit QML properties ---
    def _get_current_label(self): return self._current_label
    currentLabel = Property(str, _get_current_label, notify=currentInfoChanged)
    def _get_current_date(self): return self._current_date
    currentDate = Property(str, _get_current_date, notify=currentInfoChanged)
    def _get_current_type(self): return self._current_type
    currentType = Property(str, _get_current_type, notify=currentInfoChanged)
    def _get_current_id(self): return self._current_id
    currentId = Property(str, _get_current_id, notify=currentInfoChanged)
    def _get_current_parent_id(self): return self._current_parent_id
    currentParentId = Property(str, _get_current_parent_id, notify=currentInfoChanged)
    def _get_current_target_id(self): return self._current_target_id
    currentTargetId = Property(str, _get_current_target_id, notify=currentInfoChanged)

    # --- Marked commit QML properties ---
    def _get_marked_label(self): return self._marked_label
    markedLabel = Property(str, _get_marked_label, notify=markedInfoChanged)
    def _get_marked_date(self): return self._marked_date
    markedDate = Property(str, _get_marked_date, notify=markedInfoChanged)
    def _get_marked_type(self): return self._marked_type
    markedType = Property(str, _get_marked_type, notify=markedInfoChanged)
    def _get_marked_id(self): return self._marked_id
    markedId = Property(str, _get_marked_id, notify=markedInfoChanged)
    def _get_marked_parent_id(self): return self._marked_parent_id
    markedParentId = Property(str, _get_marked_parent_id, notify=markedInfoChanged)
    def _get_marked_target_id(self): return self._marked_target_id
    markedTargetId = Property(str, _get_marked_target_id, notify=markedInfoChanged)

    # --- Graph size properties ---
    def _get_graph_width(self): return self._graph_width
    graphWidth = Property(int, _get_graph_width, notify=graphChanged)
    def _get_graph_height(self): return self._graph_height
    graphHeight = Property(int, _get_graph_height, notify=graphChanged)
    def _get_current_node_x(self): return self._current_node_x
    currentNodeX = Property(int, _get_current_node_x, notify=graphChanged)
    def _get_current_node_y(self): return self._current_node_y
    currentNodeY = Property(int, _get_current_node_y, notify=graphChanged)

    @Slot(int)
    def setViewportHeight(self, height: int):
        """Called by QML when the DAG container resizes.

        ensures nodes anchor to the bottom when content < viewport.
        """
        if height != self._viewport_height:
            self._viewport_height = height
            self._rebuild_if_needed()

    @Slot(result=list)
    def graphNodes(self) -> list:
        return self._graph_nodes

    @Slot(result=list)
    def graphEdges(self) -> list:
        return self._graph_edges

    @Slot(result=list)
    def graphMerges(self) -> list:
        return self._graph_merges

    def _get_has_marked(self): return self._marked_commit_id is not None
    hasMarked = Property(bool, _get_has_marked, notify=markedInfoChanged)
    def _get_can_merge_marked(self): return self._can_merge_marked
    canMergeMarked = Property(bool, _get_can_merge_marked, notify=canMergeMarkedChanged)

    # Button enable state
    def _get_can_delete(self):
        """Enabled when current commit is a head and there's more than 1 commit."""
        if not self._store.has_database():
            return False
        current = self._store.state().commit_id()
        if not current.is_valid():
            return False
        db = self._store.database()
        return current in db.head_commit_ids() and len(db.commit_ids()) > 1

    canDelete = Property(bool, _get_can_delete, notify=buttonStateChanged)

    def _get_can_reset(self):
        """Enabled when current commit is valid."""
        if not self._store.has_database():
            return False
        return self._store.state().commit_id().is_valid()

    canReset = Property(bool, _get_can_reset, notify=buttonStateChanged)

    def _get_can_enable_disable(self):
        """Enabled when marked commit exists and is not the first commit."""
        if self._marked_commit_id is None or not self._store.has_database():
            return False
        first = self._store.database().first_commit_id()
        return self._marked_commit_id != first

    canEnableDisable = Property(bool, _get_can_enable_disable, notify=buttonStateChanged)

    # --- QAbstractListModel ---
    def rowCount(self, parent=QModelIndex()):
        return len(self._rows)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._rows):
            return None
        row = self._rows[index.row()]
        role_map = {
            self.Roles.CommitIdStr: "commit_id",
            self.Roles.CommitType: "commit_type",
            self.Roles.Label: "label",
            self.Roles.Date: "date",
            self.Roles.ParentIdStr: "parent_id",
            self.Roles.TargetIdStr: "target_id",
            self.Roles.IsEnabled: "is_enabled",
            self.Roles.IsCurrent: "is_current",
            self.Roles.IsMarked: "is_marked",
            self.Roles.IsHead: "is_head",
            self.Roles.Column: "column",
        }
        key = role_map.get(role)
        return row.get(key) if key else None

    def roleNames(self):
        return {
            self.Roles.CommitIdStr: b"commitId",
            self.Roles.CommitType: b"commitType",
            self.Roles.Label: b"label",
            self.Roles.Date: b"date",
            self.Roles.ParentIdStr: b"parentId",
            self.Roles.TargetIdStr: b"targetId",
            self.Roles.IsEnabled: b"isEnabled",
            self.Roles.IsCurrent: b"isCurrent",
            self.Roles.IsMarked: b"isMarked",
            self.Roles.IsHead: b"isHead",
            self.Roles.Column: b"column",
        }

    # --- Refresh (called from Python signal connections in main.py) ---
    def refresh(self):
        if not self._store.has_database():
            self._clear_all()
            return

        db = self._store.database()
        current_cid = self._store.state().commit_id()
        head_ids = db.head_commit_ids()

        # Build grid for ordering
        root_node = CommitNode.build(db)
        grid_builder = CommitNodeGridBuilder.build(root_node)
        self._grid_nodes = grid_builder.nodes()  # dict[ValueCommitId, CommitNodeGrid]
        grid_nodes = self._grid_nodes

        # Enabled state
        enabled_map = CommitStateBuilder.enabled_by_commit_id(db, current_cid) if current_cid.is_valid() else {}

        # Build flat list sorted by grid row
        entries = []
        for cid, gnode in grid_nodes.items():
            header = gnode.header()
            ts = QDateTime.fromSecsSinceEpoch(int(header.timestamp()))
            is_marked = (self._marked_commit_id is not None and
                         cid.encoded() == self._marked_commit_id.encoded())
            entries.append((gnode.row(), gnode.column(), {
                "commit_id": cid.encoded() if cid.is_valid() else "",
                "commit_type": str(header.commit_type()),
                "label": header.label(),
                "date": ts.toString("yyyy-MM-dd hh:mm:ss"),
                "parent_id": header.parent_commit_id().encoded() if header.parent_commit_id().is_valid() else "",
                "target_id": header.target_commit_id().encoded() if header.target_commit_id().is_valid() else "",
                "is_enabled": enabled_map.get(cid, True),
                "is_current": cid.encoded() == current_cid.encoded() if current_cid.is_valid() else False,
                "is_marked": is_marked,
                "is_head": cid in head_ids,
                "column": gnode.column(),
            }, cid))

        entries.sort(key=lambda e: (e[0], e[1]))

        self.beginResetModel()
        self._rows = [e[2] for e in entries]
        self._commit_ids_list = [e[3] for e in entries]
        self.endResetModel()

        self._last_grid_builder = grid_builder
        self._last_enabled_map = enabled_map
        self._last_current_cid = current_cid
        self._build_graph(grid_builder, enabled_map, current_cid)
        self._update_current_info()
        self._update_marked_info()
        self.buttonStateChanged.emit()

    def _rebuild_if_needed(self):
        """Rebuild graph with cached parameters after viewport resize."""
        if self._last_grid_builder is not None:
            self._build_graph(self._last_grid_builder,
                              self._last_enabled_map,
                              self._last_current_cid)

    def clear(self):
        self._last_grid_builder = None
        self._last_enabled_map = {}
        self._last_current_cid = None
        self._clear_all()

    def _build_graph(self, grid_builder, enabled_map, current_cid):
        """Build graph data for QML Canvas."""
        self._graph_nodes.clear()
        self._graph_edges.clear()
        self._graph_merges.clear()

        grid_nodes = grid_builder.nodes()
        row_max = grid_builder.row_max()
        col_max = grid_builder.column_max()
        self._graph_width = col_max * NODE_SPACING_X + NODE_SIZE + MARGIN * 2
        content_height = row_max * NODE_SPACING_Y + MARGIN * 2
        self._graph_height = max(content_height, self._viewport_height)

        # Evaluation order
        order_map = {}
        state = self._store.state()
        order = 1
        for ea in reversed(state.eval_actions()):
            order_map[ea.header().commit_id()] = order
            order += 1

        # Collect all nodes (BFS from root children)
        root = grid_builder.root()
        if root is None:
            self.graphChanged.emit()
            return

        visited = []
        queue = list(root.children())
        i = 0
        while i < len(queue):
            visited.append(queue[i])
            queue.extend(queue[i].children())
            i += 1

        def node_x(n):
            return MARGIN + n.column() * NODE_SPACING_X + NODE_SIZE / 2

        def node_y(n):
            return self._graph_height - MARGIN - n.row() * NODE_SPACING_Y + NODE_SIZE / 2

        def node_color(n):
            cid = n.header().commit_id()
            if cid in enabled_map and enabled_map[cid]:
                return NODE_COLORS.get(n.header().commit_type(), GRAY)
            return GRAY

        # Edges
        for n in visited:
            if n.commit_id().is_valid() and n.parent() and n.parent().commit_id().is_valid():
                px, py = node_x(n.parent()), node_y(n.parent())
                cx, cy = node_x(n), node_y(n)
                self._graph_edges.append({
                    "px": px, "py": py, "cx": cx, "cy": cy,
                    "parentColor": node_color(n.parent()),
                    "childColor": node_color(n),
                })

        # Merges
        for n in visited:
            if n.header().commit_type() == "Merge":
                target = grid_nodes.get(n.header().target_commit_id())
                if target:
                    ncx, ncy = node_x(n), node_y(n)
                    tcx, tcy = node_x(target), node_y(target)
                    # Control points — route next to target node
                    target_nx = MARGIN + target.column() * NODE_SPACING_X
                    if ncx > tcx:
                        ctrl_x = target_nx + NODE_SIZE + 2
                    else:
                        ctrl_x = target_nx - 2
                    color = node_color(n)
                    if target.header().commit_id() not in enabled_map:
                        color = GRAY
                    self._graph_merges.append({
                        "ncx": ncx, "ncy": ncy,
                        "c1x": ctrl_x, "c1y": ncy,
                        "c2x": ctrl_x, "c2y": tcy,
                        "tcx": tcx, "tcy": tcy,
                        "color": color,
                    })

        # Nodes
        marked_encoded = self._marked_commit_id.encoded() if self._marked_commit_id else ""
        current_encoded = current_cid.encoded() if current_cid.is_valid() else ""
        for n in visited:
            cid = n.header().commit_id()
            if not cid.is_valid():
                continue
            encoded = cid.encoded()
            nx = MARGIN + n.column() * NODE_SPACING_X
            ny = self._graph_height - MARGIN - n.row() * NODE_SPACING_Y
            is_current = encoded == current_encoded
            self._graph_nodes.append({
                "x": nx, "y": ny,
                "color": node_color(n),
                "isCurrent": is_current,
                "isMarked": encoded == marked_encoded,
                "order": order_map.get(cid, 0) if not is_current else 0,
                "commitId": encoded,
            })
            if is_current:
                self._current_node_x = nx + NODE_SIZE // 2
                self._current_node_y = ny + NODE_SIZE // 2

        self.graphChanged.emit()

    @Slot(float, float, bool)
    def pickNode(self, mx: float, my: float, alt: bool):
        """Pick node at mouse coordinates"""
        for n in self._graph_nodes:
            nx, ny = n["x"], n["y"]
            if nx <= mx <= nx + NODE_SIZE and ny <= my <= ny + NODE_SIZE:
                encoded = n["commitId"]
                if alt:
                    self._mark_commit_by_id(encoded)
                else:
                    self._select_commit_by_id(encoded)
                return

    def _select_commit_by_id(self, encoded: str):
        """Select commit by encoded ID string."""
        self._store.notify_stop_live()
        for i, cid in enumerate(self._commit_ids_list):
            if cid.encoded() == encoded:
                try:
                    if cid == self._store.state().commit_id():
                        return
                    self._store.use_commit(cid)
                    self._store.reset_undo_redo()
                    self._store.notify_state_did_change()
                except Exception as e:
                    print(f"selectCommit error: {e}")
                return

    def _mark_commit_by_id(self, encoded: str):
        """Mark/unmark commit by encoded ID string."""
        for i, cid in enumerate(self._commit_ids_list):
            if cid.encoded() == encoded:
                self.markCommit(i)
                return

    # --- Keyboard navigation
    @Slot()
    def moveUp(self):
        """Navigate to first child of current commit."""
        try:
            commit_id = self._store.state().commit_id()
            node = self._grid_nodes.get(commit_id)
            if node and node.has_children():
                self._select_commit_by_id(node.children()[0].header().commit_id().encoded())
        except Exception as e:
            print(f"moveUp error: {e}")

    @Slot()
    def moveDown(self):
        """Navigate to parent of current commit."""
        try:
            commit_id = self._store.state().commit_id()
            node = self._grid_nodes.get(commit_id)
            if node and node.parent() and node.parent().header().commit_id().is_valid():
                self._select_commit_by_id(node.parent().header().commit_id().encoded())
        except Exception as e:
            print(f"moveDown error: {e}")

    @Slot(int)
    def moveSibling(self, direction: int):
        """Navigate to sibling commit."""
        try:
            commit_id = self._store.state().commit_id()
            node = self._grid_nodes.get(commit_id)
            if node is None:
                return

            if node.header().commit_type() == "Merge":
                self._select_commit_by_id(node.header().target_commit_id().encoded())
                return

            parent = node.parent()
            if not (parent and parent.header().commit_id().is_valid() and parent.child_count() > 1):
                return

            index = 0
            children = parent.children()
            for child in children:
                if child.header().commit_id() == node.header().commit_id():
                    break
                index += 1

            if index != parent.child_count():
                next_index = (index + parent.child_count() + direction) % parent.child_count()
                self._select_commit_by_id(children[next_index].header().commit_id().encoded())

        except Exception as e:
            print(f"moveSibling error: {e}")

    def _clear_all(self):
        self._marked_commit_id = None
        self._grid_nodes.clear()
        if self._rows:
            self.beginResetModel()
            self._rows.clear()
            self._commit_ids_list.clear()
            self.endResetModel()
        self._current_label = self._current_date = self._current_type = ""
        self._current_id = self._current_parent_id = self._current_target_id = ""
        self.currentInfoChanged.emit()
        self._marked_label = self._marked_date = self._marked_type = ""
        self._marked_id = self._marked_parent_id = self._marked_target_id = ""
        self._can_merge_marked = False
        self.markedInfoChanged.emit()
        self.canMergeMarkedChanged.emit()
        self._graph_nodes.clear()
        self._graph_edges.clear()
        self._graph_merges.clear()
        self._graph_width = 0
        self._graph_height = 0
        self._current_node_x = 0
        self._current_node_y = 0
        self.graphChanged.emit()

    # --- Selection ---
    @Slot(int)
    def selectCommit(self, row: int):
        """Click — switch to this commit."""
        if row < 0 or row >= len(self._commit_ids_list):
            return
        self._store.notify_stop_live()
        cid = self._commit_ids_list[row]
        try:
            if cid == self._store.state().commit_id():
                return
            self._store.use_commit(cid)
            self._store.reset_undo_redo()
            self._store.notify_state_did_change()
        except Exception as e:
            print(f"selectCommit error: {e}")

    @Slot(int)
    def markCommit(self, row: int):
        """Alt+click — mark/unmark."""
        if row < 0 or row >= len(self._commit_ids_list):
            return
        cid = self._commit_ids_list[row]
        if (self._marked_commit_id is not None and
                cid.encoded() == self._marked_commit_id.encoded()):
            self._marked_commit_id = None
        else:
            self._marked_commit_id = cid
        # Update is_marked in rows
        marked_encoded = self._marked_commit_id.encoded() if self._marked_commit_id else ""
        for i, r in enumerate(self._rows):
            r["is_marked"] = (bool(marked_encoded) and
                              self._commit_ids_list[i].encoded() == marked_encoded)
        idx_start = self.index(0)
        idx_end = self.index(len(self._rows) - 1)
        self.dataChanged.emit(idx_start, idx_end, [self.Roles.IsMarked])
        # Update graph nodes so Canvas repaints the dashed mark
        for gn in self._graph_nodes:
            gn["isMarked"] = (bool(marked_encoded) and gn["commitId"] == marked_encoded)
        self.graphChanged.emit()
        self._update_marked_info()
        self.buttonStateChanged.emit()

    # --- Actions on marked ---
    @Slot()
    def enableMarked(self):
        if not self._store.has_database():
            return
        if self._marked_commit_id is None:
            return
        try:
            cid = self._marked_commit_id
            self._marked_commit_id = None
            self._store.enable_commit(cid)
        except Exception as e:
            print(f"enableMarked error: {e}")

    @Slot()
    def disableMarked(self):
        if not self._store.has_database():
            return
        if self._marked_commit_id is None:
            return
        try:
            cid = self._marked_commit_id
            self._marked_commit_id = None
            self._store.disable_commit(cid)
        except Exception as e:
            print(f"disableMarked error: {e}")

    @Slot()
    def mergeMarked(self):
        if self._marked_commit_id is None:
            return
        try:
            cid = self._marked_commit_id
            self._marked_commit_id = None
            self._store.merge_commit(cid)
        except Exception as e:
            print(f"mergeMarked error: {e}")

    @Slot()
    def deleteCurrent(self):
        if not self._store.has_database():
            return
        try:
            self._store.delete_commit(self._store.state().commit_id())
        except Exception as e:
            print(f"deleteCurrent error: {e}")

    @Slot()
    def resetCommits(self):
        self._notifier.reset_database.emit()

    @Slot(str)
    def copyToClipboard(self, text: str):
        from PySide6.QtGui import QGuiApplication
        QGuiApplication.clipboard().setText(text)

    # --- Internal ---
    def _update_current_info(self):
        if not self._store.has_database():
            return
        cid = self._store.state().commit_id()
        if not cid.is_valid():
            return
        header = self._store.database().commit_header(cid)
        self._current_label = header.label()
        ts = QDateTime.fromSecsSinceEpoch(int(header.timestamp()))
        self._current_date = ts.toString()
        self._current_type = str(header.commit_type())
        self._current_id = header.commit_id().encoded() if header.commit_id().is_valid() else ""
        self._current_parent_id = header.parent_commit_id().encoded() if header.parent_commit_id().is_valid() else ""
        self._current_target_id = header.target_commit_id().encoded() if header.target_commit_id().is_valid() else ""
        self.currentInfoChanged.emit()

    def _update_marked_info(self):
        if self._marked_commit_id is None or not self._store.has_database():
            self._marked_label = self._marked_date = self._marked_type = ""
            self._marked_id = self._marked_parent_id = self._marked_target_id = ""
            self._can_merge_marked = False
        else:
            # Verify marked commit still exists
            db = self._store.database()
            if not db.commit_exists(self._marked_commit_id):
                self._marked_commit_id = None
                self._marked_label = self._marked_date = self._marked_type = ""
                self._marked_id = self._marked_parent_id = self._marked_target_id = ""
                self._can_merge_marked = False
                self.markedInfoChanged.emit()
                self.canMergeMarkedChanged.emit()
                return
            header = db.commit_header(self._marked_commit_id)
            self._marked_label = header.label()
            ts = QDateTime.fromSecsSinceEpoch(int(header.timestamp()))
            self._marked_date = ts.toString()
            self._marked_type = str(header.commit_type())
            self._marked_id = header.commit_id().encoded() if header.commit_id().is_valid() else ""
            self._marked_parent_id = header.parent_commit_id().encoded() if header.parent_commit_id().is_valid() else ""
            self._marked_target_id = header.target_commit_id().encoded() if header.target_commit_id().is_valid() else ""
            # Can merge?
            current_cid = self._store.state().commit_id()
            try:
                self._can_merge_marked = self._store.database().is_mergeable(current_cid, self._marked_commit_id)
            except Exception:
                self._can_merge_marked = False
        self.markedInfoChanged.emit()
        self.canMergeMarkedChanged.emit()
