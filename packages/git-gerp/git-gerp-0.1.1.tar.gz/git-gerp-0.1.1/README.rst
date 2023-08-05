git-gerp
========

Git grep wrapper for arguments re-ordering,
that can use options after filenames.

This is "gErp", not "gRep".

Description
-----------

Original ``git grep`` command is sensitive to the order of arguments.
For example, you use ``git grep``, and you want to add option ``-l`` in
tail, but you must type in the correct order.

::

    # original git grep
    git grep pattern target -l  # NG `fatal: bad flag '-l' used after filename`
    git grep -l pattern target  # OK

``git-gerp`` is allow to use options after patterns and filenames.

::

    # use `g(e)rp`, instead of `g(r)ep`
    git gerp pattern target -l  # OK, you can add option '-l' in tail

``git-gerp`` is replace arguments, and execute ``git grep``.

Replacement rules:

1. Find option arguments (and option’s parameters), move these to ahead.
2. Move rest plain arguments to behind.
3. If find double-dash ``--``, treat after arguments as plain.

Requirements
------------

-  Python 2.6+ or Python 3

Installation
------------

1. Install this package using pip:

   ::

       pip install git-gerp

   and you can run under your repository:

   ::

       git gerp ...

2. Define git alias (optional):

   ::

       # define alias `g`
       git config --global alias.g gerp

   and you can run:

   ::

       git g ...

Usage
-----

::

    git gerp [<git-grep-argument>...]

Examples:

::

    # simple
    git gerp pattern
    git gerp pattern path

    # tail options
    git gerp pattern path -l -A5 --max-depth 2

    # support boolean expressions, and '(', ')'
    git gerp \( -e pattern1 --and -e pattern2 \) --or -e pattern3 path -l

    # support '--'
    git gerp pattern -l -- path1 path2 -i  # pathspecs is ['path1', 'path2', '-i']

Licence
-------

`MIT <https://github.com/htaketani/git-gerp/blob/master/LICENSE>`__

Author
------

`htaketani <https://github.com/htaketani>`__
