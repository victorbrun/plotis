import pytest 
import inspect
import pandas as pd

from plotis import PlotIs
from tests.data.sample_calling_file_linecount import get_last_lineno_of_context_test_func 
from tests.data.sample_calling_file import run_error1, run_error2, run_error3, run_ok1, run_ok2, run_ok3, run_ok4, run_ok5, run_ok6, run_ok7

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
    file_name = inspect.getabsfile(get_last_lineno_of_context_test_func)
    calling_lineno = 26 
    pi = PlotIs("mock", test_df)

    # Calling function to be tested
    line_no = pi._get_last_lineno_of_context(file_name, calling_lineno, include_calling_line=False)

    # Assering result
    assert line_no == 37

def test_get_last_lineno_of_context_2() -> None: 
    # Setting up test data
    test_data = {"x": [1,2,3,4], "y": [4,3,2,1]}
    test_df = pd.DataFrame(data=test_data)
    
    # Seting up test 
    file_name = inspect.getabsfile(get_last_lineno_of_context_test_func)
    calling_lineno = 30 
    pi = PlotIs("mock", test_df)

    # Calling function to be tested
    line_no = pi._get_last_lineno_of_context(file_name, calling_lineno, include_calling_line=False)

    # Assering result
    assert line_no == 35

def test_nested_contexts() -> None:
    """Tests if Exception is raised when trying
    to use PlotIs in nested with contexts.
    """
    with pytest.raises(Exception) as e_info:
        run_error1()

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

def test_multiple_figures_in_context() -> None:
    """Test run with multiple savefig calles in same context.
    """
    with pytest.raises(Exception) as e_info:
        run_error2()
        assert e_info == "Multiple figures are not supported. You cannot have more than one savefig or show calls in context"

    with pytest.raises(Exception) as e_info:
        run_error3()
        assert e_info == "Multiple figures are not supported. You cannot have more than one savefig or show calls in context"

def test_savfig_show_in_context() -> None:
    """Tests that no error is thorwn if we have only one
    plt.show() call or one savefig call.
    """
    try:
        run_ok5()
        run_ok6()
        run_ok7()
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")
