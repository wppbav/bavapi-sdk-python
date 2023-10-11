"""Functions to check whether `bavapi` is being run from a `jupyter` notebook.

These functions enable `bavapi` to be run from a `jupyter` notebook more easily,
avoiding the use of `async with` and `await` statements.
"""

import sys
from typing import TYPE_CHECKING, Optional

import nest_asyncio

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop


def running_in_jupyter() -> bool:
    """
    Determine if running within Jupyter.

    Inspired by <https://github.com/ipython/ipython/issues/11694>

    Returns
    -------
    bool
        True if running in Jupyter, else False.
    """
    in_ipython = False
    in_ipython_kernel = False
    ipython: Optional[object] = None

    # if IPython hasn't been imported, there's nothing to check
    if "IPython" in sys.modules:
        ipython = sys.modules["IPython"].__dict__["get_ipython"]()
        in_ipython = ipython is not None

    if in_ipython:
        in_ipython_kernel = getattr(ipython, "kernel", None) is not None

    return in_ipython_kernel


def patch_loop(loop: "AbstractEventLoop") -> None:
    """Patch asyncio loop with `nest_asyncio`.

    Parameters
    ----------
    loop: asyncio.AbstractEventLoop
        Loop to patch to allow nested loops

    """
    nest_asyncio.apply(loop)
