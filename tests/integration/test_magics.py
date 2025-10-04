from unittest.mock import Mock, patch

import responses
from requests import Request


class TestReqMagic:
    """Tests for %req magic command"""

    def test_req_with_empty_line(self, magic, capsys):
        """Test %req with no arguments shows usage."""
        result = magic.req("")
        captured = capsys.readouterr()

        assert result is None
        assert "Usage:" in captured.out

    def test_req_with_whitespace_only(self, magic, capsys):
        """Test %req with whitespace shows usage."""
        result = magic.req("   ")
        captured = capsys.readouterr()

        assert result is None
        assert "Usage:" in captured.out

    @patch("reqtools.magics.get_ipython")
    def test_req_evaluates_variable(
        self, mock_get_ipython, magic, mock_request, capsys
    ):
        """Test %req evaluates variable from user namespace."""
        mock_ip = Mock()
        mock_ip.user_ns = {"my_request": mock_request}
        mock_get_ipython.return_value = mock_ip

        result = magic.req("my_request")
        captured = capsys.readouterr()

        assert result == mock_request
        assert "Method: POST" in captured.out
        assert "https://api.example.com/users" in captured.out

    @patch("reqtools.magics.get_ipython")
    def test_req_evaluates_nested_attribute(self, mock_get_ipython, magic, capsys):
        """Test %req can evaluate nested attributes like response.request."""
        mock_response = Mock()
        mock_response.request = Request("GET", "https://api.example.com/data")

        mock_ip = Mock()
        mock_ip.user_ns = {"resp": mock_response}
        mock_get_ipython.return_value = mock_ip

        result = magic.req("resp.request")
        captured = capsys.readouterr()

        assert result is not None
        assert "Method: GET" in captured.out

    @patch("reqtools.magics.get_ipython")
    def test_req_with_invalid_variable(self, mock_get_ipython, magic, capsys):
        """Test %req with undefined variable shows error."""
        mock_ip = Mock()
        mock_ip.user_ns = {}
        mock_get_ipython.return_value = mock_ip

        result = magic.req("nonexistent")
        captured = capsys.readouterr()

        assert result is None
        assert "Error evaluating" in captured.out

    @patch("reqtools.magics.get_ipython")
    def test_req_with_wrong_type(self, mock_get_ipython, magic, capsys):
        """Test %req with non-Request object shows error."""
        mock_ip = Mock()
        mock_ip.user_ns = {"not_a_request": "just a string"}
        mock_get_ipython.return_value = mock_ip

        result = magic.req("not_a_request")
        captured = capsys.readouterr()

        assert result is None
        assert "is not a" in captured.out

    @patch("reqtools.magics.get_ipython")
    def test_req_with_prepared_request(self, mock_get_ipython, magic, capsys):
        """Test %req works with PreparedRequest."""
        prepared = Request("GET", "https://api.example.com").prepare()

        mock_ip = Mock()
        mock_ip.user_ns = {"prepped": prepared}
        mock_get_ipython.return_value = mock_ip

        result = magic.req("prepped")
        captured = capsys.readouterr()

        assert result == prepared
        assert "Method: GET" in captured.out


