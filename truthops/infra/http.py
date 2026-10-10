"""HTTP client with a DETERMINISTIC failure injection.

The first attempt to fetch the primary filing endpoint returns HTTP 503
(simulated). The attempt counter lives in the run state store, so state
survives the failure and the retry succeeds. The retry is visible in output.
"""


class HttpError(Exception):
    def __init__(self, status, url, message):
        super().__init__(f"HTTP {status} for {url}: {message}")
        self.status = status
        self.url = url


# Endpoints that fail once, deterministically, then recover.
FAIL_ONCE_URLS = {"fixture://northstar/filing-q3-2026"}


class HttpClient:
    def __init__(self, state, fixture_adapter):
        self.state = state
        self.fixture_adapter = fixture_adapter

    def get(self, url):
        attempts = self.state.data["http_attempts"].get(url, 0) + 1
        self.state.data["http_attempts"][url] = attempts
        self.state.log_event(
            "http_attempt",
            f"GET {url} (attempt {attempts})",
            url=url, attempt=attempts,
        )
        if url in FAIL_ONCE_URLS and attempts == 1:
            # Deterministic first-attempt failure. State (attempt counter,
            # gathered evidence so far) is already flushed to disk.
            self.state.log_event(
                "http_failure",
                f"GET {url} -> 503 Service Unavailable (SIMULATED). State preserved; will retry.",
                url=url, attempt=attempts, status=503,
            )
            raise HttpError(503, url, "Service Unavailable (SIMULATED deterministic failure)")
        body = self.fixture_adapter.fetch(url)
        self.state.log_event(
            "http_success",
            f"GET {url} -> 200 OK (attempt {attempts})",
            url=url, attempt=attempts, status=200,
        )
        return body
