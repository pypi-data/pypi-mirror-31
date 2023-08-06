# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import inspect
import logging
import os
import warnings

import six

from .constant import MODULE_NAME_IMPORTED_CHECKS

logger = logging.getLogger(__name__)


def _load_module(path):
    module_name = "{}.{}.{}".format(MODULE_NAME_IMPORTED_CHECKS,
                                    os.path.basename(os.path.dirname(path)),
                                    os.path.basename(path))
    if six.PY3:

        from importlib.util import module_from_spec
        from importlib.util import spec_from_file_location

        s = spec_from_file_location(module_name, path)
        m = module_from_spec(s)
        s.loader.exec_module(m)
        return m

    elif six.PY2:
        import imp

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m = imp.load_source(module_name, path)
        return m


def load_check_implementation(path):
    logger.debug("Getting check(s) from the file '{}'.".format(path))
    m = _load_module(path)

    check_classes = []
    for name, obj in inspect.getmembers(m, inspect.isclass):
        if obj.__module__.startswith(MODULE_NAME_IMPORTED_CHECKS):
            new_check = obj()
            check_classes.append(new_check)
            logger.debug("Check instance '{}' found.".format(new_check.name))
    return check_classes
