# -*- coding: utf-8 -*-

# =================================================================
# Licensed Materials - Property of IBM
#
# (c) Copyright IBM Corp. 2019, 2019 All Rights Reserved
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
# =================================================================

from __future__ import unicode_literals, print_function, absolute_import

__version__ = "1.0.0"

from abc import ABCMeta, abstractmethod
import argparse
import io
import logging
import numbers
import os
import sys
import unicodedata

import dw

#######################
# Utilities for Unicode, String, Bytes

STRING_TYPES = None
TEXT_TYPES = None
BYTES_TYPES = None
if sys.version_info[0] >= 3:
    STRING_TYPES = (bytes, str)
    TEXT_TYPES = str
    BYTES_TYPES = bytes
else:
    STRING_TYPES = basestring
    TEXT_TYPES = unicode
    BYTES_TYPES = str

NUMBER_TYPES = numbers.Number

DOUBLE_WIDTH_IDs = ['F', 'W', 'A']


def is_number(s):
    if s is None:
        return False
    if isinstance(s, NUMBER_TYPES):
        return True
    try:
        if isinstance(s, TEXT_TYPES) and ',' in s:
            s = s.replace(',', '')
        float(s)
        return True
    except Exception:
        return False


def text_width(text):
    if text is None:
        return 0
    if isinstance(text, BYTES_TYPES):
        text = unicode(text, encoding="UTF-8")
    if text == "":
        return 0
    w = 0
    for c in text:
        if unicodedata.east_asian_width(c) in DOUBLE_WIDTH_IDs:
            w += 2
        else:
            w += 1
    return w


def ensure_text(obj, encoding=None, errors=None):
    if obj is None:
        return None
    elif sys.version_info[0] >= 3:
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, BYTES_TYPES):
            encoding = encoding or DEFAULT_TEXT_ENCODING
            errors = errors or DEFAULT_TEXT_ERRORS
            return obj.decode(encoding, errors)
        elif isinstance(obj, int):
            return str(obj)
    else:
        if isinstance(obj, unicode):
            return obj
        elif isinstance(obj, str):
            encoding = encoding or DEFAULT_TEXT_ENCODING
            errors = errors or DEFAULT_TEXT_ERRORS
            return obj.decode(encoding, errors)
        elif isinstance(obj, int):
            return unicode(obj)
    raise ValueError("The object must be instance of either unicode, str, or bytes")


def ensure_bytes(obj, encoding=None, errors=None):
    if obj is None:
        return None
    elif sys.version_info[0] >= 3:
        if isinstance(obj, BYTES_TYPES):
            return obj
        elif isinstance(obj, str):
            encoding = encoding or DEFAULT_TEXT_ENCODING
            errors = errors or DEFAULT_TEXT_ERRORS
            return obj.encode(encoding, errors)
    else:
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, unicode):
            encoding = encoding or DEFAULT_TEXT_ENCODING
            errors = errors or DEFAULT_TEXT_ERRORS
            return obj.encode(encoding, errors)
    raise ValueError("The object must be instance of either unicode, str, or bytes")

################################################################################
# Constatns


LOGGER = logging.getLogger("dw")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s p%(process)d %(threadName)s %(name)s %(levelname)s %(message)s (%(filename)s L%(lineno)s)'))
LOGGER.addHandler(handler)

CLI_HELP_MAX_POSITION = 90
CLI_HELP_WIDTH = 160

DEFAULT_TEXT_ENCODING = ensure_text(os.environ["CW_TEXT_ENCODING"], encoding="UTF-8", errors="strict") if "CW_TEXT_ENCODING" in os.environ else "UTF-8"
DEFAULT_TEXT_ERRORS = ensure_text(os.environ["CW_TEXT_ERRORS"], errors="strict") if "CW_TEXT_ERRORS" in os.environ else "replace"
DEFAULT_TEXT_NEWLINE = "\n"

DEFAULT_LOG_LEVEL = ensure_text(os.environ["CW_LOG_LEVEL"]) if "CW_LOG_LEVEL" in os.environ else "WARNING"
LOGGER.setLevel(DEFAULT_LOG_LEVEL)

DEFAULT_OUTPUT = "-"
DEFAULT_INPUT = "-"

DEFAULT_CSV_DELIMITER = ensure_text(os.environ["CW_CSV_DELIMITER"]) if "CW_CSV_DELIMITER" in os.environ else ","
DEFAULT_CSV_QUOTECHAR = ensure_text(os.environ["CW_CSV_QUOTECHAR"]) if "CW_CSV_QUOTECHAR" in os.environ else '"'
DEFAULT_CSV_QUOTING = ensure_text(os.environ["CW_CSV_QUOTING"]) if "CW_CSV_QUOTING" in os.environ else 'MINIMAL'


DEFAULT_HIST_CACHE_SIZE = int(os.environ["CW_HIST_CACHE_SIZE"]) if "CW_HIST_CACHE_SIZE" in os.environ else 100

