# -*- coding: utf-8 -*-
from setuptools import setup


package_dir = {"": "python"}

packages = ["lvmecp", "lvmecp.actor", "lvmecp.actor.commands", "lvmecp.controller"]

package_data = {"": ["*"], "lvmecp": ["etc/*"]}

install_requires = [
    "click-default-group>=1.2.2,<2.0.0",
    "click>=8.0.1,<9.0.0",
    "sdss-access>=0.2.3",
    "sdss-clu>=1.4.0,<2.0.0",
    "sdss-tree>=2.15.2",
    "sdsstools>=0.4.0",
]

entry_points = {"console_scripts": ["lvmecp = lvmecp.__main__:main"]}

setup_kwargs = {
    "name": "sdss-lvmecp",
    "version": "0.1.0a0",
    "description": "osures of lvm in sdss.",
    "long_description": "# lvmecp\n\n![Versions](https://img.shields.io/badge/python->3.7-blue)\n[![Documentation Status](https://readthedocs.org/projects/sdss-lvmecp/badge/?version=latest)](https://sdss-lvmecp.readthedocs.io/en/latest/?badge=latest)\n[![Travis (.org)](https://img.shields.io/travis/sdss/lvmecp)](https://travis-ci.org/sdss/lvmecp)\n[![codecov](https://codecov.io/gh/sdss/lvmecp/branch/main/graph/badge.svg)](https://codecov.io/gh/sdss/lvmecp)\n\nSDSS-V LVMi Enclosure Control Package\n",
    "author": "mingyeong yang",
    "author_email": "mingyeong@khu.ac.kr",
    "maintainer": "None",
    "maintainer_email": "None",
    "url": "https://github.com/sdss/lvmecp",
    "package_dir": package_dir,
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "entry_points": entry_points,
    "python_requires": ">=3.7,<4.0",
}

from build import *


build(setup_kwargs)

setup(**setup_kwargs)

# This setup.py was autogenerated using poetry.
