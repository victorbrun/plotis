"""Example showing a simple use case of PlotIs.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import math

# Making sure import of PlotIs works correctly
import sys
import os
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-3]))

from plotis import PlotIs

def run() -> None:
    sample_data = generate_data() 

    # We want to save the figure to a folder named sinus_curve located
    # at the same place as this file
    this_folder_abs_path ="/".join(os.path.abspath(__file__).split("/")[0:-1]) 
    figure_folder = this_folder_abs_path + "/sinus_curve"
   
    # Performing some plotting on the padnas dataframe just 
    # as usual, but inside the PlotIs context. This will 
    # save sample_data and and the code in the context 
    # such that you can indpendently, i.e. without any 
    # dependency on this file, reproduce the plot
    with PlotIs(figure_folder, sample_data):
        # Plots data 
        sample_data.plot(x="x", y="y")
        plt.title("Sin function")
        plt.xlabel("x")
        plt.ylabel("sin(x)")

        # Shows plot 
        plt.show()

def generate_data() -> pd.DataFrame:
    """Generate sample data using sinus function.
    """
    x = np.linspace(0, 4*math.pi)
    y = np.sin(x)

    df = pd.DataFrame(data={"x": x, "y": y})

    return df

if __name__ == "__main__":
    run()

