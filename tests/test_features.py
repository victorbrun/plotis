"""Tests for the 0.2 features: formats, relocatable run.py, indentation,
CSV without index, ast parsing, style, render and failed contexts."""

import os
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from plotis import PlotIs, PlotIsError  # noqa: E402


@pytest.fixture
def df() -> pd.DataFrame:
    return pd.DataFrame({"x": [1, 2, 3, 4], "y": [4, 3, 1, 2], "g": list("aabb")})


def run_script(path: Path, cwd: Path) -> None:
    subprocess.run([sys.executable, str(path)], cwd=cwd, check=True)


def test_pdf_format_and_render(tmp_path, df):
    folder = tmp_path / "fig"
    with PlotIs(folder, df, format="pdf", render=True,
                savefig_kwargs={"bbox_inches": "tight"}):
        plt.plot(df["x"], df["y"])
    assert (folder / "figure.pdf").read_bytes().startswith(b"%PDF")
    code = (folder / "run.py").read_text(encoding="utf-8")
    assert 'plt.savefig(HERE / "figure.pdf", bbox_inches=\'tight\')' in code


def test_no_render_by_default(tmp_path, df):
    folder = tmp_path / "fig"
    with PlotIs(folder, df):
        plt.plot(df["x"], df["y"])
    plt.close("all")
    assert (folder / "run.py").exists()
    assert not (folder / "figure.png").exists()


def test_run_py_is_relocatable(tmp_path, df):
    folder = tmp_path / "fig"
    with PlotIs(folder, df, format="png"):
        plt.plot(df["x"], df["y"])
    plt.close("all")
    moved = tmp_path / "elsewhere" / "copy"
    moved.parent.mkdir()
    folder.rename(moved)
    other_cwd = tmp_path / "cwd"
    other_cwd.mkdir()
    run_script(moved / "run.py", other_cwd)
    assert (moved / "figure.png").exists()


def test_nested_blocks_keep_indentation(tmp_path, df):
    folder = tmp_path / "fig"
    with PlotIs(folder, df, format="png"):
        fig, ax = plt.subplots()
        for name, group in df.groupby("g"):
            if len(group) > 0:
                ax.plot(group["x"], group["y"], label=name)
        ax.legend()
    plt.close("all")
    code = (folder / "run.py").read_text(encoding="utf-8")
    assert "\n    if len(group) > 0:\n        ax.plot(" in code
    run_script(folder / "run.py", tmp_path)
    assert (folder / "figure.png").exists()


def test_csv_has_no_index(tmp_path, df):
    folder = tmp_path / "fig"
    with PlotIs(folder, df):
        plt.plot(df["x"], df["y"])
    plt.close("all")
    assert list(pd.read_csv(folder / "data.csv").columns) == ["x", "y", "g"]


def test_multiline_with_and_keywords(tmp_path, df):
    folder = tmp_path / "fig"
    with PlotIs(
        data=df,
        figpath=folder,
        format="png",
    ):
        plt.plot(df["x"], df["y"])
    plt.close("all")
    code = (folder / "run.py").read_text(encoding="utf-8")
    assert 'df = pd.read_csv(HERE / "data.csv")' in code
    assert "plt.plot(df[\"x\"], df[\"y\"])" in code


def test_data_must_be_a_name(tmp_path, df):
    with pytest.raises(PlotIsError):
        with PlotIs(tmp_path / "fig", df.copy()):
            plt.plot([1], [1])
    plt.close("all")


def test_show_and_savefig_are_replaced(tmp_path, df):
    folder = tmp_path / "fig"
    with PlotIs(folder, df, format="png"):
        plt.plot(df["x"], df["y"])
        plt.savefig(
            tmp_path / "elsewhere.png",
            dpi=50,
        )
    plt.close("all")
    code = (folder / "run.py").read_text(encoding="utf-8")
    assert "elsewhere" not in code
    assert "\npass\n" in code
    run_script(folder / "run.py", tmp_path)


def test_style_is_applied_and_copied(tmp_path, df):
    style = tmp_path / "house.mplstyle"
    style.write_text("lines.linewidth: 7\n", encoding="utf-8")
    folder = tmp_path / "fig"
    with PlotIs(folder, df, style=style):
        (line,) = plt.plot(df["x"], df["y"])
        assert line.get_linewidth() == 7
    plt.close("all")
    assert (folder / "house.mplstyle").exists()
    code = (folder / "run.py").read_text(encoding="utf-8")
    assert 'plt.style.use(HERE / "house.mplstyle")' in code
    # Style is no longer active outside the context
    (line,) = plt.plot([1, 2], [1, 2])
    assert line.get_linewidth() != 7
    plt.close("all")


def test_failed_context_writes_nothing(tmp_path, df):
    folder = tmp_path / "fig"
    with pytest.raises(ZeroDivisionError):
        with PlotIs(folder, df):
            1 / 0
    assert not folder.exists()


def test_non_literal_savefig_kwargs(tmp_path, df):
    with pytest.raises(PlotIsError):
        PlotIs(tmp_path, df, savefig_kwargs={"metadata": object()})


def test_unicode_labels(tmp_path, df):
    folder = tmp_path / "fig"
    with PlotIs(folder, df, format="png"):
        plt.plot(df["x"], df["y"])
        plt.title("Meningslängd – åäö")
    plt.close("all")
    run_script(folder / "run.py", tmp_path)
    assert "åäö" in (folder / "run.py").read_text(encoding="utf-8")


def test_comment_lines_are_kept(tmp_path, df):
    folder = tmp_path / "fig"
    with PlotIs(folder, df):
        # explain the plot
        plt.plot(df["x"], df["y"])  # inline note
    plt.close("all")
    code = (folder / "run.py").read_text(encoding="utf-8")
    assert "# explain the plot" in code
    assert "# inline note" in code
    assert os.path.getsize(folder / "data.csv") > 0
