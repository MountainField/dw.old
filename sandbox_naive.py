
import collections
import io
import itertools
import logging
import sys
from typing import Iterable
logging.getLogger().setLevel("DEBUG")
from collections.abc import Iterable, Mapping, Callable

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
        
    if False:
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

        


###################
if False:
    import io
    bytes_io = io.open("tmp/abc", "rb")
    try:
        for b in bytes_io:
            print(b)
    finally:
        bytes_io.close()
    
if False:
    import io
    bytes_io = io.open("tmp/abc", "rb")
    text_io = io.TextIOWrapper(bytes_io, encoding="utf-8")

    try:
        for t in text_io:
            print(t)
    finally:
        text_io.close()

if False:
    import io
    def bytes_iterable():
        bytes_io = io.open("tmp/abc", "rb")
        try:
            for b in bytes_io:
                yield b
        finally:
            bytes_io.close()
    ite = bytes_iterable()
    for b in ite:
        print(b)


if False:
    import io
    def bytes_iterable():
        bytes_io = io.open("tmp/abc", "rb")
        try:
            for b in bytes_io:
                yield b
        finally:
            bytes_io.close()
    ite = bytes_iterable()
    text_io = io.TextIOWrapper(ite, encoding="utf-8")
    for b in ite:
        print(b)
    # => Error!!

if False:
    import io

    class ClosableWrapper:
        def __init__(self, closeable):
            self.closeable = closeable
        
        # for with statements
        def __enter__(self):
            print("__ ClosableWrapper: entering")
            return self
        def __exit__(self, exc_type, exc_value, traceback):
            print("__ ClosableWrapper: exiting")
            self.close()
            if getattr(self.closeable, "__exit__", None):
                self.closeable.__exit__(exc_type, exc_value, traceback)
        
        def close(self):
            print("__ ClosableWrapper: closing")
            if getattr(self.closeable, "close", None):
                print("closing closable")
                self.closeable.close()

    class IteratorWrapper:
        def __init__(self, iter):
            self.iter = iter

        # iterable
        def __iter__(self):
            return self
        def __next__(self):
            return next(self.iter)
        next = __next__ #=> for python2 compatibility

        # method missing
        # def __getattr__(self, name ):
        #     print("called attr=", name)
        #     def _method_missing(*args):
        #         print("not found")
        #         return args
        #     return getattr(self.iter, name, _method_missing)

    
    class CloseableIteratorWrapper(IteratorWrapper, ClosableWrapper):
        def __init__(self, iter):
            IteratorWrapper.__init__(self, iter)
            ClosableWrapper.__init__(self, iter)
    
    bytes_io = io.open("tmp/abc", "rb")
    ite = CloseableIteratorWrapper(bytes_io)
    with ite:
        for b in ite:
            print(b)

if False:
    # メソッド付きジェネレータ
    class Foo(object):
        def __init__(self):
            self.j = None
        def __iter__(self):
            for i in range(10):
                self.j = 10 - i
                yield i

    my_generator = Foo()

    for k in my_generator:
        print('j is',my_generator.j)
        print('k is',k)

if False:
    import io
    class AutoCloseWrapper:
        def __init__(self, io_obj):
            if not getattr(io_obj, "close", None):
                raise ValueError("io_obj must have close method")
            self.io_obj = io_obj
        def __iter__(self):
            try:
                for event in self.io_obj:
                    yield event
            finally:
                self.io_obj.close()
        
        # method missing
        def __getattr__(self, name):
            print("called attr=", name)
            return getattr(self.io_obj, name)

    ite = io.open("tmp/abc", "rb")
    # ite = AutoCloseWrapper(sys.stdin.buffer)
    text_io = io.TextIOWrapper(ite, encoding="utf-8")
    text_io = AutoCloseWrapper(text_io)
    try:
        for b in text_io:
            sys.stdout.write(b)
    finally:
        text_io.close()

if False:
    from dataclasses import dataclass
    
    
    @dataclass
    class Object:
        x: str ='X'
        prop: Mapping[str, any]={}
        
    obj = Object()
    obj.y=10
    print(repr(obj))

if False:
    from dataclasses import dataclass
    

    class MyClass:
        def __init__(self):
            self.x: str="X"
        
        def __hash__(self):
            return hash(tuple(sorted(self.__dict__.items())))
        
        def __eq__(self, other):
            return self.__dict__ == other.__dict__ # you might want to add some type checking here
            
        def __repr__(self):
            kws = [f"{key}={value!r}" for key, value in self.__dict__.items()]
            return "{}({})".format(type(self).__name__, ", ".join(kws))
        # def __str__(self):
        #     return repr(self)

    obj = MyClass()
    obj.y=10
    print(repr(obj))
    print(str(obj))
    
    other = MyClass()
    print(obj == other, hash(obj), hash(other))
    other.y = 10
    print(obj == other, hash(obj), hash(other))

if False:
    import codecs
    c1 = codecs.lookup("UTF-8")
    print(c1.name)
    c2 = codecs.lookup("utf8")
    print(c1 is c2)


if False:

    class Foo:
        def __iter__(self):
            yield 1
            yield 2
    
    f = Foo()

    for e in f:
        print(e)
if True:
    class AutoCloseWrapper:
        def __init__(self, *io_objects):
            if not io_objects:
                raise ValueError("io_objects is empty")
            for io_object in io_objects:
                if not getattr(io_object, "close", None):
                    raise ValueError("io_object must have close method")
            
            self.io_objects = io_objects
            self.current_io_object=self.io_objects[0]

        def __iter__(self):
            for io_object in self.io_objects:
                self.current_io_object = io_object
                try:
                    for event in self.current_io_object:
                        yield event
                finally:
                    self.current_io_object.close()
        
        # method missing
        def __getattr__(self, name):
            # print("called attr=", name)
            return getattr(self.current_io_object, name)
    
    f = AutoCloseWrapper(io.open("tests/rsrc/abc.txt", "rb"))

    for e in f:
        print(e)
