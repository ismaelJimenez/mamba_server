""" Common utilities for testing """
import os
from os.path import dirname
from importlib import import_module
import tempfile
import subprocess
import sys
import yaml

from typing import Optional, Any

from mamba.core.msg import ParameterInfo, ParameterType


class CallbackTestClass:
    """ Common class to test Subject callbacks """
    def __init__(self) -> None:
        self.func_1_times_called = 0
        self.func_1_last_value = None
        self.func_2_times_called = 0
        self.func_2_last_value = None

    def test_func_1(self, rx_on_next: Optional[Any] = None):
        self.func_1_times_called += 1
        self.func_1_last_value = rx_on_next

    def test_func_2(self, rx_on_next: Optional[Any] = None):
        self.func_2_times_called += 1
        self.func_2_last_value = rx_on_next


def get_config_dict(config_file):
    with open(config_file) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def compose_service_info(config):
    service_info = {(key.replace(' ', '_').lower(), service_data.get('type')): {
        'description': service_data.get('description') or '',
        'signature': service_data.get('signature') or [[], None],
        'command': service_data.get('command'),
        'type': service_data.get('type')
    }
            for key, service_data in config['topics'].items()}

    for key, parameter_info in config['parameters'].items():
        if 'get' in parameter_info:
            service_info[(key.replace(' ', '_').lower(), 'get')] = {
                'description': parameter_info.get('description') or '',
                'signature': [[], parameter_info.get('type')],
                'command': (parameter_info.get('get')
            or {}).get('command'),
                'type': 'get'
            }

    return service_info

def get_provider_params_info(config_info, service_info):
    return [
        ParameterInfo(provider=config_info['name'].replace(' ', '_').lower(),
                      param_id=key[0],
                      param_type=ParameterType.Set
                      if key[1] == 'set' else ParameterType.Get,
                      signature=value['signature'],
                      description=value['description'])
        for key, value in service_info.items()
    ]


def get_testenv():
    """Return a OS environment dict suitable to fork processes that need
    to import this installation of Mamba, instead of a system installed one.
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = _get_pythonpath()
    return env


def cmd_exec(self, cmd, *new_args, **kwargs):
    """ Execute external command and return output status """
    with tempfile.TemporaryFile() as out:
        args = (sys.executable, '-m', cmd) + new_args
        return subprocess.call(args,
                               stdout=out,
                               stderr=out,
                               cwd=self.cwd,
                               env=self.env,
                               **kwargs)


def cmd_exec_output(self, cmd, *new_args, **kwargs):
    """ Execute external command and return terminal output """
    with tempfile.TemporaryFile() as out:
        args = (sys.executable, '-m', cmd) + new_args
        subprocess.call(args,
                        stdout=out,
                        stderr=out,
                        cwd=self.cwd,
                        env=self.env,
                        **kwargs)
        out.seek(0)
        return out.read().decode('utf-8')


# Internal


def _get_pythonpath():
    """Return a PYTHONPATH suitable to use in processes so that they find this
    installation of Mamba"""
    mamba_path = import_module('mamba').__path__[0]
    return dirname(mamba_path) + os.pathsep + os.environ.get('PYTHONPATH', '')
