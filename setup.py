# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 eduNEXT
#
# This software's license gives you freedom; you can copy, convey,
# propagate, redistribute and/or modify this program under the terms of
# the GNU Affero General Public License (AGPL) as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version of the AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.
#

# Imports ###########################################################

"""
FlowControl Xblock setup file
"""

import os
import re
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install


def get_version(*file_paths):
    """Retrieves the version from the main app __init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')

__version__ = get_version("flow_control","__init__.py")

def package_data(pkg, roots):
    """Generic function to find package_data.
    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.
    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement;
    that is, it is not blank, a comment, a URL, or an included file.
    """
    return line and not line.startswith(('-r', '#', '-e', 'git+', '-c'))


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.
    Returns a list of requirement strings.
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.split('#')[0].strip() for line in open(path).readlines()
            if is_requirement(line)
        )
    return list(requirements)


# Main ##############################################################

with open("README.rst", "r") as file:
    long_description = file.read()

setup(
    name='flow-control-xblock',
    version=__version__,
    author='eduNEXT',
    author_email='technical@edunext.co',
    description='Flow Control XBlock',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/eduNEXT/flow-control-xblock',
    packages=find_packages(),
    classifiers=[
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=load_requirements('requirements/base.in'),
    tests_require=load_requirements('requirements/test.in'),
    entry_points={
        'xblock.v1': [
            'flow-control = flow_control:FlowCheckPointXblock',
        ],
    },
    keywords='edunext xblock flowcontrol flow-control',
    include_package_data=True,
    package_data=package_data(
        "flow_control", ["templates", "public", "static"])
)
