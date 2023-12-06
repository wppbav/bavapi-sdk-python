# pylint: disable=missing-function-docstring, missing-module-docstring

import pytest

from bavapi._batched import batched


def test_batched():
    it = list(range(20))
    res = []
    for batch in batched(it, 3):
        assert len(batch) <= 3
        for i in batch:
            res.append(i)

    assert res == it


def test_batch_invalid_batch_size():
    with pytest.raises(ValueError) as exc_info:
        batched(range(20), 0)

    assert exc_info.value.args == ("n must be at least one",)
