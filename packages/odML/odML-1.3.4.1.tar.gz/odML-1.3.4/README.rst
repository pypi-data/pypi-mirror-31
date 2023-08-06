.. image:: https://travis-ci.org/G-Node/python-odml.svg?branch=master
    :target: https://travis-ci.org/G-Node/python-odml
.. image:: https://ci.appveyor.com/api/projects/status/2wfvsu7boe18kwjy?svg=true
    :target: https://ci.appveyor.com/project/mpsonntag/python-odml
.. image:: https://coveralls.io/repos/github/G-Node/python-odml/badge.svg?branch=master
    :target: https://coveralls.io/github/G-Node/python-odml?branch=master

odML (Open metaData Markup Language) core library
=================================================

The open metadata Markup Language is a file based format (XML, JSON, YAML) for storing
metadata in an organised human- and machine-readable way. odML is an initiative to define
and establish an open, flexible, and easy-to-use format to transport metadata.

The Python-odML library can be easily installed via :code:`pip`. The source code is freely
available on `GitHub <https://github.com/G-Node/python-odml>`_. If you are not familiar
with the version control system **git**, but still want to use it, have a look at the
documentation available on the `git-scm website <https://git-scm.com/>`_.

Dependencies
------------

* Python 2.7+ or 3.4+
* Python packages:

  * enum34
  * lxml
  * pyyaml

* These packages will be downloaded and installed automatically if the :code:`pip` method is used to install odML. Alternatively, they can be installed from the OS package manager. On Ubuntu, they are available as:

  * python-enum
  * python-lxml
  * python-yaml

* If you prefer installing using the Python package manager, the following packages are required to build the lxml Python package on Ubuntu 14.04:

  * libxml2-dev
  * libxslt1-dev
  * lib32z1-dev


Installation
------------

The simplest way to install Python-odML is from PyPI using the pip tool::

  $ pip install odml

On Ubuntu, the pip package manager is available in the repositories as :code:`python-pip` and :code:`python3-pip`.

If this method is used, the appropriate Python dependencies (enum and lxml) are downloaded and installed automatically.

On Linux it is more convenient to obtain the lxml and yaml libraries via the distribution's package manager (e.g., :code:`apt-get install python-lxml` and :code:`apt-get install python-yaml` for Ubuntu).


Building from source
--------------------

To download the Python-odML library please either use git and clone the
repository from GitHub::

  $ git clone https://github.com/G-Node/python-odml.git

If you don't want to use git download the ZIP file also provided on
GitHub to your computer (e.g. as above on your home directory under a "toolbox"
folder).

To install the Python-odML library, enter the corresponding directory and run::

  $ cd python-odml
  $ python setup.py install


Documentation
-------------

`Documentation <https://g-node.github.io/python-odml>`_

Bugs & Questions
----------------

Should you find a behaviour that is likely a bug, please file a bug report at
`the github bug tracker <https://github.com/G-Node/python-odml/issues>`_.

If you have questions regarding the use of the library, feel free to join the
`#gnode <http://webchat.freenode.net?channels=%23gnode>`_ IRC channel on freenode.
