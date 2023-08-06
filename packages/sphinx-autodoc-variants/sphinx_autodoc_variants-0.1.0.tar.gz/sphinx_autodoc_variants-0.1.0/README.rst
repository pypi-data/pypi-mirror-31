=======================
sphinx_autodoc_variants
=======================

.. image:: https://travis-ci.org/python-variants/sphinx_autodoc_variants.svg?branch=master
    :target: https://travis-ci.org/python-variants/sphinx_autodoc_variants

An extension for sphinx to allow automatic documentation of ``variants`` functions.

Overview
--------

The default `sphinx.ext.autodoc <http://www.sphinx-doc.org/en/master/ext/autodoc.html>`_ module does not handle function groups with variants created by the `variants <https://github.com/python-variants/variants>`_ module correctly. This extension registers an automatic documenter that detects variant functions and methods and enables documentation of both the primary and variant functions.

To use this with your project that uses ``variants``, first install this extension with ``pip`` (or, preferably, add this to the documentation dependencies):

.. code-block::

    pip install sphinx_autodoc_variants

With this installed, add ``'sphinx_autodoc_variants'`` to the ``extensions`` variable of  your ``conf.py``, e.g.:

.. code-block::

    extensions = ['sphinx.ext.autodoc',
                  'sphinx.ext.viewcode',
                  'sphinx_autodoc_variants']


This will enable proper documentation of ``variants`` functions under ``.. automodule`` or other `autodoc directives <http://www.sphinx-doc.org/en/master/ext/autodoc.html>`_.

If you want to explicitly document a ``variants`` function group, use ``.. autoprimary_function`` for functions and ``.. autoprimary_method`` for methods.


Links
-----

- Source: https://github.com/python-variants/sphinx_autodoc_variants
- Bugs: https://github.com/python-variants/sphinx_autodoc_variants/issues
