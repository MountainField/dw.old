# -*- coding: utf-8 -*-

# =================================================================
# Licensed Materials - Property of IBM
#
# (c) Copyright IBM Corp. 2021, 2021 All Rights Reserved
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
# =================================================================

from uspec import description, context, it, execute_command
from hamcrest import assert_that, equal_to, instance_of, is_not

import dw
from dw import *

with description("dw.Monadbind#bind"):

    @it("has the input iterable")
    def _(self):
        l = ["a", "b", "c"]
        m = Monad(l)
        assert_that(m, instance_of(Monad))
        assert_that(m.iterable, equal_to(l))

    @it("runs monadic_func, and pass the value from old monad to new monad.")
    def _(self):
        bin = []

        def mf(x):
            bin.append(1)
            return Monad(x)

        m1 = Monad("x")
        m2 = m1.bind(mf)

        assert_that(m2, instance_of(Monad))
        assert_that(m2.iterable, equal_to(m1.iterable))
        assert_that(bin, equal_to([1]))


with description("dw.IterableMonad"):

    @it("wraps input iterable")
    def _(self):
        l = ["a", "b", "c"]
        m = IterableMonad(l)
        l2 = [e for e in m]
        assert_that(l2, equal_to(l))

    @it("can be convered to str by str function")
    def _(self):
        l = ["a", "b", "c"]
        m = IterableMonad(l)
        assert_that(str(m), equal_to("a\nb\nc\n"))

    @it("can be convered to str by repr function")
    def _(self):
        l = ["a", "b", "c"]
        m = IterableMonad(l)
        assert_that(repr(m), equal_to("a\nb\nc\n"))

    @it("runs monadic_func, and pass the value from old monad to new monad.")
    def _(self):
        bin = []

        def mf(x):
            bin.append(1)
            return IterableMonad(x)

        m1 = IterableMonad("x")
        m2 = m1.bind(mf)

        assert_that(m2, instance_of(IterableMonad))
        assert_that(m2.iterable, equal_to(m1.iterable))
        assert_that(bin, equal_to([1]))

    @it("binds a monadic function with itself")
    def _(self):
        l = ["a", "b", "c"]

        m = IterableMonad(l).bind(dw.do_nothing)
        assert_that([e for e in m], equal_to(l))

        m = IterableMonad(l) | dw.do_nothing
        assert_that([e for e in m], equal_to(l))


with description("dw.MonadicFunctionWrapper#__ror__"):

    @it("flips left term and right term of __or__")
    def _(self):
        m = range(5) | dw.do_nothing
        assert_that(list(m), equal_to(list(range(5))))

        m = ["a", "b", "c"] | dw.do_nothing
        assert_that(list(m), equal_to(["a", "b", "c"]))

        m = set(["a", "b", "c"]) | dw.do_nothing
        assert_that(set(list(m)), equal_to(set(["a", "b", "c"])))

        m = "abc\ndef\nghi" | dw.do_nothing
        assert_that(list(m), equal_to(["abc", "def", "ghi"]))
    
with description("dw._ri_head"):

    @it("filters first n elements")
    def _(self):
        m = range(10) | dw._ri_head(3)
        l = [x for x in m]
        assert_that(l, equal_to([0, 1, 2]))


with description("dw.head"):

    @it("filters first n records")
    def _(self):
        m = range(10) | head(3)
        l = [x for x in m]
        assert_that(l, equal_to([0, 1, 2]))


with description("dw.tail"):

    @it("filters last n records")
    def _(self):
        m = range(10) | tail(3)
        l = [x for x in m]
        assert_that(l, equal_to([7, 8, 9]))


with description("dw.reversed"):

    @it("reverses the order of iterable")
    def _(self):
        m = range(5) | reversed()
        l = [x for x in m]
        assert_that(l, equal_to([4, 3, 2, 1, 0]))


with description("dw.shuffle"):

    @it("shuffles the order of iterable")
    def _(self):
        m = range(5) | shuffle()
        l = [x for x in m]
        s = set(l)
        assert_that(s, equal_to(set([0, 1, 2, 3, 4])))
        assert_that(l, is_not(equal_to([0, 1, 2, 3, 4])))


with description("dw.sample"):

    @it("samples some records from iterable")
    def _(self):
        m = range(5) | sample(k=3)
        l = [x for x in m]
        s = set(l)
        assert_that(len(l), equal_to(3))
        assert_that(s.issubset(set(range(5))), equal_to(True))


with description("dw.uniq"):

    @it("eliminates consecutively duplicated records")
    def _(self):
        m = [None, None, "a", "a", "a", "b", "a", "c", "c"] | uniq()
        l = [x for x in m]
        assert_that(l, equal_to([None, "a", "b", "a", "c"]))


with description("dw.uniq_all"):

    @it("eliminates duplicated records")
    def _(self):
        m = [None, None, "a", "a", "a", "b", "a", "c", "c"] | uniq_all()
        l = [x for x in m]
        assert_that(l, equal_to([None, "a", "b", "c"]))


with description("dw.sorted"):

    @it("sorts records")
    def _(self):
        m = ["d", "c", "a", "b", "f", "g", "e"] | sorted()
        l = [x for x in m]
        assert_that(l, equal_to(["a", "b", "c", "d", "e", "f", "g"]))


with description("dw.filter"):

    @it("filters records that match the criteria")
    def _(self):
        m = range(10) | filter(lambda x: (x % 2 == 0))
        l = [x for x in m]
        assert_that(l, equal_to([0, 2, 4, 6, 8]))


with description("dw.map"):

    @it("maps records to new records")
    def _(self):
        m = range(10) | map(lambda x: 2 * x)
        l = [x for x in m]
        assert_that(l, equal_to([0, 2, 4, 6, 8, 10, 12, 14, 16, 18]))


if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2)
