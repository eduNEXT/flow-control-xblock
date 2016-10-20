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

* From the main page of a specific course, navigate to `Settings -> Advanced Settings` from the top menu.
* Check for the `Advanced Module List` policy key, and Add ``"flow-control"``` to the policy value list.
* Click the "Save changes" button.

Usage
-----
As an instructor add a Flow Control component on the required unit
and follow these steps on "settings":

* Select the condition to check.
* Enter the problems locator ids (as many as required) to evaluate the condition.
* Select an action to apply when condition is met.


Common use cases
----------------

Flow Control can be used whenever you need to control the available course content based on grades obtained by a student,  on one or more evaluated problems in the course. Also, it is possible to check if those problems have been answered or not.


Features include
----------------

* **Studio editable settings:** allows to select custom actions or
  conditions to apply flow control on LMS contents.
* **WYSIWYG editor:** studio html editor to check how students would see your content, once a condition is met.
* **Condition operators:** allows to select a custom operator
  to check the selected condition.


About this xblock
-----------------

The Flow control Xblock was built by `eduNEXT <https://edunext.co>`_, a company specialized in open edX development and services.

It was presented at the open edX conference 2016 at Stanford University.


How to contribute
-----------------

* Fork this repository.
* Commit your changes on a new branch
* Make a pull request to the master branch
* Wait for code review and merge process


.. |build-status| image:: https://travis-ci.org/eduNEXT/flow-control-xblock.svg?branch=master
   :target: https://travis-ci.org/eduNEXT/flow-control-xblock
