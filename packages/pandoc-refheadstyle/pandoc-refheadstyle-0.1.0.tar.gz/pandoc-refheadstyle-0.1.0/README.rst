===================
pandoc-refheadstyle
===================

``pandoc-refheadstyle`` sets a custom style for the reference section header,
but only if the metadata field ``reference-section-title`` has been set to a
non-empty value.

By default, the reference section header will be assigned the custom style
'Bibliography Heading'. But you can change what style is assigned by setting
the metadata field ``reference-header-style`` to the name of a style of
your choice. If the style does not exist, it will be created.

See the `manual page <man/pandoc-refheadstyle.rst>`_ for more details.


Installing ``pandoc-refheadstyle``
======================================

You use ``pandoc-refheadstyle`` **at your own risk**. You have been warned.

You need `Python 2.7 <https://www.python.org/>`_ or newer and
`panflute <https://github.com/sergiocorreia/panflute>`_.

Simply run::

    pip install pandoc_refheadstyle

This will try to install ``pandoc-refheadstyle`` manual page, but this
will only work on a limited number of systems.

Alternatively, you can also download the source for the `current version
<https://codeload.github.com/odkr/pandoc-refheadstyle/tar.gz/v0.1.0>`_.

Simply run::

    curl https://codeload.github.com/odkr/pandoc-refheadstyle/tar.gz/v0.1.0 | tar -xz
    cd pandoc-refheadstyle-0.6.0
    python setup.py install


Documentation
=============

See the `manual page <man/pandoc-refheadstyle.rst>`_
and the source for details.


Contact
=======

If there's something wrong with ``pandoc-refheadstyle``, `open an issue
<https://github.com/odkr/pandoc-refheadstyle/issues>`_.


License
=======

Copyright 2018 Odin Kroeger

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Further Information
===================

GitHub:
<https://github.com/odkr/pandoc-refheadstyle>

PyPI:
<https://pypi.org/project/pandoc-refheadstyle>
