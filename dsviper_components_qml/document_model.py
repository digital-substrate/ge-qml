"""Document model — dbe read/write mutations via DatabaseManager.

Display layer inherited from BaseDocumentModel.
Mutations use direct database commits: db.commit() / db.commitDocument().
"""
from __future__ import annotations

from PySide6.QtCore import QModelIndex, Slot

from dsviper_components_qml.base_document_model import BaseDocumentModel
from dsviper_components_qml.database_manager import DatabaseManager


class DocumentModel(BaseDocumentModel):
    """Document tree for dbe — mutations via DatabaseManager.commit()."""

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(db_manager, parent)
        self._db = db_manager

    # ================================================================
    # Editing — direct database commit
    # ================================================================

    @Slot(QModelIndex, str, result=bool)
    def trySetValue(self, index: QModelIndex, text: str) -> bool:
        """Validate and commit. Routes entry_key/element paths correctly."""
        if not index.isValid():
            return False
        flat = index.internalPointer()
        n = flat.native
        if not n.is_editable():
            return False

        try:
            value = self._parse_value(n, text)
        except ValueError:
            self.validationFailed.emit(0, n.string_type())
            return False

        if value == n.value():
            return True  # no-op, value unchanged

        self._save_position(n)
        try:
            path = n.path()
            if path.is_entry_key_path():
                self._commit_update_entry_key(n, value)
            elif path.is_element_path():
                self._commit_update_element(n, value)
            else:
                path_const = path.regularized().const()
                if self._db.commit(n.attachment(), n.key(), path_const, value):
                    return True
                return False
            return True
        except Exception as e:
            print(f"trySetValue error: {e}")
            return False

    def _commit_update_entry_key(self, n, value):
        """Rename a map key — remove old entry, add with new key."""
        from dsviper import ValueMap
        path = n.path()
        info = path.entry_key_info()

        value_map = ValueMap.cast(info.map_path().at(n.document()))
        current_value = value_map.at(info.key(), encoded=False)
        if info.key_path().is_root():
            new_key = value
        else:
            new_key = info.key()
            info.key_path().set(new_key, value)

        self._current_path = info.map_path().copy().entry(new_key).index(0).path(info.key_path()).const()

        value_map.remove(info.key())
        value_map.set(new_key, current_value)
        self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _commit_update_element(self, n, value):
        """Replace a set element — remove old, add new."""
        from dsviper import ValueSet, Value
        path = n.path()
        info = path.element_info()

        value_set = ValueSet.cast(info.set_path().at(n.document()))
        current_value = value_set.at(info.index())

        if info.element_path().is_root():
            new_value = Value.copy(value)
        else:
            new_value = Value.copy(current_value)
            info.element_path().set(new_value, value)

        if index := value_set.index(new_value):
            self._current_path = info.set_path().copy().element(index).path(info.element_path()).const()

        value_set.remove(current_value)
        value_set.add(new_value)
        self._db.commitDocument(n.attachment(), n.key(), n.document())

    @Slot(QModelIndex, int, result=bool)
    def trySetEnum(self, index: QModelIndex, case_index: int) -> bool:
        """Set enum value by case index."""
        if not index.isValid():
            return False
        flat = index.internalPointer()
        n = flat.native
        if not n.is_enumeration():
            return False

        from dsviper import ValueEnumeration
        v = ValueEnumeration.cast(n.value())
        type_enum = v.type_enumeration()
        cases = type_enum.cases()
        if case_index < 0 or case_index >= len(cases):
            return False

        new_value = ValueEnumeration(type_enum, cases[case_index].name())
        self._save_position(n)
        path = n.path().regularized().const()
        if self._db.commit(n.attachment(), n.key(), path, new_value):
            return True
        return False

    @Slot(QModelIndex, str, result=bool)
    def trySetKey(self, index: QModelIndex, key_uuid: str) -> bool:
        """Set a ValueKey by UUID — used by key_set context action.

        Unlike trySetValue, this creates a proper ValueKey object from the UUID.
        """
        if not index.isValid():
            return False
        n = index.internalPointer().native

        from dsviper import ValueKey, ValueUUId, KeyHelper
        if not isinstance(n.value(), ValueKey):
            return False

        instance_id = ValueUUId.try_parse(key_uuid)
        if instance_id is None:
            return False

        key_type = ValueKey.cast(n.value()).type_key()
        ag = self._db.attachment_getting
        if ag is None:
            return False
        selected_key = None
        for k in KeyHelper.collect_keys(key_type, ag):
            vk = ValueKey.cast(k)
            if vk.instance_id() == instance_id:
                selected_key = vk
                break
        if selected_key is None:
            return False

        self._save_position(n)
        path = n.path().regularized().const()
        if self._db.commit(n.attachment(), n.key(), path, selected_key):
            return True
        return False

    @Slot(QModelIndex, result=list)
    def getAvailableKeys(self, index: QModelIndex) -> list:
        """Return all keys from all attachments for key selection."""
        ag = self._db.attachment_getting
        defs = self._db.definitions
        if ag is None or defs is None:
            return []

        from dsviper import KeyNamer
        key_namer = KeyNamer(defs)
        result = []
        seen = set()
        for att in defs.attachments():
            for k in ag.keys(att):
                uid = k.instance_id().encoded()
                if uid not in seen:
                    seen.add(uid)
                    name = key_namer.smart_name(k, ag) or uid[:20] + "..."
                    result.append({"uuid": uid, "name": name})
        return result

    @Slot(QModelIndex, str, result=bool)
    def setInsertKey(self, index: QModelIndex, key_uuid: str) -> bool:
        """Insert a key into a set<key>.

        ds_documents_databasing.py:198-214.
        """
        if not index.isValid():
            return False
        n = index.internalPointer().native

        from dsviper import ValueSet, ValueUUId, ValueKey, TypeKey, KeyHelper
        value_set = ValueSet.cast(n.value())

        instance_id = ValueUUId.try_parse(key_uuid)
        if instance_id is None:
            return False

        type_key = TypeKey.cast(value_set.type_set().element_type())
        ag = self._db.attachment_getting
        if ag is None:
            return False
        selected_key = None
        for k in KeyHelper.collect_keys(type_key, ag):
            vk = ValueKey.cast(k)
            if vk.instance_id() == instance_id:
                selected_key = vk
                break

        if selected_key is None:
            return False

        self._save_position(n)
        value_set.add(selected_key)
        if index := value_set.index(selected_key):
            self._save_position(n, n.path().copy().element(index).const())

        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    # ================================================================
    # Mutations
    # ================================================================

    def _mutation_optional_wrap(self, n) -> bool:
        from dsviper import ValueOptional, Value
        optional = ValueOptional.cast(n.value())
        self._save_position(n, n.path().copy().unwrap().const())
        value = ValueOptional(
            optional.type_optional(),
            Value.create(optional.type_optional().element_type())
        )
        n.path().regularized().set(n.document(), value)
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_optional_clear(self, n) -> bool:
        from dsviper import ValueOptional
        self._save_position(n)
        ValueOptional.cast(n.path().regularized().const().at(n.document())).clear()
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_vector_append(self, n) -> bool:
        from dsviper import ValueVector, Value
        vector = ValueVector.cast(n.value())
        self._save_position(n, n.path().copy().index(len(vector)).const())
        vector.append(Value.create(vector.type_vector().element_type()))
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_vector_insert(self, n) -> bool:
        from dsviper import ValueVector, Value
        parent = n.parent()
        vector = ValueVector.cast(parent.value())
        child_index = self._child_index(n)
        self._save_position(n)
        vector.insert(child_index, Value.create(vector.type_vector().element_type()))
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_vector_remove(self, n) -> bool:
        from dsviper import ValueVector
        parent = n.parent()
        vector = ValueVector.cast(parent.value())
        child_index = self._child_index(n)
        if len(vector) == 1:
            self._save_position(n, parent.path())
        else:
            idx = child_index if child_index < len(vector) - 1 else child_index - 1
            self._save_position(n, parent.path().copy().index(idx).const())
        vector.pop(child_index)
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_set_append(self, n) -> bool:
        from dsviper import ValueSet, Value
        value_set = ValueSet.cast(n.value())
        self._save_position(n, n.path().copy().element(len(value_set)).const())
        if len(value_set) == 0:
            v = Value.create(value_set.type_set().element_type())
        else:
            v = Value.succ(value_set.max(encoded=False))
        value_set.add(v)
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_set_remove(self, n) -> bool:
        from dsviper import ValueSet
        parent = n.parent()
        value_set = ValueSet.cast(parent.value())
        if len(value_set) == 1:
            self._save_position(n, parent.path())
        else:
            self._save_position(n)
        value_set.remove(n.value())
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_map_append(self, n) -> bool:
        from dsviper import ValueMap, Value
        value_map = ValueMap.cast(n.value())
        if len(value_map) == 0:
            new_key = Value.create(value_map.type_map().key_type())
        else:
            new_key = Value.succ(value_map.max(encoded=False))
        new_value = Value.create(value_map.type_map().element_type())
        self._save_position(n, n.path().copy().entry(new_key).index(0).const())
        value_map[new_key] = new_value
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_map_remove(self, n) -> bool:
        from dsviper import ValueMap
        parent = n.parent()
        value_map = ValueMap.cast(parent.value())
        if len(value_map) == 1:
            self._save_position(n, parent.path())
        else:
            child_index = self._child_index(n)
            siblings = parent.children()
            neighbor = siblings[1] if child_index == 0 else siblings[child_index - 1]
            self._save_position(n, neighbor.path())
        key = n.path().last_component_value(encoded=False)
        value_map.remove(key)
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_xarray_append(self, n) -> bool:
        from dsviper import ValueXArray, ValueUUId, Value
        value_xarray = ValueXArray.cast(n.value())
        before_position = ValueXArray.END
        new_position = ValueUUId.create()
        value = Value.create(value_xarray.type_xarray().element_type())
        self._save_position(n, n.path().copy().position(new_position).const())
        value_xarray.insert(before_position, value, new_position)
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_xarray_insert(self, n) -> bool:
        from dsviper import ValueXArray, ValueUUId, Value
        parent = n.parent()
        xarray_value = ValueXArray.cast(parent.value())
        before_position = ValueUUId.cast(n.path().last_component_value(encoded=False))
        new_position = ValueUUId.create()
        value = Value.create(xarray_value.type_xarray().element_type())
        self._save_position(n, parent.path().copy().position(new_position).const())
        xarray_value.insert(before_position, value, new_position)
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_xarray_remove(self, n) -> bool:
        from dsviper import ValueXArray, ValueUUId
        parent = n.parent()
        position = ValueUUId.cast(n.path().last_component_value(encoded=False))
        if parent.children() and len(parent.children()) == 1:
            self._save_position(n, parent.path())
        else:
            child_index = self._child_index(n)
            siblings = parent.children()
            neighbor = siblings[1] if child_index == 0 else siblings[child_index - 1]
            self._save_position(n, neighbor.path())
        value_xarray = ValueXArray.cast(parent.value())
        value_xarray.remove(position)
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_variant_reset(self, n, type_index: int) -> bool:
        from dsviper import ValueVariant, Value
        variant = ValueVariant.cast(n.value())
        vpr_type = variant.type_variant().types()[type_index]
        self._save_position(n, n.path().copy().unwrap().const())
        variant.wrap(Value.create(vpr_type))
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_any_clear(self, n) -> bool:
        from dsviper import ValueAny
        self._save_position(n)
        value = ValueAny.cast(n.value())
        value.clear()
        return self._db.commitDocument(n.attachment(), n.key(), n.document())

    def _mutation_any_reset(self, n, type_index: int):
        from dsviper import ValueAny, Value
        if type_index >= len(self._any_reset_types):
            return False
        vpr_type = self._any_reset_types[type_index]
        self._current_path = n.path().copy().unwrap().const()
        self._current_attachment = n.attachment()
        value = ValueAny.cast(n.value())
        value.wrap(Value.create(vpr_type))
        return self._db.commitDocument(n.attachment(), n.key(), n.document())
