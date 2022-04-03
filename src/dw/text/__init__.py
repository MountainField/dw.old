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

import argparse
import io
import logging
from multiprocessing.sharedctypes import Value
import os
import sys

import dw
from dw import IterableMonad, unit_func_constructor

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)

###################################################################

def _text_read_iterable(input_file=None,
                        encoding=None, errors=None, newline=None):

    if input_file == "-" or input_file is None:
        if encoding == sys.stdin.encoding:
            _LOGGER.info("Using sys.stdin as input_file with text read mode")
            text_io = sys.stdin
        else:
            _LOGGER.info("Wrapping sys.stdin.buffer as input_file with text read mode")
            text_io = io.TextIOWrapper(sys.stdin.buffer, encoding=encoding, newline=newline, errors=errors)
    elif input_file:
        if not os.path.exists(input_file):
            raise ValueError(f"input_file=='{input_file}' does not exist")
        _LOGGER.info("Opening input_file=='%s' with text read mode", input_file)
        text_io = io.open(input_file, mode="rt", encoding=encoding, newline=newline, errors=errors)
    else:
        raise ValueError()
    try:
        for t in text_io:
            yield t
    finally:
        if text_io != sys.stdin:
            _LOGGER.info("Closing input_file=='%s'", input_file)
            text_io.close()

def read_iterable(*input_files):
    if not input_files:
        input_files = ["-"]
    for input_file in input_files:
        text_io = _text_read_iterable(input_file)
        for b in text_io:
            yield b

###################################################################

# def unit_func(file):
def transform_func(*input_files):
    input_files = [x for x in input_files if x] # reduce None and empty str

    def _deco(transform_func):
        def wrapper(input_iterable, *args, **kwargs):
            # Replace or not replace the input iterable
            if input_files: # Initialize or reset iterable chain 
                input_iterable = read_iterable(*input_files)
            else:
                if input_iterable is None: # Initialize head of iterable chain
                    input_iterable = read_iterable("-")
                else: # Connect new iterable to input_iterable. do not replace it
                    pass
            return IterableMonad(transform_func(input_iterable, *args, **kwargs))
        return wrapper
    return _deco

@unit_func_constructor
def to_file(file=None,
            encoding=None, errors=None, newline=None):
    output_file = file

    def func(input_iterable):
        if output_file == "-" or output_file is None:
            if encoding == sys.stdout.encoding:
                _LOGGER.info("Using sys.stdout as output_file with text write mode")
                text_io = sys.stdout
            else:
                _LOGGER.info("Wrapping sys.stdout.buffer as output_file with text read mode")
                text_io = io.TextIOWrapper(sys.stdout.buffer, encoding=encoding, newline=newline, errors=errors)
        elif output_file:
            if os.path.exists(output_file):
                _LOGGER.warning("Found output_file=='%s' exists. Overwrite it.", output_file)
            _LOGGER.info("Opening output_file=='%s' with text write mode", output_file)
            text_io = io.open(output_file, mode="wt", encoding=encoding, newline=newline, errors=errors)
        else:
            raise ValueError()
        def ite():
            try:
                for t in input_iterable:
                    text_io.write(t)
                    yield t
            finally:
                if text_io != sys.stdout:
                    _LOGGER.info("Closing output_file=='%s'", output_file)
                    text_io.close()
        return IterableMonad(ite())

    return func

def to_stdout():
    return to_file(file="-")


###################################################################

CLI: dw.cli.ArgparseMonad = dw.cli.argparse_monad("text", "Sub command for text file with text encoding.", sub_command_of=dw.CLI, has_sub_command=True) \
                            | dw.cli.add_version_arg(dw.__version__)
###################################################################

from . import cat
# from . import grep
# from . import grep as filter

###################################################################
if __name__ == "__main__":
    sys.exit(CLI.argparse_wrapper.main())
