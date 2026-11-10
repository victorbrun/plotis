"""Tests for PlotIs: output files, run.py generation and validation."""

import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from plotis import PlotIs, PlotIsError
from tests.conftest import read_code


def run_script(path: Path, cwd: Path) -> None:
    subprocess.run([sys.executable, str(path)], cwd=cwd, check=True)


# --------------------------------------------------------------------------- #
# Output files
# --------------------------------------------------------------------------- #
def test_pdf_format_and_render(folder, df):
    with PlotIs(folder, df, format="pdf", render=True,
                savefig_kwargs={"bbox_inches": "tight"}):
        plt.plot(df["x"], df["y"])
    assert (folder / "figure.pdf").read_bytes().startswith(b"%PDF")
    assert 'plt.savefig(HERE / "figure.pdf", bbox_inches=\'tight\')' in read_code(folder)


def test_format_leading_dot_is_stripped(folder, df):
    with PlotIs(folder, df, format=".pdf"):
        plt.plot(df["x"], df["y"])
    assert 'HERE / "figure.pdf"' in read_code(folder)


def test_no_render_by_default(folder, df):
    with PlotIs(folder, df):
        plt.plot(df["x"], df["y"])
    assert (folder / "run.py").exists()
    assert not (folder / "figure.png").exists()


def test_csv_has_no_index(folder, df):
    with PlotIs(folder, df):
        plt.plot(df["x"], df["y"])
    assert list(pd.read_csv(folder / "data.csv").columns) == ["x", "y", "g"]


def test_data_is_captured_on_enter(tmp_path, folder, df):
    with PlotIs(folder, df):
        df["y"] = df["y"] * 2
        plt.plot(df["x"], df["y"])
    assert pd.read_csv(folder / "data.csv")["y"].tolist() == [4, 3, 1, 2]
    run_script(folder / "run.py", tmp_path)


def test_failed_context_writes_nothing(folder, df):
    with pytest.raises(ZeroDivisionError):
        with PlotIs(folder, df):
            1 / 0
    assert not folder.exists()


# --------------------------------------------------------------------------- #
# run.py generation
# --------------------------------------------------------------------------- #
def test_run_py_is_relocatable(tmp_path, folder, df):
    with PlotIs(folder, df, format="png"):
        plt.plot(df["x"], df["y"])
    moved = tmp_path / "elsewhere" / "copy"
    moved.parent.mkdir()
    folder.rename(moved)
    other_cwd = tmp_path / "cwd"
    other_cwd.mkdir()
    run_script(moved / "run.py", other_cwd)
    assert (moved / "figure.png").exists()


def test_nested_blocks_keep_indentation(tmp_path, folder, df):
    with PlotIs(folder, df, format="png"):
        fig, ax = plt.subplots()
        for name, group in df.groupby("g"):
            if len(group) > 0:
                ax.plot(group["x"], group["y"], label=name)
        ax.legend()
    assert "\n    if len(group) > 0:\n        ax.plot(" in read_code(folder)
    run_script(folder / "run.py", tmp_path)
    assert (folder / "figure.png").exists()


def test_one_line_with(tmp_path, folder, df):
    with PlotIs(folder, df): plt.plot(df["x"], df["y"])  # noqa: E701
    code = read_code(folder)
    assert "PlotIs" not in code
    assert 'plt.plot(df["x"], df["y"])' in code
    run_script(folder / "run.py", tmp_path)


def test_multiline_with_and_keywords(folder, df):
    with PlotIs(
        data=df,
        figpath=folder,
        format="png",
    ):
        plt.plot(df["x"], df["y"])
    code = read_code(folder)
    assert 'df = pd.read_csv(HERE / "data.csv")' in code
    assert 'plt.plot(df["x"], df["y"])' in code


def test_show_and_savefig_are_replaced(tmp_path, folder, df):
    with PlotIs(folder, df, format="png"):
        plt.plot(df["x"], df["y"])
        plt.savefig(
            tmp_path / "elsewhere.png",
            dpi=50,
        )
    code = read_code(folder)
    assert "elsewhere" not in code
    assert "\npass\n" in code
    run_script(folder / "run.py", tmp_path)


@pytest.mark.parametrize("call", ["savefig", "show"])
def test_single_savefig_or_show_is_allowed(tmp_path, folder, df, call):
    with PlotIs(folder, df):
        plt.plot(df["x"], df["y"])
        if call == "savefig":
            plt.savefig(tmp_path / "out.png")
        else:
            plt.show(block=False)
    assert (folder / "run.py").exists()


def test_style_is_applied_and_copied(tmp_path, folder, df):
    style = tmp_path / "house.mplstyle"
    style.write_text("lines.linewidth: 7\n", encoding="utf-8")
    with PlotIs(folder, df, style=style):
        (line,) = plt.plot(df["x"], df["y"])
        assert line.get_linewidth() == 7
    assert (folder / "house.mplstyle").exists()
    assert 'plt.style.use(HERE / "house.mplstyle")' in read_code(folder)
    # Style is no longer active outside the context
    (line,) = plt.plot([1, 2], [1, 2])
    assert line.get_linewidth() != 7


def test_unicode_labels(tmp_path, folder, df):
    with PlotIs(folder, df, format="png"):
        plt.plot(df["x"], df["y"])
        plt.title("Meningslängd – åäö")
    run_script(folder / "run.py", tmp_path)
    assert "åäö" in read_code(folder)


def test_comment_lines_are_kept(folder, df):
    with PlotIs(folder, df):
        # explain the plot
        plt.plot(df["x"], df["y"])  # inline note
    code = read_code(folder)
    assert "# explain the plot" in code
    assert "# inline note" in code


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def test_must_be_used_with_with(folder, df):
    with pytest.raises(PlotIsError, match="`with` statement"):
        PlotIs(folder, df).__enter__()


def test_data_must_be_a_name(folder, df):
    with pytest.raises(PlotIsError, match="plain variable name"):
        with PlotIs(folder, df.copy()):
            plt.plot([1], [1])


def test_data_must_be_a_dataframe(folder):
    with pytest.raises(TypeError, match="DataFrame"):
        PlotIs(folder, {"x": [1]})


def test_missing_style_file(tmp_path, folder, df):
    with pytest.raises(FileNotFoundError):
        PlotIs(folder, df, style=tmp_path / "missing.mplstyle")


def test_non_literal_savefig_kwargs(folder, df):
    with pytest.raises(PlotIsError, match="literals"):
        PlotIs(folder, df, savefig_kwargs={"metadata": object()})


def test_nested_plotis_is_rejected(tmp_path, folder, df):
    with pytest.raises(PlotIsError, match="nested"):
        with PlotIs(folder, df):
            with PlotIs(tmp_path / "inner", df):
                plt.plot(df["x"], df["y"])
    assert not folder.exists()


def test_multiple_savefig_is_rejected(tmp_path, folder, df):
    with pytest.raises(PlotIsError, match="Multiple figures"):
        with PlotIs(folder, df):
            plt.plot(df["x"], df["y"])
            plt.savefig(tmp_path / "a.png")
            plt.savefig(tmp_path / "b.png")


def test_multiple_show_is_rejected(folder, df):
    with pytest.raises(PlotIsError, match="Multiple figures"):
        with PlotIs(folder, df):
            plt.plot(df["x"], df["y"])
            plt.show(block=False)
            plt.show(block=False)
