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

import sys

import yaml

def main(name=None) -> int:
    if name is None: name = "defaultvalue"
    print("hello dw@python", name)
    return 0

def main_cli(*argv: list[str]) -> int:
    if not argv: argv = sys.argv[1:]
    return main(argv[0] if argv else None)
