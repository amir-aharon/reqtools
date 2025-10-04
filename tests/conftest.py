import pytest
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from requests import PreparedRequest, Request, Response

from reqtools.http.display import HTTPMessage
from reqtools.magics import ReqToolsMagics


# HTTP Display Fixtures
@pytest.fixture
def mock_response():
    """Create a mock Response object."""
    resp = Response()
    resp.status_code = 200
    resp.reason = "OK"
    resp._content = b'{"message": "Hello World", "status": "success"}'
    resp.headers["Content-Type"] = "application/json"
    resp.url = "https://api.example.com/test"

    # Mock request
    req = PreparedRequest()
    req.method = "GET"
    req.url = "https://api.example.com/test"
    req.headers = {"User-Agent": "TestClient/1.0"}
    resp.request = req

    return resp


@pytest.fixture
def mock_request():
    """Create a mock Request object."""
    return Request(
        method="POST",
        url="https://api.example.com/users",
        headers={"Content-Type": "application/json", "X-API-Key": "secret123"},
        json={"name": "Alice", "email": "alice@example.com"},
    )


@pytest.fixture
def json_message():
    """Create a message with JSON content."""
    return HTTPMessage(
        method="GET",
        url="https://api.example.com/users",
        headers={"Content-Type": "application/json", "X-Request-ID": "123"},
        body='{"users": [{"name": "Alice"}, {"name": "Bob"}]}',
        status_code=200,
        reason="OK",
    )


@pytest.fixture
def text_message():
    """Create a message with text content."""
    return HTTPMessage(
        method="GET",
        url="https://example.com/page",
        headers={"Content-Type": "text/html"},
        body="<html><body>Hello World</body></html>",
        status_code=200,
        reason="OK",
    )


@pytest.fixture
def request_message():
    """Create a message for a request (no status)."""
    return HTTPMessage(
        method="POST",
        url="https://api.example.com/create",
        headers={"Content-Type": "application/json"},
        body='{"data": "value"}',
    )


# Magic Fixtures
@pytest.fixture
def magic():
    """Create a ReqToolsMagics instance."""
    return ReqToolsMagics(shell=None)


@pytest.fixture
def mock_response_for_magics():
    """Create a mock Response object for magic tests."""
    resp = Response()
    resp.status_code = 200
    resp.reason = "OK"
    resp._content = b'{"result": "success"}'
    resp.headers["Content-Type"] = "application/json"
    resp.url = "https://api.example.com/test"

    req = PreparedRequest()
    req.method = "GET"
    req.url = "https://api.example.com/test"
    resp.request = req

    return resp


# IPython Integration Fixtures
@pytest.fixture(scope="function")
def ipython_shell():
    """Provide a fresh IPython shell for each test."""
    # Create a new IPython instance
    ip = TerminalInteractiveShell.instance()
    yield ip
    # Cleanup
    TerminalInteractiveShell.clear_instance()
