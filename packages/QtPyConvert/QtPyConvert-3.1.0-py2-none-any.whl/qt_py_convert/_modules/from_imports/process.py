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
The from_imports module is designed to fix the from import statements.
"""
from qt_py_convert._modules.expand_stars import process as stars_process
from qt_py_convert.general import __supported_bindings__, ALIAS_DICT, change, \
    supported_binding
from qt_py_convert.log import get_logger


FROM_IMPORTS_LOG = get_logger("from_imports")
IGNORED_IMPORT_TARGETS = ("right_parenthesis", "left_parenthesis")


class Processes(object):
    """Processes class for from_imports"""
    @staticmethod
    def _get_import_parts(node, binding):
        return node.dumps().replace(binding, "").lstrip(".").split(".")

    @staticmethod
    def _no_second_level_module(node, _parts, skip_lineno=False):
        text = "from Qt import {key}".format(
            key=", ".join([target.value for target in node.targets])
        )

        change(
            logger=FROM_IMPORTS_LOG,
            node=node,
            replacement=text,
            skip_lineno=skip_lineno
        )

        node.replace(text)

    @classmethod
    def _process_import(cls, red, objects, skip_lineno=False):
        """
        _process_import is designed to replace from import methods.

        :param red: redbaron process. Unused in this method.
        :type red: redbardon.RedBaron
        :param objects: List of redbaron nodes that matched for this proc.
        :type objects: list
        :param skip_lineno: Global "skip_lineno" flag.
        :type skip_lineno: bool
        """
        binding_aliases = ALIAS_DICT
        mappings = {}

        # Replace each node
        for node, binding in objects:
            from_import_parts = cls._get_import_parts(node, binding)
            if len(from_import_parts) and from_import_parts[0]:
                second_level_module = from_import_parts[0]
            else:
                cls._no_second_level_module(
                    node.parent,
                    from_import_parts,
                    skip_lineno=skip_lineno
                )
                binding_aliases["bindings"].add(binding)
                for target in node.parent.targets:
                    binding_aliases["root_aliases"].add(target.value)
                continue

            for _from_as_name in node.parent.targets:
                if _from_as_name.type in IGNORED_IMPORT_TARGETS:
                    continue
                if _from_as_name.type == "star":
                    # TODO: Make this a flag and make use the expand module.
                    _, star_mappings = stars_process(
                        red
                    )
                    mappings.update(star_mappings)
                else:
                    key = _from_as_name.target or _from_as_name.value
                    value = ".".join(from_import_parts)+"."+_from_as_name.value
                    mappings[key] = value

            replacement = "from Qt import {key}".format(
                    key=second_level_module
            )
            change(
                logger=FROM_IMPORTS_LOG,
                node=node.parent,
                replacement=replacement,
                skip_lineno=skip_lineno
            )
            node.parent.replace(replacement)
            binding_aliases["bindings"].add(binding)
            for target in node.parent.targets:
                binding_aliases["root_aliases"].add(target.value)
            if binding not in binding_aliases:
                binding_aliases[binding] = set()
            binding_aliases[binding] = binding_aliases[binding].union(
                set([target.value for target in node.parent.targets])
            )
        return binding_aliases, mappings

    FROM_IMPORT_STR = "FROM_IMPORT"
    FROM_IMPORT = _process_import


def import_process(store):
    """
    import_process is one of the more complex handlers for the _modules.

    :param store: Store is the issues dict defined in "process"
    :type store: dict
    :return: The filter_function callable.
    :rtype: callable
    """
    def filter_function(value):
        """
        filter_function takes an AtomTrailersNode or a DottedNameNode and will
        filter them out if they match something that has changed in psep0101
        """
        _raw_module = value.dumps()
        # See if that import is in our __supported_bindings__
        matched_binding = supported_binding(_raw_module)
        if matched_binding:
            store[Processes.FROM_IMPORT_STR].add(
                    (value, matched_binding)
            )
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
        Processes.FROM_IMPORT_STR: set(),
    }
    red.find_all("FromImportNode", value=import_process(issues))

    key = Processes.FROM_IMPORT_STR

    if issues[key]:
        return getattr(Processes, key)(red, issues[key], skip_lineno=skip_lineno)
    else:
        return ALIAS_DICT, {}
