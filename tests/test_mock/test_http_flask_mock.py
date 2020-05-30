import time
import http.client

from mamba.core.context import Context
from mamba.mock.http.flask_server_mock import FlaskServerMock


class TestClass:
    def test_flask_tmtc(self):
        self.mock = FlaskServerMock(Context())
        self.mock.initialize()

        time.sleep(.1)

        conn = http.client.HTTPConnection('127.0.0.1', 5000)

        conn.request("GET", "/get?param=property_1")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'1'
        conn.request("PUT", "/set?param=property_1&value=2")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'OK'
        conn.request("GET", "/get?param=property_1")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'2'

        conn.request("GET", "/get?param=property_2")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'2'
        conn.request("PUT", "/set?param=property_2&value=test_str")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'OK'
        conn.request("GET", "/get?param=property_2")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b"test_str"

        conn.request("GET", "/get?param=property_3")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'3'
        conn.request("PUT", "/set?param=property_3&value=none")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'OK'
        conn.request("GET", "/get?param=property_3")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b"none"

        self.mock._close()

    def test_error_handling(self):
        self.mock = FlaskServerMock(Context(), local_config={'port': 5001})
        self.mock.initialize()

        time.sleep(.1)

        conn = http.client.HTTPConnection('127.0.0.1', 5001)

        conn.request("GET", "/get?param=wrong")
        response = conn.getresponse()
        assert response.status == 404
        assert response.reason == 'NOT FOUND'
        assert response.read() == b'{"error":"Not found"}\n'

        conn.request("GET", "/wrong?param=property_3")
        response = conn.getresponse()
        assert response.status == 404
        assert response.reason == 'NOT FOUND'
        assert response.read() == b'{"error":"Not found"}\n'

        conn.request("GET", "/get?param=property_3&value=1")
        response = conn.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        assert response.read() == b'3'

        conn.request("PUT", "/get?param=property_3&value=1")
        response = conn.getresponse()
        assert response.status == 405
        assert response.reason == 'METHOD NOT ALLOWED'

        self.mock._close()
