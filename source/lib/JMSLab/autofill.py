from __future__ import annotations
import inspect
from pathlib import Path
from typing import Any


def AutoFill(
    macros: dict[str, Any] | list[str],
    format: str | None = "{:.2f}",
    outfile: str | Path = "autofill.tex",
    mode: str = "math",
    append: bool = False,
) -> None:
    if isinstance(macros, dict):
        resolved = macros
    elif isinstance(macros, list):
        caller_frame = inspect.currentframe().f_back
        resolved = {}
        for var in macros:
            frame = caller_frame
            while frame is not None and var not in frame.f_locals:
                frame = frame.f_back
            if frame is None:
                raise Exception(f"AutoFill: Variable '{var}' not found")
            resolved[var] = frame.f_locals[var]
    else:
        raise Exception("Argument 'macros' must be a dict or list")

    output = "".join(
        _FormatMacro(name, value, format, mode) for name, value in resolved.items()
    )
    open_mode = "a" if append else "w"
    with open(outfile, open_mode) as f:
        f.write(output)


def _FormatMacro(name: str, value: Any, format: str | None, mode: str) -> str:
    formatted = format.format(value) if format is not None else str(value)
    if mode == "text":
        return f"\\newcommand{{\\{name}}}{{\\textnormal{{{formatted}}}}}\n"
    return f"\\newcommand{{\\{name}}}{{{formatted}}}\n"
