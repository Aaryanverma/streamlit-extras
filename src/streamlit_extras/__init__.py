import inspect
from importlib import import_module
from typing import Any, Callable, Optional, TypeVar, Union, overload

from streamlit.runtime.metrics_util import gather_metrics as _gather_metrics

F = TypeVar("F", bound=Callable[..., Any])

# Typing overloads here are actually required so that you can correctly (= with correct typing) use the decorator in different ways:
#   1) as a decorator without parameters @extra
#   2) as a decorator with parameters (@extra(foo="bar") but this also refers to empty parameters @extra()
#   3) as a function: extra(my_function)


@overload
def extra(
    func: F,
) -> F:
    ...


@overload
def extra(
    func: None = None,
) -> Callable[[F], F]:
    ...


def extra(
    func: Optional[F] = None,
) -> Union[Callable[[F], F], F]:

    if func:

        filename = inspect.stack()[1].filename
        submodule = filename.split("/")[-2]
        extra_name = "streamlit_extras." + submodule
        module = import_module(extra_name)

        if hasattr(module, "__funcs__"):
            module.__funcs__ += [func]  # type: ignore
        else:
            module.__funcs__ = [func]  # type: ignore

        try:
            profiling_name = f"{module}.{func.__name__}"
            return _gather_metrics(name=profiling_name, func=func)
        except ImportError:
            return func

    def wrapper(f: F) -> F:
        return f

    return wrapper
