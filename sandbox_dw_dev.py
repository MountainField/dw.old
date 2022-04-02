import dw

if False:
    m = dw.bytes.cat.cat("tmp/abc", add_number=True) 
    print("\n cat tmp/abc")
    for line in m:
        print(line)

if False:
    print("\n cat tmp/abc")
    dw.consume(
        dw.bytes.cat.cat("tmp/abc", add_number=True) | dw.bytes.to_file()
    )

if False:
    print("\n cat tmp/abc > file()")
    
    dw.bytes.cat.cat("tmp/abc", add_number=True) > dw.bytes.to_file()

if True:
    print("\n cat tmp/abc > stdout()")
    
    dw.bytes.cat.cat("tmp/abc", add_number=True) > dw.bytes.to_stdout()

# m = cat("tmp/abc", add_number=True) | grep(b"ab")
# print("\n cat tmp/abc | grep ab")
# for line in m:
#     print(line)

# m = grep(file="tmp/abc", pattern=b"d")
# print("\n grep tmp/abc d")
# for line in m:
#     print(line)

# m = grep(file="tmp/abc", pattern=b"d") | grep(b"e")
# print("\n grep tmp/abc d | grep e")
# for line in m:
#     print(line)


