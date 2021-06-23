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

import cw

LOGGER = logging.getLogger("cw")

################################################################################
# IO

if sys.version_info[0] >= 3:

    def open_bytes_reader(input_file):
        LOGGER.info("Opening input_file: %s", input_file)
        if input_file == "-":
            bytes_reader = sys.stdin.buffer
        else:
            bytes_reader = io.open(input_file, "rb")
        return bytes_reader
    
    def open_bytes_writer(output_file):
        LOGGER.info("Opening output_file: %s", output_file)
        if output_file == "-":
            bytes_writer = sys.stdout.buffer
        else:
            bytes_writer = io.open(output_file, "wb")
        return bytes_writer

else:

    def open_bytes_reader(input_file):
        LOGGER.info("Opening input_file: %s", input_file)
        if input_file == "-":
            bytes_reader = cw.StdIoWrapper(sys.stdin)
        else:
            bytes_reader = io.open(input_file, "rb")
        return bytes_reader
    
    def open_bytes_writer(output_file):
        LOGGER.info("Opening output_file: %s", output_file)
        if output_file == "-":
            bytes_writer = cw.StdIoWrapper(sys.stdout)
        else:
            bytes_writer = io.open(output_file, "wb")
        return bytes_writer

################################################################################
# Mix-In for Cli


class HasBytesInputArg(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.arg_parser.add_argument(dest="input_file", metavar="FILE", nargs='?', default="-",
                                     help="input file or - [default: stdin]")


class HasBytesInputsArg(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.arg_parser.add_argument(dest="input_files", metavar="FILE", nargs='*', default=[ "-" ],
                                     help="input file or - [default: stdin]")


class HasBytesOutputArg(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.arg_parser.add_argument("--output", "-o", dest="output_file", metavar="FILE", nargs=None, default="-",
                                     help="output file or - [default: stdout]")

################################################################################
# print


def print_(input_file="-", output_file="-"):
    with cw.bytes.open_bytes_reader(input_file) as bytes_reader:
        with cw.bytes.open_bytes_writer(output_file) as bytes_writer:
            for bytes_line in bytes_reader:
                bytes_writer.write(bytes_line)


class ToBytes(cw.BaseCli, HasBytesInputArg, HasBytesOutputArg):
    
    def __init__(self, name="cw-bytes-to-bytes", description="cw-bytes-to-bytes", *args, **kwargs):
        super(ToBytes, self).__init__(name=name, description=description, *args, **kwargs)
        HasBytesInputArg.__init__(self)
        HasBytesOutputArg.__init__(self)
        
    def main(self, input_file="-", output_file="-",
                   log_level=cw.DEFAULT_LOG_LEVEL):
        self.set_log_config(log_level=log_level)
        print_(input_file, output_file)
        return 0
