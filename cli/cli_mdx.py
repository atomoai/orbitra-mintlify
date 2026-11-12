"""MDX rendering for the Orbitra CLI command reference.

Given ``CommandDoc`` objects (from the cyclopts tree walk in
``gen_cli_docs.py``), group them by *source* -- the package/plugin providing
each command -- and render one MDX page per source, e.g.::

    orbitra-cli-commons.mdx   # login, logout, account, email, secrets
    orbitra-cli-lake.mdx      # commands mounted by the orbitra-lake plugin
    orbitra-cli-flows.mdx     # commands mounted by the orbitra-flows plugin

The two dataclasses below are the contract with the tree walk.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from pathlib import Path


# Data model (contract with the tree walk)
@dataclass
class ArgDoc:
    """One CLI parameter of a command."""

    py_name: str  # python parameter name, e.g. "body_format"
    cli_names: list[str]  # CLI tokens, e.g. ["--body-format"] / ["NAME"]
    type_str: str  # rendered type, e.g. "str", "list[str]"
    default_repr: str | None  # repr of default, or None when required
    required: bool
    is_positional: bool
    help: str
    example: str = ""  # sample value/fragment; usually mined from the docstring


@dataclass
class CommandDoc:
    """One leaf command (a cyclopts node with a ``default_command``)."""

    path: list[str]  # e.g. ["secrets", "list"]
    help: str
    args: list[ArgDoc] = field(default_factory=list)
    source: str = ""  # who provides the command, e.g. "commons", "lake", "flows"
    example: str = ""  # full sample invocation; usually mined from the docstring


# Filename
def source_filename(source: str) -> str:
    """``orbitra-cli-<source>.mdx`` -- one page per command origin."""
    return f"orbitra-cli-{source}.mdx"


# Escaping
def _esc(text: str) -> str:
    """Escape characters that Mintlify/MDX treats specially in prose."""
    for ch in "<{}:":
        text = text.replace(ch, "\\" + ch)
    return text


def _cell(text: str) -> str:
    """Escape + flatten text for use inside a markdown table cell."""
    return _esc(" ".join(text.split())).replace("|", "\\|")


# Help refinement
# "Sample: --flag ...", "e.g. \"value\"", "e.g. ``orbitra ...``" -- an example
# embedded in docstring prose. The lookahead keeps descriptive uses of "e.g."
# (followed by plain words) untouched.
_EXAMPLE_RE = re.compile(
    r"[,;.]?\s*\b(?:Sample|Example|e\.g\.)\s*[:,]?\s*(?=[-'\"`]|orbitra\b)",
    re.IGNORECASE,
)
_DEFAULT_NOTE_RE = re.compile(r"\s*\(default:\s*[^)]*\)", re.IGNORECASE)
_TRAILING_FLAG_RE = re.compile(r",\s*(--[\w-]+)\s*(\.?)\s*$")


def _split_example(text: str) -> tuple[str, str]:
    """Split an embedded example off a help text: (description, example)."""
    m = _EXAMPLE_RE.search(text)
    if not m:
        return text.strip(), ""
    example = text[m.end():].strip().rstrip(".").strip("`").strip()
    desc = text[: m.start()].rstrip(" ,;")
    if desc and not desc.endswith("."):
        desc += "."
    return desc.strip(), example


def _refine_arg_help(a: ArgDoc) -> ArgDoc:
    """Strip embedded examples, redundant default notes and self-flag mentions."""
    desc, example = _split_example(a.help)
    desc = _DEFAULT_NOTE_RE.sub("", desc)  # the Default column already says it
    m = _TRAILING_FLAG_RE.search(desc)
    if m and m.group(1) in a.cli_names:  # "Body format, --format." -> "Body format."
        desc = desc[: m.start()] + m.group(2)
    return replace(a, help=desc.strip(), example=a.example or example)


def _refine(cmd: CommandDoc) -> CommandDoc:
    """Clean prose for rendering; mined examples feed the Examples section."""
    help_, example = _split_example(cmd.help)
    return replace(
        cmd,
        help=help_,
        example=cmd.example or example,
        args=[_refine_arg_help(a) for a in cmd.args],
    )


# Flag display
def _display_names(a: ArgDoc) -> list[str]:
    """Drop cyclopts' auto-generated companion flags (``--no-<x>`` for booleans,
    ``--empty-<x>`` for lists), keeping only the primary form.

    A companion is dropped only when its base flag (``--x``) is also present --
    the signature of auto-generation -- so a hand-named ``--no-cache`` with no
    ``--cache`` survives, as does a real ``-x`` short alias.
    """
    names = list(a.cli_names)
    bases = {n.lstrip("-") for n in names}
    kept = [
        n
        for n in names
        if not (
            (n.startswith("--no-") and n[5:] in bases)
            or (n.startswith("--empty-") and n[8:] in bases)
        )
    ]
    return kept or names


# Example synthesis
_EMAIL_TOKENS = {"to", "cc", "bcc", "email", "reply", "recipient"}
_FILE_TOKENS = {"file", "path", "attach"}
_ENV_FLAGS = ("--env", "--environment")

# Illustrative sample values for the filled-in second example, keyed by python
# parameter name. A mined docstring example always wins over these; the table
# only fills the gap so the second line reads like a real invocation instead of
# a row of <placeholders>. Values with spaces carry their own shell quotes.
# These are made-up but plausible, not tied to any real resource.
_SAMPLE_VALUES = {
    "scope": "https://graph.microsoft.com/.default",
    "subject": '"Weekly report"',
    "body": '"Hello from Orbitra"',
    "value": "s3cr3t-value",
    "name": "db-password",
    "key_vault": "my-key-vault",
    "namespace": "finance",
    "table": "daily_prices",
    "query": '"SELECT * FROM daily_prices LIMIT 10"',
    "engine": "remote",
    "deployment": "my-flow/prod",
    "run_id": "3f2504e0-4f89-11d3-9a0c-0305e82c3301",
    "select": "close_price",
    "output": "./output.json",
    "input": "./data.parquet",
    "timeout": "600",
    "poll_interval": "10",
    "format": "text",
}


def _placeholder(a: ArgDoc) -> str:
    """A ``<template>`` value for the minimal example: the docstring's own sample
    when available, otherwise an angle-bracket stand-in from the parameter name.
    """
    if a.example and not a.example.startswith(("-", "orbitra")):
        return a.example
    tokens = set(a.py_name.lower().split("_"))
    if tokens & _EMAIL_TOKENS:
        return "user@example.com"
    if tokens & _FILE_TOKENS:
        return "./example.txt"
    return "<" + a.py_name.replace("_", "-") + ">"


def _sample_value(a: ArgDoc) -> str:
    """A realistic value for the filled-in example: the docstring's own sample,
    else a curated one by parameter name/type, else the ``<template>`` fallback.
    """
    if a.example and not a.example.startswith(("-", "orbitra")):
        return a.example
    name = a.py_name.lower()
    if name in _SAMPLE_VALUES:
        return _SAMPLE_VALUES[name]
    tokens = set(name.split("_"))
    if tokens & _EMAIL_TOKENS:
        return "user@example.com"
    if tokens & _FILE_TOKENS:
        return "./example.txt"
    if a.type_str == "int":
        return "100"
    if a.type_str == "float":
        return "10"
    return _placeholder(a)


def _arg_tokens(a: ArgDoc, value_fn: Callable[[ArgDoc], str]) -> list[str]:
    """CLI tokens invoking one argument; ``value_fn`` supplies the sample value."""
    if a.example.startswith("--"):
        return [a.example]  # a ready-made flag fragment mined from the docstring
    if a.is_positional:
        return [value_fn(a)]
    flag = _display_names(a)[0]
    if a.type_str == "bool":
        return [flag]
    return [flag, value_fn(a)]


def _is_env(a: ArgDoc) -> bool:
    return a.cli_names[0] in _ENV_FLAGS


def _examples(cmd: CommandDoc) -> list[str]:
    """Two invocations: a minimal ``<template>`` call, then a filled-in one.

    The second line prefers a full invocation mined from the docstring;
    otherwise it is synthesised from the required call plus every illustrative
    option, with realistic sample values (see ``_sample_value``). ``--env`` is
    only shown when nothing else varies, and at most one boolean flag is added
    so mutually exclusive mode switches (e.g. ``orbitra login``) never collide.
    A command with nothing to vary gets a single example.
    """
    minimal = ["orbitra", *cmd.path]
    for a in cmd.args:
        if a.required:
            minimal += _arg_tokens(a, _placeholder)

    filled = ["orbitra", *cmd.path]
    used_bool = False
    added_optional = False
    for a in cmd.args:
        if _is_env(a) or (a.is_positional and not a.required):
            continue
        if a.type_str == "bool":
            if a.required:
                filled += _arg_tokens(a, _sample_value)
            elif not used_bool:  # one boolean only: avoid clashing mode switches
                filled += _arg_tokens(a, _sample_value)
                used_bool = added_optional = True
            continue
        filled += _arg_tokens(a, _sample_value)
        added_optional = added_optional or not a.required

    if not added_optional:  # nothing varied; fall back to the environment flag
        env = next((a for a in cmd.args if _is_env(a)), None)
        if env is not None:
            filled += [_display_names(env)[0], "dev"]

    all_examples = (cmd.example, *(a.example for a in cmd.args))
    mined = [e for e in all_examples if e.startswith("orbitra")]

    examples = [" ".join(minimal)]
    for candidate in (*mined, " ".join(filled)):
        if candidate not in examples:
            examples.append(candidate)
            break
    return examples


# Rendering
def _default_cell(a: ArgDoc) -> str:
    """The Default column: the repr in a code span, empty when there is none."""
    if a.default_repr is None:
        return ""
    return "`" + a.default_repr.replace("|", "\\|") + "`"


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    """A markdown table wrapped in a ``cli-table`` div so the custom CSS
    (``docs/cli/style.css``) can size columns by position (``th:nth-child``);
    keep the column count/order in sync with that stylesheet.
    """
    lines = ['<div className="cli-table">', ""]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + " --- |" * len(header))
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    lines += ["", "</div>", ""]
    return lines


def _render_command(cmd: CommandDoc) -> list[str]:
    """Render one command as a ``###`` section within a source page."""
    full = " ".join(cmd.path)
    lines = [f"### `orbitra {full}`", ""]

    positionals = [a for a in cmd.args if a.is_positional]
    options = [a for a in cmd.args if not a.is_positional]

    usage = ["orbitra", *cmd.path]
    for a in positionals:
        name = a.cli_names[0]
        usage.append(name if a.required else f"[{name}]")
    if options:
        usage.append("[OPTIONS]")
    lines += ["```bash", " ".join(usage), "```", ""]

    if cmd.help:
        lines += [_esc(cmd.help), ""]

    if positionals:
        lines += ["**Arguments:**", ""]
        lines += _table(
            ["Argument", "Type", "Required", "Description"],
            [
                [
                    f"`{a.cli_names[0]}`",
                    f"`{a.type_str}`",
                    "yes" if a.required else "no",
                    _cell(a.help),
                ]
                for a in positionals
            ],
        )

    if options:
        lines += ["**Options:**", ""]
        lines += _table(
            ["Flag", "Type", "Required", "Default", "Description"],
            [
                [
                    # one flag per line, no commas
                    "<br />".join(f"`{n}`" for n in _display_names(a)),
                    f"`{a.type_str}`",
                    "yes" if a.required else "no",
                    _default_cell(a),
                    _cell(a.help),
                ]
                for a in options
            ],
        )

    lines += ["**Examples:**", ""]
    for example in _examples(cmd):
        lines += ["```bash", example, "```", ""]

    return lines


