# -*- coding: utf-8 -*-

# =================================================================
# dw
#
# Copyright (c) 2022 Takahide Nogayama
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
# =================================================================

__version__ = "0.4.0"

from collections.abc import Iterable, Callable, Sequence, Set
import io
import logging
import os
import re
import sys

# Logger
_LOGGER: logging.Logger = logging.getLogger(__name__)
_LOG_FORMAT: str = '%(asctime)s |  %(levelname)-7s | %(message)s (%(filename)s L%(lineno)s %(name)s)'

################################################################################


class _Devnull:
    pass


DEV_NULL = _Devnull()
devnull = DEV_NULL

STDIO = "-"

################################################################################


class Monad(object):

    def __init__(self, iterable: Iterable[object] = []):
        self.iterable: Iterable = iterable

    def bind(self, monadic_func: Callable) -> object:
        return monadic_func(self.iterable)

    __or__ = bind


class IterableMonad(Monad):

    def bind(self, monadic_func: Callable) -> object:
        new_iterable_monad: IterableMonad = super().bind(monadic_func)

        if getattr(monadic_func, "sink_to_be_redirected_to", None):
            # if redirect is sandwitched by parentheses like ["a", "b"] | (grep("a") > []), this block is called
            sink_to_be_redirected_to: object = getattr(monadic_func, "sink_to_be_redirected_to", None)
            return new_iterable_monad.redirect_to(sink_to_be_redirected_to)
        elif getattr(monadic_func, "sink_to_be_appending_redirected_to", None):
            # if redirect is sandwitched by parentheses like ["a", "b"] | (grep("a") > []), this block is called
            sink_to_be_appending_redirected_to: object = getattr(monadic_func, "sink_to_be_appending_redirected_to", None)
            return new_iterable_monad.appending_redirect_to(sink_to_be_appending_redirected_to)

        return new_iterable_monad

    def __iter__(self):
        # return self.iterable
        return iter(self.iterable)

    def __str__(self) -> str:
        import io, os
        sio: io.StringIO = io.StringIO()
        for obj in self.iterable:
            sio.write(str(obj))
            sio.write("\n")
        return sio.getvalue()

    __repr__ = __str__

    def redirect_to(self, sink) -> object:
        other = self | tee(sink, append=False)
        for _ in other:
            pass
        return sink

    __gt__ = redirect_to  # range(5) | sort() > []

    def appending_redirect_to(self, sink) -> object:
        other = self | tee(sink, append=True)
        for _ in other:
            pass
        return sink

    __rshift__ = appending_redirect_to  # (range(5) | sort() ) >> "filename". because >> is stronger than |.

def cat(*iterables: list[Iterable], encoding="utf-8") -> IterableMonad:

    def _cat() -> Iterable[str]:
        for iterable in iterables:
            if isinstance(iterable, str) and ("\n" not in iterable or "\r" not in iterable):
                # Assume that this is file
                must_close: bool = False
                if iterable == STDIO:
                    iterable = sys.stdin
                else:
                    if not os.path.exists(iterable):
                        FileNotFoundError(iterable)
                    iterable = io.open(iterable, "rt", encoding=encoding)
                    must_close = True
                try:
                    for line in iterable:
                        yield line.rstrip("\r\n")
                finally:
                    if must_close:
                        iterable.close()
            else:
                for obj in iterable:
                    yield obj

    return IterableMonad(_cat())

