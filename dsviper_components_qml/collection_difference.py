"""OrderedCollectionDifference - Python equivalent of NSOrderedCollectionDifference.

Computes the minimal set of changes (insertions, removals) to transform
one ordered collection into another, preserving order.

Changes are expressed as contiguous ranges, matching Qt's beginInsertRows/beginRemoveRows
API which takes (first, last) pairs.

Usage:
    diff = OrderedCollectionDifference.from_collections(old_list, new_list, key=lambda x: x.id)
    for r in diff.removals:
        model.beginRemoveRows(parent, r.first, r.last)
        del items[r.first:r.last + 1]
        model.endRemoveRows()
    for r in diff.insertions:
        model.beginInsertRows(parent, r.first, r.last)
        items[r.first:r.first] = r.elements
        model.endInsertRows()
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TypeVar, Generic, Callable, Sequence
import difflib

T = TypeVar('T')


class ChangeType(Enum):
    INSERT = "insert"
    REMOVE = "remove"


@dataclass
class RangeChange(Generic[T]):
    """A contiguous range change — maps directly to beginInsertRows/beginRemoveRows."""
    change_type: ChangeType
    first: int
    last: int
    elements: list[T] = field(default_factory=list)

    @property
    def count(self) -> int:
        return self.last - self.first + 1


@dataclass
class OrderedCollectionDifference(Generic[T]):
    """Represents the difference between two ordered collections.

    Equivalent to NSOrderedCollectionDifference in Foundation.
    Uses difflib.SequenceMatcher (Myers diff algorithm) to compute
    the minimal set of changes. Changes are expressed as contiguous ranges.
    """
    _removals: list[RangeChange[T]]
    _insertions: list[RangeChange[T]]

    @property
    def removals(self) -> list[RangeChange[T]]:
        """Removal ranges in reverse index order (safe for applying)."""
        return self._removals

    @property
    def insertions(self) -> list[RangeChange[T]]:
        """Insertion ranges in ascending index order."""
        return self._insertions

    @property
    def has_changes(self) -> bool:
        return len(self._removals) > 0 or len(self._insertions) > 0

    @property
    def removal_count(self) -> int:
        return sum(r.count for r in self._removals)

    @property
    def insertion_count(self) -> int:
        return sum(r.count for r in self._insertions)

    @classmethod
    def from_collections(
        cls,
        old: Sequence[T],
        new: Sequence[T],
        key: Callable[[T], any] | None = None
    ) -> OrderedCollectionDifference[T]:
        """Compute the difference between two collections.

        Args:
            old: The original collection
            new: The new collection
            key: Optional function to extract comparison key from elements.
                 If None, elements are compared directly.

        Returns:
            OrderedCollectionDifference with contiguous range changes.
        """
        if key is None:
            key = lambda x: x

        old_keys = [key(e) for e in old]
        new_keys = [key(e) for e in new]

        matcher = difflib.SequenceMatcher(None, old_keys, new_keys)
        removals: list[RangeChange[T]] = []
        insertions: list[RangeChange[T]] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                removals.append(RangeChange(
                    change_type=ChangeType.REMOVE,
                    first=i1, last=i2 - 1,
                    elements=list(old[i1:i2])
                ))
            elif tag == 'insert':
                insertions.append(RangeChange(
                    change_type=ChangeType.INSERT,
                    first=j1, last=j2 - 1,
                    elements=list(new[j1:j2])
                ))
            elif tag == 'replace':
                removals.append(RangeChange(
                    change_type=ChangeType.REMOVE,
                    first=i1, last=i2 - 1,
                    elements=list(old[i1:i2])
                ))
                insertions.append(RangeChange(
                    change_type=ChangeType.INSERT,
                    first=j1, last=j2 - 1,
                    elements=list(new[j1:j2])
                ))

        # Removals in reverse order — highest index first (safe for applying)
        removals.sort(key=lambda r: r.first, reverse=True)
        # Insertions in ascending order
        insertions.sort(key=lambda r: r.first)

        return cls(_removals=removals, _insertions=insertions)

    def __repr__(self) -> str:
        return f"OrderedCollectionDifference(removals={self.removal_count}, insertions={self.insertion_count})"
