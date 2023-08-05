
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
import winvers

if winvers.get_version() < winvers.WIN_XP_SP2:
    # Dummy WinEnvPath class, used when the OS is not Windows or is older than Windows XP SP2
    class WinSysPath():
        def __init__(self):
            self._err_msg = 'This module works only on Windows XP SP2 or newer'

        def reload(self):
            raise EnvironmentError(self._err_msg)

        def get(self):
            raise EnvironmentError(self._err_msg)

        def get_str(self):
            raise EnvironmentError(self._err_msg)

        def add(self, path):
            raise EnvironmentError(self._err_msg)

        def remove(self, path):
            raise EnvironmentError(self._err_msg)
else:
    import os, ctypes

    # Cross version import of 'winreg' module
    try:
        import winreg
    except ImportError:
        import _winreg as winreg

    class WinSysPath():
        """
        Wrapper class to Windows Environment "Path" variable.

        Warning:
            - Requires Python v2.7 or newer
            - Requires Windows XP SP2 or newer
            - To edit the variable, you must be Administrator
        """

        def __init__(self):
            self._root_key      = winreg.HKEY_LOCAL_MACHINE
            self._sub_key       = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
            self._value_name    = 'PATH'
            self._paths         = []
            self._load()

        def _load(self):
            """
            Load System Path from registry and put it in the '_paths' attribute.

            Params:
                None

            Returns:
                None

            Raises:
                WindowsError if an error occurred when try to read System Path value
            """
            # Read System Path
            with winreg.OpenKeyEx(self._root_key, self._sub_key, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, self._value_name)
            # If present, remove ending value
            if value.endswith(os.pathsep):
                value = value[:-1]
            # Split the value and sort ascendantly
            self._paths = sorted(value.split(os.pathsep))

        def _save(self):
            """
            Save '_paths' System Path value into registry.

            Params:
                None

            Returns:
                None

            Raises:
                EnvironmentError if the user is not an "admin" or the admin check fails
                WindowsError if an error occurred when try to edit System Path value
            """
            # Admin check
            is_admin = False
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            except Exception:
                raise EnvironmentError('Windows OS detected, but admin check failed')
            if not is_admin:
                raise EnvironmentError('Edit System Path value requires "Admin" privileges')

            # Write on System Path
            value = os.pathsep.join(self._paths) + os.pathsep
            with winreg.OpenKeyEx(self._root_key, self._sub_key, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, self._value_name, 0, winreg.REG_EXPAND_SZ, value)
                winreg.FlushKey(key)

        def get(self):
            """
            Get System Path value as an list (ascendingly sorted).

            Params:
                None

            Returns:
                list: system path value
            """
            return self._paths[:]

        def get_str(self):
            """
            Get System Path value as a string (ascendingly sorted).

            Params:
                None

            Returns:
                str: system path value
            """
            return os.pathsep.join(self._paths) + os.pathsep

        def reload(self):
            """
            Relead the System Path value (useful if it is modified outside python).

            Params:
                None

            Returns:
                bool: True if the new System Path is different from the old, False otherwise

            Raises:
                WindowsError if an error occurred when try to edit System Path value
            """
            # Save old values
            old_paths = self._paths
            len_old_paths = len(old_paths)
            # Reload
            self._load()
            # Check if some is changed
            if len_old_paths != len(self._paths):
                return True
            if len([x for x, y in zip(old_paths, self._paths) if x == y]) != len_old_paths:
                return True
            return False

        def add(self, path):
            """
            Add a path in the System Path.
            The new System Path will be sorted ascendantly.
            The path must be exists on filesystem.
            If the path is already in the System Path, return False.

            Params:
                path (str) : directory path to add in System Path

            Returns:
                bool: True if the System Path value is modified, False otherwise

            Raises:
                EnvironmentError if the user is not an "admin" or the admin check fails
                WindowsError if an error occurred when try to edit System Path value
                ValueError if the path passed is not a string
                OSError if the path passed not exist or is not a dir
            """
            # Purge and check the path passed
            path = path.strip()
            if type(path) != str:
                raise ValueError('The path "{}" is not a string'.format(path))
            if not os.path.isdir(path):
                raise OSError('The path "{}" not exist or is not a dir'.format(path))
            # If is already in the System Path, exit
            if path in self._paths:
                return False
            # Otherwise add it
            self._paths = sorted(self._paths + [path])
            self._save()
            return True

        def remove(self, path):
            """
            Remove a path from the System Path.
            The new System Path will be sorted ascendantly.
            The path must be exists on filesystem.
            If the path is not in the System Path, return False.

            Params:
                path (str): directory path to remove from System Path

            Returns:
                bool: True if the System Path value is modified, False otherwise

            Raises:
                EnvironmentError if the user is not an "admin" or the admin check fails
                WindowsError if an error occurred when try to edit System Path value
                ValueError if the path passed is not a string
                OSError if the path passed not exist or is not a dir
            """
            # Purge and check the path passed
            path = path.strip()
            if type(path) != str:
                raise ValueError('The path "{}" is not a string'.format(path))
            if not os.path.exists(path):
                raise OSError('The path "{}" not exist, so cannot be contained in the system path'.format(path))
            # If is not in the System Path, exit
            if not path in self._paths:
                return False
            # Otherwise remove it
            self._paths.remove(path)
            self._save()
            return True
