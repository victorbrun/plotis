import pytest 
import inspect
import pandas as pd

from src.plotis.plotis import PlotIs
from tests.data.sample_calling_file import run_error, run_ok1, run_ok2, run_ok3, run_ok4

def test_plotis_enter_from_non_with_context() -> None:
    """Tests the behaviour of the `__enter__()` method of the PlotIs class
    called from a non-with context.
    """
    with pytest.raises(Exception):
        test_data = {"x": [1,2,3,4], "y": [4,3,2,1]}
        test_df = pd.DataFrame(data=test_data)
        pi = PlotIs("mock", test_df)
        pi.__enter__()

def test_get_last_lineno_of_context_1() -> None: 
    # Setting up test data
    test_data = {"x": [1,2,3,4], "y": [4,3,2,1]}
    test_df = pd.DataFrame(data=test_data)

    # Seting up test 
    file_name = inspect.getabsfile(run_error)
    calling_lineno = 18 
    pi = PlotIs("mock", test_df)

    # Calling function to be tested
    line_no = pi._get_last_lineno_of_context(file_name, calling_lineno, include_calling_line=False)

    # Assering result
    assert line_no == 30

def test_get_last_lineno_of_context_2() -> None: 
    # Setting up test data
    test_data = {"x": [1,2,3,4], "y": [4,3,2,1]}
    test_df = pd.DataFrame(data=test_data)
    
    # Seting up test 
    file_name = inspect.getabsfile(run_error)
    calling_lineno = 22 
    pi = PlotIs("mock", test_df)

    # Calling function to be tested
    line_no = pi._get_last_lineno_of_context(file_name, calling_lineno, include_calling_line=False)

    # Assering result
    assert line_no == 27

def test_nested_contexts() -> None:
    """Tests if Exception is raised when trying
    to use PlotIs in nested with contexts.
    """
    with pytest.raises(Exception) as e_info:
        run_error()

        assert e_info == "PlotIs does not support nested `with` contexts using PlotIs"

def test_simple_run1() -> None:
    """Tests if run with simple arguments works.
    """
    try:
        run_ok1()
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

def test_simple_run2() -> None:
    """Test run with data argument on the form 'data=xxx.
    """
    try:
        run_ok2()
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

def test_simple_run3() -> None:
    """Test run with argument on the form 'filepath=xxx', 'data=xxx'.
    """
    try:
        run_ok3()
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

def test_simple_run4() -> None:
    """Test run with plotting pyplot used for plotting.
    """
    try:
        run_ok4()
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")
