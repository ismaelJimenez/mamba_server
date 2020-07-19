""" Mamba generic utility functions """

import os
import re
import inspect

from typing import List, Iterator, Dict, Callable, Any
from types import ModuleType
from importlib import import_module
from pkgutil import iter_modules
from shutil import ignore_patterns, copy2, copystat

from mamba.core.context import Context
from mamba.core.exceptions import ComposeFileException


def get_properties_dict(configuration: Dict[str, dict]) -> Dict[str, Any]:
    """Return a dictionary of properties with default values composed from
    a configuration file.

    Args:
        configuration: The path string formatted in windows or linux style.

    Returns:
        The dictionary of properties.
    """
    if 'device' in configuration and 'properties' in \
            configuration['device']:
        properties_dict = {
            key: value.get('default')
            for key, value in configuration['device']['properties'].items()
        }
    else:
        properties_dict = {}

    return properties_dict


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
    """Returns a dictionary of instantiated component with context.

    Args:
        used_components: The dictionary of used component.
        modules: The folders where to look for the component.
        component_type: The class type of the component.
        context: The application context to instantiate
                           the component with.

    Returns:
        The instantiated dictionary of component.

    Raises:
        ComposeFileException: If a given component id is not found.

    """

    all_components_by_type: Dict[str, Callable] = {}

    for module in modules:
        components_in_module = get_classes_from_module(module, component_type)

        for key, value in components_in_module.items():
            if key not in all_components_by_type:
                all_components_by_type[key] = value

    dict_used_components = {}

    for component_name, args in used_components.items():
        if args is None or 'component' not in args:
            raise ComposeFileException(
                f"'{component_name}: missing component property")

        if args['component'] in all_components_by_type:
            args['name'] = component_name
            dict_used_components[component_name] = all_components_by_type[
                args['component']](context, args)
        else:
            raise ComposeFileException(
                f"{component_name}: component {args['component']}' is not a "
                f"valid component identifier")

    return dict_used_components


def merge_dicts(dict_1, dict_2):
    """
    Merge dictionary dict_2 into dict_1. In case of conflict dict_1
    has precedence
    """
    if dict_1 is None:
        return dict_2

    if dict_2 is None:
        return dict_1

    result = dict_1
    for key in dict_2:
        if key in dict_1:
            if isinstance(dict_1[key], dict) and isinstance(dict_2[key], dict):
                merge_dicts(dict_1[key], dict_2[key])
        else:
            result[key] = dict_2[key]
    return result


def copytree(src, dst, ignore_pattern=ignore_patterns('*.pyc', '.svn')):
    """
    Since the original function always creates the directory, to resolve
    the issue a new function had to be created. It's a simple copy and
    was reduced for this case.
    """
    ignore = ignore_pattern
    names = os.listdir(src)
    ignored_names = ignore(src, names)

    if not os.path.exists(dst):
        os.makedirs(dst)

    for name in names:
        if name in ignored_names:
            continue

        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if os.path.isdir(srcname):
            copytree(srcname, dstname)
        else:
            copy2(srcname, dstname)
    copystat(src, dst)


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
