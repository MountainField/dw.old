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
import logging
import sys

import dw
from dw import IterableMonad, unit_func_constructor
from dw.bytes import iterable_to_read_bytes
from dw.bytes import CLI as DW_BYTES_CLI

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)

###################################################################
@unit_func_constructor
def cat(input_files=None,
        add_number=False):
    if not input_files: input_files = ["-"]
    
    def func(input_iterable, context):
        if input_iterable is None:
            get_default = lambda: sys.stdin.buffer
        else:
            get_default = lambda: input_iterable
        
        if input_files: # Initialize or reset iterable chain 
            input_iterable = iterable_to_read_bytes(*input_files, get_default=get_default)
        else:
            # Connect new iterable to input_iterable. do not replace it
            pass
        
        # Main
        ans = input_iterable
        if add_number:
            def ite():
                for idx, b in enumerate(input_iterable):
                    yield (b"%6i\t" % idx) + b
            ans= ite()
        
        context.datatype = bytes
        return IterableMonad(ans, context)
    return func

###################################################################
def main_str(input_files: Iterable[str]=None, output_file: str=None,
             add_number: bool=False) -> int:
    if not input_files: input_files = ["-"]
    if not output_file: output_file = "-"
    cat(input_files=input_files, add_number=add_number) > dw.bytes.to_file(output_file)
    return 0

###################################################################
CLI: dw.ArgparseMonad = dw.cli.argparse_monad("cat", "concat files", sub_command_of=DW_BYTES_CLI, main_func=main_str) \
                                | dw.cli.add_version_arg(dw.__version__) \
                                | dw.cli.add_log_args() \
                                | dw.cli.add_input_files_args() \
                                | dw.cli.add_output_file_args()

if __name__ == "__main__":
    if False: # Debug
        cat(["tmp/abc"]) > dw.bytes.to_stdout()
        sys.exit()
    sys.exit(CLI.argparse_wrapper.main())
