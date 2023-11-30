# pylint: disable=invalid-name

import itertools
import sys
from typing import Iterable, Iterator, Tuple, TypeVar

T = TypeVar("T")

if sys.version_info < (3, 12):

    def batched(iterable: Iterable[T], n: int) -> Iterator[Tuple[T, ...]]:
        "Batch data into tuples of length n. The last batch may be shorter."
        # batched('ABCDEFG', 3) --> ABC DEF G
        if n < 1:
            raise ValueError("n must be at least one")
        it = iter(iterable)
        while batch := tuple(itertools.islice(it, n)):
            yield batch

else:
    batched = itertools.batched
