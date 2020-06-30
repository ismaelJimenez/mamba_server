.. command_line

Mamba Command Line
==================

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
    │   │   └── __init__.py
    ├── composer/ 
    │   └── project-compose.yml
    ├── log/ 
    │   └── __init__.py
    └── mock/ 
        └── __init__.py

