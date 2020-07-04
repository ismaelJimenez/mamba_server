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

First, we should create a new Mamba Server project:
.. code:: console

    mamba start new_mamba_project
   
That will create a new Mamba workspace, with the following structure: 
  
::

    new_mamba_project
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

Now you can run the default project composer file:

.. code:: console

    cd new_mamba_project
    mamba serve -r project
    
This should start the Mamba Server Graphical interface. It is important to notice that Mamba "serve" shall always be executed in the root workspace of the mamba project, in the example in the new_mamba_project folder.

You can also generate a new VISA controller via the command line tool with:


.. code:: console

    mamba generate visa_instrument_driver new_custom_visa_driver
    
To use the newly create controller, you will hace to add it to the project-compose.yml, with:

.. code:: yaml

    services:
        custom_controller
            component: new_custom_visa_driver

Now you are ready to create you own Mamba Server Application. You can use the standard components from mamba-server or create your own ones and add them to the project-compose.yml.
