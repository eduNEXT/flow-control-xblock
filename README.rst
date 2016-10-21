==================================
XBlock flow-control |build-status|
==================================

The Flow Control Xblock provides a way to display the content of a
unit or to redirect the user elsewhere based on compliance with a condition
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
Add a Flow Control component to the content unit you want to control access to,
and follow these steps on "settings":

* Select the condition to check.
* Enter the problem locator ids (as many as required) to evaluate the condition.
* Select an action to apply when the condition is met.


Common use cases
----------------

Flow Control can be used whenever you need to control the available course content based on grades obtained by a student, on one or more evaluated problems in the course. Also, it is possible to check if those problems have been answered or not.
Some common uses cases are:

* Only allow the learner to see unit B when a problem in unit A has been answered, otherwise displaying a explanatory message.
* Only allow the learner to see unit B when a problem in unit A has been answered, otherwise redirecting to unit A.
* Only allow the learner to see unit B when a problem in unit A has scored above a certain threshold.
* Present further explanatory content to learners that did not answer correctly a certain problem, while redirecting to the next unit learners that did answer correcly.
* Display a message congratulating the learner for passing an exam, or a message notifying the exam wasn't passed.
* Display a message notifying the learner that some of the exam's questions have not been answered yet.
* Used in combination with the subsection prerequites feature to better explain the learners why certain subsections will or will not be made available to them.


Features include
----------------

**Studio editable settings:** Allows to select the conditions and operators to evaluate and the actions to apply in a particular unit.

**Condition types:** Currently, the xblock features evaluating the score of a single problem and the average score of a list of problems

**Condition operators:** The implemented operators are:

* equals
* not equal to
* greather than
* greather than or equal to
* less than
* less than or equal to
* is empty
* is not empty
* has empty

**Actions:** This actions can be applied when a condition is met:

* Display a message
* Redirect to another unit in the same subsection (without reloading the page)
* Redirect to another unit using jump_to_id (reloading the page)
* Redirect to a given url.

**WYSIWYG editor:** A simple to use HTML editor to simplify writing the content or message that learners will get if the condition is met.

About this xblock
-----------------

The Flow control Xblock was built by `eduNEXT <https://www.edunext.co>`_, a company specialized in open edX development and services.

It was presented at the open edX con 2016 at Stanford University.


How to contribute
-----------------

* Fork this repository.
* Commit your changes on a new branch
* Make a pull request to the master branch
* Wait for code review and merge process


.. |build-status| image:: https://travis-ci.org/eduNEXT/flow-control-xblock.svg?branch=master
   :target: https://travis-ci.org/eduNEXT/flow-control-xblock
