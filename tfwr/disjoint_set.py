# https://github.com/mrapacz/disjoint-set/

# MIT License

# Copyright (c) 2019 Maciej Rapacz

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import copy
import sys
from collections import defaultdict
from collections.abc import Iterable, Iterator
from typing import Any, Generic, TypeVar

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

T = TypeVar("T")


class IdentityDict(dict[T, T]):
    """A defaultdict implementation which places the requested key as its value in case it's missing."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    def __missing__(self, key: T) -> T:
        self[key] = key
        return key


class InvalidInitialMappingError(RuntimeError):
    """Runtime error raised when invalid initial mapping causes the find() methods to change during iteration."""

    def __init__(
        self,
        msg: str = (
            "The mapping passed during ther DisjointSet initialization must have been wrong. "
            "Check that all keys are mapping to other keys and not some external values."
        ),
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(msg, *args, **kwargs)


class DisjointSet(Generic[T]):
    """A disjoint set data structure."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Disjoint set data structure.

        The data structure can be initialized as an empty disjoint set:
        >>> DisjointSet()
        DisjointSet({})

        But it can also be instantiated from an existing mapping such as:
        >>> DisjointSet({1: 2, 2: 2})
        DisjointSet({1: 2, 2: 2})
        """
        self._data: IdentityDict[T] = IdentityDict(*args, **kwargs)
        self._rev_data: dict[T, set[T]] = {}
        for k, v in self._data.items():
            if v in self._rev_data:
                self._rev_data[v].add(k)
            else:
                self._rev_data[v] = {k}

    @classmethod
    def from_iterable(cls, iterable: Iterable[T]) -> DisjointSet[T]:
        """Instantiate a DistjointSet instance by transforming each element from an interable to a canonical element."""
        return cls({x: x for x in iterable})

    def __len__(self) -> int:
        """Return the number of elements in the disjoint set."""
        return len(self._data)

    def __contains__(self, item: T) -> bool:
        """Return True if `item` is an element of the disjoint set (not necessarily a canonical one)."""
        return item in self._data

    def __bool__(self) -> bool:
        """Return True if disjoint set contains at least one element."""
        return bool(self._data)

    def __getitem__(self, element: T) -> T:
        return self.find(element)

    @override
    def __eq__(self, other: object) -> bool:
        """
        Return True if both DistjoinSet structures are equivalent.

        This may mean that their canonical elements are different, but the sets they form are the same.
        >>> DisjointSet({1: 1, 2: 1}) == DisjointSet({1: 2, 2: 2})
        True
        """
        if not isinstance(other, DisjointSet):
            return False

        return {tuple(x) for x in self.itersets()} == {
            tuple(x) for x in other.itersets()
        }

    @override
    def __repr__(self) -> str:
        """
        Print self in a reproducible way.

        >>> DisjointSet({1: 2, 2: 2})
        DisjointSet({1: 2, 2: 2})
        """
        sets = {key: val for key, val in self}
        return f"{self.__class__.__name__}({sets})"

    @override
    def __str__(self) -> str:
        return "{classname}({values})".format(
            classname=self.__class__.__name__,
            values=", ".join(str(dset) for dset in self.itersets()),
        )

    def __iter__(self) -> Iterator[tuple[T, T]]:
        """Iterate over items and their canonical elements."""
        try:
            for key in self._data:
                yield key, self.find(key)
        except RuntimeError as e:
            raise InvalidInitialMappingError() from e

    def itersets(
        self, with_canonical_elements: bool = False
    ) -> Iterator[set[T] | tuple[T, set[T]]]:
        """
        Yield sets of connected components.

        If with_canonical_elements is set to True, method will yield tuples of (<canonical_element>, <set of elements>)
        >>> ds = DisjointSet()
        >>> ds.union(1,2)
        >>> list(ds.itersets())
        [{1, 2}]
        >>> list(ds.itersets(with_canonical_elements=True))
        [(2, {1, 2})]
        """
        element_classes: defaultdict[T, set[T]] = defaultdict(set)
        for element in self._data:
            element_classes[self.find(element)].add(element)

        if with_canonical_elements:
            yield from element_classes.items()
        else:
            yield from element_classes.values()

    def find(self, x: T) -> T:
        """
        Return the canonical element of a given item.

        In case the element was not present in the data structure, the canonical element is the item itself.
        >>> ds = DisjointSet()
        >>> ds.find(1)
        1
        >>> ds.union(1, 2)
        >>> ds.find(1)
        2
        """
        while x != self._data[x]:
            self._data[x] = self._data[self._data[x]]
            x = self._data[x]
        return x

    def merge(self, x: T, y: T) -> None:
        """
        Attach the roots of x and y trees together if they are not the same already.

        :param x: first element
        :param y: second element
        """
        parent_x, parent_y = self.find(x), self.find(y)
        if parent_x != parent_y:
            self._data[parent_x] = parent_y
            old = self._rev_data.pop(parent_x)
            self._rev_data[parent_y].update(old)

    def connected(self, x: T, y: T) -> bool:
        """
        Return True if x and y belong to the same set (i.e. they have the canonical element).

        >>> ds = DisjointSet()
        >>> ds.connected(1, 2)
        False
        >>> ds.union(1, 2)
        >>> ds.connected(1, 2)
        True
        """
        return self.find(x) == self.find(y)

    # My Extension

    def add(self, item: T, target: T | None = None) -> None:
        """Add an item, optionally to an existing subset (default creates a new subset)."""
        if item in self._data:
            return
        subset = item
        if target is not None:
            subset = self.find(target)
        self._data[item] = subset
        if subset in self._rev_data:
            self._rev_data[subset].add(item)
        else:
            self._rev_data[subset] = {item}

    def remove_subset(self, item: T) -> None:
        """Remove the subset containing the given item. Does nothing if the item does not exist."""
        if item not in self._data:
            return
        subset = self.find(item)
        for v in self._rev_data[subset]:
            self._data.pop(v)
        self._rev_data.pop(subset)

    def subset_size(self, item: T) -> int:
        """Return the size of the subset containing the item."""
        root = self.find(item)
        return len(self._rev_data[root])

    def subset_count(self) -> int:
        return len(self._rev_data)

    def get_subset(self, item: T) -> set[T]:
        """Return the subset containing the item."""
        root = self.find(item)
        return copy.copy(self._rev_data[root])

    def get_subsets(self) -> list[set[T]]:
        sets = []
        for s in self._rev_data.values():
            sets.append(copy.copy(s))
        return sets


def _test_disjoint_extension() -> None:
    ds = DisjointSet({1: 2, 2: 2, 3: 3, 4: 3, 5: 5})
    print(list(ds.itersets()))
    print(ds._data)
    print(ds._rev_data)
    print()

    ds.merge(1, 3)
    print(ds._data)
    print(ds._rev_data)
    print()

    ds.add(6)
    print(ds._data)
    print(ds._rev_data)
    print()

    ds.add(7, 4)
    print(ds._data)
    print(ds._rev_data)
    print(ds.subset_size(4))
    print(ds.get_subset(7))
    print()

    ds.remove_subset(4)
    print(ds._data)
    print(ds._rev_data)
    print()