def render_source_mdx(source: str, commands: list[CommandDoc]) -> str:
    """Render every command of one source as a single MDX document."""
    package = f"orbitra-{source}"
    origin = "package" if source == "commons" else "plugin"
    # commons is the base app (orbitra login/account/...); plugins nest under
    # their own group (orbitra lake ..., orbitra flows ...).
    command = "orbitra" if source == "commons" else f"orbitra {source}"
    lines = [
        "---",
        f"title: {source}",
        f"sidebarTitle: {source}",
        "---",
        "",
        f"# `{command}`",
        "",
        f"Commands provided by the `{package}` {origin}.",
        "",
        "## Commands",
        "",
    ]
    for cmd in sorted(commands, key=lambda c: c.path):
        lines += _render_command(_refine(cmd))
    return "\n".join(lines)


# Writing
def write_source_docs(commands: list[CommandDoc], output_dir: Path) -> list[Path]:
    """Group commands by source and write one ``orbitra-cli-<source>.mdx`` each.

    Commands without a source fall back to "commons". Returns the paths
    written, commons page first, then plugins alphabetically.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    by_source: dict[str, list[CommandDoc]] = {}
    for cmd in commands:
        by_source.setdefault(cmd.source or "commons", []).append(cmd)

    written: list[Path] = []
    for source in sorted(by_source, key=lambda s: (s != "commons", s)):
        out = output_dir / source_filename(source)
        out.write_text(render_source_mdx(source, by_source[source]), encoding="utf-8")
        written.append(out)
    return written
