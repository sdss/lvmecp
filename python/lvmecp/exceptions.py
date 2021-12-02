# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-12-05 12:01:21
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-12-05 12:19:32

from __future__ import print_function, division, absolute_import


class LvmecpError(Exception):
    """A custom core Lvmecp exception"""

    def __init__(self, message=None):

        message = 'There has been an error' \
            if not message else message

        super(LvmecpError, self).__init__(message)   

class LvmecpControllerError(LvmecpError):
    """An exception raised by an '.PlcController'."""

    def __init__(self, message=None):

        message = 'Error with response from PlcController' \
            if not message else message

        super(LvmecpError, self).__init__(message)


class LvmecpNotImplemented(LvmecpError):
    """A custom exception for not yet implemented features."""

    def __init__(self, message=None):

        message = 'This feature is not implemented yet.' \
            if not message else message

        super(LvmecpNotImplemented, self).__init__(message)


class LvmecpAPIError(LvmecpError):
    """A custom exception for API errors"""

    def __init__(self, message=None):
        if not message:
            message = 'Error with Http Response from Lvmecp API'
        else:
            message = 'Http response error from Lvmecp API. {0}'.format(message)

        super(LvmecpAPIError, self).__init__(message)


class LvmecpApiAuthError(LvmecpAPIError):
    """A custom exception for API authentication errors"""
    pass


class LvmecpMissingDependency(LvmecpError):
    """A custom exception for missing dependencies."""
    pass


class LvmecpWarning(Warning):
    """Base warning for Lvmecp."""


class LvmecpUserWarning(UserWarning, LvmecpWarning):
    """The primary warning class."""
    pass


class LvmecpControllerWarning(UserWarning, LvmecpWarning):
    """A warning issued by an `.PlcController`."""

    pass