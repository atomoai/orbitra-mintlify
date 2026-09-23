"""Generate the Orbitra CLI command reference by introspecting the cyclopts app.

This does NOT execute any CLI command. It imports the root cyclopts ``app``,
mounts plugins via ``load_cli_plugins`` (entry-point resolution only, no command
runs), walks the command tree and builds one ``CommandDoc`` per leaf. Rendering
is delegated to ``cli_mdx``; this module owns discovery/extraction.

Usage:
    uv run python docs/cli/gen_cli_docs.py [--output-dir docs] [--print-tree]

``--print-tree`` dumps the discovered tree and writes nothing (a sanity-check
for the introspection before generating files).
"""

from __future__ import annotations

import argparse
import inspect
import sys
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any

import cyclopts
import docstring_parser  # dependency of cyclopts, always available with it

from cli_mdx import ArgDoc, CommandDoc, source_filename, write_source_docs


# cyclopts tree walk
def _children(app: cyclopts.App) -> dict[str, cyclopts.App]:
    """Registered subcommands of ``app`` (``--help``/``--version`` filtered out).
    """
    raw = getattr(app, "_commands", None)
    if raw is None:
        raw = {name: app[name] for name in app}  # App.__iter__ yields names
    return {name: sub for name, sub in dict(raw).items() if not name.startswith("-")}


def walk(app: cyclopts.App, path: list[str]) -> list[CommandDoc]:
    """Depth-first walk collecting every leaf command under ``app``."""
    docs: list[CommandDoc] = []
    children = _children(app)

    # A node is a leaf command when it has a callable default_command.
    default = getattr(app, "default_command", None)
    if callable(default) and path:  # skip the root itself
        summary, param_help = _parse_docstring(default)
        docs.append(
            CommandDoc(
                path=path,
                help=summary or
                str(getattr(app, "help", "") or "").split("\n\n", 1)[0].strip(),
                args=extract_arguments(app, param_help),
                source=_command_source(default),
            )
        )

    for name, sub in children.items():
        docs.extend(walk(sub, path + [name]))
    return docs


def _command_source(fn: Any) -> str:
    """Package that provides the command, from its module: ``orbitra.<pkg>.cli``
    -> "<pkg>"; non-orbitra -> top-level package; unknown -> "commons".

    More reliable than the mount point: it works even if a plugin registers a
    command directly on the root app instead of a sub-app.
    """
    module = inspect.getmodule(fn)
    parts = (getattr(module, "__name__", "") or "").split(".")
    if len(parts) >= 2 and parts[0] == "orbitra":
        return parts[1]
    return parts[0] or "commons"


def _parse_docstring(fn: Any) -> tuple[str, dict[str, str]]:
    """Return (summary, {param_name: help}) from the Google-style docstring.

    The ``Args:`` descriptions become per-flag help, so we don't dump the raw
    docstring (whose ``Args:`` block would duplicate the options table).
    """
    parsed = docstring_parser.parse(inspect.getdoc(fn) or "")
    summary = "\n\n".join(
        part.strip()
        for part in (parsed.short_description, parsed.long_description)
        if part
    )
    param_help = {
        p.arg_name: " ".join((p.description or "").split()) for p in parsed.params
    }
    return summary.strip(), param_help


# Argument extraction
def extract_arguments(app: cyclopts.App, param_help: dict[str, str]) -> list[ArgDoc]:
    """Resolve a leaf command's arguments via cyclopts' own ArgumentCollection.

    ``param_help`` (parsed from the docstring ``Args:`` section) fills in
    descriptions for parameters without an explicit ``Parameter(help=...)``.
    """
    args = _args_from_cyclopts(app)
    for arg in args:
        if not arg.help:
            arg.help = param_help.get(arg.py_name, "")
    return args


def _args_from_cyclopts(app: cyclopts.App) -> list[ArgDoc]:
    collection = app.assemble_argument_collection()  # type: ignore[attr-defined]
    out: list[ArgDoc] = []
    for arg in collection:
        # Core fields are read directly: a cyclopts API change should raise a
        # clear AttributeError here, not silently yield a wrong table.
        names: list[str] = list(arg.names or ())
        field_info = getattr(arg, "field_info", None)
        default = getattr(field_info, "default", inspect.Parameter.empty)
        empty = default is inspect.Parameter.empty
        parameter = getattr(arg, "parameter", None)
        py_name = getattr(field_info, "name", None) or (
            names[0].lstrip("-").replace("-", "_") if names else "?"
        )
        out.append(
            ArgDoc(
                py_name=py_name,
                cli_names=names,
                type_str=_type_str(arg.hint),
                default_repr=None if empty else repr(default),
                required=bool(getattr(arg, "required", empty)),
                is_positional=not any(n.startswith("-") for n in names),
                help=str(getattr(parameter, "help", "") or "").strip(),
            )
        )
    return out


def _type_str(tp: Any) -> str:
    if tp is inspect.Parameter.empty or tp is Any:
        return "Any"
    name = getattr(tp, "__name__", None)
    return name or str(tp).replace("typing.", "")


# Entry point
def load_app() -> cyclopts.App:
    """Import the root app and mount plugins (no command is executed).

    Importing ``orbitra.commons.cli`` already mounts the plugins; we call
    ``load_cli_plugins`` again only when an entry point is not mounted yet, to
    avoid "already registered" warnings.
    """
    from orbitra.commons.cli import app, load_cli_plugins

    mounted = set(_children(app))
    plugins = {ep.name for ep in entry_points(group="orbitra.cli.plugins")}
    if plugins - mounted:
        load_cli_plugins(app)
    return app


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="docs", type=Path)
    parser.add_argument(
        "--print-tree",
        action="store_true",
        help="Dump the discovered tree, write nothing.",
    )
    ns = parser.parse_args(argv[1:])

    app = load_app()
    commands = walk(app, [])

    if ns.print_tree:
        for cmd in sorted(commands, key=lambda c: (c.source, c.path)):
            print(
                f"{source_filename(cmd.source)}  ->  orbitra {' '.join(cmd.path)}"
                f"  ({len(cmd.args)} args)"
            )
            for a in cmd.args:
                req = "required" if a.required else "optional"
                print(f"    {'/'.join(a.cli_names)}  [{a.type_str}, {req}]")
        print(f"\n{len(commands)} commands discovered")
        return 0

    written = write_source_docs(commands, ns.output_dir)
    print(
        f"Wrote {len(written)} source MDX files to {ns.output_dir}: "
        + ", ".join(p.name for p in written)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
