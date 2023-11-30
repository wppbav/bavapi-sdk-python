import itertools
from typing import Iterable, Iterator, Tuple, TypeVar

T = TypeVar("T")


def batched(iterable: Iterable[T], n: int) -> Iterator[Tuple[T, ...]]:
    "Batch data into tuples of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch
