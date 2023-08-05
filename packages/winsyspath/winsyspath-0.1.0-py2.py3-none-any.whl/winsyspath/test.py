#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2018  Daniele Giudice
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function, unicode_literals
from .winsyspath import WinSysPath
import winvers

if winvers.get_version() <= winvers.WIN_XP_SP2:
    # Dummy winsyspath_test function, used when the OS is not Windows or is older than Windows XP SP2
    def winsyspath_test():
        raise EnvironmentError('This module works only on Windows XP SP2 or newer')
else:
    import ctypes

    def winsyspath_test(path='C:\\', debug=False):
        """
        Perform a test on WinEnvPath.

        Params:
            path (str): path used for tests (Default: C:\)
            debug (bool): if False nothing is printed, otherwise print the System Path value for each test (Default: False)

        Returns:
            None

        Raises:
            EnvironmentError if the OS is not Windows, or is older than Windows XP SP2, or the admin check fails
            AssertationError if some test fails
        """
        # Admin check
        is_admin = False
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            raise EnvironmentError('Windows OS detected, but admin check failed')
        if not is_admin:
            raise EnvironmentError('The test requires "Admin" privileges')

        # Init
        wrapper = WinSysPath()
        if debug:
            printd = print
        else:
            printd = lambda x: None

        # Reload and list generation test
        assert(not wrapper.reload())
        before = wrapper.get()
        assert(not path in before)
        printd('\n# BEFORE:')
        printd('\n'.join(before))

        # Add test
        res = wrapper.add(path)
        assert(res)
        res = wrapper.add(path)
        assert(not res)
        after_add = wrapper.get()
        assert(path in after_add)
        printd('\n# AFTER ADD:')
        printd('\n'.join(wrapper.get()))

        # Remove test
        res = wrapper.remove(path)
        assert(res)
        res = wrapper.remove(path)
        assert(not res)
        after_remove = wrapper.get()
        assert(not path in after_remove)
        printd('\n# AFTER REMOVE:')
        printd('\n'.join(wrapper.get()))
