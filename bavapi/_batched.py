"""Backport of `itertools.batched` class from Python 3.12 for older versions of Python"""

# pylint: disable=invalid-name, too-few-public-methods

import itertools
import sys
from typing import Generic, Iterable, Iterator, Tuple, TypeVar

T = TypeVar("T")

if sys.version_info < (3, 12):

    class batched(Generic[T]):
        # Docstring from `itertools.batched`
        """Batch data into tuples of length n. The last batch may be shorter than n.

        Loops over the input iterable and accumulates data into tuples up to size n.
        The input is consumed lazily, just enough to fill a batch.
        The result is yielded as soon as a batch is full or when the input iterable is exhausted.

        >>> for batch in batched('ABCDEFG', 3):
        ...     print(batch)
        ...
        ('A', 'B', 'C')
        ('D', 'E', 'F')
        ('G',)

        Parameters
        ----------
        iterable : Iterable[T]
            Iterable to yield in batches
        n : int
            Number of items in each batch. Must be greater than zero

        Yields
        ------
        batch : tuple[T, ...]
            Batch of items of length n. The last batch may be shorter than n.
        """

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
