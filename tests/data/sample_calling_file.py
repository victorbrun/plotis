import pandas as pd
import matplotlib.pyplot as plt

from src.plotis.plotis import PlotIs

mock_fig_folder1 = "mockfig1"
mock_fig_folder2 = "mockfig2"

mock_data = pd.DataFrame(
    data = {
        "x": [1,2,3,4,5],
        "y": [6,7,8,9,10],
        "z": [None, None, None, None, None]
    }
)

def run():
    with PlotIs(mock_fig_folder1, [mock_data]):
        # Does some arbitrary data manipulation
        mock_data["a"] = mock_data["x"] + mock_data["y"]

        with PlotIs(mock_fig_folder2, [mock_data]):
            # adding some whitespace 

            # Does some plotting
            plt.plot(mock_data["a"], mock_data["x"])

        # Does some plotting
        mock_data.plot(x="x", y="y")

if __name__ == "__main__":
    run()
