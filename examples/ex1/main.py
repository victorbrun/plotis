import pandas as pd
import numpy as np
import math

# Making sure import of PlotIs works correctly
import sys
import os
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-3]))

from src.plotis.plotis import PlotIs

def run() -> None:
    sample_data = generate_data() 

    # Making sure that figure folder is created in the same folder 
    # as this file
    this_folder_abs_path ="/".join(os.path.abspath(__file__).split("/")[0:-1]) 
    figure_folder = this_folder_abs_path + "/sinus_curve"
    
    with PlotIs(figure_folder, sample_data):
        # This needs to be imported in the context
        # to ensure that it is included in generated 
        # run file
        import matplotlib.pyplot as plt 

        # Plots data 
        plt.plot(sample_data["x"], sample_data["y"])
        plt.title("Sinus function")
        plt.xlabel("x")
        plt.ylabel("sin(x)")

        # Saves plot 
        plt.savefig(this_folder_abs_path + "/sinus.png")


def generate_data() -> pd.DataFrame:
    """Generate sample data using sinus function.
    """
    x = np.linspace(0, 4*math.pi)
    y = np.sin(x)

    df = pd.DataFrame(data={"x": x, "y": y})

    return df

if __name__ == "__main__":
    run()

