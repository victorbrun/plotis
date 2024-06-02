# Standard lib imports
import os
import inspect
import re

# Dependencies imports
import pandas as pd

# Specified imports
from contextlib import AbstractContextManager
from typing import Any, List
from types import TracebackType

class PlotIs(AbstractContextManager):
    """A context manager for isolating, and packaging everything
    needed to independently reproduce plots.
    """

    def __init__(self, figpath: str, data: pd.DataFrame) -> None:
        self.figpath = figpath
        self.data = data

        # Information about the calling file
        self.calling_filename = "" 
        self.calling_context_line_start = -1  # This is set to calling line + 1
        self.calling_line_end = -1
        self.constructing_line = "" # Line of code conaining the constructor call
        self.context_source_lines = []

    def __enter__(self) -> Any:
        calling_frame = inspect.stack()[1]
        
        # Ensuring we have calling code context
        if calling_frame.code_context is None:
            raise Exception("Could not find code context")
        self.constructing_line = calling_frame.code_context[0]
       
        # Ensuring that this function is called 
        # as part of a with statement
        regex_str = r"(\s{1,}|)with PlotIs[(](\s|\S|){1,}[)] as \S{1,}:[\n]|(\s{1,}|)with PlotIs[(](\s|\S|){1,}[)]:[\n]" 
        with_context_pattern = re.compile(regex_str)
        if with_context_pattern.fullmatch(self.constructing_line) is None :
            raise Exception(f"PlotIs must be called by `with`: {calling_frame.code_context[0]}")
       
        # Parsing calling frame to set up attributes
        self.calling_filename = calling_frame.filename
        self.calling_context_line_start = calling_frame.lineno + 1 # Exclude calling line
        self.calling_context_line_end = self._get_last_lineno_of_context(
            self.calling_filename,
            self.calling_context_line_start,
            include_calling_line=False
        )

        # Extacting source lines
        with open(self.calling_filename, "r") as fp:
            # Colleting the source lines of our context.
            # Note that code lines start counting at 1 while 
            # list index starts at 0.
            lbnd_inclusive = self.calling_context_line_start - 1 
            ubnd_exclusive = self.calling_context_line_end
            lines = fp.readlines()[lbnd_inclusive:ubnd_exclusive]

            # Strips indentation and store lines in attribute 
            self.context_source_lines = [line.lstrip() for line in lines]

        # Ensuring that there are no nested with contexts using PlotIs 
        line_match_list = [with_context_pattern.match(line) is not None for line in self.context_source_lines]
        if True in line_match_list:
            raise Exception("PlotIs does not support nested `with` contexts using PlotIs")

    def __exit__(
        self, 
        __exc_type: type[BaseException] | None, 
        __exc_value: BaseException | None, 
        __traceback: TracebackType | None
    ) -> bool | None:
        calling_frame = inspect.stack()[1]
        self.calling_line_end = calling_frame.lineno


        # Creates the folder in which to write the data and code
        if not os.path.exists(self.figpath):
            os.makedirs(self.figpath)

        # Writing data to figpath
        filepath = self.figpath + f"/data.csv"
        with open(filepath, "w+") as fp:
            self.data.to_csv(fp)

        # Writing concatinating data load code with 
        # context source and writing it to file
        abs_file_path = self.figpath + "/run.py" 
        print(abs_file_path)
        with open(abs_file_path, "w+") as fp:
            code_to_write = self._get_data_load_code() + self.context_source_lines
            fp.writelines(code_to_write)
        

    def _get_last_lineno_of_context(
        self,
        calling_filename: str,
        calling_line_no: int,
        include_calling_line: bool = False
    ) -> int:
        """Returns the last line number of the calling context specified in 
        `calling_frame`.
        """
        with open(calling_filename, "r") as fp:
            lines = fp.readlines()

        # Initiates the returning variable as the base case 
        last_lineno_context = len(lines)

        # Specifies the line to start analysing our context from.
        # The number is dependent on if we want to include the calling 
        # line. The reason for this is that in a for caluse, or with 
        # clause, the calling line has a different indentation than 
        # the context we are trying to analyse.
        starting_line_no = None 
        if include_calling_line is True:
            starting_line_no = calling_line_no
        else:
            starting_line_no = calling_line_no + 1

        # Iterate over each line of code in starting at calling frame 
        # (or one line after it) until indentation becomes less than 
        # the initial one, i.e. stepping out of the context.
        context_indent_base = None
        for lineno in range(starting_line_no, len(lines)+1):
            line = lines[lineno-1]
            current_indent = self._get_indentation(line)

            # For the first iteration we save the number 
            # of indentation defining the calling context 
            if lineno == starting_line_no:
                context_indent_base = current_indent
                continue

            # The first time at which the number of 
            # indentations are less than the context base 
            # defines beginning of the next context.
            #
            # Note: that we do not consider a new line. If we do not do this 
            # code in same context but separated by new line will be 
            # incorrecly excluded.
            any_white_space = re.compile(r"\s")
            if current_indent < context_indent_base and not any_white_space.fullmatch(line):
                # When current indent is less than base indent 
                # for the first time we are at first line in next
                # context. Therefore we subtract one to get last 
                # line in context we are analysing 
                last_lineno_context = lineno - 1
                break

        return last_lineno_context

    @staticmethod
    def _get_indentation(line: str) -> int:
        """Gets the number of indentation charachters used in `line`.

        Parameters
        ----------
        line : str 
            Code line for which to get the number of indentations.

        Returns
        -------
        int
            Number of whitespace characters used for indentation in `line`.
        """
        leading_spaces = len(line) - len(line.lstrip())
        return leading_spaces


    def _get_data_load_code(self) -> List[str]:
        """Returns the strings of code needed to load the data, which is saved in 
        data.csv, into a variable of the same name as was supplied to the data argument
        in the PlotIs constructor.

        Returns
        -------
        List[str]
            List of strings. Each entry is one line of pyhton code.
        """
        # Checking if the contructor call is using PlotIs(data=xxx, xxx)
        # or PlotIs(some_file_path, some_pd_df)
        variable_name = ""
        regex_str = r"data=[\S\s]+"
        data_pattern_match = re.search(regex_str, self.constructing_line)
        if data_pattern_match is not None:
            # Extracts the name of the variable storing the data
            variable_name = self.constructing_line.split("data=")[1].strip()
            variable_name = variable_name.replace(")", "").replace(":", "")
            variable_name = variable_name.strip()
        else:
            # Extracts the name of the variable storgin the data 
            variable_name = self.constructing_line.split(",")[1].strip()
            variable_name = variable_name.replace(")", "").replace(":", "")
            variable_name = variable_name.strip()

        # Ensuring that something was catpured by above logic
        if variable_name == "":
            raise ValueError("Something went wrong. Could not parse varable name containing data")

        # Constructing line of code to load data from data.csv into variable 
        data_load_code = [
            "import pandas as pd\n", 
            f"{variable_name} = pd.read_csv(\"data.csv\")\n\n"
        ]

        return data_load_code
