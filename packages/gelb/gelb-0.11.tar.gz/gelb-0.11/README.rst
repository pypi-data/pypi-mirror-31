GeLB: the GEneric Lattice Boltzmann framework
=============================================

Introduction
------------

GeLB is a tool for quickly developing simulations based on the lattice Boltzmann
(LB) approach. At its core lies the GeLB Description (GD) domain-specific
programming language (DSL), which allows LB (or similar) algorithms to be
expressed in a convenient manner (i.e. as close to the mathematical notation as
possible).

This Python package provides the `gelbc` program, which is the reference
implementation of a compiler for the GD language.

The intended audience is the community of researchers (or PhD students) who
develop new LB algorithms.


Installation (for GeLB users)
-----------------------------

::

   $ pip3 install gelb


Usage (**warning**: not yet functional!)
----------------------------------------

::

   $ gelbc your_gd_program.gd


Information for GeLB developers (currently, only for Dragos)
------------------------------------------------------------

Technically-speaking, `gelbc` is only a "transpiler" (rather than a normal
compiler), because currently it only generates high-level language (`C` or
`Fortran`) code, instead of machine code. This might change in future releases.

To run tests, use:
::

   $ python3 setup.py test

To upload new version to PyPI:
::

   $ cd ${GELB_ROOT}
   $ # *manually* increment version @setup.py
   $ ./utils/scripts_for_devs/cleanup_project.sh
   $ python setup.py sdist
   $ twine upload dist/*
