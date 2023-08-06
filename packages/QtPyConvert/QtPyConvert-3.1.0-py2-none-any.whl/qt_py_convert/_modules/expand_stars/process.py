# Copyright 2018 Digital Domain 3.0
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
"""
The imports module is designed to fix the import statements.
"""
import traceback

from qt_py_convert.general import ALIAS_DICT, change, supported_binding
from qt_py_convert.color import color_text, ANSI
from qt_py_convert.log import get_logger


EXPAND_STARS_LOG = get_logger("expand_stars")


class Processes(object):
    """Processes class for expand_stars"""
    @staticmethod
    def _get_children(binding, levels=None):
        """
        You have done the following:
        >>> from <binding>.<levels> import *

        And I hate you a little bit.
        I am changing it to the following:
        >>> from <binding> import <levels>

        But I don't know what the heck you used in the *
        So I am just getting everything bootstrapped in. Sorry-not-sorry
        """
        def _module_filtering(key):
            import __builtin__
            if key.startswith("__"):
                return False
            elif key in dir(__builtin__):
                return False
            return True

        def _members(_mappings, _module_, module_name):
            members = filter(_module_filtering, dir(_module))
            for member in members:
                mappings[member] = "{mod}.{member}".format(
                    mod=module_name,
                    member=member
                )

        mappings = {}
        if levels is None:
            levels = []
        try:
            _temp = __import__(binding, fromlist=levels)
        except ImportError as err:
            strerr = str(err).replace("No module named", "")

            msg = (
                "Attempting to resolve a * import from the {mod} "
                "module failed.\n"
                "This is usually because the module could not be imported. "
                "Please check that this script can import it. The error was:\n"
                "{err}"
            ).format(mod=strerr, err=str(err))
            traceback.print_exc()
            raise ImportError(msg)
        if not levels:
            _module = _temp
            _members(mappings, _module, module_name=binding)
        else:
            for level in levels:
                _module = getattr(_temp, level)
                _members(mappings, _module, module_name=level)
        return mappings

    @classmethod
    def _process_star(cls, red, stars, skip_lineno=False):
        """
        _process_star is designed to replace from X import * methods.

        :param red: redbaron process. Unused in this method.
        :type red: redbardon.RedBaron
        :param stars: List of redbaron nodes that matched for this proc.
        :type stars: list
        """
        mappings = {}
        for star in stars:
            from_import = star.parent
            binding = from_import.value[0]
            second_level_modules = None
            if len(star.parent.value) > 1:
                second_level_modules = [star.parent.value[1].dumps()]
            if len(star.parent.value) > 2:
                pass

            children = cls._get_children(binding.dumps(), second_level_modules)
            if second_level_modules is None:
                second_level_modules = children
            text = "from {binding} import {slm}".format(
                binding="Qt",
                slm=", ".join([name for name in second_level_modules])
            )

            change(
                logger=EXPAND_STARS_LOG,
                node=star.parent,
                replacement=text,
                skip_lineno=skip_lineno
            )
            mappings.update(children)
            # star.replace(
            #     text
            # )
        return mappings

    EXPAND_STR = "EXPAND"
    EXPAND = _process_star


def star_process(store):
    """
    star_process is one of the more complex handlers for the _modules.

    :param store: Store is the issues dict defined in "process"
    :type store: dict
    :return: The filter_function callable.
    :rtype: callable
    """
    def filter_function(value):
        for target in value.parent.targets:
            if target.type == "star" and supported_binding(value.dumps()):
                store[Processes.EXPAND_STR].add(value)
                return True

    return filter_function


def process(red, skip_lineno=False, **kwargs):
    """
    process is the main function for the import process.

    :param red: Redbaron ast.
    :type red: redbaron.redbaron
    :param skip_lineno: An optional performance flag. By default, when the
        script replaces something, it will tell you which line it is
        replacing on. This can be useful for tracking the places that
        changes occurred. When you turn this flag on however, it will not
        show the line numbers. This can give great performance increases
        because redbaron has trouble calculating the line number sometimes.
    :type skip_lineno: bool
    :param kwargs: Any other kwargs will be ignored.
    :type kwargs: dict
    """
    issues = {
        Processes.EXPAND_STR: set(),
    }
    EXPAND_STARS_LOG.warning(color_text(
        text="\"import star\" used. We are bootstrapping code!",
        color=ANSI.colors.red,
    ))
    EXPAND_STARS_LOG.warning(color_text(
        text="This will be very slow. It's your own fault.",
        color=ANSI.colors.red,
    ))
    values = red.find_all("FromImportNode", value=star_process(issues))

    mappings = getattr(Processes, Processes.EXPAND_STR)(
        red, issues[Processes.EXPAND_STR], skip_lineno=skip_lineno
    )
    return ALIAS_DICT, mappings
