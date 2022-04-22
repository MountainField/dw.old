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
import os
import sys

import dw
from dw import AutoCloseWrapper, unit_func_constructor

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)

###################################################################

def _iterable_to_read_bytes(input_file=None, get_default=None):
    if input_file == "-" or input_file is None:
        _LOGGER.info("Using sys.stdin.buffer as input_file with binary read mode")
        bytes_io = get_default()
    elif os.path.exists(input_file):
        _LOGGER.info("Opening input_file=='%s' with binary read mode", input_file)
        bytes_io = io.open(input_file, "rb")
    else:
        raise ValueError(f"input_file=='{input_file}' does not exist")
    return bytes_io

def iterable_to_read_bytes(*input_files, get_default=None):
    if get_default is None: raise ValueError("default io creater function is required")
    if not input_files:
        input_files = ["-"]
    bytes_ios = [_iterable_to_read_bytes(input_file, get_default) for input_file in input_files]
    return AutoCloseWrapper(*bytes_ios)

###################################################################

@unit_func_constructor(from_datatype=bytes, to_datatype=bytes)
def to_file(file=None):
    output_file = file

    def func(input_iterable, context):
        if output_file == "-" or output_file is None:
            _LOGGER.info("Using sys.stdout.buffer as output_file with binary write mode")
            bytes_io = sys.stdout.buffer
        elif output_file:
            if os.path.exists(output_file):
                _LOGGER.warning("Found output_file=='%s' exists. Overwrite it.", output_file)
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
                    bytes_io.close()
        return ite(), context
    return func

def to_stdout():
    return to_file(file="-")

@unit_func_constructor(from_datatype=bytes, to_datatype=bytes)
def to_bytes():

    def func(input_iterable, context):
        def ite():
            io_object = io.BytesIO()
            try:
                for b in input_iterable:
                    io_object.write(b)
                    yield b
            finally:
                context.output = io_object.getvalue()
                io_object.close()
        return ite(), context

    return func

###################################################################

def argparse_action_for_bytes(dest):

    class BytesAction(argparse.Action):

        def __call__(self, parser, args, str_value, option_string=None):
            bytes_value = str_value.encode('latin1')  # => Just convert from str to bytes
            setattr(args, dest, bytes_value)

    return BytesAction


def argparse_action_for_bytes_list(dest):

    class BytesAction(argparse.Action):

        def __call__(self, parser, args, str_values, option_string=None):
            bytes_values = [str_value.encode('latin1') for str_value in str_values]
            setattr(args, dest, bytes_values)

    return BytesAction


CLI: dw.cli.ArgparseMonad = dw.cli.argparse_monad("bytes", "Sub command for byte file without text encoding.", sub_command_of=dw.CLI, has_sub_command=True) \
                            | dw.cli.add_version_arg(dw.__version__)
###################################################################

from . import cat
from . import grep
from . import grep as filter

###################################################################
if __name__ == "__main__":
    sys.exit(CLI.argparse_wrapper.main())
