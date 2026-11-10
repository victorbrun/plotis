from importlib.metadata import PackageNotFoundError, version

from .plotis import PlotIs, PlotIsError

__all__ = ["PlotIs", "PlotIsError", "__version__"]

try:
    __version__ = version("plotis")
except PackageNotFoundError:  # running from a source checkout
    __version__ = "0.0.0"
