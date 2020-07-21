import xmlrpc.client

from mamba.core.context import Context
from mamba.marketplace.components.simulator.rpc.xmlrpc_mock import XmlRpcMock


class TestClass:
    def test_xmlrpc_tmtc(self):
        self.mock = XmlRpcMock(Context())
        self.mock.initialize()

        with xmlrpc.client.ServerProxy('http://localhost:8090') as client:
            assert client.query('parameter_1') == 1
            assert client.query('parameter_2') == '2'
            assert client.query('parameter_3') == 3

            assert client.query('idn') == 'Mamba Framework,XMLRPC Mock,1.0'

            assert client.write('cls') == 0

            assert client.write('parameter_1 11') == 0
            assert client.write('parameter_2 22') == 0
            assert client.write('parameter_3 33') == 0

            assert client.query('parameter_1') == '11'
            assert client.query('parameter_2') == '22'
            assert client.query('parameter_3') == '33'

            with xmlrpc.client.ServerProxy(
                    'http://localhost:8090') as client_2:
                assert client_2.query('parameter_1') == '11'
                assert client_2.query('parameter_2') == '22'
                assert client_2.query('parameter_3') == '33'

        self.mock._close()

    def test_error_handling(self):
        self.mock = XmlRpcMock(Context(),
                               local_config={'instrument': {
                                   'port': 8905
                               }})
        self.mock.initialize()

        with xmlrpc.client.ServerProxy('http://localhost:8905') as client:
            assert client.query('parameter_4') == 'key-error'

        self.mock._close()
