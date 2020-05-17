""" The GuiPlugin components make services available to the application """

import os

from mamba_server.components.interface import ComponentInterface


class GuiPluginInterface(ComponentInterface):
    """ The GuiPlugin components make services available to the application """
    def __init__(self, folder, context):
        super(GuiPluginInterface, self).__init__(folder, context)
