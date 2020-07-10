.. command_line

Mamba Command Line Interface
============================

The Mamba command-line interface (CLI) is the go-to tool for developing Mamba server applications.

Help
----

The Mamba CLI ships with command documentation that is accessible with the --help flag.

.. code:: console

    mamba --help
    mamba <command> --help

Mamba Start
-----------
The Mamba Start command creates a new Mamba Server project that can run in any OS.

.. code:: console

    mamba start <project_name>

Mamba Start will create a new mamba server workspace with the following structure:

::

    <project_name>
    ├── __init__.py
    ├── mamba.cfg
    ├── component/
    │   ├── gui/
    │   │   └── __init__.py
    │   └── instrument_driver/
    │       └── __init__.py
    ├── composer/
    │   └── project-compose.yml
    ├── log/
    │   └── __init__.py
    └── mock/
        └── __init__.py

All project specific components will be contained in the "component" folder. In the "composer" folder we will have all our project composition files. A new log will be created in the "logs" folder in every mamba server run. And the "mocks" folder will contain all equipment simulators, if any.

Mamba Serve
-----------
Mamba Server has to be run inside the mamba server project directory, and it will start a mamba server from a given composer file.

.. code:: console

    mamba serve -r <composer_file>

Mamba start generates a default composer file (project-compose.yml), that can be used as a template to generate the project specific composer file.

.. code:: console

    mamba serve -r project

After execution of the previous command the Mamba Server Graphical interface loading window shall be shown:

.. image:: images/main_gui.png

And afterward the Mamba GUI:

.. image:: images/loading_window.png


Mamba Generate
--------------
Mamba generate makes very easy the creation of standard new components.

.. code:: console

    mamba generate <component_template> <component_name>

For example, a new VISA component can be created as:

.. code:: console

    mamba generate visa_instrument_driver new_custom_visa_driver

Now, in the "component" folder a new component "new_custom_visa_driver" has been created.

To use the newly create controller, you will have to add it to the project-compose.yml, with:

.. code:: yaml

    services:
        custom_controller
            component: new_custom_visa_driver

Now you are ready to create you own Mamba Server Application. You can use the standard components from mamba-server or create your own ones and add them to the project-compose.yml.

Mamba Dump IF
-------------
The Mamba CLI dump_if command is very useful to export the mamba interface to a Mamba Client project.

.. code:: console

    mamba dump_if -r <composer_file>

This will generate an mamba_if.yml file that can be imported directly into a mamba client application.

Troubleshooting
---------------

To troubleshoot issues with the Mamba CLI, the following may be useful:

- Make sure the latest version of the Mamba CLI is installed. Get the installed version by running mamba --version
- Be sure to run "mamba <command>" in your project directory.

