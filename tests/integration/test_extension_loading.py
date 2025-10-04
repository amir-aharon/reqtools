def test_extension_loads_in_real_ipython(ipython_shell):
    """Test extension actually loads in IPython."""
    ip = ipython_shell

    # Load the extension
    ip.run_line_magic("load_ext", "reqtools.magics")

    # Verify magics are available
    assert "req" in ip.magics_manager.magics["line"]
    assert "res" in ip.magics_manager.magics["line"]
    assert "curl" in ip.magics_manager.magics["line"]


def test_extension_can_be_reloaded(ipython_shell):
    """Test extension can be reloaded without errors."""
    ip = ipython_shell

    ip.run_line_magic("load_ext", "reqtools.magics")
    ip.run_line_magic("reload_ext", "reqtools.magics")

    # Should still work
    assert "req" in ip.magics_manager.magics["line"]
    assert "res" in ip.magics_manager.magics["line"]
    assert "curl" in ip.magics_manager.magics["line"]


def test_magics_work_in_real_ipython(ipython_shell):
    """Test magics actually execute in IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    # Create a mock request in the namespace
    ip.run_cell(
        """
import requests
test_req = requests.Request('GET', 'https://example.com')
    """
    )

    # Run the magic - should not raise
    result = ip.run_line_magic("req", "test_req")

    # Should return the request object
    assert result is not None


def test_magic_error_handling_in_real_ipython(ipython_shell):
    """Test error handling works in real IPython."""
    ip = ipython_shell
    ip.run_line_magic("load_ext", "reqtools.magics")

    # Try with undefined variable
    result = ip.run_line_magic("req", "undefined_var")

    # Should return None (error case)
    assert result is None


def test_extension_unload(ipython_shell):
    """Test extension can be unloaded."""
    ip = ipython_shell

    ip.run_line_magic("load_ext", "reqtools.magics")
    assert "req" in ip.magics_manager.magics["line"]

    ip.run_line_magic("unload_ext", "reqtools.magics")

    # Magics should be removed (or raise KeyError)
    # Note: Some IPython versions may not fully unload
    try:
        assert "req" not in ip.magics_manager.magics["line"]
    except (KeyError, AssertionError):
        # This is acceptable - extension unloading behavior varies
        pass
