from __future__ import annotations
import inspect
from pathlib import Path
from typing import Any, Literal


def AutoFill(
    macros: dict[str, Any] | list[str],
    outfile: str | Path,
    format: str | list[str | None] | None = None,
    append: bool = False,
    mode: Literal["math", "text"] = "math",
) -> None:
    if isinstance(macros, dict):
        resolved = macros
    elif isinstance(macros, list):
        caller_frame = inspect.currentframe().f_back # type: ignore
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

    if isinstance(format, list):
        if len(format) != len(resolved):
            raise Exception("AutoFill: 'format' list length must match number of macros")
        formats = format
    else:
        formats = [format] * len(resolved)

    output = "".join(
        _FormatMacro(name, value, fmt, mode)
        for (name, value), fmt in zip(resolved.items(), formats)
    )
    open_mode = "a" if append else "w"
    with open(outfile, open_mode) as f:
        f.write(output)


def _FormatMacro(name: str, value: Any, format: str | None, mode: str) -> str:
    formatted = format.format(value) if format is not None else str(value)
    if mode == "text":
        return f"\\newcommand{{\\{name}}}{{\\textnormal{{{formatted}}}}}\n"
    return f"\\newcommand{{\\{name}}}{{{formatted}}}\n"
