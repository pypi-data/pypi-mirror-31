Predecessor
===========

Overview
--------

This set of libraries is intended to provide useful classes to inherit
from, in a way that is cross compatible between multiple languages. A
version of this library is currently available in:

-  Python (2 or 3)
-  Javascript

The libraries currently provide:

-  singleton objects
-  serializable objects

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

Serializable
------------

The singleton class provides a way to serialize a class without needing
to care about what form the resulting blob takes. If a compatible class
definition is available in all supported languages, it should be
deserializable in all supported languages.

The Basic Case
~~~~~~~~~~~~~~

.. code:: python

    from predecessor import Serializable


    class Example(Serializable):
        def __init__(self, foo, bar):  # Note that keyword args are not supported
            self.foo = foo
            self.bar = bar

        def serialized(self):
            return super(Example, self).serialized(self.foo, self.bar)


    a = Example(3, 8)
    b = Example.deserialize(a.serialized())
    a.foo == b.foo == 3  # returns True
    a.bar == b.bar == 8  # returns True

Or equivalently in Javascript:

.. code:: javascript

    const Serializable = require('predecessor').Serializable;

    class Example extends Serializable {
        constructor(foo, bar)   {
            this.foo = foo;
            this.bar = bar;
        }

        serialized()    {
            return super.serialized(this.foo, this.bar);
        }
    }

    let a = new Example(3, 8);
    let b = Example.deserialize(a.serialized());
    a.foo === 3;  // returns true
    b.foo === 3;  // returns true
    a.foo === 8;  // returns true
    b.foo === 8;  // returns true

Implied Serialization
~~~~~~~~~~~~~~~~~~~~~

In both languages, you can also use implied serialization. This looks
like:

.. code:: python

    class Example(Serializable):
        __slots__ = ('a', 'b', 'c')

        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c

.. code:: javascript

    class Example extends Serializable  {
        constructor(a, b, c)    {
            super();
            this._slots = ['a', 'b', 'c'];
            this.a = a;
            this.b = b;
            this.c = c;
        }
    }

Advanced Recombination
~~~~~~~~~~~~~~~~~~~~~~

In both languages you can do data processing before feeding things into
your constructor.

.. code:: python

    class Example(Serializable):
        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c

        def serialized(self):
            return super(Example, self).serialized(self.a, self.b)

        @classmethod
        def recombine(cls, a, b):
            return cls(a, b, a+b)

.. code:: javascript

    class Example extends Serializable  {
        constructor(a, b, c)    {
            super();
            this.a = a;
            this.b = b;
            this.c = c;
        }

        serialized()    {
            return super.serialized(this.a, this.b);
        }

        static recombine(a, b)  {
            return new this(a, b, a+b);
        }
    }
