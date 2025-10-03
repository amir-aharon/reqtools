import json
from typing import Any


def run_jq(data: Any, query: str, quiet: bool = False) -> Any:
    """Execute a jq-like query on JSON data."""
    try:
        import jq  # type: ignore

        compiled = jq.compile(query)
        result = compiled.input(data).all()
        output = result[0] if len(result) == 1 else result
        if not quiet:
            print(json.dumps(output, indent=2, ensure_ascii=False))
        return output
    except ImportError:
        print("Error: jq library not installed. Run: pip install jq")
        return None
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
