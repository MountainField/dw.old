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
from dw import unit_func_constructor
from dw.bytes import rectify
from dw.bytes import CLI as DW_BYTES_CLI

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)


###################################################################
@unit_func_constructor(from_datatype=bytes, to_datatype=bytes)
def cat(input_files=[],
        add_number=False):
    
    def func(input_iterable, context):
        input_bytes_iterable = rectify(input_iterable, context, *input_files)

        # Main
        ans = input_bytes_iterable
        if add_number:
            def ite():
                for idx, b in enumerate(input_bytes_iterable):
                    yield (b"%6i\t" % idx) + b
            ans= ite()
        
        return ans, context

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
    if True: # Debug
        cat(["tmp/abc"]) > dw.bytes.to_stdout()
        sys.exit()
    sys.exit(CLI.argparse_wrapper.main())
