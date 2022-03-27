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
import itertools
import logging
import os
import sys

from pip import main

import dw

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)

def byte_read_iterable(input_file):
    
    if input_file == "-":
        byte_reader = sys.stdin.buffer
    else:
        if not os.path.exists(input_file):
            raise ValueError(f"input_file=='{input_file}' does not exist")
        _LOGGER.info("Opening input_file=='%s' with binary read mode", input_file)
        byte_reader = io.open(input_file, "rb")
    
    try:
        for b in byte_reader:
            yield b
    finally:
        if byte_reader != sys.stdin.buffer:
            _LOGGER.info("Closing input_file=='%s'", input_file)
            byte_reader.close()

def byte_write_iterable(input_iterable, output_file):
    if output_file == "-":
        output_io = sys.stdout.buffer
    else:
        if os.path.exists(output_file):
            _LOGGER.warning("output_file='%s' will be overwritten.", output_file)
        _LOGGER.info("Opening ouput_file=='%s' with binary write mode", output_file)
        output_io = io.open(output_file, "wb")
    try:
        for b in input_iterable:
            output_io.write(b)
            yield
    finally:
        if output_io != sys.stdout.buffer:
            _LOGGER.info("Closing output_file=='%s'", output_file)
            output_io.close()

def main_str(input_files: Iterable[str]=None,
             output_file: str=None) -> int:
    if not input_files: input_files = ["-"]
    if not output_file: output_file = "-"

    _input_iterables = []
    for input_file in input_files:
        _input_iterables.append(byte_read_iterable(input_file))
    concat_iterable = itertools.chain.from_iterable(_input_iterables)

    main_iterable = byte_write_iterable(concat_iterable, output_file)

    # consume
    for _ in main_iterable:
        pass
    
    return 0

DW_CAT_CLI: dw.ArgparseMonad = dw.cli.argparse_monad("cat", "concat files", sub_command_of=dw.DW_CLI, main_func=main_str) \
                                | dw.cli.add_version_arg(dw.__version__) \
                                | dw.cli.add_log_args() \
                                | dw.cli.add_input_files_args() \
                                | dw.cli.add_output_file_args()

if __name__ == "__main__":
    sys.exit(DW_CAT_CLI.argparse_wrapper.main())
