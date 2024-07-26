# PlotIs
PlotIs is a plot isolation tool for python. It saves the data and python code needed to independently reproduce plots using a pythonic interface.

This project was initiated to address the issue of repository size ballooning in documentation projects where images are frequently updated. Since the most common image formats are not plain text, Git cannot version control them effectively, resulting in the storage of every version of every image. Instead of converting images to a plain text format or pruning the Git history, I chose to overengineer this solution. This solution uses Python context managers to extract the necessary code and data, enabling the independent reproduction of plots.

# Installation
```bash
pip install plotis
```

# Usage
```python
# Import base dependencies
import pandas as pd 
import matplotlib.pyplot as plt

# Imports PlotIs package
import PlotIs 

# Generates sample data
x = np.linspace(0, 4*math.pi)
y = np.sin(x)
df = pd.DataFrame(data={"x": x, "y": y})

# Creates plot inside PlotIs context
with PlotIs(figure_folder, sample_data):
	# Plots data 
	sample_data.plot(x="x", y="y")
	plt.title("Sin function")
	plt.xlabel("x")
	plt.ylabel("sin(x)")

	# Shows plot 
	plt.show()

```

# Limitations

