#####################################
[MarryDoc] Easy DocString Maintenance
#####################################

.. currentmodule:: marrydoc

.. image:: https://readthedocs.org/projects/marrydoc/badge/?version=latest
    :target: https://marrydoc.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

The :mod:`marrydoc` Python module makes maintaining consistency of
related Python docstrings easy. :mod:`marrydoc` provides decorators to
"wed" a docstring to another and provides a command line tool to
automatically update a module's docstrings when their basis docstrings
have changed.

The decorators offered annotate class, function, and method docstrings to
identify if their docstring is to be inherited from, maintained as a copy
of, or maintained as a modified copy of a docstring of another program
construct.


***********
Quick Start
***********

@inherit
========

Use the :func:`inherit()` decorator to dynamically copy a docstring from
one program construct to another when a module is imported. For example:

.. code-block:: python

    import marrydoc
    from foo import bar

    @marrydoc.inherit(bar)
    def my_bar():
        pass

    assert bar.__doc__ == my_bar.__doc__


@copied_from
============

Use the :func:`copied_from` decorator in combination with the command line
tool to evaluate if one program construct docstring is up to date with
another and automatically update the script if they are unequal. For
example:

.. code-block:: python

    import marrydoc
    from foo import bar

    @marrydoc.copied_from(bar)
    def my_bar():
        """Perform foo bar."""
        pass


Then use the command line tool to evaluate if the source docstring has
changed and automatically update if so:

.. code-block:: shell

    $ python -m marrydoc --merge my_foo.py
    my_foo.py ... OK


@based_on
=========

Use the :func:`based_on` decorator instead of :func:`copied_from`
when the docstring is a copy but has been modified. Pass an unmodified
copy of the source docstring as the second argument to :func:`based_on`
(to facilitate source docstring change detection and provide a basis of
a three way merge). For example:

.. code-block:: python

    import marrydoc
    from foo import bar

    @marrydoc.based_on(
        bar,
        """Perform foo bar.""")
    def my_bar():
        """Perform my special foo bar."""
        pass


Then use the command line tool to evaluate if the source docstring has
changed and automatically perform a three way merge if so:

.. code-block:: shell

    $ python -m marrydoc --merge my_foo.py
    my_foo.py ... UPDATED


