
import io
import dw
import sys

if False:
    # with bytes_io:
    #     for _ in bytes_io:
    #         pass
    # io_obj = dw.AutoCloseWrapper(io.open("tests/rsrc/abc", "rb"), io.open("tests/rsrc/abc2", "rb"))
    # for b in io_obj:
    #     sys.stdout.buffer.write(b)

    io_obj = io.TextIOWrapper(
                    dw.AutoCloseWrapper(io.open("tests/rsrc/abc", "rb"), io.open("tests/rsrc/abc2", "rb")), encoding="UTF-8")
    for b in io_obj:
        sys.stdout.write(b)

    
if True:

    ans = dw.bytes.cat.cat(["tmp/abc"]) > dw.to_list()
    print(ans)


