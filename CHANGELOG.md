# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [0.2.0]

### Added
- `format`, `savefig_kwargs`, `style` and `render` arguments to `PlotIs`.
- `PlotIsError`, raised when a context cannot be isolated.
- `plotis.__version__`.
- `examples/ex2`: every option, a LaTeX document and a `make reproduce` target.

### Changed
- The `with` statement is located by parsing the calling file with `ast`
  instead of regexes and line counting. Multi-line `with` statements,
  keyword arguments in any order, one-line bodies and nested blocks work.
- `run.py` resolves `data.csv`, the style file and the figure relative to
  itself, so the folder can be moved and run from any working directory.
- The data is captured when the context is entered, so changes the body makes
  to the data frame are not saved to `data.csv` (and applied twice by `run.py`).
- `savefig()`/`show()` statements are replaced by `pass` in `run.py`.
- `data.csv` is written without the index column.
- Nothing is written if the context raises an exception.
- `numpy` is no longer a runtime dependency.

### Breaking
- Errors are raised as `PlotIsError` (or `TypeError`/`FileNotFoundError` for
  invalid arguments) instead of a generic `Exception`.
- `data` must be passed as a plain variable name.
- `data.csv` has no index column: read it with `pd.read_csv(path)` and
  without `index_col=0`.
- `run.py` saves `figure.<format>` next to itself. In 0.1 the path was
  `<figpath>/figure.png` relative to the working directory, so `run.py`
  only worked when run from the same directory as the original script.

## [0.1.9]
- Last release of the regex-based implementation.
