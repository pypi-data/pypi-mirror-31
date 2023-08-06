|buildstatus|_
|coverage|_

About
=====

Mangling of various file formats that conveys binary information
(Motorola S-Record, Intel HEX and binary files).

Project homepage: https://github.com/eerimoq/bincopy

Documentation: http://bincopy.readthedocs.org/en/latest

Installation
============

.. code-block:: python

    pip install bincopy

Example usage
=============

Scripting
---------

A basic example converting from Intel HEX to Intel HEX, SREC, binary,
array and hexdump formats:

.. code-block:: python

    >>> import bincopy
    >>> f = bincopy.BinFile("tests/files/in.hex")
    >>> print(f.as_ihex())
    :20010000214601360121470136007EFE09D219012146017E17C20001FF5F16002148011979
    :20012000194E79234623965778239EDA3F01B2CA3F0156702B5E712B722B7321460134219F
    :00000001FF

    >>> print(f.as_srec())
    S32500000100214601360121470136007EFE09D219012146017E17C20001FF5F16002148011973
    S32500000120194E79234623965778239EDA3F01B2CA3F0156702B5E712B722B73214601342199
    S5030002FA

    >>> f.as_binary()
    bytearray(b'!F\x016\x01!G\x016\x00~\xfe\t\xd2\x19\x01!F\x01~\x17\xc2\x00\x01
    \xff_\x16\x00!H\x01\x19\x19Ny#F#\x96Wx#\x9e\xda?\x01\xb2\xca?\x01Vp+^q+r+s!
    F\x014!')
    >>> list(f.segments)
    [Segment(address=256, data=bytearray(b'!F\x016\x01!G\x016\x00~\xfe\t\xd2\x19\x01
    !F\x01~\x17\xc2\x00\x01\xff_\x16\x00!H\x01\x19\x19Ny#F#\x96Wx#\x9e\xda?\x01
    \xb2\xca?\x01Vp+^q+r+s!F\x014!'))]
    >>> f.minimum_address
    256
    >>> f.maximum_address
    320
    >>> len(f)
    64
    >>> f[f.minimum_address]
    33
    >>> f[f.minimum_address:f.minimum_address + 1]
    bytearray(b'!')

See the `test suite`_ for additional examples.

Command line tool
-----------------

Print general information about given binary format file(s).

.. code-block:: text

   $ bincopy info tests/files/in.hex
   Data address ranges:
                            0x00000100 - 0x00000140

Convert file(s) from one format to another.

.. code-block:: text

   $ bincopy convert -i ihex -o srec tests/files/in.hex -
   S32500000100214601360121470136007EFE09D219012146017E17C20001FF5F16002148011973
   S32500000120194E79234623965778239EDA3F01B2CA3F0156702B5E712B722B73214601342199
   S5030002FA
   $ bincopy convert -i ihex -o srec tests/files/in.hex in.srec
   $ cat in.srec
   S32500000100214601360121470136007EFE09D219012146017E17C20001FF5F16002148011973
   S32500000120194E79234623965778239EDA3F01B2CA3F0156702B5E712B722B73214601342199
   S5030002FA
   $ bincopy as_hexdump tests/files/in.hex
   00000100  21 46 01 36 01 21 47 01  36 00 7e fe 09 d2 19 01  |!F.6.!G.6.~.....|
   00000110  21 46 01 7e 17 c2 00 01  ff 5f 16 00 21 48 01 19  |!F.~....._..!H..|
   00000120  19 4e 79 23 46 23 96 57  78 23 9e da 3f 01 b2 ca  |.Ny#F#.Wx#..?...|
   00000130  3f 01 56 70 2b 5e 71 2b  72 2b 73 21 46 01 34 21  |?.Vp+^q+r+s!F.4!|
   $ bincopy as_ihex tests/files/in.hex
   :20010000214601360121470136007EFE09D219012146017E17C20001FF5F16002148011979
   :20012000194E79234623965778239EDA3F01B2CA3F0156702B5E712B722B7321460134219F
   :00000001FF
   $ bincopy as_srec tests/files/in.hex
   S32500000100214601360121470136007EFE09D219012146017E17C20001FF5F16002148011973
   S32500000120194E79234623965778239EDA3F01B2CA3F0156702B5E712B722B73214601342199
   S5030002FA
   $

Contributing
============

#. Fork the repository.

#. Install prerequisites.

   .. code-block:: text

      pip install -r requirements.txt

#. Implement the new feature or bug fix.

#. Implement test case(s) to ensure that future changes do not break
   legacy.

#. Run the tests.

   .. code-block:: text

      make test

#. Create a pull request.

.. |buildstatus| image:: https://travis-ci.org/eerimoq/bincopy.svg
.. _buildstatus: https://travis-ci.org/eerimoq/bincopy

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/bincopy/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/bincopy

.. _test suite: https://github.com/eerimoq/bincopy/blob/master/tests/test_bincopy.py
