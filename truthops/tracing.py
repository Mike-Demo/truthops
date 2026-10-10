"""neatlogs instrumentation with graceful degradation.

If the neatlogs SDK is importable AND NEATLOGS_API_KEY is set, every agent
step is traced as a span. Otherwise tracing degrades to a no-op and the run
continues — a log line records that traces are disabled. Nothing here crashes
when the key is absent.
"""

import os

_enabled = False
_nl = None

try:
    import neatlogs as _nl  # noqa: F401  (imported for feature detection)
    if os.environ.get("NEATLOGS_API_KEY"):
        _enabled = True
    else:
        _nl = None
except Exception:
    _nl = None
    _enabled = False


def is_enabled():
    return _enabled


def init(workflow_name="truthops"):
    """Initialize neatlogs once. Returns True if tracing is live."""
    global _nl, _enabled
    if _nl is None:
        try:
            import neatlogs as _nl
        except Exception:
            print("[tracing] neatlogs SDK not installed — traces disabled (graceful degradation)")
            return False
    if not os.environ.get("NEATLOGS_API_KEY"):
        print("[tracing] NEATLOGS_API_KEY not set — traces disabled (graceful degradation)")
        _enabled = False
        return False
    try:
        _nl.init(api_key=os.environ["NEATLOGS_API_KEY"], workflow_name=workflow_name)
        _enabled = True
        print("[tracing] neatlogs tracing ENABLED")
        return True
    except Exception as e:
        print(f"[tracing] neatlogs init failed ({e}) — traces disabled (graceful degradation)")
        _enabled = False
        return False


class span:
    """Context manager for one agent step. No-op when tracing is disabled."""

    def __init__(self, name, **attrs):
        self.name = name
        self.attrs = attrs
        self._cm = None

    def __enter__(self):
        if _enabled and _nl is not None and hasattr(_nl, "trace"):
            try:
                # neatlogs.trace(name, **attrs) is a context manager; span() is a decorator.
                self._cm = _nl.trace(self.name, **self.attrs)
                return self._cm.__enter__()
            except Exception:
                self._cm = None
        return self

    def __exit__(self, *exc):
        if self._cm is not None:
            try:
                return self._cm.__exit__(*exc)
            except Exception:
                return False
        return False


def flush():
    if _enabled and _nl is not None:
        try:
            if hasattr(_nl, "flush"):
                _nl.flush()
        except Exception:
            pass


def shutdown():
    if _enabled and _nl is not None:
        try:
            if hasattr(_nl, "shutdown"):
                _nl.shutdown()
        except Exception:
            pass