class MonadicFunctionWrapper(object):
    
    def __init__(self, f: Callable, obj2imonad_func=cat):
        import dw
        self.f: Callable = f
        self.obj2imonad_func: Callable = obj2imonad_func

        self.sink_to_be_redirected_to: object = None
        self.sink_to_be_appending_redirected_to: object = None

    def __call__(self, *args, **kwargs) -> object:
        return self.f(*args, **kwargs)

    def __ror__(self, other) -> IterableMonad:
        return self.obj2imonad_func(other) | self

    def redirect_to(self, sink) -> object:
        """
        if redirect is sandwitched by parentheses like ["a", "b"] | (grep("a") > []), this method is called
        """
        self.sink_to_be_redirected_to = sink
        return self

    __gt__ = redirect_to  # range(5) | sort() > []

    def appending_redirect_to(self, sink: object) -> object:
        """
        if redirect is sandwitched by parentheses like ["a", "b"] | (grep("a") >> []), this method is called
        """
        self.sink_to_be_appending_redirected_to = sink
        return self

    __rshift__ = appending_redirect_to

    def __str__(self) -> str:
        print("ho")
        m = IterableMonad()
        m2 = m.bind(self.f)
        return str(m2)
    __repr__ = __str__

# marker decorator
def monadic_function_returner(f: Callable):
    return f


def monadic_function(monadic_function_wrapper: Callable = MonadicFunctionWrapper):

    def deco(f: Callable):
        mf = monadic_function_wrapper(f)
        return mf

    return deco


def pipeable(monad_class: IterableMonad = IterableMonad, monadic_function_wrapper: Callable = MonadicFunctionWrapper):

    def deco(generator_f: Callable) -> Callable:

        @monadic_function(monadic_function_wrapper)
        def _monadic_f(iterable: Iterable[object]) -> IterableMonad:
            return monad_class(generator_f(iterable))

        return _monadic_f

    return deco


################################################################################

@pipeable()
def do_nothing(iterable: Iterable) -> Iterable[object]:
    for obj in iterable:
        yield obj

################################################################################
@monadic_function_returner
def tee(target: object,
        e:str="utf-8", encoding:str="utf-8",
        a: bool=False, append: bool = False,
        n: bool=False, ) -> Callable:
    """
    Copy standard input to each FILE, and also to standard output.
      -a, --append              append to the given FILEs, do not overwrite
    """
    encoding = encoding or e
    append = append or a

    @pipeable()
    def _tee(iterable: Iterable) -> Iterable[object]:
        import io

        sink: Iterable = target
        must_close = False
        if isinstance(sink, str):
            if sink == "-":
                sink = sys.stdout
            else:
                must_close = True
                if append:
                    sink = io.open(sink, "at", encoding=encoding)
                else:
                    if os.path.exists(sink):
                        os.remove(sink)
                    sink = io.open(sink, "wt", encoding=encoding)

        if sink is DEV_NULL:
            for obj in iterable:
                yield obj
        elif isinstance(sink, Sequence):
            if not append:
                sink.clear()
            for obj in iterable:
                sink.append(obj)
                yield obj
        elif isinstance(sink, Set):
            if not append:
                sink.clear()
            for obj in iterable:
                sink.add(obj)
                yield obj
        elif isinstance(sink, io.TextIOBase):
            # if isinstance(sink, typing.TextIO): => dont work
            try:
                for obj in iterable:
                    sink.write(str(obj))
                    # sink.write(os.linesep)
                    if not n:
                        sink.write("\n")  # see https://docs.python.org/en/3/library/os.html#os.linesep
                    yield obj
            finally:
                if must_close:
                    sink.close()
        elif isinstance(sink, io.BufferedWriter) or isinstance(sink, io.BytesIO) \
        or isinstance(sink, io.BufferedRandom) or isinstance(sink, io.FileIO):
            # elif isinstance(sink, typing.BinaryIO): => dont work
            try:
                linesep_b: bytes = bytes("\n", "utf-8")  # see https://docs.python.org/en/3/library/os.html#os.linesep
                for obj in iterable:
                    sink.write(bytes(str(obj), "utf-8"))
                    if not n:
                        sink.write(linesep_b)
                    yield obj
            finally:
                if must_close:
                    sink.close()
        elif isinstance(sink, Callable):
            for obj in iterable:
                sink(obj)
                yield obj
        else:
            raise ValueError(f"sink=={sink} is not instance of either io, Sequence, or Set")

    return _tee()


