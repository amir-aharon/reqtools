from requests import PreparedRequest, Request, Response

from reqtools.http.display import HTTPMessage


class TestHTTPMessageFromResponse:
    """Tests for HTTPMessage.from_response()"""

    def test_creates_message_from_response(self, mock_response):
        """Test basic creation from Response."""
        msg = HTTPMessage.from_response(mock_response)

        assert msg.status_code == 200
        assert msg.reason == "OK"
        assert msg.method == "GET"
        assert msg.url == "https://api.example.com/test"
        assert msg.body == '{"message": "Hello World", "status": "success"}'

    def test_extracts_headers_from_response(self, mock_response):
        """Test headers are properly extracted."""
        msg = HTTPMessage.from_response(mock_response)

        assert "Content-Type" in msg.headers
        assert msg.headers["Content-Type"] == "application/json"

    def test_handles_empty_response_body(self):
        """Test response with no body."""
        resp = Response()
        resp.status_code = 204
        resp.reason = "No Content"
        resp._content = b""
        resp.url = "https://api.example.com/test"

        req = PreparedRequest()
        req.method = "DELETE"
        req.url = "https://api.example.com/test"
        resp.request = req

        msg = HTTPMessage.from_response(resp)

        assert msg.status_code == 204
        assert msg.body == ""


class TestHTTPMessageFromRequest:
    """Tests for HTTPMessage.from_request()"""

    def test_creates_message_from_request(self, mock_request):
        """Test basic creation from Request."""
        msg = HTTPMessage.from_request(mock_request)

        assert msg.method == "POST"
        assert msg.url == "https://api.example.com/users"
        assert msg.status_code is None
        assert msg.reason is None

    def test_extracts_headers_from_request(self, mock_request):
        """Test headers are properly extracted."""
        msg = HTTPMessage.from_request(mock_request)

        assert "Content-Type" in msg.headers
        assert msg.headers["Content-Type"] == "application/json"
        assert msg.headers["X-API-Key"] == "secret123"

    def test_handles_json_body(self, mock_request):
        """Test JSON body is properly decoded."""
        msg = HTTPMessage.from_request(mock_request)

        assert msg.body is not None
        # Body should contain the JSON data as string
        assert "Alice" in msg.body

    def test_handles_prepared_request(self):
        """Test works with PreparedRequest."""
        req = Request("GET", "https://api.example.com/data")
        prepared = req.prepare()

        msg = HTTPMessage.from_request(prepared)

        assert msg.method == "GET"
        assert msg.url == "https://api.example.com/data"

    def test_handles_binary_body(self):
        """Test binary body is handled gracefully."""
        # Use invalid UTF-8 bytes
        req = Request(
            method="POST",
            url="https://api.example.com/upload",
            data=b"\xff\xfe\xfd\xfc\xfb",
        )

        msg = HTTPMessage.from_request(req)

        assert msg.body == "<binary data, 5 bytes>"

    def test_handles_empty_request_body(self):
        """Test request with no body."""
        req = Request("GET", "https://api.example.com/users")

        msg = HTTPMessage.from_request(req)

        assert msg.body is None


class TestHTTPMessageDisplay:
    """Tests for HTTPMessage.display()"""

    def test_display_prints_response_status(self, json_message, capsys):
        """Test response displays status code."""
        json_message.display()
        captured = capsys.readouterr()

        assert "Status: 200 OK" in captured.out
        assert "=" * 80 in captured.out

    def test_display_prints_request_method(self, request_message, capsys):
        """Test request displays method instead of status."""
        request_message.display()
        captured = capsys.readouterr()

        assert "Method: POST" in captured.out
        assert "Status:" not in captured.out

    def test_display_prints_url(self, json_message, capsys):
        """Test URL is displayed."""
        json_message.display()
        captured = capsys.readouterr()

        assert "URL:    https://api.example.com/users" in captured.out

    def test_display_prints_headers(self, json_message, capsys):
        """Test headers are displayed."""
        json_message.display()
        captured = capsys.readouterr()

        assert "Headers:" in captured.out
        assert "Content-Type: application/json" in captured.out
        assert "X-Request-ID: 123" in captured.out

    def test_display_formats_json_body(self, json_message, capsys):
        """Test JSON body is pretty-printed."""
        json_message.display()
        captured = capsys.readouterr()

        assert "Body:" in captured.out
        # Should be formatted with indentation
        assert '"users"' in captured.out
        assert '"name": "Alice"' in captured.out

    def test_display_shows_text_body(self, text_message, capsys):
        """Test non-JSON body is displayed as-is."""
        text_message.display()
        captured = capsys.readouterr()

        assert "Body:" in captured.out
        assert "<html><body>Hello World</body></html>" in captured.out

    def test_display_truncates_long_body(self, capsys):
        """Test long body is truncated."""
        long_body = "x" * 3000
        msg = HTTPMessage(
            method="GET",
            url="https://example.com",
            headers={},
            body=long_body,
            status_code=200,
            reason="OK",
        )

        msg.display(max_body_length=2000)
        captured = capsys.readouterr()

        assert "[truncated]" in captured.out
        assert len(captured.out) < len(long_body) + 1000  # Some buffer for formatting

    def test_display_handles_empty_body(self, capsys):
        """Test empty body displays placeholder."""
        msg = HTTPMessage(
            method="GET",
            url="https://example.com",
            headers={},
            body=None,
            status_code=204,
            reason="No Content",
        )

        msg.display()
        captured = capsys.readouterr()

        assert "Body:" in captured.out
        assert "<empty>" in captured.out

    def test_display_handles_invalid_json(self, capsys):
        """Test invalid JSON in json content-type falls back to text."""
        msg = HTTPMessage(
            method="GET",
            url="https://example.com",
            headers={"Content-Type": "application/json"},
            body="not valid json {",
            status_code=200,
            reason="OK",
        )

        msg.display()
        captured = capsys.readouterr()

        assert "not valid json {" in captured.out
