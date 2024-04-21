import pytest 
import inspect

from src.plotis.plotis import PlotIs
from tests.data.sample_calling_file import run

def test_plotis_enter_from_non_with_context() -> None:
    """Tests the behaviour of the `__enter__()` method of the PlotIs class
    called from a non-with context.
    """
    with pytest.raises(Exception):
        pi = PlotIs("mock", [[1,2,3,4], [1,2,3,4,5]])
        pi.__enter__()

def test_get_last_lineno_of_context_1() -> None: 
    # Seting up test 
    file_name = inspect.getabsfile(run)
    calling_lineno = 18 
    pi = PlotIs("mock", [[1,2,3,4], [1,2,3,4,5]])

    # Calling function to be tested
    line_no = pi._get_last_lineno_of_context(file_name, calling_lineno, include_calling_line=False)

    # Assering result
    assert line_no == 30


def test_get_last_lineno_of_context_2() -> None: 
    # Seting up test 
    file_name = inspect.getabsfile(run)
    calling_lineno = 22 
    pi = PlotIs("mock", [[1,2,3,4], [1,2,3,4,5]])

    # Calling function to be tested
    line_no = pi._get_last_lineno_of_context(file_name, calling_lineno, include_calling_line=False)

    # Assering result
    assert line_no == 27

def test_nested_contexts() -> None:
    """Tests if Exception is raised when trying
    to use PlotIs in nested with contexts.
    """
    with pytest.raises(Exception) as e_info:
        run()

        assert e_info == "PlotIs does not support nested `with` contexts using PlotIs"
