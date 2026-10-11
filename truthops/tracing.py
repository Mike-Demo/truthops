"""Neatlogs tracing shim.

v3 (2026-10-10): Combines what worked from v1 and v2.
- Span creation via neatlogs.trace() (v1): properly marked as Neatlogs-
  originated, so the _ForeignParentGuardTracer nests children correctly.
  (v2's raw OTel spans were treated as foreign — each span became its
  own root trace, producing scattered 0-span traces.)
- Flush via get_neatlogs_provider().force_flush() (v2): the v1 flush was
  a silent no-op (checked hasattr(_nl, "flush") which doesn't exist).
- try/finally in __main__.py guarantees shutdown() even on crash.
- workflow_name passed through to neatlogs.init().
"""

def _get_provider():
    """Resolve the active Neatlogs tracer provider (client-aware)."""
    try:
        from neatlogs._wrap_utils import get_neatlogs_provider
        return get_neatlogs_provider()
    except Exception:
        return None


def init(workflow_name="truthops"):
    """Initialize Neatlogs. API key comes from NEATLOGS_API_KEY env var.
    Returns True if tracing is live."""
    import os
    api_key = os.environ.get("NEATLOGS_API_KEY", "")
    if not api_key:
        print("  [tracing] NEATLOGS_API_KEY not set — traces disabled")
        return False
    try:
        import neatlogs
        neatlogs.init(api_key=api_key, workflow_name=workflow_name)
        print(f"  [tracing] neatlogs live (workflow={workflow_name})")
        return True
    except Exception as e:
        print(f"  [tracing] neatlogs init failed: {e}")
        return False


_last_trace_id = None


def get_trace_id():
    return _last_trace_id or "unavailable"


class span:
    """Context manager for one pipeline step.

    Uses neatlogs.trace() (not raw OTel) so spans are properly marked as
    Neatlogs-originated and nest correctly under the active trace.
    """

    def __init__(self, name, **attrs):
        self.name = name
        self.attrs = attrs
        self._cm = None

    def __enter__(self):
        global _last_trace_id
        try:
            import neatlogs
            # neatlogs.trace() is a context manager; enter it here so the
            # OTel context propagates to nested spans.
            self._cm = neatlogs.trace(self.name, **self.attrs)
            entered = self._cm.__enter__()
            # Capture trace ID from the entered span.
            if _last_trace_id is None and entered is not None:
                try:
                    ctx = entered.get_span_context()
                    tid = ctx.trace_id if ctx is not None else None
                except Exception:
                    tid = getattr(entered, "trace_id", None)
                if tid:
                    _last_trace_id = format(tid, "032x") if isinstance(tid, int) else str(tid)
            return entered if entered is not None else self
        except Exception as e:
            print(f"  [tracing] span start failed: {e}")
            self._cm = None
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._cm is not None:
            try:
                return self._cm.__exit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass
            self._cm = None
        return False

    def set(self, key, value):
        return self


def flush(timeout_ms=15000):
    """Flush via the SDK-level flush (handles neatlogs.trace() buffering)
    and the OTel provider flush (belt and suspenders)."""
    ok = False
    try:
        import neatlogs
        if hasattr(neatlogs, "flush"):
            ok = bool(neatlogs.flush(timeout_millis=timeout_ms))
            print(f"  [tracing] neatlogs SDK flushed (ok={ok})")
    except Exception as e:
        print(f"  [tracing] SDK flush failed: {e}")
    provider = _get_provider()
    if provider is not None and hasattr(provider, "force_flush"):
        try:
            pok = bool(provider.force_flush(timeout_millis=timeout_ms))
            print(f"  [tracing] provider flushed (ok={pok})")
            ok = ok or pok
        except Exception as e:
            print(f"  [tracing] provider flush failed: {e}")
    return ok


def shutdown():
    """Flush remaining spans and shut down the SDK + tracer provider."""
    flush()
    try:
        import neatlogs
        if hasattr(neatlogs, "shutdown"):
            neatlogs.shutdown()
            print("  [tracing] neatlogs SDK shut down")
    except Exception as e:
        print(f"  [tracing] SDK shutdown failed: {e}")
    provider = _get_provider()
    if provider is not None and hasattr(provider, "shutdown"):
        try:
            provider.shutdown()
            print("  [tracing] provider shut down")
        except Exception as e:
            print(f"  [tracing] provider shutdown failed: {e}")
