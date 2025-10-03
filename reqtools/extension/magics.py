from contextlib import redirect_stderr
from io import StringIO
from typing import Any, Optional

import uncurl  # type: ignore
from IPython import get_ipython
from IPython.core.magic import Magics, line_magic, magics_class
from requests import PreparedRequest, Request, Response

from reqtools.extension.http.display import HTTPMessage
from reqtools.extension.http.utils import run_parsed_context
from reqtools.extension.jq.processor import run_jq

__all__ = ["ReqToolsMagics", "load_ipython_extension"]


@magics_class
class ReqToolsMagics(Magics):

    @line_magic
    def curl(self, params: str = "") -> Optional[Response]:
        """Execute a curl command and return the response."""
        if not params.strip():
            print("Usage: %curl <curl_arguments>")
            print("Example: %curl http://localhost:8000/get")
            return None

        command = f"curl -s {params}"

        try:
            # Suppress uncurl's argparse error output
            with redirect_stderr(StringIO()):
                parsed_context = uncurl.parse_context(command)
            return run_parsed_context(parsed_context)
        except SystemExit:
            print("Error: Invalid curl syntax")
            return None
        except Exception as e:
            print(f"Error executing curl command: {e}")
            return None

    @line_magic
    def res(self, line: str = "") -> Optional[Response]:
        """Pretty print a requests.Response object."""
        return self._display_http_object(
            line=line,
            expected_type=Response,
            factory_method=HTTPMessage.from_response,
            type_name="response",
        )

    @line_magic
    def req(self, line: str = "") -> Optional[Request]:
        """Pretty print a requests.Request object."""
        return self._display_http_object(
            line=line,
            expected_type=(Request, PreparedRequest),
            factory_method=HTTPMessage.from_request,
            type_name="request",
        )

    @line_magic
    def jq(self, line: str = "") -> Any:
        """Apply jq-like query to JSON data.

        Usage: %jq [-q] <variable> <query>

        Options:
        -q    Quiet mode - return result without printing

        Examples:
        %jq response.json() '.users[0].name'        # Print and return
        %jq -q response.json() '.users[0].name'     # Only return (quiet)
        result = %jq data '.items | length'         # Capture result
        """
        if not line.strip():
            print("Usage: %jq [-q] <json_variable> <query>")
            return None

        # Parse quiet flag
        quiet = False
        if line.strip().startswith("-q"):
            quiet = True
            line = line.strip()[2:].strip()

        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            print("Usage: %jq [-q] <json_variable> <query>")
            return None

        var_expr, query = parts

        # Evaluate the variable
        ip = get_ipython()
        try:
            data = eval(var_expr.strip(), ip.user_ns)
        except Exception as e:
            print(f"Error evaluating '{var_expr}': {e}")
            return None

        # Run jq query
        result = run_jq(data=data, query=query, quiet=quiet)
        return result

    def _display_http_object(
        self, line: str, expected_type, factory_method, type_name: str
    ):
        """Generic method to evaluate, validate, and display HTTP objects."""
        if not line.strip():
            print(f"Usage: %{type_name[:3]} <{type_name}_variable>")
            return None

        ip = get_ipython()
        try:
            obj = eval(line.strip(), ip.user_ns)
        except Exception as e:
            print(f"Error evaluating '{line}': {e}")
            return None

        if not isinstance(obj, expected_type):
            type_str = (
                expected_type.__name__
                if hasattr(expected_type, "__name__")
                else str(expected_type)
            )
            print(f"Error: {line} is not a {type_str}")
            return None

        try:
            msg = factory_method(obj)
            msg.display()
        except Exception as e:
            print(f"Error displaying {type_name}: {e}")
            return None

        return obj


def load_ipython_extension(ipython) -> None:
    """Load the ReqTools IPython extension."""
    ipython.register_magics(ReqToolsMagics)
