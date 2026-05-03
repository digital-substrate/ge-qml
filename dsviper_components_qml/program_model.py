"""Program model — exposes commit opcodes to QML.

Shows opcodes of current commit with header info and value HTML.
"""
from __future__ import annotations

from PySide6.QtCore import (
    QAbstractTableModel, QModelIndex, QDateTime, Qt,
    Property, Signal, Slot,
)

from dsviper import (
    Html, ValueOpcode,
    ValueOpcodeDocumentSet, ValueOpcodeDocumentUpdate,
    ValueOpcodeSetUnion, ValueOpcodeSetSubtract,
    ValueOpcodeMapUnion, ValueOpcodeMapSubtract, ValueOpcodeMapUpdate,
    ValueOpcodeXArrayInsert, ValueOpcodeXArrayRemove, ValueOpcodeXArrayUpdate,
)


class ProgramModel(QAbstractTableModel):

    COLUMNS = ["Attachment", "Concept", "Instance ID", "Opcode", "Path", "Position", "Before Position"]
    _COLUMN_KEYS = ["attachment", "concept", "instance_id", "opcode_type", "path", "position", "before_position"]

    # Header properties
    headerChanged = Signal()
    valueHtmlChanged = Signal()
    useTraceChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._store = None
        self._opcodes: list[ValueOpcode] = []
        self._rows: list[dict] = []  # pre-computed row data

        # Header info
        self._label = ""
        self._date = ""
        self._commit_type = ""
        self._commit_id = ""
        self._parent_id = ""
        self._target_id = ""

        # Value display
        self._value_html = ""
        self._use_trace = False
        self._use_description = False

    def set_store(self, store, notifier):
        self._store = store
        notifier.state_did_change.connect(self.refresh)
        notifier.database_did_open.connect(self.refresh)
        notifier.database_did_close.connect(self.clear)

    # --- Header QML properties ---
    def _get_label(self): return self._label
    commitLabel = Property(str, _get_label, notify=headerChanged)

    def _get_date(self): return self._date
    commitDate = Property(str, _get_date, notify=headerChanged)

    def _get_commit_type(self): return self._commit_type
    commitType = Property(str, _get_commit_type, notify=headerChanged)

    def _get_commit_id(self): return self._commit_id
    commitId = Property(str, _get_commit_id, notify=headerChanged)

    def _get_parent_id(self): return self._parent_id
    parentId = Property(str, _get_parent_id, notify=headerChanged)

    def _get_target_id(self): return self._target_id
    targetId = Property(str, _get_target_id, notify=headerChanged)

    def _get_value_html(self): return self._value_html
    valueHtml = Property(str, _get_value_html, notify=valueHtmlChanged)

    def _get_use_trace(self): return self._use_trace
    def _set_use_trace(self, v):
        if v != self._use_trace:
            self._use_trace = v
            self.useTraceChanged.emit()
            self.refresh()

    useTrace = Property(bool, _get_use_trace, _set_use_trace, notify=useTraceChanged)

    # --- QAbstractTableModel ---
    def rowCount(self, parent=QModelIndex()):
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self.COLUMNS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._rows):
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            row = self._rows[index.row()]
            key = self._COLUMN_KEYS[index.column()]
            return row.get(key, "")
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.COLUMNS[section]
        return None

    # --- Refresh (called from Python signal connections in main.py) ---
    def refresh(self):
        if not self._store.has_database():
            self._clear_all()
            return

        db = self._store.database()
        commit_id = self._store.state().commit_id()
        if not commit_id.is_valid():
            self._clear_all()
            return

        commit = db.commit(commit_id)

        # Header
        header = commit.header()
        self._label = header.label()
        ts = QDateTime.fromSecsSinceEpoch(int(header.timestamp()))
        self._date = ts.toString()
        self._commit_type = str(header.commit_type())
        self._commit_id = header.commit_id().encoded() if header.commit_id().is_valid() else ""
        self._parent_id = header.parent_commit_id().encoded() if header.parent_commit_id().is_valid() else ""
        self._target_id = header.target_commit_id().encoded() if header.target_commit_id().is_valid() else ""
        self.headerChanged.emit()

        # Opcodes
        self._opcodes.clear()
        if self._use_trace:
            self._opcodes = self._store.state().traced_opcodes()
        else:
            if commit.program():
                self._opcodes = commit.program().all_opcodes()

        # Build rows
        defs = db.definitions()
        self.beginResetModel()
        self._rows.clear()
        for opcode in self._opcodes:
            self._rows.append(self._opcode_to_row(opcode, defs))
        self.endResetModel()

        # Auto-select first
        if self._opcodes:
            self.showValue(0)
        else:
            self._set_value_html("")

    def clear(self):
        self._clear_all()

    def _clear_all(self):
        self._label = self._date = self._commit_type = ""
        self._commit_id = self._parent_id = self._target_id = ""
        self.headerChanged.emit()
        self._opcodes.clear()
        if self._rows:
            self.beginResetModel()
            self._rows.clear()
            self.endResetModel()
        self._set_value_html("")

    def _opcode_to_row(self, opcode, defs) -> dict:
        opcode_key = opcode.key()
        att = defs.check_attachment(opcode_key.attachment_runtime_id())
        str_att = att.type_name().name()
        str_concept = defs.check_concept(opcode_key.concept_runtime_id()).representation()
        str_iid = opcode_key.instance_id().encoded()
        str_type = opcode.type()

        str_path = "-"
        if isinstance(opcode, (ValueOpcodeDocumentUpdate,
                               ValueOpcodeSetUnion, ValueOpcodeSetSubtract,
                               ValueOpcodeMapUnion, ValueOpcodeMapSubtract, ValueOpcodeMapUpdate,
                               ValueOpcodeXArrayInsert, ValueOpcodeXArrayRemove, ValueOpcodeXArrayUpdate)):
            str_path = opcode.path().representation()

        str_pos = "-"
        if isinstance(opcode, (ValueOpcodeXArrayInsert, ValueOpcodeXArrayRemove, ValueOpcodeXArrayUpdate)):
            str_pos = opcode.position().encoded()

        str_bpos = "-"
        if isinstance(opcode, ValueOpcodeXArrayInsert):
            str_bpos = opcode.before_position().encoded()

        return {
            "attachment": str_att,
            "concept": str_concept,
            "instance_id": str_iid,
            "opcode_type": str_type,
            "path": str_path,
            "position": str_pos,
            "before_position": str_bpos,
        }

    # --- Value display ---
    @Slot(int)
    def showValue(self, row: int):
        if row < 0 or row >= len(self._opcodes):
            self._set_value_html("")
            return

        opcode = self._opcodes[row]
        value = None
        if isinstance(opcode, (ValueOpcodeDocumentSet, ValueOpcodeDocumentUpdate,
                               ValueOpcodeSetUnion, ValueOpcodeSetSubtract,
                               ValueOpcodeMapUnion, ValueOpcodeMapSubtract, ValueOpcodeMapUpdate,
                               ValueOpcodeXArrayUpdate)):
            value = opcode.value()

        if value:
            content = Html.value(value, use_description=self._use_description)
            html = Html.document("Value Representation", Html.style(), Html.body(content))
            self._set_value_html(html)
        else:
            self._set_value_html("")

    @Slot(bool)
    def setUseDescription(self, v: bool):
        self._use_description = v

    @Slot(str)
    def copyToClipboard(self, text: str):
        from PySide6.QtGui import QGuiApplication
        QGuiApplication.clipboard().setText(text)

    def _set_value_html(self, html: str):
        if html != self._value_html:
            self._value_html = html
            self.valueHtmlChanged.emit()
