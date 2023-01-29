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
import codecs
import io
import logging
import os
import sys
from typing import NamedTuple

import dw
from dw import AutoCloseWrapper, unit_func_constructor
from dw.cli import ArgparseMonad

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)

###################################################################
class StrDataInfo(NamedTuple):
    type :type    = str
    encoding: str = None
    errors: str   = None
    newline:str   = None


def text2bytes_generator(input_iterable, encoding=None, errors=None, newline=None):
    if errors is None: errors = "replace" # TODO:
    for t in input_iterable:
        yield t.encode(encoding=encoding, errors=errors)

def _text2bytes_generator(input_iterable, datainfo):
    return text2bytes_generator(input_iterable, datainfo.encoding, datainfo.errors, datainfo.newline)

dw.DATATYPE2DATATYPE2CONVERTER[str][bytes] = _text2bytes_generator

###################################################################
def rectify(input_iterable, context, *input_files,
         encoding="utf-8", errors=None, newline=None):
    def get_default_iterable():
        if input_iterable is None:
            if codecs.lookup(encoding) == codecs.lookup(sys.stdin.encoding): # TODO normalize
                return sys.stdin
            else:
                raise ValueError(f"{encoding} != {sys.stdin.encoding}")
        else:
            if context.data_info_stack[-1].type in (str, "str", "text"):
                return input_iterable
            elif context.data_info_stack[-1].type in (bytes, "bytes"):
                _LOGGER.info("Insert bytes to text converter")
                return io.TextIOWrapper(input_iterable, encoding=encoding, newline=newline, errors=errors)
            else:
                raise ValueError()

    text_ios = []
    if input_files: # Initialize or reset iterable chain
        for input_file in input_files:
            if input_file == "-":
                text_ios.append(get_default_iterable())
            else:
                if os.path.exists(input_file):
                    _LOGGER.info("Opening input_file=='%s' with text read mode and encoding=='%s'", input_file, encoding)
                    text_ios.append(io.open(input_file, "rt", encoding=encoding, newline=newline, errors=errors))
                else:
                    raise ValueError(f"input_file=='{input_file}' does not exist")                
    else:
        text_ios.append(get_default_iterable())
    
    if not context.data_info_stack \
    or context.data_info_stack[-1].type not in (str, "str", "text"):
        context.data_info_stack.append(StrDataInfo(str, encoding, errors, newline))

    return AutoCloseWrapper(*text_ios)

###################################################################

@unit_func_constructor(from_datatype=str, to_datatype=str)
def text2bytes(encoding=None,
        errors=None,
        newline=None):
    if not encoding: encoding = "UTF-8"
    
    def func(input_iterable, context):
        if input_iterable is None:
            raise ValueError()
        
        # Main
        ans = input_iterable
        def ite():
            for t in input_iterable:
                b = t.encode(encoding=encoding)
                yield b
        ans = ite()
        return ans, context
    return func

@unit_func_constructor(from_datatype=str, to_datatype="file")
def to_file(file=None,
            encoding=None, errors=None, newline=None):
    output_file = file

    def func(input_iterable, context):
        if output_file == "-" or output_file is None:
            if encoding and codecs.lookup(encoding) == codecs.lookup(sys.stdout.encoding):
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
        return ite(), context

    return func

@unit_func_constructor(from_datatype=str, to_datatype="file")
def to_stdout():
    return to_file(file="-")

@unit_func_constructor(from_datatype=str, to_datatype=str)
def to_str():

    def func(input_iterable, context):
        def ite():
            io_object = io.StringIO()
            try:
                for t in input_iterable:
                    io_object.write(t)
                    yield t
            finally:
                context.output = io_object.getvalue()
                io_object.close()
        return ite(), context

    return func

###################################################################
def add_encoding_args():
    def func(argparse_wrapper):
        argparse_wrapper.arg_parser.add_argument("--encoding", metavar="ENCODING", nargs=None, default=None, dest="encoding",
                                                 help=f"decode and decode using the specified encoding[default stdio: '{sys.stdin.encoding}', file: 'utf-8']")
        return ArgparseMonad(argparse_wrapper)
    return func

        
        # self.arg_parser.add_argument("--encoding-errors", metavar="HANDLER", nargs=None, default=None, dest="encoding_errors",
        #                              help="error handler for character encoding. {strict|ignore|replace|xmlcharrefreplace|backslashreplace}"
        #                              +" [default: {0}]".format(dw.CONFIG["text"]["errors"])
        #                              +" See also https://docs.python.org/3/library/codecs.html#codec-base-classes")

CLI: dw.cli.ArgparseMonad = dw.cli.argparse_monad("text", "Sub command for text file with text encoding.", sub_command_of=dw.CLI, has_sub_command=True) \
                            | dw.cli.add_version_arg(dw.__version__)
###################################################################

from . import cat
# from . import grep
# from . import grep as filter

###################################################################
if __name__ == "__main__":
    sys.exit(CLI.argparse_wrapper.main())
