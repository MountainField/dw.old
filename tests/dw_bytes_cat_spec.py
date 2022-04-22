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

import io
import logging
import os
import sys

from uspec import description, context, it

import dw

_LOGGER = logging.getLogger(__name__)

THIS_DIR=os.path.dirname(os.path.abspath(__file__))
ASCII_FILE = os.path.join(THIS_DIR, "rsrc", "abc.txt")
ASCII_FILE_CONTENT: bytes = io.open(ASCII_FILE, "rb").read()

def execute_command(cmd, shell=False):
    _LOGGER.info("Executing command: %s", cmd)
    
    import subprocess
    p = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding=None)
    stdout, stderr = p.communicate()
    status = p.returncode
    
    return status, stdout, stderr

with description("cmd='dw bytes cat FILE'"):

    for help_option in ["-h", "--help"]:
        with context(help_option):
            @it("returns status 0 and prints help document")
            def _(self):
                status, stdout, stderr = execute_command(["dw", "bytes", "cat", help_option])
                self.assertEqual(status, 0)
                self.assertEqual(stdout, dw.bytes.cat.CLI.argparse_wrapper.arg_parser.format_help().encode("utf-8"))

    with context("--version"):
        @it("returns status 0 and prints version of dw")
        def _(self):
            status, stdout, stderr = execute_command(["dw", "bytes", "cat", "--version"])
            self.assertEqual(status, 0)
            self.assertEqual(stdout, (dw.__version__ + os.linesep).encode("utf-8"))

    with context("a file"):
        @it("returns status 0 and prints a file content")
        def _(self):
            status, stdout, stderr = execute_command(["dw", "bytes", "cat", ASCII_FILE])
            self.assertEqual(status, 0)
            self.assertEqual(stdout, ASCII_FILE_CONTENT)

    with context("files"):
        @it("returns status 0 and prints concatenated file contents")
        def _(self):
            status, stdout, stderr = execute_command(["dw", "bytes", "cat", ASCII_FILE, ASCII_FILE])
            self.assertEqual(status, 0)
            self.assertEqual(stdout, ASCII_FILE_CONTENT + ASCII_FILE_CONTENT)

with description("cmd='cat FILE | dw bytes cat'"):
    
    @it("returns status 0 and prints stdin content")
    def _(self):
        status, stdout, stderr = execute_command(f"cat {ASCII_FILE} | dw bytes cat", shell=True)
        self.assertEqual(status, 0)
        self.assertEqual(stdout, ASCII_FILE_CONTENT)

with description("dw.bytes.cat"):

    with context("a file"):
        @it("loads a file content")
        def _(self):
            bytes_io = io.BytesIO()
            m = dw.bytes.cat.cat([ASCII_FILE])
            for b in m:
                bytes_io.write(b)
            self.assertEqual(bytes_io.getvalue(), ASCII_FILE_CONTENT)

    with context("files"):
        @it("loads file contents")
        def _(self):
            bytes_io = io.BytesIO()
            m = dw.bytes.cat.cat([ASCII_FILE, ASCII_FILE])
            for b in m:
                bytes_io.write(b)
            self.assertEqual(bytes_io.getvalue(), ASCII_FILE_CONTENT + ASCII_FILE_CONTENT)
    
    with context("stdin"):
        @it("loads stdin content")
        def _(self):
            # replace sys.stdin 
            sys.stdin = io.open(ASCII_FILE, "rt")

            bytes_io = io.BytesIO()
            m = dw.bytes.cat.cat()
            for b in m:
                bytes_io.write(b)
            self.assertEqual(bytes_io.getvalue(), ASCII_FILE_CONTENT)

    with context("pipe DSL"):
        @it("loads file content")
        def _(self):
            bytes_io = io.BytesIO()
            m = dw.bytes.cat.cat([ASCII_FILE]) | dw.bytes.cat.cat()
            for b in m:
                bytes_io.write(b)
            self.assertEqual(bytes_io.getvalue(), ASCII_FILE_CONTENT)

    with context("add_number=True"):
        @it("add number")
        def _(self):
            bytes_io = io.BytesIO()
            m = dw.bytes.cat.cat([ASCII_FILE], add_number=True)
            for b in m:
                bytes_io.write(b)
            self.assertEqual(bytes_io.getvalue(), b"     0\tabc\n" +
                                                  b"     1\tdef\n")


if __name__ == "__main__":
    pass
