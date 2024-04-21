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

    def __init__(self, figpath: str, data: List[pd.DataFrame]) -> None:
        self.figpath = figpath
        self.data = data

        # Information about the calling file
        self.calling_filename = "" 
        self.calling_line_start = -1 
        self.calling_line_end = -1
        self.context_source_lines = []

    def __enter__(self) -> Any:
        calling_frame = inspect.stack()[1]
        
        # Ensuring we have calling code context
        if calling_frame.code_context is None:
            raise Exception("Could not find code context")
        calling_context = calling_frame.code_context[0]
        
        # Ensuring that this function is called 
        # as part of a with statement
        regex_str = r"(\s{1,}|)with PlotIs[(](\s|\S|){1,}[)] as \S{1,}:[\n]|(\s{1,}|)with PlotIs[(](\s|\S|){1,}[)]:[\n]" 
        with_context_pattern = re.compile(regex_str)
        if with_context_pattern.fullmatch(calling_context) is None :
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
        for ix, dataset in enumerate(self.data):
            filepath = self.figpath + f"/data{ix}.csv"
            with open(filepath, "w+") as fp:
                dataset.to_csv(fp)

        # Writing context source to file 
        abs_file_path = self.figpath + "/run.py" 
        with open(abs_file_path, "w+") as fp:
            fp.writelines(self.context_source_lines)
        

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


