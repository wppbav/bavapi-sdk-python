# pylint: disable=missing-module-docstring, missing-function-docstring

from typing import Callable, Optional, Type, TypeVar, Union

T = TypeVar("T")
ASGIApp = Callable[..., "ASGIApp"]


def wraps(
    return_value: Optional[T] = None,
    *,
    raises: Optional[Union[Type[Exception], Exception]] = None,
) -> Callable[..., Optional[T]]:
    def _wraps(*_, **__):
        if raises is not None:
            raise raises
        return return_value

    return _wraps


def mock_app(*args, **kwargs) -> ASGIApp:
    return mock_app(*args, **kwargs)  # pragma: no cover
