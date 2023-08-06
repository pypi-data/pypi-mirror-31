Predecessor
===========

Overview
--------

This set of libraries is intended to provide useful classes to inherit
from, in a way that is cross compatible between multiple languages. A
version of this library is currently available in:

-  Python (2 or 3)
-  Javascript

Singleton
---------

The singleton class provides a way to ensure you only have one instance
of a class. For instance:

.. code:: python

    from predecessor import Singleton


    class Example(Singleton):
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar


    a = Example(3, 8)
    b = Example(2, 9)
    a is b  # returns True
    a.foo == b.foo == 3  # returns True

Or equivalently in Javascript:

.. code:: javascript

    const Singleton = require('predecessor').Singleton;

    class Example extends Singleton {
        constructor(foo, bar)   {
            this.foo = foo;
            this.bar = bar;
        }
    }

    let a = new Example(3, 8);
    let b = new Example(2, 9);
    a === b;  // returns true
    a.foo === 3;  // returns true
    b.foo === 3;  // returns true
