import time
import http.client

from mamba.core.context import Context
from mamba.marketplace.components.simulator.http_flask_server_sim import FlaskServerMock


class TestClass:
    def test_flask_tmtc(self):
        self.mock = FlaskServerMock(Context())
        self.mock.initialize()

        time.sleep(.1)

        conn = http.client.HTTPConnection('127.0.0.1', 5000)

        conn.request("GET", "/query?param=parameter_1")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'1'
        conn.request("GET", "/query?param=parameter_2")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'2'
        conn.request("GET", "/query?param=parameter_3")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'3'

        conn.request("GET", "/query?param=idn")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'Mamba Framework,HTTP Flask Mock,1.0'

        conn.request("GET", "/query?param=cls")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'None'

        conn.request("PUT", "/write?param=parameter_1&value=11")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'OK'
        conn.request("PUT", "/write?param=parameter_2&value=22")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'OK'
        conn.request("PUT", "/write?param=parameter_3&value=33")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'OK'

        conn.request("GET", "/query?param=parameter_1")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'11'
        conn.request("GET", "/query?param=parameter_2")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'22'
        conn.request("GET", "/query?param=parameter_3")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'33'

        conn_2 = http.client.HTTPConnection('127.0.0.1', 5000)

        conn_2.request("GET", "/query?param=parameter_1")
        response = conn_2.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'11'
        conn_2.request("GET", "/query?param=parameter_2")
        response = conn_2.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'22'
        conn_2.request("GET", "/query?param=parameter_3")
        response = conn_2.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'33'

        self.mock._close()

    def test_error_handling(self):
        self.mock = FlaskServerMock(
            Context(), local_config={'instrument': {
                'port': 5001
            }})
        self.mock.initialize()

        time.sleep(.1)

        conn = http.client.HTTPConnection('127.0.0.1', 5001)

        conn.request("GET", "/query?param=wrong")
        response = conn.getresponse()
        assert response.status == 404
        assert response.reason == 'NOT FOUND'
        assert response.read() == b'{"error":"Not found"}\n'

        conn.request("GET", "/wrong?param=parameter_3")
        response = conn.getresponse()
        assert response.status == 404
        assert response.reason == 'NOT FOUND'
        assert response.read() == b'{"error":"Not found"}\n'

        conn.request("GET", "/query?param=parameter_3&value=1")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'3'

        conn.request("PUT", "/query?param=parameter_3&value=1")
        response = conn.getresponse()
        assert response.status == 405
        assert response.reason == 'METHOD NOT ALLOWED'

        self.mock._close()
