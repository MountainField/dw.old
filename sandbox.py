import logging
logging.getLogger().setLevel("DEBUG")

import dw

# dw.main() #=> help

dw.main("cat", "DCO1.1.txt")

# # dw.DW.argparse_wrapper.main("--help")
# # dw.DW_CAT.argparse_wrapper.main("--help")

#print(dw.bytes.cat)
