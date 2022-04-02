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

import io
import logging
import os
import sys

from dw import IterableMonad, unit_func_constructor

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)


def _byte_read_iterable(input_file=None):
    if input_file == "-" or input_file is None:
        bytes_io = sys.stdin.buffer
    elif input_file:
        if not os.path.exists(input_file):
            raise ValueError(f"input_file=='{input_file}' does not exist")
        _LOGGER.info("Opening input_file=='%s' with binary read mode", input_file)
        bytes_io = io.open(input_file, "rb")
    else:
        raise ValueError()
    try:
        for b in bytes_io:
            yield b
    finally:
        if bytes_io != sys.stdin.buffer:
            _LOGGER.info("Closing input_file=='%s'", input_file)
            bytes_io.close

def read_iterable(*input_files):
    if not input_files:
        input_files = ["-"]
    for input_file in input_files:
        bytes_io = _byte_read_iterable(input_file)
        for b in bytes_io:
            yield b

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
def to_file(file=None):
    output_file = file

    def func(input_iterable):
        if output_file == "-" or output_file is None:
            bytes_io = sys.stdout.buffer
        elif output_file:
            if os.path.exists(output_file):
                raise ValueError(f"output_file=='{output_file}' exists")
            _LOGGER.info("Opening output_file=='%s' with binary write mode", output_file)
            bytes_io = io.open(output_file, "wb")
        else:
            raise ValueError()
        def ite():
            try:
                for b in input_iterable:
                    bytes_io.write(b)
                    yield b
            finally:
                if bytes_io != sys.stdout.buffer:
                    _LOGGER.info("Closing output_file=='%s'", output_file)
                    bytes_io.close
        return IterableMonad(ite())

    return func

def to_stdout():
    return to_file(file="-")

from . import cat
