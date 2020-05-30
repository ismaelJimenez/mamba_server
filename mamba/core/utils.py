""" Mamba generic utility functions """

import os
import re
import inspect

from typing import List, Iterator, Dict, Any, Callable
from types import ModuleType
from importlib import import_module
from pkgutil import iter_modules

from mamba.core.context import Context
from mamba.core.exceptions import ComposeFileException


def path_from_string(path_str: str) -> str:
    """Return a valid path from a given path string, formatted with windows
       or linux slashes.

    Args:
        path_str: The path string formatted in windows or linux style.

    Returns:
        The valid path string.
    """
    path = os.path.join(*re.split(r' |/|\\', path_str))

    if path_str[0] == '/':  # Fix for absolute path
        path = '/' + path

    return path


def get_classes_from_module(module: str,
                            search_class: type) -> Dict[str, Callable]:
    """Return a dictionary with all classes 'search_class' defined in the
    given module that can be instantiated.
    """

    classes_dict: Dict[str, Callable] = {}
    for cls in _iter_classes(module, search_class):
        cls_name = cls.__module__.split('.')[-1]
        classes_dict[cls_name] = cls
    return classes_dict


def get_components(used_components: Dict[str, dict], modules: List[str],
                   component_type: type,
                   context: Context) -> Dict[str, object]:
    """Returns a dictionary of instantiated components with context.

    Args:
        used_components: The dictionary of used components.
        modules: The folders where to look for the components.
        component_type: The class type of the components.
        context: The application context to instantiate
                           the components with.

    Returns:
        The instantiated dictionary of components.

    Raises:
        ComposeFileException: If a given component id is not found.

    """

    all_components_by_type: Dict[str, Callable] = {}

    for module in modules:
        components_in_module = get_classes_from_module(module, component_type)

        all_components_set = set(all_components_by_type)
        new_components_set = set(components_in_module)

        intersection = all_components_set.intersection(new_components_set)

        if len(intersection) > 0:
            raise ComposeFileException(
                f"Component identifier '{intersection}' is duplicated")

        all_components_by_type.update(components_in_module)

    dict_used_components = {}

    for component_name, args in used_components.items():
        if args is None or 'component' not in args:
            raise ComposeFileException(
                f"'{component_name}: missing component property")

        if args['component'] in all_components_by_type:
            dict_used_components[component_name] = all_components_by_type[
                args['component']](context, args)
        else:
            raise ComposeFileException(
                f"{component_name}: component {args['component']}' is not a "
                f"valid component identifier")

    return dict_used_components


def _walk_modules(path: str) -> List[ModuleType]:
    """Loads a module and all its submodules from the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.
    For example: walk_modules('mamba.mock')
    """

    mods = []
    mod = import_module(path)
    mods.append(mod)

    # Any module that contains a __path__ attribute is considered a package.
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(getattr(mod, '__path__')):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += _walk_modules(fullpath)
            else:
                submod = import_module(fullpath)
                mods.append(submod)
    return mods


def _iter_classes(module_name: str, search_class: type) -> Iterator[Callable]:
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
