"""Base HTTP client for REST API tests.

`BaseApiClient` owns everything mechanical about talking HTTP — a pooled
`requests.Session`, connection retries with backoff, a per-call timeout, request
/response logging, and turning every raw response into an `ApiResponse`. Endpoint
clients subclass it and add intent-revealing methods.

The single most important quirk this layer hides: the AutomationExercise API
**always answers with transport status `200 OK`** and serves the *real* status
code inside the JSON body as `responseCode` (with `Content-Type: text/html`, not
`application/json`). Tests therefore assert on `ApiResponse.response_code`, not on
the HTTP status line. `ApiResponse` exposes both so a mistake is impossible to
make silently.
"""
from __future__ import annotations

from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.config import Config
from utils.logger import get_logger

log = get_logger("api")

# A browser-like UA. The target sits behind Cloudflare; a realistic agent keeps
# us off the automated-traffic path the way the UI suite masks its fingerprint.
_DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class ApiResponse:
    """Thin wrapper over `requests.Response` for this API's response shape.

    Prefer `response_code` / `message` / `get()` over poking at the raw body so
    the "code lives in the body" quirk stays in exactly one place.
    """

    def __init__(self, response: requests.Response):
        self.raw = response
        self._body: Optional[dict] = None

    @property
    def http_status(self) -> int:
        """The transport status line. For this API it is almost always 200 —
        assert on `response_code` instead unless you are deliberately checking
        the HTTP layer."""
        return self.raw.status_code

    @property
    def body(self) -> dict:
        """The parsed JSON body. Cached. Raises a clear error if the payload is
        not JSON (e.g. a Cloudflare HTML interstitial), which is far easier to
        debug than a bare `JSONDecodeError` from deep in a test."""
        if self._body is None:
            try:
                self._body = self.raw.json()
            except ValueError as exc:
                snippet = self.raw.text[:300].replace("\n", " ")
                raise AssertionError(
                    f"Expected a JSON body from {self.raw.request.method} "
                    f"{self.raw.url} but could not parse one ({exc}). "
                    f"First 300 chars: {snippet!r}"
                ) from exc
        return self._body

    @property
    def response_code(self) -> int:
        """The API's real status code, read from the JSON body's `responseCode`.
        Falls back to the transport status if the field is ever absent."""
        return int(self.body.get("responseCode", self.http_status))

    @property
    def message(self) -> Optional[str]:
        """The human-readable `message` field, when the endpoint returns one.
        Data endpoints (products/brands/user) return a payload key instead."""
        return self.body.get("message")

    def get(self, key: str, default: Any = None) -> Any:
        """Fetch a payload key from the body, e.g. 'products', 'brands', 'user'."""
        return self.body.get(key, default)

    def __repr__(self) -> str:
        return (
            f"<ApiResponse http={self.http_status} "
            f"responseCode={self.body.get('responseCode')!r} "
            f"message={self.message!r}>"
        )


class BaseApiClient:
    """Owns the HTTP session, retries, timeout and logging for API tests."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        self.base_url = (base_url or Config.API_BASE_URL).rstrip("/")
        self.timeout = timeout if timeout is not None else Config.API_TIMEOUT
        self.session = self._build_session()

    @staticmethod
    def _build_session() -> requests.Session:
        session = requests.Session()
        # Retry transient connection failures and the occasional Cloudflare 5xx
        # with exponential backoff. The API's own error codes (400/404/405) live
        # in the body with a 200 status line, so they are never retried.
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,
            status_forcelist=(429, 502, 503, 504),
            allowed_methods=None,  # retry every method on connection-level errors
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update({"User-Agent": _DEFAULT_USER_AGENT})
        return session

    def request(self, method: str, path: str, **kwargs) -> ApiResponse:
        """Perform a request relative to `base_url` and wrap the result.

        `path` may be a bare endpoint ('productsList') or a leading-slash path;
        either way it is joined onto the configured API base.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)
        log.info("API %s %s%s", method.upper(), url,
                 f" data={kwargs['data']}" if kwargs.get("data") else "")

        response = self.session.request(method, url, **kwargs)
        wrapped = ApiResponse(response)
        # Read the body once here so a non-JSON payload fails loudly at the call
        # site (with method/url context) rather than later inside an assertion.
        log.info("API <- http=%s responseCode=%s message=%s",
                 wrapped.http_status, wrapped.body.get("responseCode"), wrapped.message)
        return wrapped

    # Thin verb helpers — endpoint clients read more clearly with these.
    def get(self, path: str, **kwargs) -> ApiResponse:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> ApiResponse:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> ApiResponse:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> ApiResponse:
        return self.request("DELETE", path, **kwargs)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "BaseApiClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
