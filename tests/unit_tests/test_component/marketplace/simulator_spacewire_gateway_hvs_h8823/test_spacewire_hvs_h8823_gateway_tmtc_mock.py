import socket
import time

from mamba.core.context import Context
from mamba.marketplace.components.simulator.spacewire_gateway_hvs_h8823_tmtc_sim import H8823GatewayTmTcMock


class TestClass:
    def test_simple_tmtc(self):
        self.mock = H8823GatewayTmTcMock(
            Context(),
            local_config={'instrument': {
                'port': {
                    'tc': 23456,
                    'tm': 23457
                }
            }})
        self.mock.initialize()

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect(("localhost", 23456))

            # Create a socket (SOCK_STREAM means a TCP socket)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tm:
                # Connect to server and send data
                sock_tm.connect(("localhost", 23457))

                # Test cyclic telemetry reception
                time.sleep(.1)
                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 20
                assert 'SPWG_TM_SPW_AUTOSTART 0 0 0 0' in received
                assert 'SPWG_TM_SPW_CRED_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_DISC_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_ENABLED 0 0 0 0' in received
                assert 'SPWG_TM_SPW_ESC_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_PAR_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_STS 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RUNNING 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_BYTE_CTR 0 0 0 0' in received
                assert 'SWPG_TM_SPW_RX_EEP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_EOP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_RATE 0 0 0 0' in received
                assert 'SPWG_TM_SPW_START 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TCP_CONN 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TIMECODE_ENABLED 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_BYTE_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_CLK 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_EEP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_EOP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_TICK_CTR 0 0 0 0' in received

                sock.sendall(
                    bytes('SPWG_TC_SPW_LINK_ENA_0\nSPWG_TC_SPW_LINK_ENA_2\n',
                          "utf-8"))
                time.sleep(.1)
                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 2
                assert 'SPWG_TC_SPW_LINK_ENA_0' in received
                assert 'SPWG_TC_SPW_LINK_ENA_2' in received

                sock.sendall(
                    bytes(
                        'SPWG_TC_SPW_LINK_AUTO_ENA_1\nSPWG_TC_SPW_LINK_AUTO_ENA_3\n',
                        "utf-8"))
                time.sleep(.1)
                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 2
                assert 'SPWG_TC_SPW_LINK_AUTO_ENA_1' in received
                assert 'SPWG_TC_SPW_LINK_AUTO_ENA_3' in received

                sock.sendall(
                    bytes(
                        'SPWG_TC_SPW_TIMECODE_ENA_0\nSPWG_TC_SPW_TIMECODE_ENA_2\n',
                        "utf-8"))
                sock.sendall(
                    bytes('SPWG_TC_SPW_TX_CLK_0 10\nSPWG_TC_SPW_TX_CLK_2 20\n',
                          "utf-8"))
                sock.sendall(
                    bytes(
                        'SPWG_TC_SPW_LINK_START_ENA_1\nSPWG_TC_SPW_LINK_START_ENA_3\n',
                        "utf-8"))

                time.sleep(.1)
                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 6
                assert 'SPWG_TC_SPW_TIMECODE_ENA_0' in received
                assert 'SPWG_TC_SPW_TIMECODE_ENA_2' in received
                assert 'SPWG_TC_SPW_TX_CLK_0 10' in received
                assert 'SPWG_TC_SPW_TX_CLK_2 20' in received
                assert 'SPWG_TC_SPW_LINK_START_ENA_1' in received
                assert 'SPWG_TC_SPW_LINK_START_ENA_3' in received

                time.sleep(5.1)
                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 20
                assert 'SPWG_TM_SPW_AUTOSTART 0 1 0 1' in received
                assert 'SPWG_TM_SPW_CRED_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_DISC_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_ENABLED 1 0 1 0' in received
                assert 'SPWG_TM_SPW_ESC_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_PAR_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_STS 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RUNNING 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_BYTE_CTR 0 0 0 0' in received
                assert 'SWPG_TM_SPW_RX_EEP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_EOP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_RATE 0 0 0 0' in received
                assert 'SPWG_TM_SPW_START 0 1 0 1' in received
                assert 'SPWG_TM_SPW_TCP_CONN 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TIMECODE_ENABLED 1 0 1 0' in received
                assert 'SPWG_TM_SPW_TX_BYTE_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_CLK 10 0 20 0' in received
                assert 'SPWG_TM_SPW_TX_EEP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_EOP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_TICK_CTR 0 0 0 0' in received

                sock.sendall(
                    bytes('SPWG_TC_SPW_LINK_ENA_1\nSPWG_TC_SPW_LINK_ENA_3\n',
                          "utf-8"))
                sock.sendall(
                    bytes(
                        'SPWG_TC_SPW_LINK_AUTO_ENA_0\nSPWG_TC_SPW_LINK_AUTO_ENA_2\n',
                        "utf-8"))
                sock.sendall(
                    bytes(
                        'SPWG_TC_SPW_TIMECODE_ENA_1\nSPWG_TC_SPW_TIMECODE_ENA_3\n',
                        "utf-8"))
                sock.sendall(
                    bytes('SPWG_TC_SPW_TX_CLK_1 11\nSPWG_TC_SPW_TX_CLK_3 30\n',
                          "utf-8"))
                sock.sendall(
                    bytes(
                        'SPWG_TC_SPW_LINK_START_ENA_0\nSPWG_TC_SPW_LINK_START_ENA_2\n',
                        "utf-8"))

                time.sleep(.1)

                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 10

                time.sleep(5.1)

                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 20
                assert 'SPWG_TM_SPW_AUTOSTART 1 1 1 1' in received
                assert 'SPWG_TM_SPW_CRED_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_DISC_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_ENABLED 1 1 1 1' in received
                assert 'SPWG_TM_SPW_ESC_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_PAR_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_STS 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RUNNING 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_BYTE_CTR 0 0 0 0' in received
                assert 'SWPG_TM_SPW_RX_EEP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_EOP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_RATE 0 0 0 0' in received
                assert 'SPWG_TM_SPW_START 1 1 1 1' in received
                assert 'SPWG_TM_SPW_TCP_CONN 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TIMECODE_ENABLED 1 1 1 1' in received
                assert 'SPWG_TM_SPW_TX_BYTE_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_CLK 10 11 20 30' in received
                assert 'SPWG_TM_SPW_TX_EEP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_EOP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_TICK_CTR 0 0 0 0' in received

                sock.sendall(
                    bytes('SPWG_TC_SPW_LINK_DIS_1\nSPWG_TC_SPW_LINK_DIS_3\n',
                          "utf-8"))
                sock.sendall(
                    bytes(
                        'SPWG_TC_SPW_LINK_AUTO_DIS_0\nSPWG_TC_SPW_LINK_AUTO_DIS_2\n',
                        "utf-8"))
                sock.sendall(
                    bytes(
                        'SPWG_TC_SPW_TIMECODE_DIS_1\nSPWG_TC_SPW_TIMECODE_DIS_3\n',
                        "utf-8"))
                sock.sendall(
                    bytes(
                        'SPWG_TC_SPW_LINK_START_DIS_0\nSPWG_TC_SPW_LINK_START_DIS_2\n',
                        "utf-8"))

                time.sleep(.1)

                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 8

                time.sleep(5.1)

                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 20
                assert 'SPWG_TM_SPW_AUTOSTART 0 1 0 1' in received
                assert 'SPWG_TM_SPW_CRED_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_DISC_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_ENABLED 1 0 1 0' in received
                assert 'SPWG_TM_SPW_ESC_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_PAR_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_STS 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RUNNING 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_BYTE_CTR 0 0 0 0' in received
                assert 'SWPG_TM_SPW_RX_EEP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_EOP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_RATE 0 0 0 0' in received
                assert 'SPWG_TM_SPW_START 0 1 0 1' in received
                assert 'SPWG_TM_SPW_TCP_CONN 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TIMECODE_ENABLED 1 0 1 0' in received
                assert 'SPWG_TM_SPW_TX_BYTE_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_CLK 10 11 20 30' in received
                assert 'SPWG_TM_SPW_TX_EEP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_EOP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_TICK_CTR 0 0 0 0' in received

                sock.sendall(
                    bytes(
                        'SPWG_TC_SPW_LINK_RESET_1\nSPWG_TC_SPW_LINK_RESET_3\n',
                        "utf-8"))
                sock.sendall(
                    bytes('SPWG_TC_SPW_RST_CTR_1\nSPWG_TC_SPW_RST_CTR_3\n',
                          "utf-8"))

                time.sleep(.1)
                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 4

                sock.sendall(
                    bytes('SPWG_TC_TX_RAW_0 ABCD\nSPWG_TC_TX_RAW_1 01ADB\n',
                          "utf-8"))
                time.sleep(.1)
                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 2
                assert 'SPWG_TC_TX_RAW_0 ABCD' in received
                assert 'SPWG_TC_TX_RAW_1 01ADB' in received

                sock.sendall(
                    bytes(
                        'SPWG_TC_TX_RAW_EEP_0 ABCD\nSPWG_TC_TX_RAW_EEP_1 01ADB\n',
                        "utf-8"))
                time.sleep(.1)
                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 2
                assert 'SPWG_TC_TX_RAW_EEP_0 ABCD' in received
                assert 'SPWG_TC_TX_RAW_EEP_1 01ADB' in received

                sock.sendall(
                    bytes(
                        'SPWG_TC_TX_RAW_PART_0 ABCD\nSPWG_TC_TX_RAW_PART_1 01ADB\n',
                        "utf-8"))
                time.sleep(.1)
                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 2
                assert 'SPWG_TC_TX_RAW_PART_0 ABCD' in received
                assert 'SPWG_TC_TX_RAW_PART_1 01ADB' in received

                sock.sendall(bytes('SPWG_TC_TM_PERIOD 1\n', "utf-8"))

                time.sleep(5.2)

                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) >= 20

                time.sleep(1.1)

                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) >= 20

                # Create a socket (SOCK_STREAM means a TCP socket)
                with socket.socket(socket.AF_INET,
                                   socket.SOCK_STREAM) as sock_2_tm:
                    # Connect to server and send data
                    sock_2_tm.connect(("localhost", 23457))

                    # Test cyclic telemetry reception
                    time.sleep(.1)

                    # Receive data from the server and shut down
                    received = str(sock_2_tm.recv(1024), "utf-8")
                    assert len(received.split('\n')[:-1]) == 20
                    assert 'SPWG_TM_SPW_AUTOSTART 0 1 0 1' in received
                    assert 'SPWG_TM_SPW_CRED_ERR_CTR 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_DISC_ERR_CTR 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_ENABLED 1 0 1 0' in received
                    assert 'SPWG_TM_SPW_ESC_ERR_CTR 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_PAR_ERR_CTR 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_STS 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_RUNNING 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_RX_BYTE_CTR 0 0 0 0' in received
                    assert 'SWPG_TM_SPW_RX_EEP_CTR 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_RX_EOP_CTR 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_RX_RATE 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_START 0 1 0 1' in received
                    assert 'SPWG_TM_SPW_TCP_CONN 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_TIMECODE_ENABLED 1 0 1 0' in received
                    assert 'SPWG_TM_SPW_TX_BYTE_CTR 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_TX_CLK 10 11 20 30' in received
                    assert 'SPWG_TM_SPW_TX_EEP_CTR 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_TX_EOP_CTR 0 0 0 0' in received
                    assert 'SPWG_TM_SPW_RX_TICK_CTR 0 0 0 0' in received

        self.mock._close()

    def test_error_handling(self):
        self.mock = H8823GatewayTmTcMock(
            Context(),
            local_config={'instrument': {
                'port': {
                    'tc': 23458,
                    'tm': 23459
                }
            }})
        self.mock.initialize()

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect(("localhost", 23458))

            # Create a socket (SOCK_STREAM means a TCP socket)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tm:
                # Connect to server and send data
                sock_tm.connect(("localhost", 23459))

                # Test cyclic telemetry reception
                time.sleep(.1)
                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 20

                # Test wrong number or parameters
                sock.sendall(bytes('SPWG_TC_SPW_TX_CLK_1\n', "utf-8"))

                time.sleep(.1)
                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert 'SPWG_ER_SPW_TX_CLK_1' in received

                time.sleep(5.1)
                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert len(received.split('\n')[:-1]) == 20
                assert 'SPWG_TM_SPW_AUTOSTART 0 0 0 0' in received
                assert 'SPWG_TM_SPW_CRED_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_DISC_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_ENABLED 0 0 0 0' in received
                assert 'SPWG_TM_SPW_ESC_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_PAR_ERR_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_STS 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RUNNING 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_BYTE_CTR 0 0 0 0' in received
                assert 'SWPG_TM_SPW_RX_EEP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_EOP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_RATE 0 0 0 0' in received
                assert 'SPWG_TM_SPW_START 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TCP_CONN 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TIMECODE_ENABLED 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_BYTE_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_CLK 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_EEP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_TX_EOP_CTR 0 0 0 0' in received
                assert 'SPWG_TM_SPW_RX_TICK_CTR 0 0 0 0' in received

        self.mock._close()
