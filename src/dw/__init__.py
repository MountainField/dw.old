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

__version__="0.0.28"

from collections import defaultdict
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
class AutoCloseWrapper:
    def __init__(self, *io_objects):
        if not io_objects:
            raise ValueError("io_objects is empty")
        # for io_object in io_objects:
        #     if not getattr(io_object, "close", None):
        #         raise ValueError("io_object must have close method")
        
        self.io_objects = io_objects
        self.current_io_object=self.io_objects[0]

    def __iter__(self):
        for io_object in self.io_objects:
            self.current_io_object = io_object
            try:
                for event in self.current_io_object:
                    yield event
            finally:
                if getattr(io_object, "close", None):
                    self.current_io_object.close()
    
    # method missing
    def __getattr__(self, name):
        # print("called attr=", name)
        return getattr(self.current_io_object, name)

###################################################################
class PipelineContext:
    def __init__(self):
        self.data_info_stack=[]
        self.output: any=None
    
    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
        
    def __repr__(self):
        kws = [f"{key}={value!r}" for key, value in self.__dict__.items()]
        return "{}({})".format(type(self).__name__, ", ".join(kws))

###################################################################

def consume(iterable):
    for _ in iterable:
        pass

class IterableMonad(object):
    
    def __init__(self, value, context: PipelineContext=PipelineContext()):
        self.value = value
        self.context = context
    
    def bind(self, unit_func):
        return unit_func(self.value, self.context)
    
    __or__ = bind
    then = bind

    def __iter__(self):
        # return self.value
        return iter(self.value)
    
    def redirect(self, unit_func):
        m = self.bind(unit_func)
        for event in m:
            pass
        return m.context.output
    
    __gt__ = redirect

class HeadOfPipeIterableMonad(IterableMonad):
    
    def __init__(self, unit_func):
        super().__init__(None)
        self.unit_func = unit_func
    
    def _ensure_iterable(self):
        if self.value is None:
            m = self.unit_func(None, self.context)
            self.value = m.value
            self.context = m.context
    
    def bind(self, unit_func):
        self._ensure_iterable()
        return super().bind(unit_func)
    __or__ = bind
    
    def __iter__(self):
        self._ensure_iterable()
        return super().__iter__()

    def __call__(self, input_iterable, context):
        return self.unit_func(input_iterable, context)

def _unit_functionalization(unit_func):
    def f(*args, **kwargs):
        ans, context = unit_func(*args, **kwargs)
        return IterableMonad(ans, context)
    return f

# decorator
def unit_func_constructor(from_datatype=None, to_datatype=None):
    def f(constructor_func):
        def _unit_func_constructor_wrapper(*args, **kwargs):
            unit_func = constructor_func(*args, **kwargs)
            unit_func = _unit_functionalization(unit_func)
            m = HeadOfPipeIterableMonad(unit_func)
            return m
        return _unit_func_constructor_wrapper
    return f

DATATYPE2DATATYPE2CONVERTER = defaultdict(dict)

###################################################################
from . import cli

CLI: cli.ArgparseMonad = cli.argparse_monad("dw", "data wrangler", has_sub_command=True) \
                            | cli.add_version_arg(__version__)

def main_cli(*args: Iterable[str]) -> int:
    return CLI.argparse_wrapper.main(*args)

###################################################################


@unit_func_constructor(from_datatype=any)
def to_list():

    def func(input_iterable, context):
        context.output = []
        def ite():
            for b in input_iterable:
                context.output.append(b)
                yield b
        return ite(), context
    return func

###################################################################

from . import bytes
from . import text

###################################################################

if __name__ == "__main__":
    sys.exit(main_cli())
