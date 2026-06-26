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
        macro_values = macros
    elif isinstance(macros, list):
        caller_frame = inspect.currentframe().f_back # type: ignore
        macro_values = {}
        for var in macros:
            frame = caller_frame
            found = False
            while frame is not None:
                found, value = _LookupVar(var, frame)
                if found:
                    break
                frame = frame.f_back
            if not found:
                raise Exception(f"AutoFill: Variable '{var}' not found")
            macro_values[var] = value
    else:
        raise Exception("Argument 'macros' must be a dict or list")

    if isinstance(format, list):
        if len(format) != len(macro_values):
            raise Exception("AutoFill: 'format' list length must match number of macros")
        formats = format
    else:
        formats = [format] * len(macro_values)

    output = "".join(
        _FormatMacro(name, value, fmt, mode)
        for (name, value), fmt in zip(macro_values.items(), formats)
    )
    open_mode = "a" if append else "w"
    with open(outfile, open_mode) as f:
        f.write(output)


def _LookupVar(name: str, frame) -> tuple[bool, Any]:
    if name in frame.f_locals:
        return True, frame.f_locals[name]
    if name in frame.f_globals:
        return True, frame.f_globals[name]
    return False, None


def _FormatMacro(name: str, value: Any, format: str | None, mode: str) -> str:
    formatted = format.format(value) if format is not None else str(value)
    if mode == "text":
        return f"\\newcommand{{\\{name}}}{{\\textnormal{{{formatted}}}}}\n"
    return f"\\newcommand{{\\{name}}}{{{formatted}}}\n"
