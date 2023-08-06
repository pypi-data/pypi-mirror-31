This package defines two classes:

* `subrange` -- continuous subrange of integers as a ``min..max`` object

* `subrangef` -- annotated `subrange` with reach formatting capabilities

If you are new to this package, start with the `subrange`. It implements
the core features of subranges::

    from subrange import subrange

    r = subrange(1, 5)          # subrange of integers 1..5

    print r                     # 1..5
    print r.min, r.max          # 1 5
    print repr(r)               # subrange(1, 5)
    print "{:04b}".format(r)    # 0001..0101
    print 4 in r                # True
    print [i for i in r]        # [1, 2, 3, 4, 5]
    print r < 6                 # True

If you need annotated subranges with reach formatting, consider using
`subrangef`::

    from subrange import subrangef

    f = subrangef(0, 127,
                  str_spec="0x{value:02X} {id!r}",  # format string
                  id="ASCII_CHARSET",               # annotation
                  brief="ASCII character codes")    # annotation

    print f     # 0x00..7F 'ASCII_CHARSET'

    print "{brief}: {min} to {max}".format(**f.__dict__)
    # ASCII character codes: 0 to 127

Subrange instances are immutable hashable ordered collections of unique
integers in the range from ``min`` to ``max`` inclusively.

Annotated subranges are initialized with custom set of attributes (those
are ``id`` and ``brief`` in the example above, but it may be almost
arbitrary set of attributes) and a format string ``str_spec`` that
defines the default formatting of the created instance.

Much more detailed description with examples may be found in
documentation to `subrange` and `subrangef` classes.
