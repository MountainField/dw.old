import collections
import io
import itertools
import logging
from multiprocessing.sharedctypes import Value
from typing import Iterable
logging.getLogger().setLevel("DEBUG")

import dw

# dw.main() #=> help

# dw.main("cat", "DCO1.1.txt")

# # dw.DW.argparse_wrapper.main("--help")
# # dw.DW_CAT.argparse_wrapper.main("--help")

#print(dw.bytes.cat)

if False:
    # https://docs.python.org/ja/3/library/itertools.html
    import itertools

    citer = itertools.chain.from_iterable([["a", "b", "c"], ["x", "y", "z"]])
    print(list(citer))

    citer2 = itertools.chain(iter(["a", "b", "c"]), iter(["x", "y", "z"]))
    print(list(citer2))

    citer3 = itertools.chain(["a", "b", "c"], ["x", "y", "z"])
    print(list(citer3))

    for i in iter(["a", "b", "c"]):
        print(i)



if True:
    def io_iter():
        byte_reader = io.open("README.md", "rb")
        try:
            for idx, line in enumerate(byte_reader):
                # if idx == 10:
                #     raise ValueError("a")
                yield line
            
        finally:
            print("Closing")
            byte_reader.close()

    print("Iterable", hasattr(io_iter(), '__iter__'))

    concat_iter = itertools.chain.from_iterable([io_iter(), io_iter()])
    for line in concat_iter:
        print(line)
