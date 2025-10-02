from IPython.core.magic import (
    Magics,
    magics_class,
    line_magic,
)

__all__ = ["ReqTools", "load_ipython_extension"]

from IPython.terminal.interactiveshell import TerminalInteractiveShell


@magics_class
class ReqTools(Magics):
    @line_magic  # type: ignore[misc]
    def curl(self, params: str = "") -> str:
        cmd = f"curl {params}"
        return cmd


def load_ipython_extension(ipython: TerminalInteractiveShell) -> None:
    ipython.register_magics(ReqTools)  # type: ignore[no-untyped-call]
