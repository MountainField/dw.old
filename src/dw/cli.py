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

from abc import ABCMeta, abstractmethod
import argparse

from collections.abc import Iterable, Mapping, Callable
import logging
import os
import sys

import inspect as _inspect

import dw

argcomplete=None
# import argcomplete

_LOGGER: logging.Logger = logging.getLogger(__name__)

class ArgparseWrapper:
    def __init__(self, arg_parser, sub_parsers_action=None, main_func: Callable=None):
        self.arg_parser = arg_parser
        self.sub_parsers_action = sub_parsers_action
        
        arg_parser.set_defaults(post_funcs=[])
        arg_parser.set_defaults(main_func=main_func)


    def main(self, *args: Iterable[str]):
        if not args: args = sys.argv[1:]

        arg2value = vars(self.arg_parser.parse_args(args))

        post_funcs = arg2value.pop("post_funcs")
        for f in post_funcs:
            arg2value_shrink = {k: arg2value[k] for k in _inspect.signature(f).parameters.keys() if k in arg2value}
            f(**arg2value_shrink)
        
        _LOGGER.debug("Found arg2value=='%s'", arg2value)
        
        main_func = arg2value.pop("main_func")
        arg2value_shrink = {k: arg2value[k] for k in _inspect.signature(main_func).parameters.keys() if k in arg2value}
        return main_func(**arg2value_shrink)

class ArgparseMonad(metaclass=ABCMeta):
    
    def __init__(self, argparse_wrapper):
        self.argparse_wrapper = argparse_wrapper
    
    def bind(self, a_to_m_b):
        return a_to_m_b(self.argparse_wrapper)
    
    __or__ = bind
    
    def __eq__(self, other):
        return self is other or isinstance(other, ArgparseMonad) and other.argparse_wrapper == self.argparse_wrapper
        
# class Just(ArgparseMonad):
#     pass

# class Nothing(ArgparseMonad):
#     def __repr__(self):
#         return 'Nothing'
# NOTHING = Nothing(None)

def argparse_monad(prog: str, description: str, aliases=[],
                   main_func: Callable=None,
                   has_sub_command: bool=False, sub_command_of: ArgparseMonad=None,
                   max_help_position: int=90, help_width: int=160):

    if sub_command_of is None:
        arg_parser = argparse.ArgumentParser(
            prog=prog, description=description,
            formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(prog, max_help_position=max_help_position, width=help_width))
    else:
        arg_parser = sub_command_of.argparse_wrapper.sub_parsers_action.add_parser(
            name=prog, help=description, aliases=aliases,
            formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(prog, max_help_position=max_help_position, width=help_width))
    
    sub_parsers_action=None
    if has_sub_command:
        sub_parsers_action = arg_parser.add_subparsers(help="sub commands")

    if main_func is None:
        def _(*args, **kwargs) -> int:
            arg_parser.print_help()
            return 0
        main_func = _

    return ArgparseMonad(ArgparseWrapper(arg_parser, sub_parsers_action, main_func))

def add_version_arg(version: str):

    class VersionAction(argparse.Action):

        def __init__(self, *args, **kwargs):
            kwargs['dest'] = argparse.SUPPRESS
            super().__init__(*args, **kwargs)

        def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values, option_string=None):
            sys.stdout.write(version)
            sys.stdout.write(os.linesep)
            parser.exit()

    def func(argparse_wrapper):
        argparse_wrapper.arg_parser.add_argument('--version', nargs=0, action=VersionAction, help="show program's version number and exit")
        return ArgparseMonad(argparse_wrapper)
    return func


def configure_logging(log_levels=[], **kwargs):
    if len(logging.getLogger().handlers) > 0:
        pass
    else:
        logging.basicConfig(format=dw.DEFAULT_LOG_FORMAT, level="INFO")

    for log_level in log_levels:
        if "=" not in log_level:
            logging.getLogger().info("Setting log level %s to root logger", log_level)
            logging.getLogger().setLevel(log_level)
        else: #=> modulename=loglevel e.g., json=INFO
            module_name, level = log_level.split("=", 1)
            logging.getLogger().info("Setting log level %s to logger %s", level, module_name)
            logging.getLogger(module_name).setLevel(level)
            

def add_log_args():

    def func(argparse_wrapper):

        
        _acceptable_levels = list(logging._nameToLevel.keys())
        _acceptable_levels.remove("NOTSET")

        argparse_wrapper.arg_parser.add_argument('--log-level', dest="log_levels", metavar="[NAME=]LEVEL", nargs="*", default=[],
                                help=f"set log level for a loggger with NAME. Acceptable levels are {_acceptable_levels}")
        
        # argparse_wrapper.post_funcs.append(configure_logging)
        post_funcs = argparse_wrapper.arg_parser.get_default("post_funcs")
        post_funcs.append(configure_logging)

        return ArgparseMonad(argparse_wrapper)

    return func

def add_input_file_args():
    def func(argparse_wrapper):
        argparse_wrapper.arg_parser.add_argument(dest="input_file", metavar="FILE", nargs='?', default=None,
                                                 help="input file or - [default: stdin]")
        return ArgparseMonad(argparse_wrapper)
    return func

def add_input_files_args():
    def func(argparse_wrapper):
        argparse_wrapper.arg_parser.add_argument(dest="input_files", metavar="FILE", nargs='*', default=[ "-" ],
                                                 help="input file or - [default: stdin]")
        return ArgparseMonad(argparse_wrapper)
    return func

def add_output_file_args():
    def func(argparse_wrapper):
        argparse_wrapper.arg_parser.add_argument("-o", "--output", dest="output_file", metavar="FILE", nargs=None, default=None,
                                                 help="output file or - [default: stdout]")
        return ArgparseMonad(argparse_wrapper)
    return func
