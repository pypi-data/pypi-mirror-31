ComPath HGNC |build| |coverage| |documentation|
===============================================
This package support the mapping across different protein/gene identifiers.

Citation
--------
Gray KA, Yates B, Seal RL, Wright MW, Bruford EA. genenames.org: the HGNC resources in 2015. Nucleic Acids Res. 2015
Jan;43(Database issue):D1079-85. doi: 10.1093/nar/gku1071. http://www.ncbi.nlm.nih.gov/pubmed/25361968

Installation |pypi_version| |python_versions| |pypi_license|
------------------------------------------------------------
``compath_hgnc`` can be installed easily from `PyPI <https://pypi.python.org/pypi/compath_hgnc>`_ with the
following code in your favorite terminal:

.. code-block:: sh

    $ python3 -m pip install compath_hgnc

or from the latest code on `GitHub <https://github.com/compath/compath_hgnc>`_ with:

.. code-block:: sh

    $ python3 -m pip install git+https://github.com/compath/compath_hgnc.git@master

Setup
-----
HGNC can be downloaded and populated from either the Python REPL or the automatically installed command line
utility.

Python REPL
~~~~~~~~~~~
.. code-block:: python

    >>> import compath_hgnc
    >>> compath_hgnc_manager = compath_hgnc.Manager()
    >>> compath_hgnc_manager.populate()

Command Line Utility
~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    compath_hgnc populate

Acknowledgements
----------------
- This package heavily relies on Andrej Konotopez's package `PyHGNC <https://github.com/lekono/pyhgnc>`_ and the
  `Bio2BEL HGNC <https://github.com/bio2bel/hgnc>`_.

.. |build| image:: https://travis-ci.org/compath/compath_hgnc.svg?branch=master
    :target: https://travis-ci.org/compath/compath_hgnc
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/compath/compath_hgnc/coverage.svg?branch=master
    :target: https://codecov.io/gh/compath/compath_hgnc?branch=master
    :alt: Coverage Status

.. |documentation| image:: http://readthedocs.org/projects/compath_hgnc/badge/?version=latest
    :target: http://bio2bel.readthedocs.io/projects/compath_hgnc/en/latest/?badge=latest
    :alt: Documentation Status

.. |climate| image:: https://codeclimate.com/github/compath/compath_hgnc/badges/gpa.svg
    :target: https://codeclimate.com/github/compath/compath_hgnc
    :alt: Code Climate

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/compath_hgnc.svg
    :alt: Stable Supported Python Versions

.. |pypi_version| image:: https://img.shields.io/pypi/v/compath_hgnc.svg
    :alt: Current version on PyPI

.. |pypi_license| image:: https://img.shields.io/pypi/l/compath_hgnc.svg
    :alt: MIT License
