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

__version__="0.0.10"

from collections.abc import Iterable, Mapping, Callable
import logging
import os
import sys

import yaml

DEFAULT_LOG_FORMAT: str = os.environ.get('DW_LOG_FORMAT', '%(asctime)s | %(threadName)-10s | %(levelname)-5s | %(name)s | %(message)s (%(filename)s L%(lineno)s)')
DEFAULT_LOG_LEVEL: str = os.environ.get('DW_LOG_LEVEL', 'WARNING')

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)
_LOGGER.setLevel(DEFAULT_LOG_LEVEL)

from . import cli

DW_CLI: cli.ArgparseMonad = cli.argparse_monad("dw", "data wrangler", has_sub_command=True) \
                            | cli.add_version_arg(__version__) \
                            | cli.add_log_args()

def main_cli(*args: Iterable[str]) -> int:
    return DW_CLI.argparse_wrapper.main(*args)

from . import bytes

if __name__ == "__main__":
    sys.exit(main_cli())
