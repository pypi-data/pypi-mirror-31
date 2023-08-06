.. -*- coding: utf-8 -*-

Changes
-------

0.4 (2018-04-26)
~~~~~~~~~~~~~~~~

- New ``escape`` option to ``HTMLPrinter`` that by default uses `html.escape(text,
  quote=True)`__ to emit safe text spans

  __ https://docs.python.org/3/library/html.html#html.escape


0.3 (2018-04-20)
~~~~~~~~~~~~~~~~

- Support for hyperlinks

- Support for headings

- New function to emit a Quill Delta representation of an AST


0.2 (2018-03-10)
~~~~~~~~~~~~~~~~

- Fix HTML representation of numbered list items without a value

- Raise a specific InvalidNestingError exception instead of generic AssertionError


0.1 (2018-02-25)
~~~~~~~~~~~~~~~~

- Renamed to metapensiero.markup.semtext


0.0 (unreleased)
~~~~~~~~~~~~~~~~

- Initial effort.
