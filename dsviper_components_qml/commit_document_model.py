"""Commit document model — CommitStore mutations.

Display layer inherited from BaseDocumentModel.
Mutations use granular attachment_mutating operations via CommitStoreManager,
"""
from __future__ import annotations

from PySide6.QtCore import QModelIndex, Slot

from dsviper_components_qml.base_document_model import BaseDocumentModel
from dsviper_components_qml.commit_store_manager import CommitStoreManager


class CommitDocumentModel(BaseDocumentModel):
    """Document tree for cdbe/graph_editor — mutations via CommitStore."""

    def __init__(self, mgr: CommitStoreManager, parent=None):
        super().__init__(mgr, parent)
        self._mgr = mgr

    # ================================================================
    # Editing — CommitStore pattern
    # ================================================================

    @Slot(QModelIndex, str, result=bool)
    def trySetValue(self, index: QModelIndex, text: str) -> bool:
        """Routes to update_entry_key / update_element / update_or_set
        depending on the path type.
        """
        if not index.isValid():
            return False
        n = index.internalPointer().native
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
                self._commit_update_or_set(n, value)
            return True
        except Exception as e:
            print(f"trySetValue error: {e}")
            return False

    def _commit_update_or_set(self, n, value):
        path = n.path().regularized().const()
        ms = self._mgr.mutableState()
        if path.is_root():
            label = f"Set {value}"
            ms.attachment_mutating().set(n.attachment(), n.key(), value)
        else:
            label = f"Update to {value}"
            ms.attachment_mutating().update(n.attachment(), n.key(), path, value)
        self._mgr.commitMutations(label, ms)

    def _commit_update_entry_key(self, n, value):
        from dsviper import ValueMap, ValueSet
        path = n.path()
        info = path.entry_key_info()

        value_map = ValueMap.cast(info.map_path().at(n.document()))
        if info.key_path().is_root():
            new_key = value
        else:
            new_key = info.key()
            info.key_path().set(new_key, value)

        self._current_path = info.map_path().copy().entry(new_key).index(0).path(info.key_path()).const()

        subtract_set = ValueSet(value_map.type_map().keys_type())
        subtract_set.add(info.key())

        union_map = ValueMap(value_map.type_map())
        union_map[new_key] = value_map[info.key()]

        ms = self._mgr.mutableState()
        map_path = info.map_path().regularized().const()
        ms.attachment_mutating().subtract_in_map(n.attachment(), n.key(), map_path, subtract_set)
        ms.attachment_mutating().union_in_map(n.attachment(), n.key(), map_path, union_map)
        self._mgr.commitMutations("Update Key in Map", ms)

    def _commit_update_element(self, n, value):
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

        subtract_set = ValueSet(value_set.type_set())
        subtract_set.add(current_value)

        union_set = ValueSet(value_set.type_set())
        union_set.add(new_value)

        ms = self._mgr.mutableState()
        set_path = info.set_path().regularized().const()
        ms.attachment_mutating().subtract_in_set(n.attachment(), n.key(), set_path, subtract_set)
        ms.attachment_mutating().union_in_set(n.attachment(), n.key(), set_path, union_set)
        self._mgr.commitMutations("Update Element in Set", ms)

    @Slot(QModelIndex, int, result=bool)
    def trySetEnum(self, index: QModelIndex, case_index: int) -> bool:
        if not index.isValid():
            return False
        n = index.internalPointer().native
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
        try:
            path = n.path().regularized().const()
            ms = self._mgr.mutableState()
            ms.attachment_mutating().update(n.attachment(), n.key(), path, new_value)
            self._mgr.commitMutations("Update Enumeration", ms)
            return True
        except Exception as e:
            print(f"trySetEnum error: {e}")
            return False

    @Slot(QModelIndex, str, result=bool)
    def trySetKey(self, index: QModelIndex, key_uuid: str) -> bool:
        """Set a ValueKey field to the key matching key_uuid.

        ValueKey object from the UUID string, then commits the mutation.
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
        ag = self._mgr.attachment_getting
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
        try:
            path = n.path()
            if path.is_entry_key_path():
                self._commit_update_entry_key(n, selected_key)
            elif path.is_element_path():
                self._commit_update_element(n, selected_key)
            else:
                self._commit_update_or_set(n, selected_key)
            return True
        except Exception as e:
            print(f"trySetKey error: {e}")
            return False

    @Slot(QModelIndex, result=list)
    def getAvailableKeys(self, index: QModelIndex) -> list:
        """Collects keys of the same type as the ValueKey at index,
        excluding the current key.
        """
        if not index.isValid():
            return []
        n = index.internalPointer().native
        from dsviper import ValueKey, KeyHelper, KeyNamer
        if not isinstance(n.value(), ValueKey):
            return []
        key = ValueKey.cast(n.value())
        ag = self._mgr.attachment_getting
        defs = self._mgr.definitions
        if ag is None or defs is None:
            return []
        keys = KeyHelper.collect_keys(key.type_key(), ag)
        keys.discard(key)
        key_namer = KeyNamer(defs)
        result = []
        for k in keys:
            vk = ValueKey.cast(k)
            uid = vk.instance_id().encoded()
            name = key_namer.smart_name(vk, ag) or uid[:20] + "..."
            result.append({"uuid": uid, "name": name})
        return result

    @Slot(QModelIndex, str, result=bool)
    def setInsertKey(self, index: QModelIndex, key_uuid: str) -> bool:
        if not index.isValid():
            return False
        n = index.internalPointer().native
        from dsviper import ValueSet, ValueUUId, ValueKey, TypeKey, KeyHelper
        value_set = ValueSet.cast(n.value())
        instance_id = ValueUUId.try_parse(key_uuid)
        if instance_id is None:
            return False
        type_key = TypeKey.cast(value_set.type_set().element_type())
        ag = self._mgr.attachment_getting
        if ag is None:
            return False
        keys = KeyHelper.collect_keys(type_key, ag)
        selected_key = None
        for k in keys:
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
        # Granular mutation
        union_set = ValueSet(value_set.type_set())
        union_set.add(selected_key)
        path = n.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().union_in_set(n.attachment(), n.key(), path, union_set)
        self._mgr.commitMutations("Insert a Key", ms)
        return True

    # ================================================================
    # Mutations
    # ================================================================

    def _mutation_optional_wrap(self, n) -> bool:
        from dsviper import ValueOptional, Value
        optional = ValueOptional.cast(n.value())
        self._save_position(n, n.path().copy().unwrap().const())
        value = ValueOptional(optional.type_optional(), Value.create(optional.type_optional().element_type()))
        path = n.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().update(n.attachment(), n.key(), path, value)
        self._mgr.commitMutations("Reset an Optional", ms)
        return True

    def _mutation_optional_clear(self, n) -> bool:
        from dsviper import ValueOptional
        self._save_position(n)
        value = ValueOptional.cast(n.value())
        value.clear()
        path = n.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().update(n.attachment(), n.key(), path, value)
        self._mgr.commitMutations("Clear an Optional", ms)
        return True

    def _mutation_vector_append(self, n) -> bool:
        from dsviper import ValueVector, Value
        vector = ValueVector.cast(n.value())
        self._save_position(n, n.path().copy().index(len(vector)).const())
        vector.append(Value.create(vector.type_vector().element_type()))
        path = n.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().update(n.attachment(), n.key(), path, vector)
        self._mgr.commitMutations("Append in Vector", ms)
        return True

    def _mutation_vector_insert(self, n) -> bool:
        from dsviper import ValueVector, Value
        parent = n.parent()
        vector = ValueVector.cast(parent.value())
        child_index = self._child_index(n)
        self._save_position(n)
        vector.insert(child_index, Value.create(vector.type_vector().element_type()))
        path = parent.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().update(n.attachment(), n.key(), path, vector)
        self._mgr.commitMutations("Insert in Vector", ms)
        return True

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
        path = parent.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().update(n.attachment(), n.key(), path, vector)
        self._mgr.commitMutations("Remove in Vector", ms)
        return True

    def _mutation_set_append(self, n) -> bool:
        from dsviper import ValueSet, Value
        value_set = ValueSet.cast(n.value())
        if len(value_set) == 0:
            v = Value.create(value_set.type_set().element_type())
        else:
            v = Value.succ(value_set.max(encoded=False))
        self._save_position(n, n.path().copy().element(len(value_set)).const())
        union_set = ValueSet(value_set.type_set())
        union_set.add(v)
        path = n.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().union_in_set(n.attachment(), n.key(), path, union_set)
        self._mgr.commitMutations("Insert in Set", ms)
        return True

    def _mutation_set_remove(self, n) -> bool:
        from dsviper import ValueSet
        parent = n.parent()
        value_set = ValueSet.cast(parent.value())
        if len(value_set) == 1:
            self._save_position(n, parent.path())
        else:
            self._save_position(n)
        subtract_set = ValueSet(value_set.type_set())
        subtract_set.add(n.value())
        path = parent.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().subtract_in_set(n.attachment(), n.key(), path, subtract_set)
        self._mgr.commitMutations("Subtract in Set", ms)
        return True

    def _mutation_map_append(self, n) -> bool:
        from dsviper import ValueMap, Value
        value_map = ValueMap.cast(n.value())
        if len(value_map) == 0:
            new_key = Value.create(value_map.type_map().key_type())
        else:
            new_key = Value.succ(value_map.max(encoded=False))
        new_value = Value.create(value_map.type_map().element_type())
        self._save_position(n, n.path().copy().entry(new_key).index(0).const())
        union_map = ValueMap(value_map.type_map())
        union_map[new_key] = new_value
        path = n.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().union_in_map(n.attachment(), n.key(), path, union_map)
        self._mgr.commitMutations("Append in Map", ms)
        return True

    def _mutation_map_remove(self, n) -> bool:
        from dsviper import ValueMap, ValueSet
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
        subtract_set = ValueSet(value_map.type_map().keys_type())
        subtract_set.add(key)
        path = parent.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().subtract_in_map(n.attachment(), n.key(), path, subtract_set)
        self._mgr.commitMutations("Subtract in Map", ms)
        return True

    def _mutation_xarray_append(self, n) -> bool:
        from dsviper import ValueXArray, ValueUUId, Value
        value_xarray = ValueXArray.cast(n.value())
        before_position = ValueXArray.END
        new_position = ValueUUId.create()
        value = Value.create(value_xarray.type_xarray().element_type())
        self._save_position(n, n.path().copy().position(new_position).const())
        path = n.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().insert_in_xarray(n.attachment(), n.key(), path, before_position, new_position, value)
        self._mgr.commitMutations("Append in XArray", ms)
        return True

    def _mutation_xarray_insert(self, n) -> bool:
        from dsviper import ValueXArray, ValueUUId, Value
        parent = n.parent()
        xarray_value = ValueXArray.cast(parent.value())
        before_position = ValueUUId.cast(n.path().last_component_value(encoded=False))
        new_position = ValueUUId.create()
        value = Value.create(xarray_value.type_xarray().element_type())
        self._save_position(n, parent.path().copy().position(new_position).const())
        path = parent.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().insert_in_xarray(n.attachment(), n.key(), path, before_position, new_position, value)
        self._mgr.commitMutations("Insert in XArray", ms)
        return True

    def _mutation_xarray_remove(self, n) -> bool:
        from dsviper import ValueUUId
        parent = n.parent()
        position = ValueUUId.cast(n.path().last_component_value(encoded=False))
        if parent.children() and len(parent.children()) == 1:
            self._save_position(n, parent.path())
        else:
            child_index = self._child_index(n)
            siblings = parent.children()
            neighbor = siblings[1] if child_index == 0 else siblings[child_index - 1]
            self._save_position(n, neighbor.path())
        path = parent.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().remove_in_xarray(n.attachment(), n.key(), path, position)
        self._mgr.commitMutations("Remove In XArray", ms)
        return True

    def _mutation_variant_reset(self, n, type_index: int) -> bool:
        from dsviper import ValueVariant, Value
        variant = ValueVariant.cast(n.value())
        vpr_type = variant.type_variant().types()[type_index]
        self._save_position(n, n.path().copy().unwrap().const())
        value = ValueVariant(variant.type_variant(), Value.create(vpr_type))
        path = n.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().update(n.attachment(), n.key(), path, value)
        self._mgr.commitMutations(f"Reset a Variant to {vpr_type.representation()}", ms)
        return True

    def _mutation_any_clear(self, n) -> bool:
        from dsviper import ValueAny
        self._save_position(n)
        value = ValueAny.cast(n.value())
        value.clear()
        path = n.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().update(n.attachment(), n.key(), path, value)
        self._mgr.commitMutations("Clear an Any", ms)
        return True

    def _mutation_any_reset(self, n, type_index: int) -> bool:
        from dsviper import ValueAny, Value
        if type_index >= len(self._any_reset_types):
            return False
        vpr_type = self._any_reset_types[type_index]
        self._save_position(n, n.path().copy().unwrap().const())
        value = ValueAny(Value.create(vpr_type))
        path = n.path().regularized().const()
        ms = self._mgr.mutableState()
        ms.attachment_mutating().update(n.attachment(), n.key(), path, value)
        self._mgr.commitMutations(f"Reset an Any to {vpr_type.representation()}", ms)
        return True