################################################################################
def body(monadic_function, n: int = 1) -> Callable:
    """
    See https://github.com/jeroenjanssens/dsutils/blob/master/body
    """
    
    @pipeable()
    def _body(iterable: Iterable[object]) -> Iterable[object]:
        iterator = iter(iterable)

        headers = []
        try:
            for idx in range(n):
                headers.append(next(iterator))
        except StopIteration:
            pass
        
        m2 = IterableMonad(iterator) | monadic_function
        
        for obj in headers:
            yield obj
        for obj in m2:
            yield obj
        
    return _body

################################################################################
@monadic_function_returner
def echo(text: str=""):
    """
    NAME
        echo - display a line of text

    SYNOPSIS
        echo [SHORT-OPTION]... [STRING]...
        echo LONG-OPTION

    DESCRIPTION
        Echo the STRING(s) to standard output.

        -n     do not output the trailing newline

        -e     enable interpretation of backslash escapes

        -E     disable interpretation of backslash escapes (default)
    """
    @pipeable()
    def _echo(_: Iterable) -> Iterable[object]:
        # ignore input!!
        yield text
    return _echo

@monadic_function_returner
def _ri_head(n: int = 5) -> Callable:
    if n < 0:
        raise ValueError("n must be non negative value.")

    @monadic_function()
    def _mf(iterable: Iterable) -> Iterable[object]:

        def _head():
            idx: int = 0
            for obj in iterable:
                if idx < n:
                    idx += 1
                    yield obj
                else:
                    break

        return IterableMonad(_head())

    return _mf


@monadic_function_returner
def head(n: int = 5):
    if n < 0:
        raise ValueError("n must be non negative value.")

    @pipeable()
    def _head(iterable: Iterable) -> Iterable[object]:
        idx: int = 0
        for obj in iterable:
            if idx < n:
                idx += 1
                yield obj
            else:
                break

    return _head


@monadic_function_returner
def tail(n: int = 5) -> Callable:
    if n < 0:
        raise ValueError("n must be non negative value.")

    @pipeable()
    def _tail(iterable: Iterable) -> Iterable[object]:
        buffer: list = [None for x in range(n)]
        pos: int = 0
        count: int = 0
        for obj in iterable:
            buffer[pos] = obj
            pos += 1
            if pos >= n:
                pos = 0
            count += 1
        idx: int = 0
        m: int = min(n, count)
        for idx in range(m):
            yield buffer[(pos + idx) % m]

    return _tail


_original_reversed = reversed


@monadic_function_returner
def reversed() -> Callable:

    @pipeable()
    def _reversed(iterable: Iterable) -> Iterable[object]:
        return _original_reversed(iterable)

    return _reversed


@monadic_function_returner
def shuffle() -> Callable:

    @pipeable()
    def _shuffle(iterable: Iterable) -> Iterable[object]:
        import random
        buffer: list = [x for x in iterable]
        return random.sample(buffer, k=len(buffer))

    return _shuffle


@monadic_function_returner
def sample(k: int, counts=None) -> Callable:

    @pipeable()
    def _sample(iterable: Iterable) -> Iterable[object]:
        import random
        buffer: list = [x for x in iterable]
        return random.sample(buffer, k=k, counts=counts)

    return _sample


