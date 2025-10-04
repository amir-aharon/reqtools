from unittest.mock import MagicMock, Mock, patch

from reqtools.jq.processor import run_jq


class TestRunJq:
    """Tests for run_jq() function"""

    def test_basic_jq_query(self):
        """Test basic jq query execution."""
        data = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}
        query = ".users[0].name"

        # Mock the jq module by patching the import
        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = ["Alice"]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)

            assert result == "Alice"
            mock_jq.compile.assert_called_once_with(query)
            mock_compiled.input.assert_called_once_with(data)

    def test_jq_query_with_single_result(self):
        """Test jq query with single result."""
        data = {"value": 42}
        query = ".value"

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = [42]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)

            assert result == 42

    def test_jq_query_with_multiple_results(self):
        """Test jq query with multiple results."""
        data = {"items": [1, 2, 3, 4, 5]}
        query = ".items[]"

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = [1, 2, 3, 4, 5]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)

            assert result == [1, 2, 3, 4, 5]

    def test_jq_quiet_mode(self, capsys):
        """Test quiet mode (no printing)."""
        data = {"message": "Hello World"}
        query = ".message"

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = ["Hello World"]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query, quiet=True)
            captured = capsys.readouterr()

            assert result == "Hello World"
            assert captured.out == ""  # No output in quiet mode

    def test_jq_verbose_mode(self, capsys):
        """Test verbose mode (with printing)."""
        data = {"message": "Hello World"}
        query = ".message"

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = ["Hello World"]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query, quiet=False)
            captured = capsys.readouterr()

            assert result == "Hello World"
            assert '"Hello World"' in captured.out  # Should print JSON

    def test_jq_with_invalid_query(self, capsys):
        """Test error handling for invalid queries."""
        data = {"test": "value"}
        query = "invalid jq syntax {"

        mock_jq = MagicMock()
        mock_jq.compile.side_effect = Exception("Invalid jq syntax")

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)
            captured = capsys.readouterr()

            assert result is None
            assert "Error executing query: Invalid jq syntax" in captured.out

    def test_jq_with_jq_not_installed(self, capsys):
        """Test ImportError handling when jq is not installed."""
        data = {"test": "value"}
        query = ".test"

        # Simulate ImportError by patching the import
        def mock_import(name, *args, **kwargs):
            if name == "jq":
                raise ImportError("No module named jq")
            return __import__(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            result = run_jq(data, query)
            captured = capsys.readouterr()

            assert result is None
            assert (
                "Error: jq library not installed. Run: pip install jq" in captured.out
            )

    def test_jq_with_json_data(self):
        """Test with JSON data."""
        data = '{"users": [{"name": "Alice"}]}'
        query = ".users[0].name"

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = ["Alice"]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)

            assert result == "Alice"

    def test_jq_with_dict_data(self):
        """Test with Python dict data."""
        data = {"key": "value", "number": 42}
        query = ".key"

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = ["value"]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)

            assert result == "value"

    def test_jq_with_list_data(self):
        """Test with Python list data."""
        data = [1, 2, 3, 4, 5]
        query = ".[0]"

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = [1]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)

            assert result == 1

    def test_jq_with_string_data(self):
        """Test with string data."""
        data = "Hello World"
        query = "."

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = ["Hello World"]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)

            assert result == "Hello World"

    def test_jq_with_none_data(self):
        """Test with None data."""
        data = None
        query = "."

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = [None]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)

            assert result is None

    def test_jq_complex_query(self):
        """Test complex jq queries."""
        data = {
            "users": [
                {"name": "Alice", "age": 30, "active": True},
                {"name": "Bob", "age": 25, "active": False},
                {"name": "Charlie", "age": 35, "active": True},
            ]
        }
        query = ".users[] | select(.active) | .name"

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = ["Alice", "Charlie"]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)

            assert result == ["Alice", "Charlie"]

    def test_jq_query_exception_handling(self, capsys):
        """Test general exception handling."""
        data = {"test": "value"}
        query = ".test"

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.side_effect = RuntimeError(
            "Unexpected error"
        )
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)
            captured = capsys.readouterr()

            assert result is None
            assert "Error executing query: Unexpected error" in captured.out

    def test_jq_empty_result(self):
        """Test jq query with empty result."""
        data = {"items": []}
        query = ".items[]"

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = []
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)

            assert result == []

    def test_jq_unicode_handling(self):
        """Test jq query with unicode data."""
        data = {"message": "Hello 世界", "emoji": "🚀"}
        query = ".message"

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = ["Hello 世界"]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            result = run_jq(data, query)

            assert result == "Hello 世界"

    def test_jq_ensure_ascii_false_in_output(self, capsys):
        """Test that ensure_ascii=False is used in JSON output."""
        data = {"message": "Hello 世界"}
        query = ".message"

        mock_jq = MagicMock()
        mock_compiled = Mock()
        mock_compiled.input.return_value.all.return_value = ["Hello 世界"]
        mock_jq.compile.return_value = mock_compiled

        with patch.dict("sys.modules", {"jq": mock_jq}):
            with patch("json.dumps") as mock_dumps:
                mock_dumps.return_value = '"Hello 世界"'
                run_jq(data, query, quiet=False)

                mock_dumps.assert_called_once()
                args, kwargs = mock_dumps.call_args
                assert kwargs.get("ensure_ascii") is False
                assert kwargs.get("indent") == 2
