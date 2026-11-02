"""Client for the Plagiarism Checker Plus public API. Standard library only."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

DEFAULT_BASE_URL = "https://app.plagiarismcheckerplus.com/api/public/v1"
VERSION = "1.0.0"

# (method, url, headers, body) -> (status, headers, body)
Transport = Callable[[str, str, Mapping[str, str], Optional[bytes]], Tuple[int, Mapping[str, str], bytes]]


class ErrorCodes:
    PLAN_REQUIRED = "plan_required"
    TEXT_TOO_SHORT = "text_too_short"
    DOC_TOO_LONG = "doc_too_long"
    INSUFFICIENT_WORDS = "insufficient_words"


class PlagiarismCheckerPlusError(Exception):
    """A non-2xx response. `code` is the API's error code, such as plan_required."""

    def __init__(
        self,
        message: str,
        status: int = 0,
        code: Optional[str] = None,
        retry_after: Optional[float] = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.retry_after = retry_after
        self.body = body


class ScanTimeoutError(Exception):
    def __init__(self, scan_id: str, timeout: float) -> None:
        super().__init__(f"Scan {scan_id} did not finish within {timeout} seconds")
        self.scan_id = scan_id


def parse_retry_after(value: Optional[str]) -> Optional[float]:
    """Seconds from a Retry-After header (delta-seconds or HTTP date), or None."""
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, when.timestamp() - time.time())


def _urllib_transport(timeout: float) -> Transport:
    def send(method: str, url: str, headers: Mapping[str, str], body: Optional[bytes]):
        request = urllib.request.Request(url, data=body, headers=dict(headers), method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status, dict(response.headers.items()), response.read()
        except urllib.error.HTTPError as error:
            return error.code, dict(error.headers.items()), error.read()

    return send


class PlagiarismCheckerPlus:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        transport: Optional[Transport] = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._transport = transport or _urllib_transport(timeout)

    def _request(
        self,
        method: str,
        path: str,
        query: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = self.base_url + path
        params = {k: v for k, v in (query or {}).items() if v is not None}
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": f"plagiarism-checker-plus-python/{VERSION}",
        }
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")
        status, response_headers, raw = self._transport(method, url, headers, data)
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else None
        except ValueError:
            payload = None
        if not 200 <= status < 300:
            error = payload.get("error") if isinstance(payload, dict) else None
            error = error if isinstance(error, dict) else {}
            retry = next((v for k, v in response_headers.items() if k.lower() == "retry-after"), None)
            raise PlagiarismCheckerPlusError(
                error.get("message") or f"HTTP {status}",
                status=status,
                code=error.get("code"),
                retry_after=parse_retry_after(retry),
                body=payload,
            )
        return payload

    def create_scan(self, text: str, tools: Sequence[str], name: Optional[str] = None) -> Dict[str, Any]:
        """Submit text. tools: any of "plagiarism" and "ai_detect"."""
        body: Dict[str, Any] = {"text": text, "tools": list(tools)}
        if name is not None:
            body["name"] = name
        return self._request("POST", "/scans", body=body)

    def get_scan(self, scan_id: str, include_text: bool = False) -> Dict[str, Any]:
        """Read a scan and its results."""
        query = {"include_text": "true"} if include_text else None
        return self._request("GET", "/scans/" + urllib.parse.quote(scan_id, safe=""), query=query)

    def list_scans(self, page: Optional[int] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """List scans, newest first."""
        return self._request("GET", "/scans", query={"page": page, "limit": limit})

    def get_account(self) -> Dict[str, Any]:
        """Plan and remaining words."""
        return self._request("GET", "/account")

    def wait_for_scan(
        self,
        scan_id: str,
        timeout: float = 300.0,
        interval: float = 2.0,
        max_interval: float = 10.0,
        include_text: bool = False,
        sleep: Callable[[float], None] = time.sleep,
    ) -> Dict[str, Any]:
        """Poll until the scan is completed or failed, honouring Retry-After on 429."""
        deadline = time.monotonic() + timeout
        delay = interval
        while True:
            wait = delay
            try:
                scan = self.get_scan(scan_id, include_text=include_text)
                if scan.get("status") in ("completed", "failed"):
                    return scan
                delay = min(delay * 1.5, max_interval)
            except PlagiarismCheckerPlusError as error:
                if error.status != 429:
                    raise
                wait = error.retry_after if error.retry_after is not None else delay
            if time.monotonic() + wait > deadline:
                raise ScanTimeoutError(scan_id, timeout)
            sleep(wait)


__all__: List[str] = [
    "DEFAULT_BASE_URL",
    "ErrorCodes",
    "PlagiarismCheckerPlus",
    "PlagiarismCheckerPlusError",
    "ScanTimeoutError",
    "parse_retry_after",
]
