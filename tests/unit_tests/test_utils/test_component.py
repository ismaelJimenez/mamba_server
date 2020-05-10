import pytest

from mamba_server.utils import component
from mamba_server.exceptions import ComponentConfigException, ComponentSettingsException
from mamba_server.components.gui.main.window.window import MainWindow


def test_generate_component_configuration_wo_settings_file_local():
    assert component.generate_component_configuration() == {}


def test_generate_component_configuration_composition_from_file_wo_local():
    assert component.generate_component_configuration(
        config_file={'param_1': 1}) == {
            'param_1': 1
        }


def test_generate_component_configuration_composition_from_local_wo_file():
    assert component.generate_component_configuration(
        local_config={'param_1': 1}) == {
            'param_1': 1
        }


def test_generate_component_configuration_composition_local_precedence_over_file(
):
    assert component.generate_component_configuration(
        config_file={'param_1': 2}, local_config={'param_1': 1}) == {
            'param_1': 1
        }
    assert component.generate_component_configuration(config_file={
        'param_1': 2,
        'param_3': 3
    },
                                                      local_config={
                                                          'param_1': 1,
                                                          'param_2': 2
                                                      }) == {
                                                          'param_1': 1,
                                                          'param_2': 2,
                                                          'param_3': 3
                                                      }


def test_generate_component_configuration_settings_existing_required_parameter(
):
    assert component.generate_component_configuration(
        settings={
            'param_1': {
                'description': 'Param 1 description',
                'required': True
            }
        },
        config_file={'param_1': 1}) == {
            'param_1': 1
        }


def test_generate_component_configuration_settings_non_existing_required_parameter(
):
    with pytest.raises(ComponentConfigException) as excinfo:
        component.generate_component_configuration(settings={
            'param_2': {
                'description': 'Param 2 description',
                'required': True
            }
        },
                                                   config_file={'param_1': 1})

    assert 'missing parameter' in str(excinfo.value)


def test_generate_component_configuration_settings_non_existing_required_parameter_w_component_name(
):
    with pytest.raises(ComponentConfigException) as excinfo:
        component.generate_component_configuration(settings={
            'param_2': {
                'description': 'Param 2 description',
                'required': True
            }
        },
                                                   config_file={
                                                       'param_1':
                                                       1,
                                                       'name':
                                                       'test_component_name'
                                                   })

    assert 'test_component_name' in str(excinfo.value)


def test_generate_component_configuration_settings_missing_required_field():
    with pytest.raises(ComponentSettingsException) as excinfo:
        component.generate_component_configuration(
            settings={'param_2': {
                'description': 'Param 2 description'
            }},
            config_file={'param_1': 1})

    assert 'param_2' in str(excinfo.value)
    assert 'missing required field "required"' in str(excinfo.value)


def test_generate_component_configuration_settings_non_existing_optional_parameter_wo_default(
):
    with pytest.raises(ComponentSettingsException) as excinfo:
        assert component.generate_component_configuration(
            settings={
                'param_2': {
                    'description': 'Param 2 description',
                    'required': False
                }
            },
            config_file={'param_1': 1})

    assert 'param_2' in str(excinfo.value)
    assert 'missing required field "default"' in str(excinfo.value)


def test_generate_component_configuration_settings_non_existing_optional_parameter_w_default(
):
    assert component.generate_component_configuration(
        settings={
            'param_2': {
                'description': 'Param 2 description',
                'required': False,
                'default': 0
            }
        },
        config_file={'param_1': 1}) == {
            'param_1': 1,
            'param_2': 0
        }

