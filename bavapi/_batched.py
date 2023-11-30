# pylint: disable=invalid-name

import itertools
import sys
from typing import Generic, Iterable, Iterator, Tuple, TypeVar

T = TypeVar("T")

if sys.version_info < (3, 12):

    class batched(Generic[T]):
        def __init__(self, iterable: Iterable[T], n: int) -> None:
            if n < 1:
                raise ValueError("n must be at least one")
            self.iterable = iterable
            self.n = n

        def __iter__(self) -> Iterator[Tuple[T, ...]]:
            it = iter(self.iterable)
            while batch := tuple(itertools.islice(it, self.n)):
                yield batch

else:
    batched = itertools.batched
