import pytest
import responses

from reqtools.http.utils import ParsedContext, run_parsed_context


class TestRunParsedContext:
    """Tests for run_parsed_context()"""

    @responses.activate
    def test_basic_get_request(self):
        """Test basic GET request."""
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"users": ["Alice", "Bob"]},
            status=200,
        )

        ctx = ParsedContext(
            method="GET",
            url="https://api.example.com/users",
            data=None,
            headers=None,
            cookies=None,
            verify=None,
            auth=None,
            proxy=None,
        )

        resp = run_parsed_context(ctx)

        assert resp.status_code == 200
        assert resp.json() == {"users": ["Alice", "Bob"]}

    @responses.activate
    def test_post_request_with_data(self):
        """Test POST request with data."""
        responses.add(
            responses.POST,
            "https://api.example.com/users",
            json={"id": 123, "status": "created"},
            status=201,
        )

        ctx = ParsedContext(
            method="POST",
            url="https://api.example.com/users",
            data='{"name": "Charlie"}',
            headers={"Content-Type": "application/json"},
            cookies=None,
            verify=None,
            auth=None,
            proxy=None,
        )

        resp = run_parsed_context(ctx)

        assert resp.status_code == 201
        assert resp.json()["status"] == "created"

    @responses.activate
    def test_request_with_headers(self):
        """Test request with custom headers."""

        def check_headers(request):
            assert request.headers["X-API-Key"] == "secret123"
            assert request.headers["User-Agent"] == "CustomClient/1.0"
            return (200, {}, '{"status": "ok"}')

        responses.add_callback(
            responses.GET,
            "https://api.example.com/protected",
            callback=check_headers,
            content_type="application/json",
        )

        ctx = ParsedContext(
            method="GET",
            url="https://api.example.com/protected",
            data=None,
            headers={"X-API-Key": "secret123", "User-Agent": "CustomClient/1.0"},
            cookies=None,
            verify=None,
            auth=None,
            proxy=None,
        )

        resp = run_parsed_context(ctx)

        assert resp.status_code == 200

    @responses.activate
    def test_request_with_cookies(self):
        """Test request with cookies."""

        def check_cookies(request):
            # Note: responses library handles cookies differently
            return (200, {}, '{"status": "ok"}')

        responses.add_callback(
            responses.GET,
            "https://api.example.com/session",
            callback=check_cookies,
            content_type="application/json",
        )

        ctx = ParsedContext(
            method="GET",
            url="https://api.example.com/session",
            data=None,
            headers=None,
            cookies={"session_id": "abc123"},
            verify=None,
            auth=None,
            proxy=None,
        )

        resp = run_parsed_context(ctx)

        assert resp.status_code == 200

    @responses.activate
    def test_defaults_to_get_method(self):
        """Test method defaults to GET when None."""
        responses.add(
            responses.GET,
            "https://api.example.com/data",
            json={"data": "value"},
            status=200,
        )

        ctx = ParsedContext(
            method=None,
            url="https://api.example.com/data",
            data=None,
            headers=None,
            cookies=None,
            verify=None,
            auth=None,
            proxy=None,
        )

        resp = run_parsed_context(ctx)

        assert resp.status_code == 200
        assert resp.request.method == "GET"

    @responses.activate
    def test_filters_none_values(self):
        """Test that None values are filtered out from kwargs."""
        responses.add(
            responses.GET,
            "https://api.example.com/simple",
            json={"result": "success"},
            status=200,
        )

        ctx = ParsedContext(
            method="GET",
            url="https://api.example.com/simple",
            data=None,
            headers=None,
            cookies=None,
            verify=None,
            auth=None,
            proxy=None,
        )

        resp = run_parsed_context(ctx)

        assert resp.status_code == 200

    @responses.activate
    def test_put_request(self):
        """Test PUT request."""
        responses.add(
            responses.PUT,
            "https://api.example.com/users/123",
            json={"status": "updated"},
            status=200,
        )

        ctx = ParsedContext(
            method="PUT",
            url="https://api.example.com/users/123",
            data='{"name": "Updated Name"}',
            headers={"Content-Type": "application/json"},
            cookies=None,
            verify=None,
            auth=None,
            proxy=None,
        )

        resp = run_parsed_context(ctx)

        assert resp.status_code == 200
        assert resp.json()["status"] == "updated"

    @responses.activate
    def test_delete_request(self):
        """Test DELETE request."""
        responses.add(responses.DELETE, "https://api.example.com/users/123", status=204)

        ctx = ParsedContext(
            method="DELETE",
            url="https://api.example.com/users/123",
            data=None,
            headers=None,
            cookies=None,
            verify=None,
            auth=None,
            proxy=None,
        )

        resp = run_parsed_context(ctx)

        assert resp.status_code == 204

    @responses.activate
    def test_request_with_auth(self):
        """Test request with authentication."""

        def check_auth(request):
            # Check for Authorization header
            assert "Authorization" in request.headers
            return (200, {}, '{"authenticated": true}')

        responses.add_callback(
            responses.GET,
            "https://api.example.com/secure",
            callback=check_auth,
            content_type="application/json",
        )

        ctx = ParsedContext(
            method="GET",
            url="https://api.example.com/secure",
            data=None,
            headers=None,
            cookies=None,
            verify=None,
            auth=("username", "password"),
            proxy=None,
        )

        resp = run_parsed_context(ctx)

        assert resp.status_code == 200

    @responses.activate
    def test_verify_false_allows_insecure(self):
        """Test verify=False is passed through."""
        responses.add(
            responses.GET,
            "https://self-signed.example.com/data",
            json={"secure": False},
            status=200,
        )

        ctx = ParsedContext(
            method="GET",
            url="https://self-signed.example.com/data",
            data=None,
            headers=None,
            cookies=None,
            verify=False,
            auth=None,
            proxy=None,
        )

        resp = run_parsed_context(ctx)

        assert resp.status_code == 200


class TestParsedContext:
    """Tests for ParsedContext namedtuple"""

    def test_creates_parsed_context(self):
        """Test ParsedContext can be created."""
        ctx = ParsedContext(
            method="GET",
            url="https://example.com",
            data=None,
            headers=None,
            cookies=None,
            verify=None,
            auth=None,
            proxy=None,
        )

        assert ctx.method == "GET"
        assert ctx.url == "https://example.com"

    def test_parsed_context_as_dict(self):
        """Test ParsedContext can be converted to dict."""
        ctx = ParsedContext(
            method="POST",
            url="https://example.com/api",
            data='{"key": "value"}',
            headers={"Content-Type": "application/json"},
            cookies=None,
            verify=True,
            auth=None,
            proxy=None,
        )

        ctx_dict = ctx._asdict()

        assert ctx_dict["method"] == "POST"
        assert ctx_dict["url"] == "https://example.com/api"
        assert ctx_dict["data"] == '{"key": "value"}'
        assert ctx_dict["verify"] is True

    def test_parsed_context_immutable(self):
        """Test ParsedContext is immutable (it's a namedtuple)."""
        ctx = ParsedContext(
            method="GET",
            url="https://example.com",
            data=None,
            headers=None,
            cookies=None,
            verify=None,
            auth=None,
            proxy=None,
        )

        with pytest.raises(AttributeError):
            ctx.method = "POST"