@monadic_function_returner
def uniq(g:bool=False, globally:bool=False) -> Callable:
    """
    Usage: uniq [OPTION]... [INPUT [OUTPUT]]
    Filter adjacent matching lines from INPUT (or standard input),
    writing to OUTPUT (or standard output).

    With no options, matching lines are merged to the first occurrence.

    Mandatory arguments to long options are mandatory for short options too.
    -c, --count           prefix lines by the number of occurrences
    -d, --repeated        only print duplicate lines, one for each group
    -D                    print all duplicate lines
        --all-repeated[=METHOD]  like -D, but allow separating groups
                                    with an empty line;
                                    METHOD={none(default),prepend,separate}
    -f, --skip-fields=N   avoid comparing the first N fields
        --group[=METHOD]  show all items, separating groups with an empty line;
                            METHOD={separate(default),prepend,append,both}
    -i, --ignore-case     ignore differences in case when comparing
    -s, --skip-chars=N    avoid comparing the first N characters
    -u, --unique          only print unique lines
    -z, --zero-terminated     line delimiter is NUL, not newline
    -w, --check-chars=N   compare no more than N characters in lines
    """

    globally = globally or g

    if globally:

        @pipeable()
        def _uniq(iterable: Iterable) -> Iterable[object]:
            from collections import defaultdict
            d = defaultdict(int)
            for obj in iterable:
                d[obj] += 1
            for obj in d.keys():
                yield obj

        return _uniq
    else:

        @pipeable()
        def _uniq(iterable: Iterable) -> Iterable[object]:
            last: object = None
            for idx, obj in enumerate(iterable):
                if idx == 0 or obj != last:
                    last = obj
                    yield obj

        return _uniq

_original_sorted = sorted


@monadic_function_returner
def sorted(key: Callable = None, reverse: bool = False) -> Callable:

    @pipeable()
    def _sorted(iterable: Iterable) -> Iterable[object]:
        return _original_sorted(iterable, key=key, reverse=reverse)

    return _sorted

sort = sorted


import functools as _functools


def _compare(a, b) -> int:
    if a == b: return 0
    if a is None:  # a > b
        return 1
    if b is None:
        return -1
    return -1 if a < b else 1


none_aware_key_func = _functools.cmp_to_key(_compare)

_original_filter = filter


@monadic_function_returner
def filter(condition_f: Callable) -> Callable:

    @pipeable()
    def _filter(iterable: Iterable) -> Iterable[object]:
        return _original_filter(condition_f, iterable)

    return _filter


_original_map = map


@monadic_function_returner
def map(condition_f: Callable) -> Callable:

    @pipeable()
    def _map(iterable: Iterable) -> Iterable[object]:
        return _original_map(condition_f, iterable)

    return _map


################################################################################




@monadic_function_returner
def grep(*patterns: list[str], \
         i=False, ignore_case=False, \
         n=False, line_number=False, \
         v=False, invert_match=False) -> Callable:
    ignore_case = ignore_case or i
    line_number = line_number or n
    invert_match = invert_match or v

    flags = 0
    if ignore_case:
        flags |= re.IGNORECASE

    compiled_patterns = [re.compile(p, flags=flags) for p in patterns]

    @pipeable()
    def _grep(iterable: Iterable[str]) -> Iterable[str]:
        for idx, obj in enumerate(iterable):
            for compiled_pattern in compiled_patterns:
                m = compiled_pattern.search(obj)
                if (m and not invert_match) or (not m and invert_match):
                    if line_number:
                        yield [idx, obj]
                    else:
                        yield obj
                    break

    return _grep


################################################################################

@monadic_function_returner
def count() -> Callable:

    @pipeable
    def _count(iterable: Iterable) -> Iterable[list]:
        from collections import defaultdict
        obj2count = defaultdict(int)
        for obj in iterable:
            obj2count[obj] += 1
        for obj, count in obj2count.items():
            yield [count, obj]

    return _count


wc_l = count

################################################################################

@monadic_function_returner
def touch(*filenames) -> Callable:

    for filename in filenames:
        with io.open(filename, "wb") as f:
            pass
    
    @pipeable
    def _touch(iterable: Iterable) -> Iterable[list]:
        for filename in iterable:
            with io.open(filename, "bw") as f:
                pass
        if False:
            yield
        
    return _touch




################################################################################


def execute_command(cmd, args, **popen_kwargs):
    
    import subprocess
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **popen_kwargs)
    stdout, stderr = p.communicate()
    status = p.returncode
        
    return (status, stdout, stderr)



################################################################################

if __name__ == "__main__":
    # sys.exit(cli_main(*sys.argv[1:]))
    logging.basicConfig(stream=sys.stderr, format=_LOG_FORMAT, level=logging.WARNING)
    # sys.exit(_cli_main("home"))

    print(echo("a"))

