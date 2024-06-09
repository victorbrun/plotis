import sys 
import os
import shutil

def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    # Getting absolute path to tests folder, i.e. folder 
    # of this file
    tests_folder_path = "/".join(os.path.abspath(__file__).split("/")[0:-1])

    # Removing the temporary folders created as part of tests 
    shutil.rmtree(tests_folder_path + "/tmp", ignore_errors=True)
    shutil.rmtree(tests_folder_path + "/temp", ignore_errors=True)
