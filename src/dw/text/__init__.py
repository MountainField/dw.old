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

import dw
from dw import AutoCloseWrapper, unit_func_constructor
from dw.cli import ArgparseMonad

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)

###################################################################

def _iterable_to_read_text(input_file=None, get_default=None, 
                        encoding=None, errors=None, newline=None):
    if input_file == "-" or input_file is None:
        text_io = get_default()
    elif os.path.exists(input_file):
        _LOGGER.info("Opening input_file=='%s' with text read mode", input_file)
        text_io = AutoCloseWrapper(io.open(input_file, mode="rt", encoding=encoding, newline=newline, errors=errors))
    else:
        raise ValueError(f"input_file=='{input_file}' does not exist")
    return text_io

def iterable_to_read_text(*input_files, get_default=None,
                          encoding=None, errors=None, newline=None):
    if not input_files:
        input_files = ["-"]
    text_ios = [_iterable_to_read_text(input_file, get_default, encoding, errors, newline) for input_file in input_files]
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
