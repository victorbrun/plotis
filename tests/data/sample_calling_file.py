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

def run_error():
    with PlotIs(mock_fig_folder1, mock_data):
        # Does some arbitrary data manipulation
        mock_data["a"] = mock_data["x"] + mock_data["y"]

        with PlotIs(mock_fig_folder2, mock_data):
            # adding some whitespace 

            # Does some plotting
            plt.plot(mock_data["a"], mock_data["x"])

        # Does some plotting
        mock_data.plot(x="x", y="y")

def run_ok1():
    with PlotIs(mock_fig_folder1, mock_data):
        # Does some arbitrary data manipulation
        mock_data["a"] = mock_data["x"] + mock_data["y"]

        # Does some plotting
        mock_data.plot(x="x", y="y")

def run_ok2():
    with PlotIs(mock_fig_folder1, data=mock_data):
        # Does some arbitrary data manipulation
        mock_data["a"] = mock_data["x"] + mock_data["y"]

        # Does some plotting
        mock_data.plot(x="x", y="y")

def run_ok3():
    with PlotIs(figpath=mock_fig_folder1, data=mock_data):
        # Does some arbitrary data manipulation
        mock_data["a"] = mock_data["x"] + mock_data["y"]

        # Does some plotting
        mock_data.plot(x="x", y="y")

def run_ok4():
    with PlotIs(figpath=mock_fig_folder1, data=mock_data):
        import matplotlib.pyplot as plt

        #Does some arbitrary data manipulation
        mock_data["a"] = mock_data["x"] + mock_data["y"]

        # Does some plotting
        plt.plot(mock_data["a"], mock_data["y"])
