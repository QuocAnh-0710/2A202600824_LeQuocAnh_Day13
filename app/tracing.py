from __future__ import annotations

import os
from typing import Any


try:
    from langfuse import observe, get_client as _get_client

    class _LangfuseContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            _get_client().update_current_trace(**kwargs)

        def update_current_observation(self, **kwargs: Any) -> None:
            _get_client().update_current_span(**kwargs)

        def update_current_generation(self, **kwargs: Any) -> None:
            _get_client().update_current_generation(**kwargs)

    langfuse_context = _LangfuseContext()

    def get_langfuse_client():
        return _get_client()

except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

        def update_current_generation(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()

    class _DummyClient:
        def flush(self) -> None:
            return None

    def get_langfuse_client():
        return _DummyClient()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
