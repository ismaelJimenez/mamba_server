import xmlrpc.client

from mamba.core.context import Context
from mamba.mock.rpc.xmlrpc_mock import XmlRpcMock


class TestClass:
    def test_xmlrpc_tmtc(self):
        self.mock = XmlRpcMock(Context())
        self.mock.initialize()

        with xmlrpc.client.ServerProxy('http://localhost:8090') as client:
            assert client.get_tm('telemetry_1') == 1
            assert client.get_tm('telemetry_2') == '2'
            assert client.get_tm('telemetry_3') == 3

        self.mock._close()

    def test_error_handling(self):
        self.mock = XmlRpcMock(Context(),
                               local_config={'instrument': {
                                   'port': 8091
                               }})
        self.mock.initialize()

        with xmlrpc.client.ServerProxy('http://localhost:8091') as client:
            assert client.get_tm('telemetry_4') == 'key-error'

        self.mock._close()
