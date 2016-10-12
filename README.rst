==================================
XBlock flow-control |build-status|
==================================

The Flow Control Xblock provides a way to display the content of a
unit or to redirect the user based on compliance with a condition
that evaluates the submission or the score of a problem or a set 
of problems.

Installation
------------

Install the requirements into the Python virtual environment of your
`edx-platform` installation by running the following command from the
root folder:

```
$ pip install -r requirements.txt
```

Enabling in Studio
-------------------

After successful installation, you can activate this component for a 
course following these steps:

1. From the main page of a specific course, navigate to 
`Settings -> Advanced Settings` from the top menu.
2. Check for the `Advanced Module List` policy key, and Add 
```"flow-control"``` to the policy value list.
3. Click the "Save changes" button.

Usage
-----




Features include
----------------

* **Studio editable settings:** allows to select custom actions or
  conditions to apply flow control on LMS contents.
* **Custom operators:** allows to select a custom operator
  to check the selected condition.

Testing
-------


i18n compatibility
------------------


About this xblock
-----------------

The Flow control Xblock was built by [eduNEXT](https://edunext.co), a company specialized in open edX development and services.

It was presented at the open edX con 2016 at Stanford university.


How to contribute
-----------------




.. |build-status| image:: https://travis-ci.org/eduNEXT/flow-control-xblock.svg?branch=master
   :target: https://travis-ci.org/eduNEXT/flow-control-xblock
