.. Getting Started

=================================
Getting Started with Mamba Server
=================================

Install
=======

Mamba-Server runs on `Python <http://www.python.org/>`__ 3. To install Mamba-Server:

.. code:: console

    pip3 install mamba-server

Test mamba has been properly installed by running:

.. code:: console

    mamba --version

Make sure the latest version of the Mamba Server is installed.

Create a new Mamba Server Project
=================================

Next start a new Mamba Server Project

.. code:: console

    mamba start my_mamba_server

Then go the the newly created directory and initialize the Mamba Environment:

.. code:: console

    python3 -m venv venv

Once you’ve created a virtual environment, you can activate it.

On Windows, run:

.. code:: console

    venv\Scripts\activate.bat

On Unix or MacOS, run:
.. code:: console

    source venv/bin/activate

Then, install the project requirements:

.. code:: console

    pip install -r requirements.txt

Set Up an Editor
================
You can build a Mamba Server application using any text editor combined with the Mamba command-line tools.

Follow the steps below to get the set by step procedure to set-up the most common code editors: PyCharm or VS Code. If you want to use a different editor, that’s OK, skip ahead to the Test Drive Chapter.

This is a link to the RST Overview: :ref:`RST Set Up PyCharm`

- `Set Up PyCharm for Mamba Server App Development <https://github.com/mamba-framework/mamba-server/blob/master/docs/set_up_pycharm.rst>`__
- Set Up Visual Code for Mamba Server App Development

Create your first component
===========================
In the command line, go to the project root and type

.. code:: console

    mamba generate visa_instrument_driver new_custom_visa_driver

Now, in the "component" folder a new component "new_custom_visa_driver" has been created.

To use the newly create controller, you will have to add it to the project-compose.yml, with:

.. code:: yaml

    services:
        custom_controller
            component: new_custom_visa_driver

Run again the Mamba Server application, and check that you new component is available, in the "Parameter Setter" window.

Now you are ready to create you own Mamba Server Application. You can use the standard components from mamba-server or create your own ones and add them to the project-compose.yml.
