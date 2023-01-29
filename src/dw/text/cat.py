# -*- coding: utf-8 -*-

# =================================================================
# dw
#
# Copyright (c) 2022 Takahide Nogayama
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
# =================================================================

# https://future-architect.github.io/articles/20201223/
from __future__ import annotations

from collections.abc import Iterable, Mapping, Callable
import io
import logging
import sys

import dw
from dw import AutoCloseWrapper, unit_func_constructor
from dw.text import rectify, add_encoding_args
from dw.text import CLI as DW_TEXT_CLI

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)

###################################################################
@unit_func_constructor(from_datatype=str, to_datatype=str)
def cat(input_files=[],
        encoding=None, errors=None, newline=None,
        add_number=False):
    if not input_files: input_files = ["-"]
    if not encoding: encoding = "UTF-8"
    
    def func(input_iterable, context):
        input_text_iterable = rectify(input_iterable, context, *input_files, encoding=encoding, errors=errors, newline=newline)

        # Main
        ans = input_text_iterable
        if add_number:
            def ite():
                for idx, t in enumerate(input_text_iterable):
                    yield ("%6i\t" % idx) + t
            ans = ite()
        return ans, context
    return func

###################################################################
def main_str(input_files: Iterable[str]=None,
             output_file: str=None,
             add_number: bool=False,
             ) -> int:
    if not input_files: input_files = ["-"]
    if not output_file: output_file = "-"

    cat(input_files=input_files, add_number=add_number) > dw.text.to_file(output_file)
    
    return 0

###################################################################
CLI: dw.ArgparseMonad = dw.cli.argparse_monad("cat", "concat files", sub_command_of=DW_TEXT_CLI, main_func=main_str) \
                                | dw.cli.add_version_arg(dw.__version__) \
                                | dw.cli.add_log_args() \
                                | dw.cli.add_input_files_args() \
                                | dw.cli.add_output_file_args() \
                                | add_encoding_args()

if __name__ == "__main__":
    if True: # Debug
        cat() > dw.text.to_stdout()

        # Iterable[bytes] -> Iterable[text] 
        dw.bytes.cat.cat(["tmp/abc"]) | cat() > dw.text.to_stdout()

        sys.exit(0)
    sys.exit(CLI.argparse_wrapper.main())
