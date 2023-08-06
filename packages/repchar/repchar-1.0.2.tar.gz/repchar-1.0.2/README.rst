*******
repchar
*******

This is a simple command line script that creates a list of all
characters contained in a given document.

Download, Installation
======================

repchar is available on PyPI <https://pypi.python.org/pypi/repchar/>.

Install with ``pip install repchar``.

Usage
=====

repchar [-h] -o OUTFILENAME [-v] [-c] INFILENAME

positional arguments:
  INFILENAME            Filename

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILENAME, --outfile OUTFILENAME, --out OUTFILENAME
                        Filename for report
  -v, --verbose         Set log level to INFO.
  --version             show program's version number and exit
  -c, --comb, --combining
                        Create special report for combining characters

The ``Reporter`` class
======================

You can also use the ``CharReporter`` class in your own code:

.. code:: pycon

    >>> from repchar import CharReporter
    >>> s = u"ABCD"
    >>> r = CharReporter()
    >>> r.feed(s)
    >>> print(r.report())
    chr	hex	count	unicode
    A	0041	1	LATIN CAPITAL LETTER A
    B	0042	1	LATIN CAPITAL LETTER B
    C	0043	1	LATIN CAPITAL LETTER C
    D	0044	1	LATIN CAPITAL LETTER D

The count of each letter is stored in ``CharReporter.chars``:

.. code:: pycon

    >>> r.chars
    {u'A': 1, u'C': 1, u'B': 1, u'D': 1}

Special information about combining characters can be collected in
``CharReporter.combdir`` if you say so at instantiation:

.. code:: pycon

    >>> from repchar import CharReporter
    >>> r2 = CharReporter(combining=True)
    >>> s = u"Caffe\u0300"
    >>> r2.feed(s)
    >>> print(r2.report().encode("UTF-8"))
    chr	hex	count	unicode
    C	0043	1	LATIN CAPITAL LETTER C
    a	0061	1	LATIN SMALL LETTER A
    e	0065	1	LATIN SMALL LETTER E
    f	0066	2	LATIN SMALL LETTER F
     ̀	0300	1	COMBINING GRAVE ACCENT
                            1 with: LATIN SMALL LETTER E
    >>> r2.combdir
    {u'\u0300': {u'e': 1}}

