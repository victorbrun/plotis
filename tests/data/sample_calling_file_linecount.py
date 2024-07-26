"""sample_calling_file_linecount.py contains a single function needed to set up the necessary 
environment to test PlotIs._get_last_lineno_of_context().

NOTE: Any changes to this file, which introduces or removes rows, will cause the test of above
mentioned function to fail.
"""

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

def get_last_lineno_of_context_test_func():
    with PlotIs(mock_fig_folder1, mock_data):
        # Does some arbitrary data manipulation
        mock_data["a"] = mock_data["x"] + mock_data["y"]

        with PlotIs(mock_fig_folder2, mock_data):
            # adding some whitespace 

            # Does some plotting
            plt.plot(mock_data["a"], mock_data["x"])

        # Does some plotting
        mock_data.plot(x="x", y="y")