################################################################################
# os
def mkdir_p(path):
    import errno
    LOGGER.debug("Making parent directories: %s", path)
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

################################################################################
# IO utils


class StdIoWrapper(object):
    
    def __init__(self, stdio):
        if stdio is None:
            raise ValueError("The argument reader must not be None.")
        self.stdio = stdio
        self.closed = False
    
    # io.IOBase ##################
    def seekable(self): return False

    def readable(self): return True

    def writable(self): return True

    def close(self):
        self.closed = True
        if self.stdio is sys.stdout or self.stdio is sys.stdin:
            pass
        elif hasattr(self.stdio, 'close'):
            self.stdio.close()
        
    # iterator( __iter__, next (2.x) __next__ (3.x) )
    def __iter__(self):
        return self.stdio.__iter__()

    # with statement
    def __enter__(self, *args):
        self.stdio.__enter__()
        return self

    def __exit__(self, *args):
        if hasattr(self.stdio, 'flush'):
            return self.stdio.flush()
        return self.close()

    # Since io.BufferedReader.__init__ calls raw_checkReadable(), this method is required
    def _checkReadable(self, msg=None): pass
    
    def __getattr__(self, method_name):
        # _LOGGER.debug('MethodMissing: %s, %s', type(self), method_name)
        return getattr(self.stdio, method_name)

################################################################################
# Cli utils


class AbstractArgparseCli(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, name, description,
                 max_help_position=CLI_HELP_MAX_POSITION, help_width=CLI_HELP_WIDTH):
        if not name: raise ValueError("name is Empty")
        if not description: raise ValueError("description is Empty")
        
        formatter = lambda prog: argparse.RawDescriptionHelpFormatter(prog, max_help_position=max_help_position, width=help_width)
        self.arg_parser = argparse.ArgumentParser(prog=name, description=description, formatter_class=formatter)

        if self.arg_parser.epilog is None:
            self.arg_parser.epilog = ""
    
    def parse_argv(self, argv=None):
        
        # Ensure text in case of python 2.x
        if argv is None: argv = [dw.ensure_text(v) for v in sys.argv[1:]]
        
        # parse
        namespace_k2v = self.arg_parser.parse_args(argv)
        
        # convert it to dict
        dict_k2v = vars(namespace_k2v)
        
        # remove key value pairs which are not argumented.
        for key in list(dict_k2v.keys()):
            if key in dict_k2v and dict_k2v.get(key) is None:
                del dict_k2v[key]
        
        return dict_k2v

    @abstractmethod
    def main(self):
        pass
    
    def do(self, argv=None):
        dict_k2v = self.parse_argv(argv)
        return self.main(**dict_k2v)


class HasVersionArg(object):
    __metaclass__ = ABCMeta

    def __init__(self, version):

        class VersionAction(argparse.Action):
    
            def __init__(self, *args, **kwargs):
                kwargs['dest'] = argparse.SUPPRESS
                super(VersionAction, self).__init__(*args, **kwargs)
    
            def __call__(self, parser, namespace, values, option_string=None):
                sys.stdout.write(version)
                sys.stdout.write(os.linesep)
                parser.exit()
    
        self.arg_parser.add_argument('--version', nargs=0, action=VersionAction, help="show program's version number and exit")


class HasLogConfigArg(object):
    __metaclass__ = ABCMeta

    def __init__(self, logger_name):
        logger = logging.getLogger(logger_name)
        default_loglevel = logging.getLevelName(logger.getEffectiveLevel())
        
        self.arg_parser.add_argument('--log-level', '--log_level', dest="log_level", metavar="LEVEL", nargs=None,
                                     default=None,
                                     choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                                     help="set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) to logger '{0}' [default: {1}]".format(logger_name, default_loglevel))

    def set_log_config(self, log_level=dw.DEFAULT_LOG_LEVEL):
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(getattr(logging, log_level.upper()))


class BaseCli(AbstractArgparseCli, HasVersionArg, HasLogConfigArg):
    __metaclass__ = ABCMeta
    
    def __init__(self, name, description,
                       version=dw.__version__, logger_name="dw",
                       *args, **kwargs):
        super(BaseCli, self).__init__(name=name, description=description, *args, **kwargs)
        HasVersionArg.__init__(self, version)
        HasLogConfigArg.__init__(self, logger_name)
        
        self.logger_name = logger_name
    
    def parse_argv(self, argv=None):
        dict_k2v = super(BaseCli, self).parse_argv(argv)
        if dict_k2v.get("log_level"):
            logger = logging.getLogger(self.logger_name)
            logger.setLevel(getattr(logging, dict_k2v.get("log_level").upper()))
        LOGGER.debug("Found dict_k2v: %s", dict_k2v)
        return dict_k2v


from . import bytes
from . import text
from . import csv

