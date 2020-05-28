""" Mamba generic utility functions for commands and components """

import os
import re
import inspect

from importlib import import_module
from pkgutil import iter_modules

from mamba.exceptions import LaunchFileException


def path_from_string(path_str):
    """Return a valid path from a given path string, formatted with windows
       or linux slashes.

    Args:
        path_str (str): The path string formatted in windows or linux style.

    Returns:
        The valid path string.
    """
    path = os.path.join(*re.split(r' |/|\\', path_str))

    if path_str[0] == '/':  # Fix for absolute path
        path = '/' + path

    return path


def get_classes_from_module(module, search_class):
    """Return a dictionary with all classes 'search_class' defined in the
    given module that can be instantiated.
    """

    classes_dict = {}
    for cls in _iter_classes(module, search_class):
        cls_name = cls.__module__.split('.')[-1]
        classes_dict[cls_name] = cls
    return classes_dict


def get_components(used_components, modules, component_type, context):
    """Returns a dictionary of instantiated components with context.

    Args:
        used_components (list<str>): The identifiers of the components.
        modules (list<str>): The folders where to look for the components.
        component_type (class): The class type of the components.
        context (Context): The application context to instantiate
                           the components with.

    Returns:
        The instantiated dictionary of components.

    Raises:
        LaunchFileException: If a given component id is not found.

    """

    all_components_by_type = {}

    for module in modules:
        components_in_module = get_classes_from_module(module, component_type)

        all_components_set = set(all_components_by_type)
        new_components_set = set(components_in_module)

        intersection = all_components_set.intersection(new_components_set)

        if len(intersection) > 0:
            raise LaunchFileException(
                f"Component identifier '{intersection}' is duplicated")

        all_components_by_type.update(components_in_module)

    dict_used_components = {}

    for used_component, args in used_components.items():
        if used_component in all_components_by_type:
            dict_used_components[used_component] = all_components_by_type[
                used_component](context, args)
        else:
            raise LaunchFileException(
                f"'{used_component}' is not a valid component identifier")

    return dict_used_components


def _walk_modules(path):
    """Loads a module and all its submodules from the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.
    For example: walk_modules('mamba.utils')
    """

    mods = []
    mod = import_module(path)
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += _walk_modules(fullpath)
            else:
                submod = import_module(fullpath)
                mods.append(submod)
    return mods


def _iter_classes(module_name, search_class):
    """Return an iterator over all classes 'search_class' defined in the given
    module that can be instantiated.
    """
    for module in _walk_modules(module_name):
        for obj in vars(module).values():
            if inspect.isclass(obj) and \
                    issubclass(obj, search_class) and \
                    obj.__module__ == module.__name__ and \
                    not obj == search_class:
                yield obj
