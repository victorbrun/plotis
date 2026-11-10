"""Example showing a simple use case of PlotIs.

Run ``make`` in this folder. It runs this script, which writes
``sinus_curve/data.csv`` and ``sinus_curve/run.py``, then regenerates the
figure from ``run.py`` alone and builds ``main.pdf``.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from plotis import PlotIs  # noqa: E402

# The figure folder is placed next to this file, whatever the working directory
FIGURE_FOLDER = Path(__file__).resolve().parent / "sinus_curve"


def generate_data() -> pd.DataFrame:
    """Generate sample data using the sine function."""
    x = np.linspace(0, 4 * np.pi)
    return pd.DataFrame({"x": x, "y": np.sin(x)})


def run() -> None:
    sample_data = generate_data()

    # Plot the data frame as usual, but inside the PlotIs context. This saves
    # sample_data and the code in the context, so that the plot can be
    # reproduced without any dependency on this file.
    with PlotIs(FIGURE_FOLDER, sample_data):
        sample_data.plot(x="x", y="y")
        plt.title("Sine function")
        plt.xlabel("x")
        plt.ylabel("sin(x)")

        # Replaced by `pass` in run.py
        plt.show()


if __name__ == "__main__":
    run()
