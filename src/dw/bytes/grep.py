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
import re

import dw
from dw import IterableMonad, unit_func_constructor
from dw.bytes import iterable_to_read_bytes, argparse_action_for_bytes_list
from dw.bytes import CLI as DW_BYTES_CLI

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)

###################################################################
@unit_func_constructor
def grep(input_file=None, patterns=None, max_count=None, ignore_case=False):
    if not input_file: input_file = "-"
    if not patterns: patterns = []
    for pattern in patterns:
        if not isinstance(pattern, bytes):
            raise ValueError("pattern must be bytes object")
    regexp_flag: int=0
    if ignore_case:
        regexp_flag = regexp_flag | re.IGNORECASE
    
    def func(input_iterable, context):
        ans = input_iterable
        if input_file: # Initialize or reset iterable chain 
            input_iterable = iterable_to_read_bytes(input_file)
        else:
            if input_iterable is None: # Initialize head of iterable chain
                input_iterable = iterable_to_read_bytes("-")
            else: # Connect new iterable to input_iterable. do not replace it
                pass
        
        # Main
        if patterns:
            regex_patterns = [re.compile(pattern, flags=regexp_flag) for pattern in patterns if pattern]
            def ite():
                count = 0
                for idx, b in enumerate(input_iterable):
                    print_this_line = False
                    for regex_pattern in regex_patterns:
                        if regex_pattern.search(b):
                            print_this_line = True
                            break
                    if print_this_line:
                        count += 1
                        yield b
                    if max_count and count >= max_count:
                        break
            ans = ite()
        
        return IterableMonad(ans, context)
    return func

###################################################################
def main_str(input_file: str=None, output_file: str=None,
            patterns=None, max_count=None, ignore_case=False,
            ) -> int:
    if not input_file: input_file = "-"
    if not output_file: output_file = "-"
    if not patterns: patterns = []

    grep(input_file=input_file, patterns=patterns, max_count=max_count, ignore_case=ignore_case) > dw.bytes.to_file(output_file)
        
    return 0

###################################################################
def add_patterns_args():
    def func(argparse_wrapper):
        argparse_wrapper.arg_parser.add_argument('-e', '--pattern', '--regexp', dest="patterns", metavar="PATTERNS",
                                                nargs="*", default=[],
                                                action=argparse_action_for_bytes_list(dest="patterns"),
                                                help="use PATTERNS for matching")
        return dw.cli.ArgparseMonad(argparse_wrapper)
    return func

def add_max_count_args():
    def func(argparse_wrapper):
        argparse_wrapper.arg_parser.add_argument('-m', '--max-count', dest="max_count", metavar="NUM", nargs=None, default=None, type=int,
                                                 help="stop after NUM selected lines")
        return dw.cli.ArgparseMonad(argparse_wrapper)
    return func

def add_ignore_case_args():
    def func(argparse_wrapper):
        argparse_wrapper.arg_parser.add_argument('-i', '--ignore-case', dest="ignore_case", default=False, action='store_true',
                                                 help="ignore case distinctions in patterns and data")
        return dw.cli.ArgparseMonad(argparse_wrapper)
    return func

CLI: dw.cli.ArgparseMonad = dw.cli.argparse_monad("grep", "print lines that match patterns", aliases=["filter"], sub_command_of=DW_BYTES_CLI, main_func=main_str) \
                                | dw.cli.add_version_arg(dw.__version__) \
                                | dw.cli.add_log_args() \
                                | dw.cli.add_input_file_args() \
                                | dw.cli.add_output_file_args() \
                                | add_patterns_args() \
                                | add_max_count_args() \
                                | add_ignore_case_args()

if __name__ == "__main__":
    import sys

    if True: # Debug
        grep("tmp/abc", patterns=[b"a.+z"]) > dw.bytes.to_stdout()
        
        sys.exit()

    sys.exit(CLI.argparse_wrapper.main())
