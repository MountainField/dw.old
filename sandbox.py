import logging
logging.getLogger().setLevel("DEBUG")

import dw

# # dw.main() #=> help

dw.main("cat", "x")

# # dw.DW.argparse_wrapper.main("--help")
# # dw.DW_CAT.argparse_wrapper.main("--help")

if True:

    def dw_cat(input_files: Iterable[str], output_file: str) -> int:
        print("hello", input_files, output_file)
        return 0

    DW: cli.ArgparseMonad = cli.argparse_monad("dw", "data wrangler", has_sub_command=True) \
                                | cli.add_version_arg(__version__) \
                                | cli. add_log_args()

    DW_CAT: cli.ArgparseMonad = cli.argparse_monad("cat", "concat files", sub_command_of=DW, main_func=dw_cat) \
                                    | cli.add_version_arg(__version__) \
                                    | cli.add_log_args() \
                                    | cli.add_input_files_args() \
                                    | cli.add_output_file_args()
