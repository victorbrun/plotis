import pandas as pd
import matplotlib.pyplot as plt

from plotis import PlotIs

output_path = "tests/tmp"
mock_fig_folder1 = output_path + "/mockfig1"
mock_fig_folder2 = output_path + "/mockfig2"

mock_data = pd.DataFrame(
    data = {
        "x": [1,2,3,4,5],
        "y": [6,7,8,9,10],
        "z": [None, None, None, None, None]
    }
)

def run_error1():
    with PlotIs(mock_fig_folder1, mock_data):
        # Does some arbitrary data manipulation
        mock_data["a"] = mock_data["x"] + mock_data["y"]

        with PlotIs(mock_fig_folder2, mock_data):
            # adding some whitespace 

            # Does some plotting
            plt.plot(mock_data["a"], mock_data["x"])

        # Does some plotting
        mock_data.plot(x="x", y="y")

def run_error2():
    """Trying to save to figures in PlotIs context.
    """
    with PlotIs(mock_fig_folder1, mock_data):
        mock_data.plot(x="x", y="y")
        plt.savefig(output_path + "/nice_path1.png")
        plt.savefig(output_path + "/nice_path2.png")

def run_error3():
    """Trying to show multiple figures in PlotIs context.
    """
    with PlotIs(mock_fig_folder1, mock_data):
        mock_data.plot(x="x", y="y")

        # Block set to false so that windows does not 
        # block execution.
        plt.show(block=False)
        plt.show(block=False)


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

def run_ok5():
    """Showing and saving plot in PlotIs context.
    """
    with PlotIs(figpath=mock_fig_folder1, data=mock_data):
        mock_data.plot(x="x", y="y")
        
        # Block set to false so that windows does not 
        # block execution.
        plt.show(block=False)
        plt.savefig(output_path + "/nice_path.png")

def run_ok6():
    """Showing plot in PlotIs context.
    """
    with PlotIs(figpath=mock_fig_folder1, data=mock_data):
        mock_data.plot(x="x", y="y")
        
        # Block set to false so that windows does not 
        # block execution.
        plt.show(block=False)

def run_ok7():
    """Saving plot in PlotIs context
    """
    with PlotIs(figpath=mock_fig_folder1, data=mock_data):
        mock_data.plot(x="x", y="y")
        plt.savefig(output_path + "/nice_path.png")
