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

from abc import ABCMeta
import argparse
import io
import logging
import sys

import dw
import textwrap

LOGGER = logging.getLogger("dw")

if sys.version_info[0] >= 3:

    def open_text_reader(input_file, text_encoding=dw.DEFAULT_TEXT_ENCODING, text_errors=dw.DEFAULT_TEXT_ERRORS, text_newline=dw.DEFAULT_TEXT_NEWLINE):
        
        LOGGER.info("Opening input_file: %s, encoding: %s, errors: %s, newline: %s", input_file, text_encoding, text_errors, text_newline)
        if input_file == "-":
            if text_encoding == sys.stdin.encoding:
                text_reader = sys.stdin
            else:
                text_reader = io.TextIOWrapper(sys.stdin.buffer, encoding=text_encoding, newline=text_newline, errors=text_errors)
        else:
            text_reader = io.open(input_file, mode="rt", encoding=text_encoding, newline=text_newline, errors=text_errors)
        return text_reader
    
    def open_text_writer(output_file, text_encoding=dw.DEFAULT_TEXT_ENCODING, text_errors=dw.DEFAULT_TEXT_ERRORS, text_newline=dw.DEFAULT_TEXT_NEWLINE):
        
        LOGGER.info("Opening output_file: %s, encoding: %s, errors: %s, newline: %s", output_file, text_encoding, text_errors, text_newline)
        if output_file == "-":
            if text_encoding == sys.stdout.encoding:
                text_writer = sys.stdout
            else:
                text_writer = io.TextIOWrapper(sys.stdout.buffer, encoding=text_encoding, newline=text_newline, errors=text_errors)
        else:
            text_writer = io.open(output_file, mode="wt", encoding=text_encoding, newline=text_newline, errors=text_errors)
        return text_writer

else:
    
    def open_text_reader(input_file, text_encoding=dw.DEFAULT_TEXT_ENCODING, text_errors=dw.DEFAULT_TEXT_ERRORS, text_newline=dw.DEFAULT_TEXT_NEWLINE):
        
        LOGGER.info("Opening input_file: %s, encoding: %s, errors: %s, newline: %s", input_file, text_errors, text_errors, text_newline)
        if input_file == "-":
            byte_reader = io.BufferedReader(dw.StdIoWrapper(sys.stdin))
            text_reader = io.TextIOWrapper(byte_reader, encoding=text_encoding, newline=text_newline, errors=text_errors)
        else:
            text_reader = io.open(input_file, mode="rt", encoding=text_encoding, newline=text_newline, errors=text_errors)
        return text_reader
    
    def open_text_writer(output_file, text_encoding=dw.DEFAULT_TEXT_ENCODING, text_errors=dw.DEFAULT_TEXT_ERRORS, text_newline=dw.DEFAULT_TEXT_NEWLINE):
        
        LOGGER.info("Opening output_file: %s, encoding: %s, errors: %s, newline: %s", output_file, text_encoding, text_errors, text_newline)
        if output_file == "-":
            byte_writer = dw.StdIoWrapper(sys.stdout)
            text_writer = io.TextIOWrapper(byte_writer, encoding=text_encoding, newline=text_newline, errors=text_errors)

        else:
            text_writer = io.open(output_file, mode="wt", encoding=text_encoding, newline=text_newline, errors=text_errors)
        return text_writer

################################################################################
# Mix-In for Cli


class AbstractHasEncodingArg(object):
    __metaclass__ = ABCMeta
    
    ___epilog_text_encoding_is_added = False

    def __init__(self):
        
        if not self.___epilog_text_encoding_is_added:
            
            self.arg_parser.epilog += textwrap.dedent("""
                Text encoding:
                    The encoding rule to decode from bytes to unicode, and to encode from unicode to bytes.
                    
                    The dw-text command prints supported encoding in your system.
                    $ dw-text --supported-encoding | grep utf
                        utf16
                        utf32
                        utf7
                        utf8
                        ...
        
                    see https://docs.python.org/ja/3/library/codecs.html#module-codecs for more information.
    
                """)
            
            self.___epilog_text_encoding_is_added = True


class HasInputEncodingArg(AbstractHasEncodingArg):
    __metaclass__ = ABCMeta

    def __init__(self):
        AbstractHasEncodingArg.__init__(self)
        
        self.arg_parser.add_argument("--input-encoding", "--encoding", "-e", metavar="ENCODING", nargs=None,
                                     dest="input_text_encoding", default=dw.DEFAULT_TEXT_ENCODING,
                                     help="text encoding for input. [default stdio: '{0}']".format(dw.DEFAULT_TEXT_ENCODING))