class TestResMagic:
    """Tests for %res magic command"""

    def test_res_with_empty_line(self, magic, capsys):
        """Test %res with no arguments shows usage."""
        result = magic.res("")
        captured = capsys.readouterr()

        assert result is None
        assert "Usage:" in captured.out

    @patch("reqtools.magics.get_ipython")
    def test_res_evaluates_variable(
        self, mock_get_ipython, magic, mock_response_for_magics, capsys
    ):
        """Test %res evaluates variable from user namespace."""
        mock_ip = Mock()
        mock_ip.user_ns = {"my_response": mock_response_for_magics}
        mock_get_ipython.return_value = mock_ip

        result = magic.res("my_response")
        captured = capsys.readouterr()

        assert result == mock_response_for_magics
        assert "Status: 200 OK" in captured.out
        assert "https://api.example.com/test" in captured.out

    @patch("reqtools.magics.get_ipython")
    def test_res_with_invalid_variable(self, mock_get_ipython, magic, capsys):
        """Test %res with undefined variable shows error."""
        mock_ip = Mock()
        mock_ip.user_ns = {}
        mock_get_ipython.return_value = mock_ip

        result = magic.res("nonexistent")
        captured = capsys.readouterr()

        assert result is None
        assert "Error evaluating" in captured.out

    @patch("reqtools.magics.get_ipython")
    def test_res_with_wrong_type(self, mock_get_ipython, magic, capsys):
        """Test %res with non-Response object shows error."""
        mock_ip = Mock()
        mock_ip.user_ns = {"not_a_response": 123}
        mock_get_ipython.return_value = mock_ip

        result = magic.res("not_a_response")
        captured = capsys.readouterr()

        assert result is None
        assert "is not a" in captured.out


class TestCurlMagic:
    """Tests for %curl magic command"""

    def test_curl_with_empty_params(self, magic, capsys):
        """Test %curl with no arguments shows usage."""
        result = magic.curl("")
        captured = capsys.readouterr()

        assert result is None
        assert "Usage:" in captured.out

    def test_curl_with_whitespace(self, magic, capsys):
        """Test %curl with whitespace shows usage."""
        result = magic.curl("   ")
        captured = capsys.readouterr()

        assert result is None
        assert "Usage:" in captured.out

    @responses.activate
    @patch("reqtools.magics.uncurl")
    def test_curl_executes_command(self, mock_uncurl, magic):
        """Test %curl executes curl command."""
        # Mock uncurl.parse_context
        from reqtools.http.utils import ParsedContext

        mock_context = ParsedContext(
            method="GET",
            url="https://api.example.com/data",
            data=None,
            headers=None,
            cookies=None,
            verify=None,
            auth=None,
            proxy=None,
        )
        mock_uncurl.parse_context.return_value = mock_context

        # Mock the HTTP response
        responses.add(
            responses.GET,
            "https://api.example.com/data",
            json={"status": "ok"},
            status=200,
        )

        result = magic.curl("https://api.example.com/data")

        assert result is not None
        assert result.status_code == 200

    @patch("reqtools.magics.uncurl")
    def test_curl_handles_invalid_syntax(self, mock_uncurl, magic, capsys):
        """Test %curl handles invalid curl syntax gracefully."""
        # Mock uncurl raising SystemExit
        mock_uncurl.parse_context.side_effect = SystemExit(2)

        result = magic.curl("--invalid-flag")
        captured = capsys.readouterr()

        assert result is None
        assert "Error" in captured.out

    @patch("reqtools.magics.uncurl")
    def test_curl_handles_general_error(self, mock_uncurl, magic, capsys):
        """Test %curl handles general errors."""
        mock_uncurl.parse_context.side_effect = Exception("Something went wrong")

        result = magic.curl("https://example.com")
        captured = capsys.readouterr()

        assert result is None
        assert "Error executing curl command" in captured.out


class TestDisplayHttpObject:
    """Tests for _display_http_object helper method"""

    @patch("reqtools.magics.get_ipython")
    def test_display_validates_type(self, mock_get_ipython, magic, capsys):
        """Test _display_http_object validates type correctly."""
        mock_ip = Mock()
        mock_ip.user_ns = {"obj": "not the right type"}
        mock_get_ipython.return_value = mock_ip

        from reqtools.http.display import HTTPMessage

        result = magic._display_http_object(
            line="obj",
            expected_type=Request,
            factory_method=HTTPMessage.from_request,
            type_name="request",
        )
        captured = capsys.readouterr()

        assert result is None
        assert "is not a" in captured.out

    @patch("reqtools.magics.get_ipython")
    def test_display_handles_factory_error(self, mock_get_ipython, magic, capsys):
        """Test _display_http_object handles factory method errors."""
        mock_obj = Mock()

        mock_ip = Mock()
        mock_ip.user_ns = {"obj": mock_obj}
        mock_get_ipython.return_value = mock_ip

        # Factory that raises error
        def bad_factory(obj):
            raise ValueError("Cannot create message")

        result = magic._display_http_object(
            line="obj", expected_type=Mock, factory_method=bad_factory, type_name="test"
        )
        captured = capsys.readouterr()

        assert result is None
        assert "Error displaying" in captured.out


