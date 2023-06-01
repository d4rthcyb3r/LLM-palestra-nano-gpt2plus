import inspect
from collections.abc import Callable
from numbers import Number
from typing import List, Optional


def grab_arguments(func: Callable, kwargs: dict, ignore_kwargs: Optional[List[str]] = None) -> dict:
    """Return dictionary only with arguments that the func expects.

    Parameters
    ----------
    func : Callable
        function that expects some arguments;
        this helper function will grab only args that are expected
    kwargs : dict
        dictionary with keyword arguments
    ignore_kwargs : Optional[List[str]], optional
        kwargs to ignore, by default None

    Returns
    -------
    dict
        kwargs that are expected by the provided function
    """
    ignore_kwargs = set(["self"] + (ignore_kwargs or []))
    expected_args = {kwarg for kwarg in inspect.signature(func).parameters if kwarg not in ignore_kwargs}

    return {k: v for k, v in kwargs.items() if k in expected_args}


class ArgumentSaverMixin:
    def save_arguments(self, ignore: Optional[List[str]] = None) -> None:
        """Save all provided arguments into __dict__ by setattr.

        Parameters
        ----------
        ignore : Optional[List[str]], optional
            list of arguments to ignore, by default None
        """
        ignore = set(["self"] + (ignore or []))
        # get local variables of the frame that called current one
        local_vars = inspect.currentframe().f_back.f_locals
        for arg_name, arg_value in local_vars.items():
            if arg_name not in ignore and not arg_name.startswith("_"):
                setattr(self, arg_name, arg_value)


class RangeChecker:
    def __init__(self, start: Number, end: Number, inclusive_start: bool = True, inclusive_end: bool = True) -> None:
        """Create custom range class, initially created for argparser.

        This class allows to specify to have range with inclusive or exclusive start and end.
        In contrast built-in range function doesn't allow it: always start inclusive and end exclusive.

        Parameters
        ----------
        start : Number
            start of the range
        end : Number
            end of the range
        inclusive_start : bool, optional
            should the start of the range be included in comparison, by default True
        inclusive_end : bool, optional
            should the end of the range be included in comparison, by default True
        """
        self.start = start
        self.end = end
        self.inclusive_start = inclusive_start
        self.inclusive_end = inclusive_end

    def __eq__(self, other: Number) -> bool:
        if self.inclusive_start and self.inclusive_end:
            return self.start <= other <= self.end
        if self.inclusive_start:
            return self.start <= other < self.end
        if self.inclusive_end:
            return self.start < other <= self.end
        return self.start < other < self.end

    def __contains__(self, item: Number) -> bool:
        return self.__eq__(item)

    def __iter__(self) -> "RangeChecker":
        yield self

    def __str__(self) -> str:
        if self.inclusive_start and self.inclusive_end:
            return f"[{self.start},{self.end}]"
        if self.inclusive_start:
            return f"[{self.start},{self.end})"
        if self.inclusive_end:
            return f"({self.start},{self.end}]"
        return f"({self.start},{self.end})"
