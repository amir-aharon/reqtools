from unittest.mock import Mock, patch

import pytest
from requests import PreparedRequest, Request, Response


class TestReqToolsMagicsPrivateMethods:
    """Tests for private methods in ReqToolsMagics"""

    def test_get_user_namespace_success(self, magic):
        """Test successful user namespace retrieval."""
        mock_ip = Mock()
        mock_ip.user_ns = {"test_var": "test_value"}

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            user_ns = magic._get_user_namespace()

            assert user_ns == {"test_var": "test_value"}

    def test_get_user_namespace_no_ipython(self, magic):
        """Test when not in IPython environment."""
        with patch("reqtools.magics.get_ipython", return_value=None):
            with pytest.raises(
                RuntimeError, match="Not running in IPython environment"
            ):
                magic._get_user_namespace()

    def test_get_user_namespace_no_user_ns(self, magic):
        """Test when IPython has no user_ns attribute."""
        mock_ip = Mock()
        del mock_ip.user_ns  # Remove user_ns attribute

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            with pytest.raises(RuntimeError, match="IPython instance has no user_ns"):
                magic._get_user_namespace()

    def test_display_http_object_success(self, magic, capsys):
        """Test successful display of HTTP object."""
        mock_request = Request("GET", "https://example.com")

        mock_ip = Mock()
        mock_ip.user_ns = {"my_request": mock_request}

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            with patch("reqtools.magics.HTTPMessage") as mock_http_message:
                mock_msg = Mock()
                mock_http_message.from_request.return_value = mock_msg

                result = magic._display_http_object(
                    line="my_request",
                    expected_type=Request,
                    factory_method=mock_http_message.from_request,
                    type_name="request",
                )

                assert result == mock_request
                mock_http_message.from_request.assert_called_once_with(mock_request)
                mock_msg.display.assert_called_once()

    def test_display_http_object_evaluation_error(self, magic, capsys):
        """Test evaluation errors in _display_http_object."""
        mock_ip = Mock()
        mock_ip.user_ns = {}

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            result = magic._display_http_object(
                line="nonexistent_var",
                expected_type=Request,
                factory_method=Mock(),
                type_name="request",
            )
            captured = capsys.readouterr()

            assert result is None
            assert "Error evaluating 'nonexistent_var'" in captured.out

    def test_display_http_object_type_validation(self, magic, capsys):
        """Test type validation in _display_http_object."""
        mock_ip = Mock()
        mock_ip.user_ns = {"not_a_request": "just a string"}

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            result = magic._display_http_object(
                line="not_a_request",
                expected_type=Request,
                factory_method=Mock(),
                type_name="request",
            )
            captured = capsys.readouterr()

            assert result is None
            assert "Error: not_a_request is not a Request" in captured.out

    def test_display_http_object_factory_error(self, magic, capsys):
        """Test factory method errors in _display_http_object."""
        mock_request = Request("GET", "https://example.com")

        mock_ip = Mock()
        mock_ip.user_ns = {"my_request": mock_request}

        def failing_factory(obj):
            raise ValueError("Factory method failed")

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            result = magic._display_http_object(
                line="my_request",
                expected_type=Request,
                factory_method=failing_factory,
                type_name="request",
            )
            captured = capsys.readouterr()

            assert result is None
            assert "Error displaying request: Factory method failed" in captured.out

    def test_display_http_object_with_prepared_request(self, magic, capsys):
        """Test _display_http_object with PreparedRequest."""
        mock_request = Request("GET", "https://example.com")
        prepared_request = mock_request.prepare()

        mock_ip = Mock()
        mock_ip.user_ns = {"prepared": prepared_request}

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            with patch("reqtools.magics.HTTPMessage") as mock_http_message:
                mock_msg = Mock()
                mock_http_message.from_request.return_value = mock_msg

                result = magic._display_http_object(
                    line="prepared",
                    expected_type=(Request, PreparedRequest),
                    factory_method=mock_http_message.from_request,
                    type_name="request",
                )

                assert result == prepared_request
                mock_http_message.from_request.assert_called_once_with(prepared_request)

    def test_display_http_object_with_response(self, magic, capsys):
        """Test _display_http_object with Response."""
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response._content = b'{"message": "success"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.url = "https://example.com"

        # Mock request
        mock_request = Request("GET", "https://example.com")
        prepared_request = mock_request.prepare()
        mock_response.request = prepared_request

        mock_ip = Mock()
        mock_ip.user_ns = {"my_response": mock_response}

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            with patch("reqtools.magics.HTTPMessage") as mock_http_message:
                mock_msg = Mock()
                mock_http_message.from_response.return_value = mock_msg

                result = magic._display_http_object(
                    line="my_response",
                    expected_type=Response,
                    factory_method=mock_http_message.from_response,
                    type_name="response",
                )

                assert result == mock_response
                mock_http_message.from_response.assert_called_once_with(mock_response)

    def test_display_http_object_empty_line(self, magic, capsys):
        """Test _display_http_object with empty line."""
        result = magic._display_http_object(
            line="", expected_type=Request, factory_method=Mock(), type_name="request"
        )
        captured = capsys.readouterr()

        assert result is None
        assert "Usage: %req <request_variable>" in captured.out

    def test_display_http_object_whitespace_line(self, magic, capsys):
        """Test _display_http_object with whitespace-only line."""
        result = magic._display_http_object(
            line="   ",
            expected_type=Request,
            factory_method=Mock(),
            type_name="request",
        )
        captured = capsys.readouterr()

        assert result is None
        assert "Usage: %req <request_variable>" in captured.out

    def test_display_http_object_with_tuple_expected_type(self, magic, capsys):
        """Test _display_http_object with tuple expected type."""
        mock_request = Request("GET", "https://example.com")

        mock_ip = Mock()
        mock_ip.user_ns = {"my_request": mock_request}

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            with patch("reqtools.magics.HTTPMessage") as mock_http_message:
                mock_msg = Mock()
                mock_http_message.from_request.return_value = mock_msg

                result = magic._display_http_object(
                    line="my_request",
                    expected_type=(Request, PreparedRequest),
                    factory_method=mock_http_message.from_request,
                    type_name="request",
                )

                assert result == mock_request

    def test_display_http_object_with_single_expected_type(self, magic, capsys):
        """Test _display_http_object with single expected type."""
        mock_request = Request("GET", "https://example.com")

        mock_ip = Mock()
        mock_ip.user_ns = {"my_request": mock_request}

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            with patch("reqtools.magics.HTTPMessage") as mock_http_message:
                mock_msg = Mock()
                mock_http_message.from_request.return_value = mock_msg

                result = magic._display_http_object(
                    line="my_request",
                    expected_type=Request,
                    factory_method=mock_http_message.from_request,
                    type_name="request",
                )

                assert result == mock_request

    def test_display_http_object_type_name_in_error_message(self, magic, capsys):
        """Test that type name appears correctly in error messages."""
        mock_ip = Mock()
        mock_ip.user_ns = {"not_a_response": 123}

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            result = magic._display_http_object(
                line="not_a_response",
                expected_type=Response,
                factory_method=Mock(),
                type_name="response",
            )
            captured = capsys.readouterr()

            assert result is None
            assert "Error: not_a_response is not a Response" in captured.out

    def test_display_http_object_with_none_object(self, magic, capsys):
        """Test _display_http_object with None object."""
        mock_ip = Mock()
        mock_ip.user_ns = {"none_var": None}

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            result = magic._display_http_object(
                line="none_var",
                expected_type=Request,
                factory_method=Mock(),
                type_name="request",
            )
            captured = capsys.readouterr()

            assert result is None
            assert "Error: none_var is not a Request" in captured.out

    def test_display_http_object_with_wrong_type_class(self, magic, capsys):
        """Test _display_http_object with wrong type class."""
        mock_ip = Mock()
        mock_ip.user_ns = {"wrong_type": "string"}

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            result = magic._display_http_object(
                line="wrong_type",
                expected_type=Response,
                factory_method=Mock(),
                type_name="response",
            )
            captured = capsys.readouterr()

            assert result is None
            assert "Error: wrong_type is not a Response" in captured.out

    def test_display_http_object_factory_method_called_with_correct_object(self, magic):
        """Test that factory method is called with the correct object."""
        mock_request = Request("POST", "https://api.example.com", json={"key": "value"})

        mock_ip = Mock()
        mock_ip.user_ns = {"my_request": mock_request}

        mock_factory = Mock()
        mock_factory.return_value = Mock()

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            magic._display_http_object(
                line="my_request",
                expected_type=Request,
                factory_method=mock_factory,
                type_name="request",
            )

            mock_factory.assert_called_once_with(mock_request)

    def test_display_http_object_display_method_called(self, magic):
        """Test that display method is called on the created message."""
        mock_request = Request("GET", "https://example.com")

        mock_ip = Mock()
        mock_ip.user_ns = {"my_request": mock_request}

        mock_factory = Mock()
        mock_message = Mock()
        mock_factory.return_value = mock_message

        with patch("reqtools.magics.get_ipython", return_value=mock_ip):
            magic._display_http_object(
                line="my_request",
                expected_type=Request,
                factory_method=mock_factory,
                type_name="request",
            )

            mock_message.display.assert_called_once()
