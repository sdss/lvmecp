#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2022-05-24
# @Filename: __init__.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from clu import Command

from .actor import ECPActor


ECPCommand = Command[ECPActor]
