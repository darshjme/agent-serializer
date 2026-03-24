"""@serialized decorator for automatic ser/de of function args and return values."""

from __future__ import annotations

import functools
import inspect
from typing import Any, Callable

from .serializer import Serializer


def serialized(serializer: Serializer) -> Callable:
    """Decorator that serializes return values and deserializes dict arguments.

    Usage::

        s = Serializer()

        @serialized(s)
        def process(data: dict) -> dict:
            ...

    - Incoming ``dict`` arguments are passed through :meth:`Serializer.loads`
      after being re-encoded to JSON so type tokens are decoded.
    - The return value is passed through :meth:`Serializer.dumps` then
      :meth:`Serializer.loads`, ensuring consistent round-trip types.
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Deserialize dict arguments that look like serialized payloads
            new_args = []
            for arg in args:
                if isinstance(arg, dict):
                    try:
                        # Re-serialize to JSON and decode so type hooks apply
                        new_args.append(serializer.loads(serializer.dumps(arg)))
                    except Exception:
                        new_args.append(arg)
                else:
                    new_args.append(arg)

            new_kwargs = {}
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    try:
                        new_kwargs[k] = serializer.loads(serializer.dumps(v))
                    except Exception:
                        new_kwargs[k] = v
                else:
                    new_kwargs[k] = v

            result = fn(*new_args, **new_kwargs)

            # Serialize return value (round-trip for type consistency)
            if result is not None:
                try:
                    return serializer.loads(serializer.dumps(result))
                except Exception:
                    return result
            return result

        return wrapper

    return decorator
