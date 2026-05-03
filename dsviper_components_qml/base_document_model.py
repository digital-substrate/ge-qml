"""Base document model — tree model built from dsviper native DocumentNode.

Shared display layer for DocumentModel (dbe) and CommitDocumentModel (cdbe/graph_editor).
Uses DocumentNode.create_documents(key, attachment_getting) which returns one root
node per attachment. Each node provides:
  string_component, string_value, string_path, string_type,
  is_expandable, is_editable, is_boolean, is_enumeration, is_key, ...
  children(), parent(), path(), value(), key(), attachment()

Subclasses implement mutations only — all display/navigation/context menu is here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

from PySide6.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QTimer,
    Qt,
    Signal,
    Slot,
)


@dataclass
class FlatNode:
    """Wrapper around native DocumentNode for tree bookkeeping."""
    native: 'Any'        # dsviper.DocumentNode
    depth: int
    parent_node: 'FlatNode | None' = None
    children: list['FlatNode'] = field(default_factory=list)


class BaseDocumentModel(QAbstractItemModel):
    """Tree model built from dsviper DocumentNode.create_documents().

    4 columns: Component, Value, Path, Type — matching ge-py QTreeWidget.
    TreeView handles expand/collapse natively.

    Subclasses must implement:
      - trySetValue(index, text) → bool
      - trySetEnum(index, case_index) → bool
      - trySetKey(index, key_uuid) → bool
      - getAvailableKeys(index) → list
      - setInsertKey(index, key_uuid) → bool
      - All _mutation_* methods called by executeContextAction
    """

    validationFailed = Signal(int, str)
    jumpToKey = Signal(object)  # emits ValueKey for main.py to handle
    selectionChanged = Signal(object, object, object)  # key, attachment, path — for navigation tracking

    class Roles(IntEnum):
        Name = Qt.ItemDataRole.UserRole + 1
        Value = Qt.ItemDataRole.UserRole + 2
        ValueType = Qt.ItemDataRole.UserRole + 3
        Editable = Qt.ItemDataRole.UserRole + 4
        EnumCases = Qt.ItemDataRole.UserRole + 5
        EnumIndex = Qt.ItemDataRole.UserRole + 6
        IsKey = Qt.ItemDataRole.UserRole + 7

    _HEADERS = ["Component", "Value", "Path", "Type"]

    expandNodes = Signal(list)        # list of QModelIndex to expand
    scrollToIndex = Signal(QModelIndex)

    def __init__(self, source, parent=None):
        """Initialize with a data source (DatabaseManager or CommitStoreManager).

        The source must expose: attachment_getting, definitions,
        databaseClosed (signal), stateChanged (signal).
        """
        super().__init__(parent)
        self._source = source
        self._roots: list[FlatNode] = []
        self._current_key = None
        self._current_attachments: list = []
        # Path expansion state
        self._current_path = None       # PathConst to restore after rebuild
        self._current_attachment = None  # Attachment to match root
        self._any_reset_types: list = []  # Cached Fuzzer types for any_reset menu

        self._source.databaseClosed.connect(self.clear)
        self._source.stateChanged.connect(self._rebuild)

    # ================================================================
    # QAbstractItemModel interface
    # ================================================================

    def index(self, row: int, column: int = 0, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            if row < len(self._roots):
                return self.createIndex(row, column, self._roots[row])
            return QModelIndex()
        parent_node = parent.internalPointer()
        if row < len(parent_node.children):
            return self.createIndex(row, column, parent_node.children[row])
        return QModelIndex()

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        node = index.internalPointer()
        parent_node = node.parent_node
        if parent_node is None:
            return QModelIndex()
        if parent_node.parent_node is None:
            row = self._roots.index(parent_node)
        else:
            row = parent_node.parent_node.children.index(parent_node)
        return self.createIndex(row, 0, parent_node)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return len(self._roots)
        return len(parent.internalPointer().children)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 4

    def hasChildren(self, parent: QModelIndex = QModelIndex()) -> bool:
        if not parent.isValid():
            return len(self._roots) > 0
        node = parent.internalPointer()
        return len(node.children) > 0

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        flat = index.internalPointer()
        n = flat.native
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return n.string_component()
            if col == 1:
                return n.string_value()
            if col == 2:
                return n.string_path()
            if col == 3:
                return n.string_type()
            return None

        # Custom roles — column-independent (for editors)
        if role == self.Roles.Name:
            return n.string_component()
        if role == self.Roles.Value:
            return n.string_value()
        if role == self.Roles.ValueType:
            return n.string_type()
        if role == self.Roles.Editable:
            return n.is_editable()
        if role == self.Roles.EnumCases:
            if n.is_enumeration():
                from dsviper import ValueEnumeration
                v = ValueEnumeration.cast(n.value())
                return [c.name() for c in v.type_enumeration().cases()]
            return []
        if role == self.Roles.EnumIndex:
            if n.is_enumeration():
                from dsviper import ValueEnumeration
                return ValueEnumeration.cast(n.value()).index()
            return 0
        if role == self.Roles.IsKey:
            return n.is_key()
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(self._HEADERS):
                return self._HEADERS[section]
        return None

    def roleNames(self):
        return {
            Qt.ItemDataRole.DisplayRole: b"display",
            self.Roles.Name: b"name",
            self.Roles.Value: b"value",
            self.Roles.ValueType: b"valueType",
            self.Roles.Editable: b"editable",
            self.Roles.EnumCases: b"enumCases",
            self.Roles.EnumIndex: b"enumIndex",
            self.Roles.IsKey: b"isKey",
        }

    # ================================================================
    # Tree build
    # ================================================================

    def setKey(self, key, attachments: list, restore_attachment=None, restore_path=None):
        """Build document tree for the given key and its attachments."""
        self._current_key = key
        self._current_attachments = attachments
        if restore_attachment is not None:
            self._current_attachment = restore_attachment
        if restore_path is not None:
            self._current_path = restore_path
        self._rebuild()

    def _rebuild(self):
        """Rebuild tree using native DocumentNode.create_documents().

        For concept inheritance (e.g. LightSky inherits Light), a single key
        may have documents across attachments with different type_keys.
        We call create_documents with adapted keys and deduplicate by
        attachment runtime_id.
        """
        if self._current_key is None:
            return

        ag = self._source.attachment_getting
        if ag is None:
            return

        from dsviper import DocumentNode

        seen_att_ids = set()
        roots = []
        for att in self._current_attachments:
            att_id = att.runtime_id().encoded()
            if att_id in seen_att_ids:
                continue
            try:
                adapted_key = self._current_key.to_key(att.type_key())
            except Exception:
                continue  # key type incompatible with this attachment (e.g. sibling concepts)
            if not ag.has(att, adapted_key):
                continue
            doc = ag.get(att, adapted_key)
            if doc.is_nil():
                continue
            seen_att_ids.add(att_id)
            # create_documents returns all attachments for this key form;
            # pick only the one matching our target attachment
            for native in DocumentNode.create_documents(adapted_key, ag):
                if native.attachment().runtime_id() == att.runtime_id():
                    roots.append(self._wrap(native, 0, None))

        self.beginResetModel()
        self._roots = roots
        self.endResetModel()

        # TreeView needs a frame to process endResetModel before expanding
        QTimer.singleShot(0, self._expand_path)

    def _wrap(self, native, depth: int, parent_flat: FlatNode | None) -> FlatNode:
        """Wrap a native DocumentNode into a FlatNode with children."""
        flat = FlatNode(native=native, depth=depth, parent_node=parent_flat)
        if native.is_expandable():
            for child in native.children():
                flat.children.append(self._wrap(child, depth + 1, flat))
        return flat

    @Slot(str)
    def copyToClipboard(self, text: str):
        from PySide6.QtGui import QGuiApplication
        QGuiApplication.clipboard().setText(text)

    def inspectNode(self, index: QModelIndex):
        """Return (key, attachment, path) for the node at index.

        """
        if not index.isValid():
            return self._current_key, None, None
        n = index.internalPointer().native
        return n.key(), n.attachment(), n.path().regularized().const()

    @Slot(QModelIndex)
    def setSelectedIndex(self, index: QModelIndex):
        """Track selected node from QML TreeView for inspect_selection."""
        self._selected_index = index
        if index.isValid():
            n = index.internalPointer().native
            self._current_attachment = n.attachment()
            self._current_path = n.path()
            self.selectionChanged.emit(n.key(), n.attachment(), n.path())
        else:
            self._current_attachment = None
            self._current_path = None

    def getSelectedInspection(self):
        """Return (key, attachment, path) for the currently selected tree node."""
        idx = getattr(self, '_selected_index', QModelIndex())
        return self.inspectNode(idx)

    # ================================================================
    # Context Menu
    # ================================================================

    @Slot(QModelIndex, result=list)
    def getContextMenu(self, index: QModelIndex) -> list:
        """Return context menu actions for the node at index.

        Returns list of {"id": str, "label": str} dicts.
        """
        if not index.isValid():
            return []

        from dsviper import (
            ValueOptional, ValueVector, ValueSet, ValueMap,
            ValueXArray, ValueVariant, ValueAny, ValueKey, TypeKey,
        )

        n = index.internalPointer().native
        if n.path().is_entry_key_path():
            return []

        item_blocked = n.path().is_element_path()
        parent_blocked = n.parent() is not None and n.parent().path().is_element_path()
        val = n.value()
        actions = []

        # Container operations — mutation uses item path
        if not item_blocked:

            if isinstance(val, ValueOptional):
                opt = ValueOptional.cast(val)
                if opt.is_nil():
                    actions.append({"id": "optional_wrap", "label": "Wrap Default"})
                else:
                    actions.append({"id": "optional_clear", "label": "Clear"})
                return actions

            if isinstance(val, ValueVector):
                actions.append({"id": "vector_append", "label": "Append"})
                return actions

            if isinstance(val, ValueSet):
                vset = ValueSet.cast(val)
                element_type = vset.type_set().element_type()
                if isinstance(element_type, TypeKey):
                    actions.append({"id": "set_insert_key", "label": "Insert Key"})
                else:
                    from dsviper import TypeOptional, TypeVector, TypeVec, TypeMap, TypeXArray, TypeVariant, TypeAny, TypeSet
                    if not isinstance(element_type, (TypeOptional, TypeVector, TypeVec, TypeSet, TypeMap, TypeXArray, TypeVariant, TypeAny)):
                        actions.append({"id": "set_append", "label": "Append"})
                return actions

            if isinstance(val, ValueMap):
                actions.append({"id": "map_append", "label": "Append"})
                return actions

            if isinstance(val, ValueXArray):
                actions.append({"id": "xarray_append", "label": "Append"})
                return actions

            if isinstance(val, ValueVariant):
                variant = ValueVariant.cast(val)
                for i, vpr_type in enumerate(variant.type_variant().types()):
                    actions.append({
                        "id": f"variant_reset_{i}",
                        "label": f"Reset to {vpr_type.representation()}"
                    })
                return actions

            if isinstance(val, ValueAny):
                any_val = ValueAny.cast(val)
                if not any_val.is_nil():
                    actions.append({"id": "any_clear", "label": "Clear"})
                from dsviper import Fuzzer, TypeBlob, TypeBlobId
                defs = self._source.definitions
                if defs is not None:
                    fuzzer = Fuzzer(defs)
                    self._any_reset_types = []
                    for vpr_type in fuzzer.types():
                        if isinstance(vpr_type, (TypeBlob, TypeBlobId)):
                            continue
                        self._any_reset_types.append(vpr_type)
                        actions.append({
                            "id": f"any_reset_{len(self._any_reset_types) - 1}",
                            "label": f"Reset to {vpr_type.representation()}"
                        })
                return actions

        # Child operations — mutation uses parent path
        parent_node = n.parent()
        if not parent_blocked and parent_node:
            parent_val = parent_node.value()

            if isinstance(parent_val, ValueVector):
                actions.append({"id": "vector_remove", "label": "Remove"})
                actions.append({"id": "vector_insert", "label": "Insert"})

            elif isinstance(parent_val, ValueSet):
                actions.append({"id": "set_remove", "label": "Remove"})

            elif isinstance(parent_val, ValueMap):
                actions.append({"id": "map_remove", "label": "Remove"})

            elif isinstance(parent_val, ValueXArray):
                actions.append({"id": "xarray_remove", "label": "Remove"})
                actions.append({"id": "xarray_insert", "label": "Insert"})

        # Key type — ds_documents.py:823-842
        if isinstance(val, ValueKey):
            if actions:
                actions.append({"id": "_sep", "label": "-"})
            actions.append({"id": "key_set", "label": "Set Key"})
            key_val = ValueKey.cast(val)
            if key_val.instance_id().is_valid():
                actions.append({"id": "key_jump", "label": "Jump To Key"})
            actions.append({"id": "key_copy", "label": "Copy Key Instance ID"})

        return actions

    @Slot(QModelIndex, str, result=bool)
    def executeContextAction(self, index: QModelIndex, action_id: str) -> bool:
        """Execute a context menu action. Dispatches to mutation methods.

        Mutation methods are implemented by subclasses.
        """
        if not index.isValid():
            return False

        n = index.internalPointer().native

        try:
            # Optional — ds_documents_databasing.py:127-149
            if action_id == "optional_wrap":
                return self._mutation_optional_wrap(n)
            if action_id == "optional_clear":
                return self._mutation_optional_clear(n)

            # Vector — ds_documents_databasing.py:153-194
            if action_id == "vector_append":
                return self._mutation_vector_append(n)
            if action_id == "vector_insert":
                return self._mutation_vector_insert(n)
            if action_id == "vector_remove":
                return self._mutation_vector_remove(n)

            # Set — ds_documents_databasing.py:216-242
            if action_id == "set_append":
                return self._mutation_set_append(n)
            if action_id == "set_remove":
                return self._mutation_set_remove(n)

            # Map — ds_documents_databasing.py:246-287
            if action_id == "map_append":
                return self._mutation_map_append(n)
            if action_id == "map_remove":
                return self._mutation_map_remove(n)

            # XArray — ds_documents_databasing.py:291-347
            if action_id == "xarray_append":
                return self._mutation_xarray_append(n)
            if action_id == "xarray_insert":
                return self._mutation_xarray_insert(n)
            if action_id == "xarray_remove":
                return self._mutation_xarray_remove(n)

            # Variant — ds_documents_databasing.py:351-367
            if action_id.startswith("variant_reset_"):
                type_index = int(action_id.split("_")[-1])
                return self._mutation_variant_reset(n, type_index)

            # Any — ds_documents_databasing.py:371-398
            if action_id == "any_clear":
                return self._mutation_any_clear(n)
            if action_id.startswith("any_reset_"):
                type_index = int(action_id.split("_")[-1])
                return self._mutation_any_reset(n, type_index)

            # Key actions — ds_documents.py:746-778, 801-821
            if action_id == "key_jump":
                self._key_jump_to(n)
                return True
            if action_id == "key_copy":
                self._key_copy(n)
                return True
            # key_set is handled by QML (opens keyDialog)

        except Exception as e:
            print(f"Context action error: {e}")
            return False

        return False

    # ================================================================
    # Key selection — shared query, subclass-specific mutation
    # ================================================================

    @Slot(QModelIndex, result=list)
    def getSetInsertKeyCandidates(self, index: QModelIndex) -> list:
        """Return candidate keys for set<key> insertion.

        Returns list of {"uuid": str, "name": str} for the key dialog.
        """
        if not index.isValid():
            return []
        n = index.internalPointer().native

        from dsviper import ValueSet, TypeKey, KeyHelper, KeyNamer
        value_set = ValueSet.cast(n.value())
        type_key = TypeKey.cast(value_set.type_set().element_type())
        ag = self._source.attachment_getting
        defs = self._source.definitions
        if ag is None or defs is None:
            return []

        keys = KeyHelper.collect_keys(type_key, ag)
        keys.difference_update(value_set)

        key_namer = KeyNamer(defs)
        result = []
        for k in keys:
            from dsviper import ValueKey
            vk = ValueKey.cast(k)
            uid = vk.instance_id().encoded()
            name = key_namer.smart_name(vk, ag) or uid[:20] + "..."
            result.append({"uuid": uid, "name": name})
        return result

    # ================================================================
    # Key Actions
    # ================================================================

    @Slot(QModelIndex)
    def tryJumpToKey(self, index: QModelIndex):
        if not index.isValid():
            return
        n = index.internalPointer().native
        from dsviper import ValueKey
        if isinstance(n.value(), ValueKey):
            self._key_jump_to(n)

    def _key_jump_to(self, n):
        """Jump to the key referenced by this node.

        Emits jumpToKey signal — main.py handles navigation.
        """
        from dsviper import ValueKey
        key = ValueKey.cast(n.value())
        if not key.instance_id().is_valid():
            return
        go_key = key.to_concept_key()
        self.jumpToKey.emit(go_key)

    def _key_copy(self, n):
        """Copy key instance ID to clipboard.

        """
        from dsviper import ValueKey
        from PySide6.QtGui import QGuiApplication
        key = ValueKey.cast(n.value())
        QGuiApplication.clipboard().setText(key.instance_id().encoded())

    # ================================================================
    # Helpers
    # ================================================================

    def _save_position(self, n, path=None):
        """Save current position for path expansion after rebuild.

        """
        self._current_attachment = n.attachment()
        self._current_path = path if path else n.path()

    def _parse_value(self, node, text: str):
        """Parse text to a typed dsviper Value using try_parse.

        Transposition of ge-py DSDocuments._value_from_representation.
        Returns a Value or raises ValueError if invalid.
        """
        from dsviper import (
            Value, Type,
            ValueBool, ValueUInt8, ValueUInt16, ValueUInt32, ValueUInt64,
            ValueInt8, ValueInt16, ValueInt32, ValueInt64,
            ValueFloat, ValueDouble,
            ValueBlobId, ValueCommitId, ValueUUId, ValueEnumeration,
            TypeBool, TypeUInt8, TypeUInt16, TypeUInt32, TypeUInt64,
            TypeInt8, TypeInt16, TypeInt32, TypeInt64,
            TypeFloat, TypeDouble,
            TypeBlobId, TypeCommitId, TypeUUId,
            TypeString, TypeEnumeration,
        )
        vpr_type = node.value().type()

        if isinstance(vpr_type, TypeBool):
            result = ValueBool.try_parse(text)
        elif isinstance(vpr_type, TypeUInt8):
            result = ValueUInt8.try_parse(text)
        elif isinstance(vpr_type, TypeUInt16):
            result = ValueUInt16.try_parse(text)
        elif isinstance(vpr_type, TypeUInt32):
            result = ValueUInt32.try_parse(text)
        elif isinstance(vpr_type, TypeUInt64):
            result = ValueUInt64.try_parse(text)
        elif isinstance(vpr_type, TypeInt8):
            result = ValueInt8.try_parse(text)
        elif isinstance(vpr_type, TypeInt16):
            result = ValueInt16.try_parse(text)
        elif isinstance(vpr_type, TypeInt32):
            result = ValueInt32.try_parse(text)
        elif isinstance(vpr_type, TypeInt64):
            result = ValueInt64.try_parse(text)
        elif isinstance(vpr_type, TypeFloat):
            result = ValueFloat.try_parse(text)
        elif isinstance(vpr_type, TypeDouble):
            result = ValueDouble.try_parse(text)
        elif isinstance(vpr_type, TypeBlobId):
            result = ValueBlobId.try_parse(text)
        elif isinstance(vpr_type, TypeCommitId):
            result = ValueCommitId.try_parse(text)
        elif isinstance(vpr_type, TypeUUId):
            result = ValueUUId.try_parse(text)
        elif isinstance(vpr_type, TypeString):
            result = Value.create(Type.STRING, text)
        elif isinstance(vpr_type, TypeEnumeration):
            result = ValueEnumeration.try_parse(text, vpr_type)
        else:
            result = None

        if result is None:
            raise ValueError(f"Invalid value for {vpr_type.representation()}")
        return result

    def _child_index(self, n) -> int:
        """Find the index of node n among its parent's children."""
        parent = n.parent()
        if parent is None:
            return 0
        node_uuid = n.uuid()
        for i, sibling in enumerate(parent.children()):
            if sibling.uuid() == node_uuid:
                return i
        return 0

    # ================================================================
    # Path Expansion
    # ================================================================

    def _index_for_node(self, node: FlatNode) -> QModelIndex:
        """Create QModelIndex for a FlatNode."""
        if node.parent_node is None:
            row = self._roots.index(node)
        else:
            row = node.parent_node.children.index(node)
        return self.createIndex(row, 0, node)

    def _expand_path(self):
        """After rebuild, re-expand to _current_path + _current_attachment.

        Emits expandNodes signal for QML TreeView to process.
        """
        if not self._roots:
            return

        is_resolved = False
        if self._current_path and self._current_attachment:
            for flat in self._roots:
                n = flat.native
                if n.attachment().runtime_id() == self._current_attachment.runtime_id():
                    is_resolved = self._expand_path_node(self._current_path, flat)
                    if is_resolved:
                        break

        # Default: expand single root
        if not is_resolved and len(self._roots) == 1:
            self.expandNodes.emit([self._index_for_node(self._roots[0])])

    def _expand_path_node(self, path, flat: FlatNode) -> bool:
        """Walk ancestors of path to find and expand matching nodes.

        Emits expandNodes + scrollToIndex for QML TreeView.
        """
        ancestors = path.ancestors()
        if ancestors:
            ancestors.pop()  # remove root path

        # Walk down the tree following path ancestors
        current = flat
        nodes_to_expand = [flat]  # always expand root

        while ancestors:
            search_path = ancestors[-1]
            found = None
            for child in current.children:
                if child.native.path() == search_path.const():
                    found = child
                    break
            if found:
                ancestors.pop()
                nodes_to_expand.append(found)
                current = found
            else:
                break

        # Emit indices to expand
        indices = [self._index_for_node(node) for node in nodes_to_expand
                   if node.children]
        if indices:
            self.expandNodes.emit(indices)

        is_resolved = len(ancestors) == 0
        if is_resolved:
            self.scrollToIndex.emit(self._index_for_node(current))

        return is_resolved

    def clear(self):
        self._current_key = None
        self._current_attachments = []
        self._current_path = None
        self._current_attachment = None
        self.beginResetModel()
        self._roots = []
        self.endResetModel()
