import collections
import io
import itertools
import logging
from multiprocessing.sharedctypes import Value
import sys
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



if False:
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

if True:

    class Maybe(object):
        
        def __init__(self, value):
            self.value = value
        
        def bind(self, a_to_m_b):
            if self is NOTHING:
                return NOTHING
            else:
                return a_to_m_b(self.value)
        
        __or__ = bind
        
        def __eq__(self, other):
            return self is other or isinstance(other, Maybe) and other.value == self.value
        
        def consume(self, consumer):
            return consumer(self.value)
        __gt__ = consume
        
    class Just(Maybe):
        def __repr__(self):
            return 'Just(%r)' % self.value

    class Nothing(Maybe):
        def __repr__(self):
            return 'Nothing'
    NOTHING = Nothing(None)

    if False:
        # Version 1
        def cat(file):
            def func(iter):
                iter = io.open(file, "rb")
                return Maybe(iter)
            return func

        m = Just("").bind(cat("tmp/abc"))
        iter = m.value

        for line in iter:
            print(line)

    if False:
        # Version 2
        def cat(file=None):
            def func(input_iterable):
                if file is not None:
                    input_iterable = io.open(file, "rb")
                else:
                    if input_iterable is None:
                        raise ValueError("No resource to load")
                return Maybe(input_iterable)
            return func

        m = Just("") | cat("tmp/abc")
        iter = m.value

        for line in iter:
            print(line)

    if False:
        # Version 3 クラスで実現しちゃう
        class cat:
            def __init__(self, file=None):
                self.file = file
                self.value = None
                if file:
                    self.value = io.open(self.file, "rb")

            def __call__(self, input_iterable):
                if self.file is not None:
                    input_iterable = io.open(self.file, "rb")
                else:
                    if input_iterable is None:
                        raise ValueError("No resource to load")
                return Maybe(input_iterable)

            def bind(self, a_to_m_b):
                if self is NOTHING:
                    return NOTHING
                else:
                    return a_to_m_b(self.value)
            
            __or__ = bind

        m = Just("") | cat("tmp/abc")
        for line in m.value:
            print(line)
        
        m = cat("tmp/abc") 
        for line in m.value:
            print(line)
        
        m = cat("tmp/abc") | cat()
        for line in m.value:
            print(line)
    
    if False:

        class Maybe(object):
            
            def __init__(self, value, func=None):
                self.value = value
                self.func = func
            
            def bind(self, a_to_m_b):
                if self is NOTHING:
                    return NOTHING
                else:
                    return a_to_m_b(self.value)
            
            __or__ = bind

            def __call__(self, input_iterable):
                return self.func(input_iterable)

                # Version 4
        def cat(file=None):
            def func(input_iterable):
                if file is not None:
                    input_iterable = io.open(file, "rb")
                else:
                    if input_iterable is None:
                        raise ValueError("No resource to load")
                return Maybe(input_iterable)

            if file:
                iterable = io.open(file, "rb")
            else:
                iterable = sys.stdin.buffer
            
            return Maybe(iterable, func)

        m = Just("") | cat("tmp/abc")
        for line in m.value:
            print(line)
        
        m = cat("tmp/abc") 
        for line in m.value:
            print(line)
        
        m = cat("tmp/abc") | cat()
        for line in m.value:
            print(line)

    if False:
        # Version 4.1
        def byte_read_iterable(file):
            if file:
                iterable = io.open(file, "rb")
            else:
                iterable = sys.stdin.buffer
            try:
                for b in iterable:
                    yield b
            finally:
                if iterable != sys.stdin.buffer:
                    iterable.close


        class Maybe(object):
            
            def __init__(self, value, func=None):
                self.value = value
                self.func = func
            
            def bind(self, a_to_m_b):
                if self is NOTHING:
                    return NOTHING
                else:
                    return a_to_m_b(self.value)
            
            __or__ = bind

            def __call__(self, input_iterable):
                return self.func(input_iterable)


        def cat(file=None):
            
            def func(input_iterable):
                input_iterable = byte_read_iterable(file)
                return Maybe(input_iterable)

            # return func

            input_iterable = byte_read_iterable(file)
            return Maybe(input_iterable, func)

        m = Just("") | cat("tmp/abc")
        for line in m.value:
            print(line)
        
        m = cat("tmp/abc") 
        for line in m.value:
            print(line)
        
        m = cat("tmp/abc") | cat()
        for line in m.value:
            print(line)

    if False:
        # Version 4.1
        def byte_read_iterable(file):
            if file:
                iterable = io.open(file, "rb")
            else:
                iterable = sys.stdin.buffer
            try:
                for b in iterable:
                    yield b
            finally:
                if iterable != sys.stdin.buffer:
                    iterable.close


        class Maybe(object):
            
            def __init__(self, value, func=None):
                self.value = value
                self.func = func
            
            def bind(self, a_to_m_b):
                if self is NOTHING:
                    return NOTHING
                else:
                    return a_to_m_b(self.value)
            
            __or__ = bind

            def __call__(self, input_iterable):
                return self.func(input_iterable)

            def __iter__(self):
                return self.value



        def cat(file=None, add_number=False):
            
            def func(input_iterable):
                if file:
                    input_iterable = byte_read_iterable(file)
                elif input_iterable is None:
                    input_iterable = byte_read_iterable("-")
                
                if add_number:
                    input_iterable_bk = input_iterable
                    def ite():
                        for idx, b in enumerate(input_iterable_bk):
                            yield (b"%6i\t" % idx) + b
                    input_iterable = ite()
                
                return Maybe(input_iterable)

            # return func

            m = func(None)
            m.func = func
            return m
            # return Maybe(input_iterable, func)

        m = Just("") | cat("tmp/abc", add_number=True)
        for line in m:
            print(line)

        m = Maybe(io.open("tmp/abc", "br")) | cat(add_number=True)
        for line in m:
            print(line)
        
        m = cat("tmp/abc", add_number=True) 
        for line in m:
            print(line)
        
        m = cat("tmp/abc", add_number=True) | cat(add_number=True)
        for line in m:
            print(line)
        

    if False:
        # Version 4.1
        def byte_read_iterable(file):
            if file:
                iterable = io.open(file, "rb")
            else:
                iterable = sys.stdin.buffer
            try:
                for b in iterable:
                    yield b
            finally:
                if iterable != sys.stdin.buffer:
                    iterable.close


        class Maybe(object):
            
            def __init__(self, value):
                self.value = value
            
            def bind(self, a_to_m_b):
                if self is NOTHING:
                    return NOTHING
                else:
                    return a_to_m_b(self.value)
            
            __or__ = bind

            def __iter__(self):
                return self.value

        class HeadOfPipeMaybe(Maybe):
            
            def __init__(self, func):
                super().__init__(func)
                self.func = func
            
            def _ensure_iterable(self):
                m = self.func(None)
                self.value = m.value
            
            def bind(self, a_to_m_b):
                self._ensure_iterable()
                return super().bind(a_to_m_b)
            
            __or__ = bind

            def __iter__(self):
                self._ensure_iterable()
                return self.value

            def __call__(self, input_iterable):
                return self.func(input_iterable)


        def cat(file=None, add_number=False):
            
            def func(input_iterable):
                if file:
                    input_iterable = byte_read_iterable(file)
                elif input_iterable is None:
                    input_iterable = byte_read_iterable("-")
                
                if add_number:
                    input_iterable_bk = input_iterable
                    def ite():
                        for idx, b in enumerate(input_iterable_bk):
                            yield (b"%6i\t" % idx) + b
                    input_iterable = ite()
                
                return Maybe(input_iterable)

            # return func
            m = HeadOfPipeMaybe(func)
            return m
            # return Maybe(input_iterable, func)

        m = Just("") | cat("tmp/abc", add_number=True)
        for line in m:
            print(line)

        m = Maybe(io.open("tmp/abc", "br")) | cat(add_number=True)
        for line in m:
            print(line)
        
        m = cat("tmp/abc", add_number=True) 
        for line in m:
            print(line)
        
        m = cat("tmp/abc", add_number=True) | cat(add_number=True)
        for line in m:
            print(line)
        
    if True:
        # Version 5
        def byte_read_iterable(file):
            if file == "-":
                iterable = sys.stdin.buffer
            elif file:
                iterable = io.open(file, "rb")
            else:
                raise ValueError()

            try:
                for b in iterable:
                    yield b
            finally:
                if iterable != sys.stdin.buffer:
                    iterable.close


        class Maybe(object):
            
            def __init__(self, value):
                self.value = value
            
            def bind(self, a_to_m_b):
                if self is NOTHING:
                    return NOTHING
                else:
                    return a_to_m_b(self.value)
            
            __or__ = bind

            def __iter__(self):
                return self.value

        class HeadOfPipeMaybe(Maybe):
            
            def __init__(self, func):
                super().__init__(None)
                self.func = func
            
            def _ensure_iterable(self):
                if self.value is None:
                    m = self.func(None)
                    self.value = m.value
            
            def bind(self, a_to_m_b):
                self._ensure_iterable()
                return super().bind(a_to_m_b)
            __or__ = bind
            
            def __iter__(self):
                self._ensure_iterable()
                return self.value

            def __call__(self, input_iterable):
                return self.func(input_iterable)

        def deco(ffff):

            def wrapper(*args, **kwargs):
                func = ffff(*args, **kwargs)
                m = HeadOfPipeMaybe(func)
                return m

            return wrapper

        @deco
        def cat(file=None, add_number=False):
            
            def func(input_iterable):
                # Replace or not replace the input iterable
                if file: # Initialize or reset iterable chain 
                    input_iterable = byte_read_iterable(file)
                else:
                    if input_iterable is None: # Initialize head of iterable chain
                        input_iterable = byte_read_iterable("-")
                    else: # Connect new iterable to input_iterable. do not replace it
                        pass
                
                # Main
                if add_number:
                    input_iterable_bk = input_iterable
                    def ite():
                        for idx, b in enumerate(input_iterable_bk):
                            yield (b"%6i\t" % idx) + b
                    input_iterable = ite()
                
                return Maybe(input_iterable)

            return func

        m = Just("") | cat("tmp/abc", add_number=True)
        for line in m:
            print(line)

        m = Maybe(io.open("tmp/abc", "br")) | cat(add_number=True)
        for line in m:
            print(line)
        
        m = cat("tmp/abc", add_number=True) 
        for line in m:
            print(line)
        
        m = cat("tmp/abc", add_number=True) | cat(add_number=True)
        for line in m:
            print(line)

        
        @deco
        def grep(pattern: bytes, file=None):

            def func(input_iterable):
                # Replace or not replace the input iterable
                if file: # Initialize or reset iterable chain 
                    input_iterable = byte_read_iterable(file)
                else:
                    if input_iterable is None: # Initialize head of iterable chain
                        input_iterable = byte_read_iterable("-")
                    else: # Connect new iterable to input_iterable. do not replace it
                        pass
                
                # Main
                input_iterable_bk = input_iterable
                def ite():
                    import re

                    for idx, b in enumerate(input_iterable_bk):
                        if re.search(pattern, b):
                            yield b
                input_iterable = ite()
                
                return Maybe(input_iterable)

            return func

        m = cat("tmp/abc", add_number=True) | grep(b"ab")
        print("\n grep ab")
        for line in m:
            print(line)

        def unit(file):
            def _deco(ffff):
                def wrapper(input_iterable, *args, **kwargs):
                    # Replace or not replace the input iterable
                    if file: # Initialize or reset iterable chain 
                        input_iterable = byte_read_iterable(file)
                    else:
                        if input_iterable is None: # Initialize head of iterable chain
                            input_iterable = byte_read_iterable("-")
                        else: # Connect new iterable to input_iterable. do not replace it
                            pass
                    return ffff(input_iterable, *args, **kwargs)
                return wrapper
            return _deco

        # def deco3(f):
        #     def wrapper(*args, **kwargs):
        #         iterable = f(*args, **kwargs)
        #         return Maybe(iterable)
        #     return wrapper
        # @unit(file)
        # @deco3

        @deco
        def grep(pattern: bytes, file=None):

            @unit(file)
            def func(input_iterable):

                # Main
                input_iterable_bk = input_iterable
                def ite():
                    import re

                    for idx, b in enumerate(input_iterable_bk):
                        if re.search(pattern, b):
                            yield b
                input_iterable = ite()
                
                return Maybe(input_iterable)

            return func

        m = cat("tmp/abc", add_number=True) 
        print("\n cat tmp/abc")
        for line in m:
            print(line)

        m = cat("tmp/abc", add_number=True) | grep(b"ab")
        print("\n cat tmp/abc | grep ab")
        for line in m:
            print(line)
        
        m = grep(file="tmp/abc", pattern=b"d")
        print("\n grep tmp/abc d")
        for line in m:
            print(line)

        m = grep(file="tmp/abc", pattern=b"d") | grep(b"e")
        print("\n grep tmp/abc d | grep e")
        for line in m:
            print(line)

