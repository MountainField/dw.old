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
from tabnanny import verbose

from uspec import description, context, it

import dw

_LOGGER = logging.getLogger(__name__)

THIS_DIR=os.path.dirname(os.path.abspath(__file__))
ASCII_FILE = os.path.join(THIS_DIR, "rsrc", "abc.txt")
ASCII_FILE_CONTENT: bytes = io.open(ASCII_FILE, "rb").read()

with description("dw.AutoCloseWrapper"):

    with context("one io object"):
        @it("loads content and closes the io object")
        def _(self):
            io_obj = io.open(ASCII_FILE, "rb")
            auto_close_wrapper = dw.AutoCloseWrapper(io_obj)
            
            bytes_io = io.BytesIO()
            for e in auto_close_wrapper:
                bytes_io.write(e)
            
            self.assertEqual(io_obj.closed, True)
            self.assertEqual(bytes_io.getvalue(), ASCII_FILE_CONTENT)

    with context("two io objects"):
        @it("concatenates content and closes the io objects")
        def _(self):
            io_obj1 = io.open(ASCII_FILE, "rb")
            io_obj2 = io.open(ASCII_FILE, "rb")
            auto_close_wrapper = dw.AutoCloseWrapper(io_obj1, io_obj2)
            
            bytes_io = io.BytesIO()
            for e in auto_close_wrapper:
                bytes_io.write(e)
            
            self.assertEqual(io_obj1.closed, True)
            self.assertEqual(io_obj2.closed, True)
            self.assertEqual(bytes_io.getvalue(), ASCII_FILE_CONTENT + ASCII_FILE_CONTENT)

    with context("list"):
        @it("loads content ")
        def _(self):
            m = dw.AutoCloseWrapper(["a", "b", "c"])
            ans = [e for e in m]
            self.assertEqual(ans, ["a", "b", "c"])

with description("dw.IterableMonad"):

    @it("wraps list iterable")
    def _(self):
        m = dw.IterableMonad(["a", "b", "c"])
        ans = [e for e in m]
        self.assertEqual(ans, ["a", "b", "c"])

if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)

