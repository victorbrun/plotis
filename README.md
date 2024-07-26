# PlotIs
PlotIs is a plot isolation tool for python. It saves the data and python code needed to independently reproduce plots using a pythonic interface.

# Installation
```bash
pip install plotis
```

# Example
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

