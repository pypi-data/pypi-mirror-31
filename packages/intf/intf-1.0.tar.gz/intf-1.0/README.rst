``intf`` provides a simple base class for integers with specified
default formatting. Define your own subclasses derived from `BaseIntF`
and specify desired formatting right with the class name. Decimal,
binary, octal and hexadecimal formats are supported. See `BaseIntF` for
more details.

Example::

    from intf import BaseIntF

    class int_04X(BaseIntF):
        pass

    x = int_04X(123)
    print '{}'.format(x)  # prints 0x007B

    class int_06o(BaseIntF):
        pass

    y = int_06o(123)
    print '{}'.format(y)  # prints 0o000173

    class int_08b(BaseIntF):
        pass

    z = int_08b(123)
    print '{}'.format(z)  # prints 0b01111011

    print '{:02x}'.format(z)  # still prints 7b