class HasOutputEncodingArg(AbstractHasEncodingArg):
    __metaclass__ = ABCMeta

    def __init__(self):
        AbstractHasEncodingArg.__init__(self)
        
        self.arg_parser.add_argument("--output-encoding", "--Encoding", "-E", metavar="ENCODING", nargs=None,
                                     dest="output_text_encoding", default=dw.DEFAULT_TEXT_ENCODING,
                                     help="text encoding for output. [default stdio: '{0}']".format(dw.DEFAULT_TEXT_ENCODING))


class AbstractHasErrorsArg(object):
    __metaclass__ = ABCMeta
    
    ___epilog_text_errors_is_added = False

    def __init__(self):
        
        if not self.___epilog_text_errors_is_added:

            self.arg_parser.epilog += textwrap.dedent("""
                Text encoding error:
                    The option for how the encoding error handled.
                    
                    - strict: raise an exception when unknown character found
                    - ignore: ignore unknown character
                    - replace: replace the unknown character with maker chararcter U+FFFD
                    - xmlcharrefreplace, backslashreplace, namereplace, surrogateescape, surrogatepass, are also available. 
                        See https://docs.python.org/ja/3/library/codecs.html#error-handlers for more information.
    
                """)
            self.___epilog_text_errors_is_added = True


class HasInputErrorsArg(AbstractHasErrorsArg):
    __metaclass__ = ABCMeta

    def __init__(self):
        AbstractHasErrorsArg.__init__(self)
        
        self.arg_parser.add_argument("--input-errors", "--errors", metavar="ERRORS", nargs=None,
                                     dest="input_text_errors", default=dw.DEFAULT_TEXT_ERRORS,
                                     help="error handler of text encoding for input. [default: {0}]".format(dw.DEFAULT_TEXT_ERRORS))


class HasOutputErrorsArg(AbstractHasErrorsArg):
    __metaclass__ = ABCMeta

    def __init__(self):
        AbstractHasErrorsArg.__init__(self)
        
        self.arg_parser.add_argument("--output-errors", "--Errors", metavar="ERRORS", nargs=None,
                                     dest="output_text_errors", default=dw.DEFAULT_TEXT_ERRORS,
                                     help="error handler of text encoding for output. [default: {0}]".format(dw.DEFAULT_TEXT_ERRORS))

################################################################################
# print


def to_text(input_file="-", output_file="-",
           input_text_encoding=dw.DEFAULT_TEXT_ENCODING, input_text_errors=dw.DEFAULT_TEXT_ERRORS,
           output_text_encoding=dw.DEFAULT_TEXT_ENCODING, output_text_errors=dw.DEFAULT_TEXT_ERRORS):

    with dw.text.open_text_writer(output_file, text_encoding=output_text_encoding, text_errors=output_text_errors) as text_writer:
        with dw.text.open_text_reader(input_file, text_encoding=input_text_encoding, text_errors=input_text_errors) as text_reader:
            for text_line in text_reader:
                text_writer.write(text_line)


class ToTextCli(dw.bytes.ToBytes, HasInputEncodingArg, HasInputErrorsArg, HasOutputEncodingArg, HasOutputErrorsArg):
    
    def __init__(self, name="dw-text-to-text", description="dw-text-to-text", *args, **kwargs):
        
        super(ToTextCli, self).__init__(name=name, description=description, *args, **kwargs)
        HasInputEncodingArg.__init__(self)
        HasOutputEncodingArg.__init__(self)
        HasInputErrorsArg.__init__(self)
        HasOutputErrorsArg.__init__(self)
        
    def main(self,
             input_file="-", output_file="-",
             input_text_encoding=dw.DEFAULT_TEXT_ENCODING, input_text_errors=dw.DEFAULT_TEXT_ERRORS,
             output_text_encoding=dw.DEFAULT_TEXT_ENCODING, output_text_errors=dw.DEFAULT_TEXT_ERRORS,
             log_level=dw.DEFAULT_LOG_LEVEL):
        self.set_log_config(log_level=log_level)
        to_text(input_file, output_file,
                input_text_encoding=input_text_encoding, input_text_errors=input_text_errors,
                output_text_encoding=output_text_encoding, output_text_errors=output_text_errors)
        return 0
