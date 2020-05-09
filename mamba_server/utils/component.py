"""Component handling utility functions"""

from mamba_server.exceptions import ComponentSettingsException, ComponentConfigException


def generate_component_configuration(component_name="",
                                     settings=None,
                                     config_file=None,
                                     local_config=None):
    """Returns a dictionary with the component configuration.

    Local configurations passed via launch file have precedence over configuration file settings.

    The configuration dictionary is composed of the local configuration, then the configurations
    from file that are not in local, and then the settings that are neither in file nor in local
    but have default values.

    Args:
        component_name (str, optional): The component name. Only used for feedback on the error
                                        handling.
        settings (dict, optional): The dictionary with the description of the component settings.
        config_file (dict, optional): The dictionary of the component settings retrieved from
                                      component.config.json.
        local_config (dict, optional): The dictionary of the component settings passed via
                                       launch file.

    Returns:
        dict: The validated component configuration parameters.

    Raises:
        ComponentConfigException: If a required setting is not present in local nor
                                  in file parameters.
        ComponentSettingsException: If a setting is missing the 'required' field or the
                                    'default' field if it is not a required parameter.

    """

    settings = settings or {}
    config_file = config_file or {}
    local_config = local_config or {}

    composed_config = dict(list(config_file.items()) + list(local_config.items()))

    for key, value in settings.items():
        if key not in composed_config:
            if 'required' not in value:
                raise ComponentSettingsException(
                    f'Setting "{key}" is missing required field "required"')
            if value['required']:
                raise ComponentConfigException(
                    f'Component "{component_name}" configuration is missing parameter "{key}"')
            if (not value['required']) and ('default' not in value):
                raise ComponentSettingsException(
                    f'Setting "{key}" is missing required field "default"')

            composed_config[key] = value['default']

    return composed_config
