Changelog
=========

1.1.0 (unreleased)
-----------------------

1.1.0b1 (2018-05-12)
-----------------------

- Fix and re-enable the ``SaveExporter()`` class.

- Fix some issues with pattern matching module requiring non obvious
  imports from user's side.

- Fix pattern matching macro need to import ``_matching`` symbol

- Add an ``OptionalMatcher`` to pattern matching macro to support
  exclusive or conditions.

- Refactor documentation using sphinx.

- Refactor the macro expansion core code. Now the macro expansion
  order is from inside-out. This allows to use macros inside other
  macro's body.

- Added support for Python 3.4.

- Added ``SELECT * FROM country`` emulation in `pinq` macro.

- Update the examples.

- Update tco and pyxl macros.

- Prevent the import hooks from raising errors.


1.0.4.dev2 (2017-09-08)
-----------------------

- Add MANIFEST.in;

1.0.4.dev1 (2017-09-08)
-----------------------

- Updated the import machinery and macro detection to be compatible
  with Python 3.5+.

- Removed support for Python 2, supporting it would require a way to
  manage differences at the ast level, but i don't use Python2 anymore.

- Added support for Python 3.5+ in the form of new call arguments form
  and new ``AsyncFunctionDef``.

- Basic scope analysis now available in the form of the ``@Scoped``
  decorator, to be used in conjunction with ``@Walker``.

1.0.3
-----

- Error messages are now raised at run-time rather than at import
  time, with other improvements (double stack traces, catchability).

- ``@enum`` macro now has much better error messages

- Improved error messages for mis-use of stub functions outside their
  related macro (e.g. the ``u``, ``name``, ``ast`` stubs for the ``q``/``hq``
  macros)

- Improved error messages for invalid case class signatures

- Hygienic Quasiquotes now allow lexical capture of module objects

1.0.2
-----

- Removed unit test from PyPI distribution

1.0.1
-----
- Fixed a bug in ``ast_ctx_fixer``
- ``gen_sym()`` is now ``gen_sym(name="sym")``, allowing you to override the base name
- Implemented ``macropy.case_classes.enum`` macro
- Implemented ``macropy.quick_lambda.lazy`` and ``macropy.quick_lambda.interned`` macros
