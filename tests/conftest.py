from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from plotis.plotis import CODE_FILE  # noqa: E402


@pytest.fixture
def df() -> pd.DataFrame:
    return pd.DataFrame({"x": [1, 2, 3, 4], "y": [4, 3, 1, 2], "g": list("aabb")})


@pytest.fixture
def folder(tmp_path: Path) -> Path:
    return tmp_path / "fig"


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


def read_code(folder: Path) -> str:
    return (folder / CODE_FILE).read_text(encoding="utf-8")
