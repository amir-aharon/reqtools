def test_jq_magic_in_real_ipython(ipython_shell):
    """Test jq magic in real IPython environment."""
    ip = ipython_shell

    # Load the extension
    ip.run_line_magic("load_ext", "reqtools.magics")

    # Create test data in the namespace
    test_data = {
        "users": [
            {"name": "Alice", "age": 30, "active": True},
            {"name": "Bob", "age": 25, "active": False},
            {"name": "Charlie", "age": 35, "active": True},
        ]
    }

    # Use Python literal instead of JSON to avoid true/false issues
    ip.run_cell(f"data = {test_data}")

    # Test basic jq query
    result = ip.run_line_magic("jq", "data .users[0].name")

    # Should return the first user's name
    assert result == "Alice"


def test_jq_with_real_json_data(ipython_shell):
    """Test jq with real JSON responses."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    # Create test data directly instead of using mock
    response_data = {
        "status": "success",
        "data": {
            "items": [
                {"id": 1, "name": "Item 1", "price": 10.99},
                {"id": 2, "name": "Item 2", "price": 15.50},
                {"id": 3, "name": "Item 3", "price": 8.75},
            ]
        },
    }

    ip.run_cell(f"response_data = {response_data}")

    # Test jq query on response data
    result = ip.run_line_magic("jq", "response_data .data.items[0].name")

    assert result == "Item 1"


def test_jq_error_handling_in_ipython(ipython_shell):
    """Test error handling in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    # Test with undefined variable
    result = ip.run_line_magic("jq", "nonexistent .test")

    # Should return None for error case
    assert result is None


def test_jq_quiet_mode_in_ipython(ipython_shell, capsys):
    """Test jq quiet mode in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    test_data = {"message": "Hello World"}
    ip.run_cell(f"data = {test_data}")

    # Test quiet mode
    result = ip.run_line_magic("jq", "-q data .message")
    captured = capsys.readouterr()

    assert result == "Hello World"
    assert captured.out == ""  # No output in quiet mode


def test_jq_verbose_mode_in_ipython(ipython_shell, capsys):
    """Test jq verbose mode in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    test_data = {"message": "Hello World"}
    ip.run_cell(f"data = {test_data}")

    # Test verbose mode (default)
    result = ip.run_line_magic("jq", "data .message")
    captured = capsys.readouterr()

    assert result == "Hello World"
    assert '"Hello World"' in captured.out  # Should print JSON


def test_jq_with_complex_queries_in_ipython(ipython_shell):
    """Test jq with complex queries in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    complex_data = {
        "users": [
            {"name": "Alice", "age": 30, "active": True, "roles": ["admin", "user"]},
            {"name": "Bob", "age": 25, "active": False, "roles": ["user"]},
            {
                "name": "Charlie",
                "age": 35,
                "active": True,
                "roles": ["user", "moderator"],
            },
        ]
    }

    ip.run_cell(f"data = {complex_data}")

    # Test complex query to get active users with admin role
    result = ip.run_line_magic(
        "jq",
        'data .users[] | select(.active and (.roles | contains(["admin"]))) | .name',
    )

    assert result == "Alice"  # jq returns single result, not array


def test_jq_with_nested_attributes_in_ipython(ipython_shell):
    """Test jq with nested attribute access in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    # Create test data directly instead of using mock
    response_data = {
        "metadata": {"pagination": {"page": 1, "per_page": 10, "total": 100}},
        "data": [{"id": 1, "name": "Test"}],
    }

    ip.run_cell(f"response_data = {response_data}")

    # Test nested attribute access
    result = ip.run_line_magic("jq", "response_data .metadata.pagination.total")

    assert result == 100


def test_jq_with_list_operations_in_ipython(ipython_shell):
    """Test jq with list operations in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    list_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ip.run_cell(f"numbers = {list_data}")

    # Test list operations
    result = ip.run_line_magic("jq", "numbers .[] | select(. > 5)")

    assert result == [6, 7, 8, 9, 10]


def test_jq_with_mathematical_operations_in_ipython(ipython_shell):
    """Test jq with mathematical operations in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    math_data = {
        "numbers": [1, 2, 3, 4, 5],
        "operations": {"sum": "addition", "product": "multiplication"},
    }

    ip.run_cell(f"data = {math_data}")

    # Test mathematical operations
    result = ip.run_line_magic("jq", "data .numbers | length")

    assert result == 5


def test_jq_with_string_manipulation_in_ipython(ipython_shell):
    """Test jq with string manipulation in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    string_data = {"text": "Hello World", "words": ["Hello", "World", "Test"]}

    ip.run_cell(f"data = {string_data}")

    # Test string manipulation
    result = ip.run_line_magic("jq", "data .text | length")

    assert result == 11  # Length of "Hello World"


def test_jq_with_conditional_logic_in_ipython(ipython_shell):
    """Test jq with conditional logic in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    conditional_data = {
        "items": [
            {"name": "A", "value": 10, "category": "high"},
            {"name": "B", "value": 5, "category": "low"},
            {"name": "C", "value": 15, "category": "high"},
            {"name": "D", "value": 3, "category": "low"},
        ]
    }

    ip.run_cell(f"data = {conditional_data}")

    # Test conditional logic
    result = ip.run_line_magic("jq", "data .items[] | select(.value > 8) | .name")

    assert result == ["A", "C"]


def test_jq_with_array_operations_in_ipython(ipython_shell):
    """Test jq with array operations in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    array_data = {"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}

    ip.run_cell(f"data = {array_data}")

    # Test array operations
    result = ip.run_line_magic("jq", "data .matrix[0]")

    assert result == [1, 2, 3]


def test_jq_error_handling_with_invalid_syntax_in_ipython(ipython_shell):
    """Test jq error handling with invalid syntax in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    test_data = {"key": "value"}
    ip.run_cell(f"data = {test_data}")

    # Test with invalid jq syntax
    result = ip.run_line_magic("jq", "data invalid syntax {")

    # Should return None for syntax error
    assert result is None


def test_jq_with_unicode_data_in_ipython(ipython_shell):
    """Test jq with unicode data in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    unicode_data = {"message": "Hello 世界", "emoji": "🚀", "special": "café"}

    ip.run_cell(f"data = {unicode_data}")

    # Test unicode handling
    result = ip.run_line_magic("jq", "data .message")

    assert result == "Hello 世界"


def test_jq_with_large_dataset_in_ipython(ipython_shell):
    """Test jq with large dataset in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    # Create a large dataset
    large_data = {
        "items": [{"id": i, "value": i * 2, "active": i % 2 == 0} for i in range(1000)]
    }

    ip.run_cell(f"data = {large_data}")

    # Test with large dataset
    result = ip.run_line_magic("jq", "data .items | length")

    assert result == 1000


def test_jq_magic_help_in_ipython(ipython_shell, capsys):
    """Test jq magic help in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    # Test help/usage
    result = ip.run_line_magic("jq", "")
    captured = capsys.readouterr()

    assert result is None
    assert "Usage:" in captured.out
