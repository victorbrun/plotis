"""Example showing every PlotIs 0.2 option.

Run ``make`` in this folder. It runs this script, which writes two figure
folders (``figures/waves`` and ``figures/bars``), each with ``data.csv``,
``run.py``, the copied style file and the rendered ``figure.pdf``. It then
builds ``main.pdf``. ``make reproduce`` deletes the PDFs, moves the folders
and regenerates them from their ``run.py`` alone.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from plotis import PlotIs  # noqa: E402

HERE = Path(__file__).resolve().parent
STYLE = HERE / "house.mplstyle"


def waves() -> None:
    x = np.linspace(0, 4 * np.pi, 200)
    df = pd.DataFrame({
        "x": np.tile(x, 3),
        "y": np.concatenate([np.sin(x), np.sin(x + 1), np.sin(x + 2)]),
        "series": np.repeat(["phase 0", "phase 1", "phase 2"], len(x)),
    })

    # A multi-line `with` with keyword arguments in any order
    with PlotIs(
        data=df,
        figpath=HERE / "figures" / "waves",
        format="pdf",                            # vector output for LaTeX
        savefig_kwargs={"bbox_inches": "tight"},  # literals only
        style=STYLE,                             # applied here and in run.py
        render=True,                             # writes figure.pdf on exit
    ):
        # Loops and conditionals keep their indentation in run.py
        fig, ax = plt.subplots()
        for name, group in df.groupby("series"):
            if name == "phase 0":
                ax.plot(group["x"], group["y"], label=name, lw=2)
            else:
                ax.plot(group["x"], group["y"], label=name, lw=1, ls="--")
        ax.set_xlabel("x")
        ax.set_ylabel("sin(x + phase)")
        ax.legend(loc="upper right")
        plt.show()  # replaced by `pass` in run.py


def bars() -> None:
    df = pd.DataFrame({"label": ["åäö", "b", "c"], "value": [3, 5, 2]})
    with PlotIs(HERE / "figures" / "bars", df, format="pdf", style=STYLE, render=True):
        fig, ax = plt.subplots(figsize=(3, 2))
        ax.bar(df["label"], df["value"])
        ax.set_title("UTF-8 labels work: åäö")
        plt.savefig(HERE / "figures" / "preview.png")  # replaced by `pass` in run.py


if __name__ == "__main__":
    waves()
    bars()
