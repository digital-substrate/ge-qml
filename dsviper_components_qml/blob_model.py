"""Blob model — lists blob infos from BlobGetting.

Read-only inspector for database binary blobs.
"""
from __future__ import annotations

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
    Property,
    Signal,
    Slot,
)

from .database_manager import DatabaseManager


def _format_unit(value: float) -> str:
    """Format like NSByteCountFormatter — no decimals above 10, one below."""
    if value >= 100:
        return str(int(round(value)))
    if value >= 10:
        return str(int(round(value)))
    return f"{value:.1f}" if value % 1 >= 0.05 else str(int(value))


def _byte_count(value: int) -> str:
    if value == 1:
        return "1 byte"
    if value < 1000:
        return f"{value} bytes"
    kb = value / 1000
    if kb < 1000:
        return f"{_format_unit(kb)} KB"
    mb = kb / 1000
    if mb < 1000:
        return f"{_format_unit(mb)} MB"
    gb = mb / 1000
    return f"{_format_unit(gb)} GB"


class BlobModel(QAbstractTableModel):
    """Lists blob infos for the Blobs dialog.

    """

    COLUMNS = ["Blob ID", "Layout", "Size", "Chunked", "RowId"]
    _COLUMN_KEYS = ["blob_id", "layout", "size", "chunked", "row_id"]

    statisticsChanged = Signal()

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self._db = db_manager
        self._items: list[dict] = []
        self._blob_ids: set = set()
        # Statistics
        self._count = "-"
        self._total = "-"
        self._min = "-"
        self._max = "-"

        self._db.databaseOpened.connect(self._on_opened)
        self._db.databaseClosed.connect(self._clear)

    def columnCount(self, parent=QModelIndex()):
        return len(self.COLUMNS)

    # Statistics as QML properties
    def _get_count(self) -> str:
        return self._count

    def _get_total(self) -> str:
        return self._total

    def _get_min(self) -> str:
        return self._min

    def _get_max(self) -> str:
        return self._max

    statCount = Property(str, _get_count, notify=statisticsChanged)
    statTotal = Property(str, _get_total, notify=statisticsChanged)
    statMin = Property(str, _get_min, notify=statisticsChanged)
    statMax = Property(str, _get_max, notify=statisticsChanged)

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            row = self._items[index.row()]
            key = self._COLUMN_KEYS[index.column()]
            return row.get(key, "")
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.COLUMNS[section]
        return None

    def sort(self, column, order=Qt.SortOrder.AscendingOrder):
        self.beginResetModel()
        key = self._COLUMN_KEYS[column]
        # Size column: sort on raw numeric value, not formatted string
        if key == "size":
            sort_key = lambda x: x["size_raw"]
        else:
            sort_key = lambda x: x[key]
        self._items.sort(key=sort_key, reverse=(order == Qt.SortOrder.DescendingOrder))
        self.endResetModel()

    def _on_opened(self):
        bg = self._db.blob_getting
        if bg is None:
            return
        self._blob_ids = bg.blob_ids()
        items = []
        for info in bg.blob_infos(self._blob_ids):
            items.append({
                "blob_id": info.blob_id().representation(),
                "layout": info.blob_layout().representation(),
                "size": _byte_count(info.size()),
                "size_raw": info.size(),
                "chunked": "Yes" if info.chunked() else "No",
                "row_id": info.row_id(),
            })
        # Sort by blob_id
        items.sort(key=lambda x: x["blob_id"])

        self.beginResetModel()
        self._items = items
        self.endResetModel()
        self._update_statistics()

    @Slot()
    def refresh(self):
        bg = self._db.blob_getting
        if bg is None:
            return
        self._update_statistics()

        # Check for new blobs
        stats = bg.blob_statistics()
        if stats.count() == len(self._blob_ids):
            return

        db_blob_ids = bg.blob_ids()
        added = db_blob_ids.difference(self._blob_ids)
        new_items = []
        for info in bg.blob_infos(added):
            new_items.append({
                "blob_id": info.blob_id().representation(),
                "layout": info.blob_layout().representation(),
                "size": _byte_count(info.size()),
                "size_raw": info.size(),
                "chunked": "Yes" if info.chunked() else "No",
                "row_id": info.row_id(),
            })
        if new_items:
            pos = len(self._items)
            self.beginInsertRows(QModelIndex(), pos, pos + len(new_items) - 1)
            self._items.extend(new_items)
            self.endInsertRows()

        self._blob_ids = db_blob_ids

    def _update_statistics(self):
        bg = self._db.blob_getting
        if bg is None:
            return
        stats = bg.blob_statistics()
        self._count = str(stats.count())
        self._total = _byte_count(stats.total_size())
        self._min = _byte_count(stats.min_size())
        self._max = _byte_count(stats.max_size())
        self.statisticsChanged.emit()

    def _clear(self):
        self._blob_ids = set()
        self.beginResetModel()
        self._items = []
        self.endResetModel()
        self._count = "-"
        self._total = "-"
        self._min = "-"
        self._max = "-"
        self.statisticsChanged.emit()
