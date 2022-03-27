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
import os
import sys

import dw

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)

def main_io(input_ios: Iterable[io.BytesIO]=None,
         output_io: io.BytesIO=None) -> int:
    if not input_ios: input_ios = [sys.stdin.buffer]
    if not output_io: output_io = sys.stdout.buffer

    for input_io in input_ios:
        for line in input_io:
            output_io.write(line)
    return 0

def main_str(input_files: Iterable[str]=None,
         output_file: str=None) -> int:
    if not input_files: input_files = ["-"]
    if not output_file: output_file = "-"

    input_ios = []
    for input_file in input_files:
        if input_file == "-":
            input_ios.append(sys.stdin.buffer)
        else:
            if not os.path.exists(input_file):
                raise ValueError(f"input_file=='{input_file}' does not exist")
            input_ios.append(io.open(input_file, "rb"))

    if output_file == "-":
        output_io = sys.stdout.buffer
    else:
        if os.path.exists(output_file):
            logging.warning("output_file='%s' will be overwritten.", output_file)
        output_io = io.open(output_file, "wb")
    
    return main_io(input_ios, output_io)

DW_CAT_CLI: dw.ArgparseMonad = dw.cli.argparse_monad("cat", "concat files", sub_command_of=dw.DW_CLI, main_func=main_str) \
                                | dw.cli.add_version_arg(dw.__version__) \
                                | dw.cli.add_log_args() \
                                | dw.cli.add_input_files_args() \
                                | dw.cli.add_output_file_args()

if __name__ == "__main__":
    sys.exit(DW_CAT_CLI.argparse_wrapper.main())
