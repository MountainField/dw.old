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
from typing import NamedTuple

import dw
from dw import AutoCloseWrapper, unit_func_constructor

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)

###################################################################
class BytesDataInfo(NamedTuple):
    type = bytes

def rectify(input_iterable, context, *input_files):
    def get_default_iterable():
        if input_iterable is None:
            return sys.stdin.buffer
        else:
            if context.data_info_stack[-1].type in (bytes, "bytes"):
                return input_iterable
            elif dw.DATATYPE2DATATYPE2CONVERTER[context.data_info_stack[-1].type][bytes]:
                converter = dw.DATATYPE2DATATYPE2CONVERTER[context.data_info_stack[-1].type][bytes]
                return converter(input_iterable, context.data_info_stack[-1])
            else:
                raise ValueError()

    bytes_ios = []
    if input_files: # Initialize or reset iterable chain
        for input_file in input_files:
            if input_file == "-":
                bytes_ios.append(get_default_iterable())
            else:
                if os.path.exists(input_file):
                    _LOGGER.info("Opening input_file=='%s' with binary read mode", input_file)
                    bytes_ios.append(io.open(input_file, "rb"))
                else:
                    raise ValueError(f"input_file=='{input_file}' does not exist")                
    else:
        bytes_ios.append(get_default_iterable())
    
    if not context.data_info_stack \
    or context.data_info_stack[-1].type not in (bytes, "bytes"):
        context.data_info_stack.append(BytesDataInfo())

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
