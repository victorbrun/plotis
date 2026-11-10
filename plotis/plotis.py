"""Isolate the data and code needed to reproduce a matplotlib figure.

Usage::

    with PlotIs("figures/sine", df, format="pdf", render=True):
        plt.plot(df["x"], df["y"])

On exit, ``figures/sine/`` contains ``data.csv`` (the data frame) and
``run.py`` (the body of the ``with`` block wrapped with the imports, data
loading and ``savefig`` needed to run it on its own). With ``render=True``
the figure itself (``figure.<format>``) is written too.
"""

from __future__ import annotations

import ast
import inspect
import os
import shutil
import sys
import textwrap
from contextlib import AbstractContextManager, ExitStack
from pathlib import Path
from types import TracebackType
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd

__all__ = ["PlotIs", "PlotIsError"]

DATA_FILE = "data.csv"
CODE_FILE = "run.py"
FIGURE_STEM = "figure"
_FIGURE_CALLS = ("savefig", "show")

_WithNode = Union[ast.With, ast.AsyncWith]


class PlotIsError(Exception):
    """Raised when a PlotIs context cannot be isolated."""


class PlotIs(AbstractContextManager):
    """A context manager for isolating, and packaging everything needed to
    independently reproduce a plot.

    The plotting logic placed in this context may only rely on the data
    frame passed as ``data``, ``pandas`` imported as ``pd`` and
    ``matplotlib.pyplot`` imported as ``plt`` (plus anything it imports
    itself). It may only produce a single figure.

    Every ``.show()`` and ``.savefig()`` statement is replaced by ``pass``
    in ``run.py``; ``run.py`` saves the figure itself.

    Parameters
    ----------
    figpath : str or os.PathLike
        Folder in which ``data.csv``, ``run.py`` (and ``figure.<format>``)
        are written. Created if it does not exist.
    data : pandas.DataFrame
        Data used by the plotting logic. Must be passed as a plain variable
        name, since ``run.py`` recreates that variable from ``data.csv``.
        The data is captured as it is when the context is entered.
    format : str
        File format of the saved figure, e.g. ``"png"``, ``"pdf"``, ``"svg"``.
    savefig_kwargs : dict, optional
        Extra keyword arguments for ``plt.savefig`` (e.g. ``{"dpi": 300,
        "bbox_inches": "tight"}``). Values must be Python literals.
    style : str or os.PathLike, optional
        Path to a matplotlib style file. It is applied while the context
        runs, copied into ``figpath`` and applied by ``run.py``.
    render : bool
        If True, the figure is saved to ``figpath/figure.<format>`` when the
        context exits, and then closed.
    """

    def __init__(
        self,
        figpath: str | os.PathLike,
        data: pd.DataFrame,
        format: str = "png",
        savefig_kwargs: dict | None = None,
        style: str | os.PathLike | None = None,
        render: bool = False,
    ) -> None:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas.DataFrame")
        self.figpath = Path(figpath)
        self.data = data
        self.format = format.lstrip(".")
        self.savefig_kwargs = dict(savefig_kwargs or {})
        self.style = Path(style) if style is not None else None
        self.render = render

        self._check_literal(self.savefig_kwargs)
        if self.style is not None and not self.style.is_file():
            raise FileNotFoundError(f"Style file not found: {self.style}")

        # Set in __enter__
        self.calling_filename = ""
        self.data_variable = ""
        self.context_source_lines: list[str] = []
        self._snapshot: pd.DataFrame | None = None
        self._stack = ExitStack()

    # ------------------------------------------------------------------ #
    # Context protocol
    # ------------------------------------------------------------------ #
    def __enter__(self) -> PlotIs:
        frame = sys._getframe(1)
        self.calling_filename = frame.f_code.co_filename
        source = self._read_source(self.calling_filename)
        tree = ast.parse(source, filename=self.calling_filename)

        with_node, call = self._find_with_node(tree, frame.f_lineno)
        self.data_variable = self._data_variable_name(call)
        figure_calls = [c for stmt in with_node.body for c in self._figure_calls(stmt)]
        self._check_body(with_node, figure_calls)
        self.context_source_lines = self._extract_body(source, with_node, figure_calls)

        # Capture the data before the body can mutate it, so that run.py
        # starts from the same state as the context did.
        self._snapshot = self.data.copy()
        if self.style is not None:
            self._stack.enter_context(plt.style.context(str(self.style)))
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        with self._stack:
            if exc_type is not None:
                return  # do not write anything for a failed context

            self.figpath.mkdir(parents=True, exist_ok=True)
            self._snapshot.to_csv(self.figpath / DATA_FILE, index=False)
            if self.style is not None:
                shutil.copyfile(self.style, self.figpath / self.style.name)
            (self.figpath / CODE_FILE).write_text(self.generate_code(), encoding="utf-8")

            if self.render:
                plt.savefig(self.figure_path, **self.savefig_kwargs)
                plt.close()

    # ------------------------------------------------------------------ #
    # Public helpers
    # ------------------------------------------------------------------ #
    @property
    def figure_name(self) -> str:
        return f"{FIGURE_STEM}.{self.format}"

    @property
    def figure_path(self) -> Path:
        return self.figpath / self.figure_name

    def generate_code(self) -> str:
        """Return the source of the standalone ``run.py``."""
        lines = [
            "from pathlib import Path\n",
            "\n",
            "import pandas as pd\n",
            "import matplotlib.pyplot as plt\n",
            "\n",
            "HERE = Path(__file__).resolve().parent\n",
        ]
        if self.style is not None:
            lines.append(f'plt.style.use(HERE / "{self.style.name}")\n')
        lines.append(f'{self.data_variable} = pd.read_csv(HERE / "{DATA_FILE}")\n')
        lines.append("\n")
        lines.extend(self.context_source_lines)
        kwargs = "".join(f", {k}={v!r}" for k, v in self.savefig_kwargs.items())
        lines.append("\n")
        lines.append(f'plt.savefig(HERE / "{self.figure_name}"{kwargs})\n')
        return "".join(lines)

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    @staticmethod
    def _check_literal(kwargs: dict) -> None:
        try:
            if ast.literal_eval(repr(kwargs)) != kwargs:
                raise ValueError
        except (ValueError, SyntaxError):
            raise PlotIsError("savefig_kwargs may only contain Python literals") from None

    @staticmethod
    def _read_source(filename: str) -> str:
        try:
            return Path(filename).read_text(encoding="utf-8")
        except OSError:
            raise PlotIsError(
                f"PlotIs must be used in a source file, could not read {filename!r}"
            ) from None

    @staticmethod
    def _is_plotis_call(node: ast.AST) -> bool:
        if not isinstance(node, ast.Call):
            return False
        func = node.func
        name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
        return name == "PlotIs"

    @classmethod
    def _find_with_node(cls, tree: ast.AST, lineno: int) -> tuple[_WithNode, ast.Call]:
        """Return the innermost ``with`` statement whose header spans
        ``lineno`` and contains a PlotIs call, together with that call."""
        best = None
        for node in ast.walk(tree):
            if not isinstance(node, (ast.With, ast.AsyncWith)):
                continue
            header_end = max(node.body[0].lineno - 1, node.lineno)
            if not node.lineno <= lineno <= header_end:
                continue
            for item in node.items:
                if cls._is_plotis_call(item.context_expr):
                    if best is None or node.lineno >= best[0].lineno:
                        best = (node, item.context_expr)
        if best is None:
            raise PlotIsError("PlotIs must be used as a `with` statement")
        return best

    @staticmethod
    def _data_variable_name(call: ast.Call) -> str:
        """Return the variable name passed as ``data``, resolved against the
        signature of ``PlotIs.__init__`` so positional and keyword use agree."""
        keywords = {kw.arg: kw.value for kw in call.keywords if kw.arg is not None}
        try:
            bound = inspect.signature(PlotIs.__init__).bind_partial(None, *call.args, **keywords)
        except TypeError as exc:
            raise PlotIsError(f"Could not parse the PlotIs arguments: {exc}") from None
        expr = bound.arguments.get("data")
        if not isinstance(expr, ast.Name):
            raise PlotIsError(
                "The data argument of PlotIs must be a plain variable name "
                "so that run.py can recreate it"
            )
        return expr.id

    @staticmethod
    def _figure_calls(node: ast.AST) -> list[ast.Expr]:
        return [
            child for child in ast.walk(node)
            if isinstance(child, ast.Expr)
            and isinstance(child.value, ast.Call)
            and isinstance(child.value.func, ast.Attribute)
            and child.value.func.attr in _FIGURE_CALLS
        ]

    @classmethod
    def _check_body(cls, with_node: _WithNode, figure_calls: list[ast.Expr]) -> None:
        for stmt in with_node.body:
            for child in ast.walk(stmt):
                if isinstance(child, (ast.With, ast.AsyncWith)) and any(
                    cls._is_plotis_call(i.context_expr) for i in child.items
                ):
                    raise PlotIsError(
                        "PlotIs does not support nested `with` contexts using PlotIs"
                    )
        for name in _FIGURE_CALLS:
            if sum(c.value.func.attr == name for c in figure_calls) > 1:
                raise PlotIsError(
                    "Multiple figures are not supported. You cannot have more "
                    "than one savefig or show call in the context"
                )

    @staticmethod
    def _extract_body(source: str, with_node: _WithNode, figure_calls: list[ast.Expr]) -> list[str]:
        """Return the body of ``with_node`` dedented, with every
        ``savefig``/``show`` statement replaced by ``pass``."""
        lines = source.splitlines(keepends=True)
        first_stmt = with_node.body[0]
        start = first_stmt.lineno
        end = with_node.body[-1].end_lineno
        # Keep comment lines directly above the first statement
        while start - 1 > with_node.lineno and lines[start - 2].strip().startswith("#"):
            start -= 1
        body = lines[start - 1:end]

        # One-line `with PlotIs(...): stmt`: drop the header from the line.
        # col_offset counts UTF-8 bytes, hence the encode/decode.
        if first_stmt.lineno == with_node.lineno:
            body[0] = body[0].encode("utf-8")[first_stmt.col_offset:].decode("utf-8")

        for call in sorted(figure_calls, key=lambda c: c.lineno, reverse=True):
            first, last = call.lineno - start, call.end_lineno - start
            indent = body[first][: len(body[first]) - len(body[first].lstrip())]
            body[first:last + 1] = [f"{indent}pass\n"]

        text = textwrap.dedent("".join(body))
        if not text.endswith("\n"):
            text += "\n"
        return text.splitlines(keepends=True)
