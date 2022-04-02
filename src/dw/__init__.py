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

__version__="0.0.21"

from collections.abc import Iterable, Mapping, Callable
import logging
import os
import sys

import yaml

DEFAULT_LOG_FORMAT: str = os.environ.get('DW_LOG_FORMAT', '%(asctime)s | %(threadName)-10s | %(levelname)-7s | %(name)s | %(message)s (%(filename)s L%(lineno)s)')
DEFAULT_LOG_LEVEL: str = os.environ.get('DW_LOG_LEVEL', 'WARNING')
DEFAULT_LOG_OUTPUT: str = os.environ.get('DW_LOG_OUTPUT', 'stdout')

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)

###################################################################

def consume(iterable):
    for _ in iterable:
        pass

class IterableMonad(object):
    
    def __init__(self, value):
        self.value = value
    
    def bind(self, unit_func):
        return unit_func(self.value)
    
    __or__ = bind

    def __iter__(self):
        return self.value
    
    def redirect(self, unit_func):
        m = self.bind(unit_func)
        for event in m:
            pass
        return m.value
    
    __gt__ = redirect

class _HeadOfPipeMaybe(IterableMonad):
    
    def __init__(self, unit_func):
        super().__init__(None)
        self.unit_func = unit_func
    
    def _ensure_iterable(self):
        if self.value is None:
            m = self.unit_func(None)
            self.value = m.value
    
    def bind(self, unit_func):
        self._ensure_iterable()
        return super().bind(unit_func)
    __or__ = bind
    
    def __iter__(self):
        self._ensure_iterable()
        return self.value

    def __call__(self, input_iterable):
        return self.unit_func(input_iterable)

# decorator
def unit_func_constructor(constructor_func):

    def wrapper(*args, **kwargs):
        unit_func = constructor_func(*args, **kwargs)
        m = _HeadOfPipeMaybe(unit_func)
        return m

    return wrapper

###################################################################

from . import cli

CLI: cli.ArgparseMonad = cli.argparse_monad("dw", "data wrangler", has_sub_command=True) \
                            | cli.add_version_arg(__version__)

def main_cli(*args: Iterable[str]) -> int:
    return CLI.argparse_wrapper.main(*args)
###################################################################

# @unit_func_constructor
# def to_list():

#     def func(input_iterable):
#         def ite():
#             sink = []
#             for event in input_iterable:
#                 sink.append(event)
#                 yield event
#         return IterableMonad(ite())

#     return func

###################################################################

from . import bytes
from .bytes import transform_func as transform_func_for_bytes

# from . import text

###################################################################

if __name__ == "__main__":
    sys.exit(main_cli())
