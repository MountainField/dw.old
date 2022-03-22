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

import logging
import os
import sys

import yaml

DEFAULT_LOG_FORMAT: str = os.environ.get('DW_LOG_FORMAT', '%(asctime)s | %(threadName)-10s | %(levelname)-5s | %(name)s | %(message)s (%(filename)s L%(lineno)s)')
DEFAULT_LOG_LEVEL: str = os.environ.get('DW_LOG_LEVEL', 'WARNING')

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)
_LOGGER.setLevel(DEFAULT_LOG_LEVEL)

def main(name:str=None) -> int:
    if name is None: name = "defaultvalue"
    _LOGGER.info("hello dw")
    print("hello dw@python", name)
    return 0

def main_cli(*argv: list[str]) -> int:
    if not argv: argv = sys.argv[1:]
    logging.basicConfig(format=DEFAULT_LOG_FORMAT)
    return main(argv[0] if argv else None)