class TestJqMagic:
    """Tests for %jq magic command"""

    def test_jq_with_empty_line(self, magic, capsys):
        """Test %jq with no arguments shows usage."""
        result = magic.jq("")
        captured = capsys.readouterr()

        assert result is None
        assert "Usage:" in captured.out

    def test_jq_with_whitespace_only(self, magic, capsys):
        """Test %jq with whitespace shows usage."""
        result = magic.jq("   ")
        captured = capsys.readouterr()

        assert result is None
        assert "Usage:" in captured.out

    def test_jq_with_invalid_syntax(self, magic, capsys):
        """Test %jq with invalid syntax shows usage."""
        result = magic.jq("invalid")
        captured = capsys.readouterr()

        assert result is None
        assert "Usage:" in captured.out

    def test_jq_with_missing_query(self, magic, capsys):
        """Test %jq with missing query parameter shows usage."""
        result = magic.jq("data_var")
        captured = capsys.readouterr()

        assert result is None
        assert "Usage:" in captured.out

    @patch("reqtools.magics.get_ipython")
    def test_jq_with_missing_variable(self, mock_get_ipython, magic, capsys):
        """Test %jq with undefined variable shows error."""
        mock_ip = Mock()
        mock_ip.user_ns = {}
        mock_get_ipython.return_value = mock_ip

        result = magic.jq("nonexistent .test")
        captured = capsys.readouterr()

        assert result is None
        assert "Error evaluating" in captured.out

    @patch("reqtools.magics.get_ipython")
    def test_jq_quiet_flag_parsing(self, mock_get_ipython, magic, capsys):
        """Test -q flag parsing."""
        mock_ip = Mock()
        mock_ip.user_ns = {"data": {"key": "value"}}
        mock_get_ipython.return_value = mock_ip

        with patch("reqtools.magics.run_jq") as mock_run_jq:
            mock_run_jq.return_value = "value"

            result = magic.jq("-q data .key")
            capsys.readouterr()

            assert result == "value"
            mock_run_jq.assert_called_once_with(
                data={"key": "value"}, query=".key", quiet=True
            )

    @patch("reqtools.magics.get_ipython")
    def test_jq_variable_evaluation_error(self, mock_get_ipython, magic, capsys):
        """Test variable evaluation errors."""
        mock_ip = Mock()
        mock_ip.user_ns = {}
        mock_get_ipython.return_value = mock_ip

        result = magic.jq("invalid_var .test")
        captured = capsys.readouterr()

        assert result is None
        assert "Error evaluating" in captured.out

    @patch("reqtools.magics.get_ipython")
    def test_jq_successful_execution(self, mock_get_ipython, magic, capsys):
        """Test successful jq execution."""
        mock_ip = Mock()
        mock_ip.user_ns = {"data": {"users": [{"name": "Alice"}]}}
        mock_get_ipython.return_value = mock_ip

        with patch("reqtools.magics.run_jq") as mock_run_jq:
            mock_run_jq.return_value = "Alice"

            result = magic.jq("data .users[0].name")
            capsys.readouterr()

            assert result == "Alice"
            mock_run_jq.assert_called_once_with(
                data={"users": [{"name": "Alice"}]}, query=".users[0].name", quiet=False
            )

    @patch("reqtools.magics.get_ipython")
    def test_jq_quiet_mode_execution(self, mock_get_ipython, magic, capsys):
        """Test quiet mode execution."""
        mock_ip = Mock()
        mock_ip.user_ns = {"data": {"value": 42}}
        mock_get_ipython.return_value = mock_ip

        with patch("reqtools.magics.run_jq") as mock_run_jq:
            mock_run_jq.return_value = 42

            result = magic.jq("-q data .value")
            capsys.readouterr()

            assert result == 42
            mock_run_jq.assert_called_once_with(
                data={"value": 42}, query=".value", quiet=True
            )

    @patch("reqtools.magics.get_ipython")
    def test_jq_verbose_mode_execution(self, mock_get_ipython, magic, capsys):
        """Test verbose mode execution."""
        mock_ip = Mock()
        mock_ip.user_ns = {"data": {"message": "Hello"}}
        mock_get_ipython.return_value = mock_ip

        with patch("reqtools.magics.run_jq") as mock_run_jq:
            mock_run_jq.return_value = "Hello"

            result = magic.jq("data .message")
            capsys.readouterr()

            assert result == "Hello"
            mock_run_jq.assert_called_once_with(
                data={"message": "Hello"}, query=".message", quiet=False
            )

    @patch("reqtools.magics.get_ipython")
    def test_jq_with_nested_attribute(self, mock_get_ipython, magic, capsys):
        """Test jq with nested attribute access."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"users": [{"name": "Bob"}]}}

        mock_ip = Mock()
        mock_ip.user_ns = {"resp": mock_response}
        mock_get_ipython.return_value = mock_ip

        with patch("reqtools.magics.run_jq") as mock_run_jq:
            mock_run_jq.return_value = "Bob"

            result = magic.jq("resp.json() .data.users[0].name")
            capsys.readouterr()

            assert result == "Bob"
            mock_run_jq.assert_called_once_with(
                data={"data": {"users": [{"name": "Bob"}]}},
                query=".data.users[0].name",
                quiet=False,
            )

    @patch("reqtools.magics.get_ipython")
    def test_jq_with_complex_data(self, mock_get_ipython, magic, capsys):
        """Test jq with complex data structures."""
        complex_data = {
            "users": [
                {"name": "Alice", "age": 30, "active": True},
                {"name": "Bob", "age": 25, "active": False},
            ]
        }

        mock_ip = Mock()
        mock_ip.user_ns = {"data": complex_data}
        mock_get_ipython.return_value = mock_ip

        with patch("reqtools.magics.run_jq") as mock_run_jq:
            mock_run_jq.return_value = ["Alice"]

            result = magic.jq("data '.users[] | select(.active) | .name'")
            capsys.readouterr()

            assert result == ["Alice"]
            mock_run_jq.assert_called_once_with(
                data=complex_data,
                query="'.users[] | select(.active) | .name'",
                quiet=False,
            )

    @patch("reqtools.magics.get_ipython")
    def test_jq_with_whitespace_in_query(self, mock_get_ipython, magic, capsys):
        """Test jq with whitespace in query."""
        mock_ip = Mock()
        mock_ip.user_ns = {"data": {"key": "value"}}
        mock_get_ipython.return_value = mock_ip

        with patch("reqtools.magics.run_jq") as mock_run_jq:
            mock_run_jq.return_value = "value"

            result = magic.jq("data ' .key '")
            capsys.readouterr()

            assert result == "value"
            mock_run_jq.assert_called_once_with(
                data={"key": "value"}, query="' .key '", quiet=False
            )


class TestLoadExtension:
    """Tests for load_ipython_extension"""

    def test_load_extension_registers_magics(self):
        """Test extension registration."""
        from reqtools.magics import ReqToolsMagics as ReqToolsMagicsClass
        from reqtools.magics import load_ipython_extension

        mock_ipython = Mock()
        load_ipython_extension(mock_ipython)

        mock_ipython.register_magics.assert_called_once()

        # Check that ReqToolsMagics was registered
        args = mock_ipython.register_magics.call_args[0]
        assert args[0] == ReqToolsMagicsClass
