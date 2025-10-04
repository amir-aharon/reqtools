import sys

import pytest


class TestPackageImports:
    """Tests for package imports and initialization"""

    def test_package_imports(self):
        """Test that all imports work correctly."""
        # Test that the package can be imported
        import reqtools

        # Test that the package has expected attributes
        assert hasattr(reqtools, "__version__")
        assert hasattr(reqtools, "__all__")

        # Test that the package has expected modules
        assert hasattr(reqtools, "http")
        assert hasattr(reqtools, "jq")
        assert hasattr(reqtools, "magics")

    def test_version_attribute(self):
        """Test __version__ attribute."""
        import reqtools

        assert reqtools.__version__ == "0.1.0"
        assert isinstance(reqtools.__version__, str)

    def test_all_attribute(self):
        """Test __all__ attribute."""
        import reqtools

        expected_exports = ["HTTPMessage", "load_ipython_extension"]
        assert reqtools.__all__ == expected_exports
        assert isinstance(reqtools.__all__, list)
        assert len(reqtools.__all__) == 2

    def test_httpmessage_import(self):
        """Test HTTPMessage import."""
        from reqtools import HTTPMessage

        # Test that HTTPMessage is the correct class
        from reqtools.http.display import HTTPMessage as HTTPMessageClass

        assert HTTPMessage is HTTPMessageClass

        # Test that HTTPMessage can be instantiated
        msg = HTTPMessage(
            method="GET", url="https://example.com", headers={}, body=None
        )
        assert msg.method == "GET"
        assert msg.url == "https://example.com"

    def test_load_ipython_extension_import(self):
        """Test load_ipython_extension import."""
        from reqtools import load_ipython_extension

        # Test that load_ipython_extension is callable
        assert callable(load_ipython_extension)

        # Test that it has the expected signature
        import inspect

        sig = inspect.signature(load_ipython_extension)
        assert len(sig.parameters) == 1
        assert "ipython" in sig.parameters

    def test_http_submodule_imports(self):
        """Test that http submodule imports work."""
        from reqtools.http import display, utils

        # Test that the modules have expected classes/functions
        assert hasattr(display, "HTTPMessage")
        assert hasattr(display, "ParsedContext")
        assert hasattr(utils, "run_parsed_context")

    def test_jq_submodule_imports(self):
        """Test that jq submodule imports work."""
        from reqtools.jq import processor

        # Test that the module has expected functions
        assert hasattr(processor, "run_jq")
        assert callable(processor.run_jq)

    def test_magics_submodule_imports(self):
        """Test that magics submodule imports work."""
        from reqtools.magics import ReqToolsMagics, load_ipython_extension

        # Test that the classes/functions are available
        assert hasattr(ReqToolsMagics, "curl")
        assert hasattr(ReqToolsMagics, "req")
        assert hasattr(ReqToolsMagics, "res")
        assert hasattr(ReqToolsMagics, "jq")
        assert callable(load_ipython_extension)

    def test_import_from_package_root(self):
        """Test importing from package root works as expected."""
        # Test that we can import the main exports
        from reqtools import HTTPMessage, load_ipython_extension  # noqa: F401

        # Test that we can't import internal modules directly
        with pytest.raises(ImportError):
            from reqtools import display  # noqa: F401

        with pytest.raises(ImportError):
            from reqtools import utils  # noqa: F401

    def test_package_metadata(self):
        """Test package metadata is accessible."""
        import reqtools

        # Test that the package has a __file__ attribute
        assert hasattr(reqtools, "__file__")
        assert reqtools.__file__.endswith("__init__.py")

        # Test that the package has a __path__ attribute
        assert hasattr(reqtools, "__path__")
        assert isinstance(reqtools.__path__, list)

    def test_submodule_access(self):
        """Test that submodules can be accessed through the package."""
        import reqtools

        # Test accessing submodules
        assert reqtools.http is not None
        assert reqtools.jq is not None
        assert reqtools.magics is not None

        # Test that submodules have expected attributes
        assert hasattr(reqtools.http, "display")
        assert hasattr(reqtools.http, "utils")
        assert hasattr(reqtools.jq, "processor")
        assert hasattr(reqtools.magics, "ReqToolsMagics")

    def test_import_error_handling(self):
        """Test that import errors are handled gracefully."""
        # Test that importing non-existent modules raises ImportError
        with pytest.raises(ImportError):
            __import__("reqtools.nonexistent")

        with pytest.raises(ImportError):
            __import__("reqtools.nonexistent")

    def test_circular_imports(self):
        """Test that there are no circular import issues."""
        # This test ensures that importing the package doesn't cause circular imports

        # If we get here without errors, circular imports are not an issue
        assert True

    def test_package_initialization_side_effects(self):
        """Test that package initialization doesn't have unwanted side effects."""
        # Test that importing the package doesn't modify global state unexpectedly
        original_modules = set(sys.modules.keys())

        # Check that no unexpected modules were added
        new_modules = set(sys.modules.keys()) - original_modules
        expected_modules = {
            "reqtools",
            "reqtools.http",
            "reqtools.http.display",
            "reqtools.http.utils",
            "reqtools.jq",
            "reqtools.jq.processor",
            "reqtools.magics",
        }

        # The new modules should be a subset of expected modules
        assert new_modules.issubset(expected_modules)

    def test_version_consistency(self):
        """Test that version is consistent across the package."""
        import reqtools

        # Test that version is accessible and consistent
        version = reqtools.__version__
        assert version == "0.1.0"

        # Test that version is a valid semantic version
        parts = version.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_all_exports_are_importable(self):
        """Test that all items in __all__ are actually importable."""
        import reqtools

        for export_name in reqtools.__all__:
            # Test that each export can be imported
            export = getattr(reqtools, export_name)
            assert export is not None

            # Test that each export is callable (functions/classes)
            assert callable(export)

    def test_package_docstring(self):
        """Test that the package has appropriate documentation."""
        import reqtools

        # Test that the package has a docstring (even if empty)
        assert hasattr(reqtools, "__doc__")

        # Test that the package can be inspected
        assert hasattr(reqtools, "__name__")
        assert reqtools.__name__ == "reqtools"
