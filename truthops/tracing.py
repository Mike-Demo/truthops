"""Neatlogs tracing shim — proper OTel spans via Neatlogs' internal tracer.

v2 (2026-10-10): The v1 shim misused neatlogs.trace() — an API designed for
prompt-template tracking and session management — for generic pipeline spans.
This version creates standard OpenTelemetry spans directly through Neatlogs'
own tracer provider, bypassing the trace() prompt machinery entirely.

v2.1: Added explicit flush()/shutdown() using get_neatlogs_provider() (which
resolves the active client provider, not just the module-level fallback).
The OTel BatchSpanProcessor buffers spans and exports on a timer; without a
flush before exit, short-lived scripts terminate with zero spans transmitted
— the trace ID registers but no span data arrives, producing Neatlogs'
"couldn't finish preparing this trace" backend error.
"""

def _get_tracer():
    """Resolve Neatlogs' internal tracer lazily (after init() has run)."""
    try:
        from neatlogs._wrap_utils import get_internal_tracer
        t = get_internal_tracer(__name__)
        return t
    except Exception:
        return None


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
        neatlogs.init(api_key=api_key)
        ok = _get_tracer() is not None
        print(f"  [tracing] neatlogs live (workflow={workflow_name})" if ok
              else "  [tracing] neatlogs init ok but no tracer")
        return ok
    except Exception as e:
        print(f"  [tracing] neatlogs init failed: {e}")
        return False


_last_trace_id = None


def get_trace_id():
    return _last_trace_id or "unavailable"


class span:
    """Context manager yielding a proper OTel span via Neatlogs' provider."""

    def __init__(self, name, **attrs):
        self.name = name
        # OTel attributes must be primitives; coerce defensively.
        self.attrs = {k: v for k, v in attrs.items()
                      if isinstance(v, (str, int, float, bool))}
        self._cm = None

    def __enter__(self):
        global _last_trace_id
        tracer = _get_tracer()
        if tracer is not None:
            try:
                self._cm = tracer.start_as_current_span(
                    self.name, attributes=self.attrs)
                otel_span = self._cm.__enter__()
                try:
                    ctx = otel_span.get_span_context()
                    if ctx and ctx.trace_id:
                        _last_trace_id = format(ctx.trace_id, "032x")
                except Exception:
                    pass
            except Exception as e:
                print(f"  [tracing] span start failed: {e}")
                self._cm = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._cm is not None:
            try:
                self._cm.__exit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass
            self._cm = None
        return False

    def set(self, key, value):
        return self


def flush(timeout_ms=15000):
    """Force-flush all pending spans to Neatlogs before exit."""
    provider = _get_provider()
    if provider is not None and hasattr(provider, "force_flush"):
        try:
            ok = provider.force_flush(timeout_millis=timeout_ms)
            print(f"  [tracing] spans flushed (ok={ok})")
            return bool(ok)
        except Exception as e:
            print(f"  [tracing] flush failed: {e}")
    else:
        print("  [tracing] flush: no provider available")
    return False


def shutdown():
    """Flush remaining spans and shut down the tracer provider."""
    flush()
    provider = _get_provider()
    if provider is not None and hasattr(provider, "shutdown"):
        try:
            provider.shutdown()
            print("  [tracing] provider shut down")
        except Exception as e:
            print(f"  [tracing] shutdown failed: {e}")
