############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" FTP controller base """

import os
from typing import Optional
from multiprocessing import Process

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from mamba.core.component_base import InstrumentDriver
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import ServiceResponse
from mamba.core.context import Context


class FTPServerComponent(InstrumentDriver):
    """ FTP controller base class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        self._ftp_server: Optional[FTPServer] = None

        if self._configuration.get('ftp', {}).get('user_name') is None:
            raise ComponentConfigException(
                'Missing user name in FTP Configuration')

        if self._configuration.get('ftp', {}).get('user_password') is None:
            raise ComponentConfigException(
                'Missing user password in FTP Configuration')

        if self._configuration.get('ftp', {}).get('port') is None:
            raise ComponentConfigException('Missing port in FTP Configuration')

        self._ftp_folder = None
        if self._configuration.get('ftp',
                                   {}).get('source_folder',
                                           {}).get('global') is not None:
            self._ftp_folder = self._configuration.get('ftp', {}).get(
                'source_folder', {}).get('global')
        elif self._configuration.get('ftp',
                                     {}).get('source_folder',
                                             {}).get('local') is not None:
            self._ftp_folder = os.path.join(
                os.path.dirname(__file__),
                self._configuration.get('ftp', {}).get('source_folder',
                                                       {}).get('local'))
        else:
            raise ComponentConfigException(
                'Missing source folder in FTP Configuration')

    def _instrument_connect(self,
                            result: Optional[ServiceResponse] = None) -> None:

        ftp_config = self._configuration.get('ftp')

        # Instantiate a dummy authorizer for managing 'virtual' users
        authorizer = DummyAuthorizer()

        # Define a new user having full r/w permissions and a read-only
        # anonymous user
        authorizer.add_user(ftp_config['user_name'],
                            ftp_config['user_password'],
                            self._ftp_folder,
                            perm='elradfmwMT')

        # Instantiate FTP handler class
        handler = FTPHandler
        handler.authorizer = authorizer

        # Define a customized banner (string returned when client connects)
        handler.banner = "pyftpdlib based ftpd ready."

        # Specify a masquerade address and the range of ports to use for
        # passive connections.  Decomment in case you're behind a NAT.
        # handler.masquerade_address = '151.25.42.11'
        handler.passive_ports = range(60000, 65535)

        # Instantiate FTP server class and listen on 0.0.0.0:port
        address = ('', ftp_config['port'])
        self._ftp_server = FTPServer(address, handler)

        # set a limit for connections
        self._ftp_server.max_cons = 256
        self._ftp_server.max_cons_per_ip = 5

        # start ftp server
        self._ftp_process = Process(target=self._ftp_server.serve_forever)
        self._ftp_process.start()

    def _instrument_disconnect(self,
                               result: Optional[ServiceResponse] = None
                               ) -> None:
        if self._ftp_server is not None:
            self._ftp_server.close_all()
            self._ftp_process.terminate()
            self._ftp_server = None
