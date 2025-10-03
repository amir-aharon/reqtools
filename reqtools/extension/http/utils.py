import requests

from reqtools.extension.http.display import ParsedContext


def run_parsed_context(ctx: ParsedContext) -> requests.Response:
    """Run an HTTP request from a ParsedContext."""
    # Convert to dict and drop None values
    kwargs = {k: v for k, v in ctx._asdict().items() if v is not None}

    # Extract method and url (required)
    method = kwargs.pop("method", "GET")
    url = kwargs.pop("url")

    return requests.request(method=method, url=url, **kwargs)
