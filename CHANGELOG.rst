Change Log
----------

..
   All enhancements and patches to flow-control-xblock will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).
   
   This project adheres to Semantic Versioning (http://semver.org/).
.. There should always be an "Unreleased" section for changes pending release.
Unreleased
~~~~~~~~~~

*

[2.0.0] - 2025-01-23
**********************************************

Added
=====

* Support for Python 3.11 and Django 4.2
* Add  github workflow

Removed
_______

* **BREAKING CHANGE**: Dropped support for Python 3.5
* Drop CircleCI support
* Remove support to "redirect to another unit in the same subsection" action

Changed
=======

* Fix UI issues

[1.0.1] - 2020-10-14
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fixed
_____

* Python3 and Juniper issues
* Fix applyFlowControl in injection to applied correctly the actions of flow-control 


[1.0.0] - 2020-06-18
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added
_____

* Support for Juniper/Python 3.5-3.8

Removed
_______

* **BREAKING CHANGE**: Dropped support for Ironwood/Python 2.7


[0.2.1] - 2020-06-12
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added
_____

* First release on PyPI.
* Support for Ironwood/Python2.7
