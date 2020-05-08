import inspect

from importlib import import_module
from pkgutil import iter_modules


def walk_modules(path):
    """Loads a module and all its submodules from the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.
    For example: walk_modules('mamba_server.utils')
    """

    mods = []
    mod = import_module(path)
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += walk_modules(fullpath)
            else:
                submod = import_module(fullpath)
                mods.append(submod)
    return mods


def iter_classes(module_name, search_class):
    """Return an iterator over all classes 'search_class' defined in the given module
    that can be instantiated.
    """
    for module in walk_modules(module_name):
        for obj in vars(module).values():
            if inspect.isclass(obj) and \
                    issubclass(obj, search_class) and \
                    obj.__module__ == module.__name__ and \
                    not obj == search_class:
                yield obj


def get_classes_from_module(module, search_class):
    d = {}
    for cls in iter_classes(module, search_class):
        cls_name = cls.__module__.split('.')[-1]
        d[cls_name] = cls
    return d