import json
from collections import namedtuple
from dataclasses import dataclass
from typing import Dict, Optional

import requests

ParsedContext = namedtuple(
    "ParsedContext",
    ["method", "url", "data", "headers", "cookies", "verify", "auth", "proxy"],
)


@dataclass
class HTTPMessage:
    """A class to pretty print HTTP requests and responses."""

    method: Optional[str]
    url: Optional[str]
    headers: Dict[str, str]
    body: Optional[str]
    status_code: Optional[int] = None
    reason: Optional[str] = None

    @classmethod
    def from_request(cls, req: requests.Request) -> "HTTPMessage":
        """Create an HTTPMessage from a requests.Request object."""
        prepared = req if isinstance(req, requests.PreparedRequest) else req.prepare()

        body = None
        if prepared.body:
            if isinstance(prepared.body, bytes):
                try:
                    body = prepared.body.decode("utf-8")
                except UnicodeDecodeError:
                    body = f"<binary data, {len(prepared.body)} bytes>"
            else:
                body = str(prepared.body)

        return cls(
            method=prepared.method,
            url=prepared.url,
            headers=dict(prepared.headers),
            body=body,
        )

    @classmethod
    def from_response(cls, resp: requests.Response) -> "HTTPMessage":
        """Create an HTTPMessage from a requests.Response object."""
        return cls(
            method=resp.request.method,
            url=resp.url,
            headers=dict(resp.headers),
            body=resp.text,
            status_code=resp.status_code,
            reason=resp.reason,
        )

    def display(self, max_body_length: int = 2000) -> None:
        """Pretty print the HTTP message."""
        print("=" * 80)

        # Print status line (response) or method line (request)
        if self.status_code is not None:
            print(f"Status: {self.status_code} {self.reason}")
        else:
            print(f"Method: {self.method}")

        print(f"URL:    {self.url}")
        print("-" * 80)

        # Print headers
        print("Headers:")
        for k, v in self.headers.items():
            print(f"  {k}: {v}")
        print("-" * 80)

        # Print body
        print("Body:")
        if not self.body:
            print("  <empty>")
        else:
            content_type = self.headers.get("Content-Type", "")

            # Try to pretty print JSON
            if "application/json" in content_type:
                try:
                    parsed = json.loads(self.body)
                    print(json.dumps(parsed, indent=2, ensure_ascii=False))
                except Exception:
                    self._print_body_with_truncation(
                        body=self.body, max_len=max_body_length
                    )
            else:
                self._print_body_with_truncation(
                    body=self.body, max_len=max_body_length
                )

        print("=" * 80)

    def _print_body_with_truncation(self, body: str, max_len: int) -> None:
        """Print body with truncation if it exceeds max_len."""
        if len(body) > max_len:
            print(body[:max_len] + "\n... [truncated]")
        else:
            print(body)
