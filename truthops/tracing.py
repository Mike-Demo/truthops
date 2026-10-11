"""Neatlogs tracing shim.

v4 (2026-10-10): Use the SDK's internal neatlogs_span() context manager —
the same primitive the @span decorator uses. This is the isolation-safe
replacement for tracer.start_as_current_span: it creates properly-marked
Neatlogs spans that nest correctly via _ForeignParentGuardTracer, without
the prompt/session machinery of neatlogs.trace() (which is not designed
for basic span creation and was silently dropping spans).

History:
- v1: neatlogs.trace() + manual __enter__ — nested OK in the morning,
  but flush() was a silent no-op (hasattr check for nonexistent method).
- v2: raw OTel spans via get_internal_tracer — flush worked, but spans
  were treated as foreign; each became its own root trace (0-span scatter).
- v3: back to neatlogs.trace() — single trace again, but trace() buffers
  on its own thread; spans never completed/transmitted.
- v4: neatlogs_span() — proper spans, proper nesting, flushable.
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

    Uses the SDK-internal neatlogs_span() — the same primitive the @span
    decorator uses — so spans are properly marked, nest correctly, and
    flush through the standard pipeline.
    """

    def __init__(self, name, **attrs):
        self.name = name
        # OTel attributes must be primitives; coerce defensively.
        self.attrs = {k: v for k, v in attrs.items()
                      if isinstance(v, (str, int, float, bool))}
        self._cm = None

    def __enter__(self):
        global _last_trace_id
        try:
            from neatlogs._wrap_utils import neatlogs_span
            # neatlogs_span is a context manager; enter it so the OTel
            # context propagates to nested spans.
            self._cm = neatlogs_span(__name__, self.name,
                                     attributes=self.attrs)
            entered = self._cm.__enter__()
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
    """Flush via the SDK-level flush and the OTel provider flush."""
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
