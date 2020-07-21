import os
import pytest
import copy
import time
from ftplib import FTP, error_perm
from tempfile import mkdtemp

from rx import operators as op

from mamba.core.testing.utils import compose_service_info, get_config_dict, CallbackTestClass, get_provider_params_info
from mamba.core.context import Context
from mamba.marketplace.components.networking.ftp_server import FTPServerComponent
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import Empty, ServiceRequest, ServiceResponse, ParameterType

component_path = os.path.join('marketplace', 'components', 'networking',
                              'ftp_server')


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        self.mamba_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                       '..', '..', 'mamba')

        self.default_component_config = get_config_dict(
            os.path.join(self.mamba_path, component_path, 'config.yml'))

        self.default_service_info = compose_service_info(
            self.default_component_config)

    def teardown_class(self):
        """ teardown_class called once for the class """
        pass

    def setup_method(self):
        """ setup_method called for every method """
        self.context = Context()
        self.context.set(
            'mamba_dir',
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                         'mamba'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_wo_context(self):
        """ Test component behaviour without required context """
        with pytest.raises(TypeError) as excinfo:
            FTPServerComponent()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_w_default_context_component_creation(self):
        """ Test component creation behaviour with default context """
        component = FTPServerComponent(self.context)

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {}
        assert component._shared_memory_getter == {}
        assert component._shared_memory_setter == {}
        assert component._parameter_info == {}
        assert component._inst is None
        assert component._ftp_server is None
        assert 'ftp_example_folder' in component._ftp_folder

        assert component._instrument.address == 'None'
        assert component._instrument.port == 0
        assert component._instrument.encoding == 'ascii'
        assert component._instrument.terminator_write == '\r\n'
        assert component._instrument.terminator_read == '\n'

    def test_w_default_context_component_initialization(self):
        """ Test component initialization behaviour with default context """
        component = FTPServerComponent(self.context)
        component.initialize()

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {'connected': 0}
        assert component._shared_memory_getter == {'connected': 'connected'}
        assert component._shared_memory_setter == {'connect': 'connected'}
        assert component._parameter_info == {
            ('connect', ParameterType.set): {
                'description':
                'Connection status to '
                'TCP server',
                'instrument_command':
                None,
                'signature': [[{
                    'connect': {
                        'type': 'int',
                        'valid': [0, 1]
                    }
                }], None],
                'type':
                ParameterType.set
            },
            ('connected', ParameterType.get): {
                'description': 'Connection status to '
                'TCP server',
                'instrument_command': None,
                'signature': [[], 'int'],
                'type': ParameterType.get
            }
        }
        assert component._inst is None
        assert component._ftp_server is None
        assert 'ftp_example_folder' in component._ftp_folder

        assert component._instrument.address == 'None'
        assert component._instrument.port == 0
        assert component._instrument.encoding == 'ascii'
        assert component._instrument.terminator_write == '\r\n'
        assert component._instrument.terminator_read == '\n'

    def test_w_custom_context(self):
        """ Test component creation behaviour with default context """
        component = FTPServerComponent(self.context,
                                  local_config={
                                      'name': 'custom_name',
                                      'ftp': {
                                          'user_name': 'test_name',
                                          'user_password': 54321,
                                          'port': 1212,
                                          'source_folder': {
                                              'global': '/test/test_folder'
                                          }
                                      },
                                  })
        component.initialize()

        custom_component_config = copy.deepcopy(self.default_component_config)
        custom_component_config['name'] = 'custom_name'
        custom_component_config['ftp']['user_name'] = 'test_name'
        custom_component_config['ftp']['user_password'] = 54321
        custom_component_config['ftp']['port'] = 1212
        custom_component_config['ftp']['source_folder'] = {
            'global': '/test/test_folder',
            'local': 'ftp_example_folder'
        }

        # Test default configuration load
        assert component._configuration == custom_component_config

        # Test custom variables default values
        assert component._shared_memory == {'connected': 0}
        assert component._shared_memory_getter == {'connected': 'connected'}
        assert component._shared_memory_setter == {'connect': 'connected'}
        assert component._parameter_info == {
            ('connect', ParameterType.set): {
                'description':
                'Connection status to '
                'TCP server',
                'instrument_command':
                None,
                'signature': [[{
                    'connect': {
                        'type': 'int',
                        'valid': [0, 1]
                    }
                }], None],
                'type':
                ParameterType.set
            },
            ('connected', ParameterType.get): {
                'description': 'Connection status to '
                'TCP server',
                'instrument_command': None,
                'signature': [[], 'int'],
                'type': ParameterType.get
            }
        }

        custom_service_info = compose_service_info(custom_component_config)
        assert component._parameter_info == custom_service_info
        assert component._inst is None
        assert component._ftp_server is None
        assert component._ftp_folder == '/test/test_folder'

        assert component._instrument.address == 'None'
        assert component._instrument.port == 0
        assert component._instrument.encoding == 'ascii'
        assert component._instrument.terminator_write == '\r\n'
        assert component._instrument.terminator_read == '\n'

    def test_w_wrong_custom_context(self):
        # Test with missing user name
        with pytest.raises(ComponentConfigException) as excinfo:
            FTPServerComponent(self.context,
                          local_config={
                              'ftp': {
                                  'user_name': None
                              }
                          }).initialize()
        assert "Missing user name in FTP Configuration" in str(excinfo.value)

        # Test with missing user password
        with pytest.raises(ComponentConfigException) as excinfo:
            FTPServerComponent(self.context,
                          local_config={
                              'ftp': {
                                  'user_password': None
                              }
                          }).initialize()
        assert "Missing user password in FTP Configuration" in str(
            excinfo.value)

        # Test with missing port
        with pytest.raises(ComponentConfigException) as excinfo:
            FTPServerComponent(self.context, local_config={
                'ftp': {
                    'port': None
                }
            }).initialize()
        assert "Missing port in FTP Configuration" in str(excinfo.value)

        # Test with missing source folder
        with pytest.raises(ComponentConfigException) as excinfo:
            FTPServerComponent(self.context,
                          local_config={
                              'ftp': {
                                  'source_folder': {
                                      'local': None
                                  }
                              }
                          }).initialize()
        assert "Missing source folder in FTP Configuration" in str(
            excinfo.value)

    def test_io_signature_publication(self):
        """ Test component io_signature observable """
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_service_signature'].subscribe(
            dummy_test_class.test_func_1)

        component = FTPServerComponent(self.context)
        component.initialize()

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1

        received_params_info = str([
            str(parameter_info)
            for parameter_info in dummy_test_class.func_1_last_value
        ])
        expected_params_info = str([
            str(parameter_info) for parameter_info in get_provider_params_info(
                self.default_component_config, self.default_service_info)
        ])
        assert received_params_info == expected_params_info

    def test_io_service_request_observer_local_folder(self):
        """ Test component io_service_request observer """
        # Start FTP Client
        ftp = FTP()  # connect to host, default port

        # Start Test
        component = FTPServerComponent(self.context)
        component.initialize()
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # 1 - Test that component only gets activated for implemented services
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='ftp_server',
                           id='NOT_EXISTING',
                           type='any',
                           args=[]))

        assert dummy_test_class.func_1_times_called == 0
        assert dummy_test_class.func_1_last_value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='NOT_EXISTING',
                           id='connect',
                           type='any',
                           args=[]))

        assert dummy_test_class.func_1_times_called == 0
        assert dummy_test_class.func_1_last_value is None

        # 2 - Test client connection before server has started
        with pytest.raises(ConnectionRefusedError) as excinfo:
            ftp.connect(host='localhost', port=2121)

        assert str(excinfo.value) == '[Errno 111] Connection refused'

        # 3 - Start FTP Server
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='ftp_server',
                           id='connect',
                           type=ParameterType.set,
                           args=['1']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 4 - Test FTP Read command
        ftp.connect(host='localhost', port=2121)
        ftp.login(user='user',
                  passwd='12345')  # user anonymous, passwd anonymous@
        ftp.cwd('folder_1')  # change into directory
        ftp.retrlines('LIST')  # list directory contents
        ftp.cwd('..')  # change into directory

        with open('README', 'wb') as fp:
            ftp.retrbinary('RETR folder_1/README', fp.write)

        assert os.path.exists('README')

        # 5 - Test FTP Write command

        with open(
                os.path.join(os.path.dirname(__file__), 'ftp_test_utils',
                             'README_2'), 'rb') as fp:
            ftp.storbinary('STOR folder_1/example_write_2', fp)

        with open(
                os.path.join(os.path.dirname(__file__), 'ftp_test_utils',
                             'README_2_RETRIEVED'), 'wb') as fp:
            ftp.retrbinary('RETR folder_1/example_write_2', fp.write)

        assert os.path.join(os.path.dirname(__file__), 'ftp_test_utils',
                            'README_2_RETRIEVED')

        # 6 - Clean Workspace

        ftp.delete('folder_1/example_write_2')
        os.remove(
            os.path.join(os.path.dirname(__file__), 'ftp_test_utils',
                         'README_2_RETRIEVED'))
        os.remove('README')

        # 7 - Stop FTP Server
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='ftp_server',
                           id='connect',
                           type=ParameterType.set,
                           args=['0']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 2
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['quit'].on_next(Empty())

        time.sleep(1)

    def test_io_service_request_observer_global_folder(self):
        """ Test component io_service_request observer """
        # Create FTP Folder structure
        temp_path = mkdtemp()
        os.mkdir(os.path.join(temp_path, 'folder_2'))
        f = open(os.path.join(temp_path, 'folder_2', 'README_GLOBAL'), "w+")
        f.close()

        # Start FTP Client
        ftp = FTP()  # connect to host, default port

        # Start Test
        component = FTPServerComponent(
            self.context,
            local_config={'ftp': {
                'source_folder': {
                    'global': temp_path
                }
            }})
        component.initialize()
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # 1 - Test that component only gets activated for implemented services
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='ftp_server',
                           id='NOT_EXISTING',
                           type='any',
                           args=[]))

        assert dummy_test_class.func_1_times_called == 0
        assert dummy_test_class.func_1_last_value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='NOT_EXISTING',
                           id='connect',
                           type='any',
                           args=[]))

        assert dummy_test_class.func_1_times_called == 0
        assert dummy_test_class.func_1_last_value is None

        # 2 - Test client connection before server has started
        with pytest.raises(ConnectionRefusedError) as excinfo:
            ftp.connect(host='localhost', port=2121)

        assert str(excinfo.value) == '[Errno 111] Connection refused'

        # 3 - Start FTP Server
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='ftp_server',
                           id='connect',
                           type=ParameterType.set,
                           args=['1']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 4 - Test FTP Read command
        ftp.connect(host='localhost', port=2121)
        ftp.login(user='user',
                  passwd='12345')  # user anonymous, passwd anonymous@

        with pytest.raises(error_perm) as excinfo:
            ftp.cwd('folder_1')  # change into directory

        assert str(excinfo.value) == '550 No such file or directory.'

        ftp.cwd('folder_2')  # change into directory
        ftp.retrlines('LIST')  # list directory contents
        ftp.cwd('..')  # change into directory

        with open('README', 'wb') as fp:
            ftp.retrbinary('RETR folder_2/README_GLOBAL', fp.write)

        assert os.path.exists('README')

        # 5 - Test FTP Write command

        with open(
                os.path.join(os.path.dirname(__file__), 'ftp_test_utils',
                             'README_2'), 'rb') as fp:
            ftp.storbinary('STOR folder_2/example_write_2', fp)

        with open(
                os.path.join(os.path.dirname(__file__), 'ftp_test_utils',
                             'README_2_RETRIEVED'), 'wb') as fp:
            ftp.retrbinary('RETR folder_2/example_write_2', fp.write)

        assert os.path.exists(
            os.path.join(os.path.dirname(__file__), 'ftp_test_utils',
                         'README_2_RETRIEVED'))

        # 6 - Clean Workspace

        ftp.delete('folder_2/example_write_2')
        os.remove(
            os.path.join(os.path.dirname(__file__), 'ftp_test_utils',
                         'README_2_RETRIEVED'))
        os.remove('README')

        # 7 - Stop FTP Server
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='ftp_server',
                           id='connect',
                           type=ParameterType.set,
                           args=['0']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 2
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['quit'].on_next(Empty())

        time.sleep(1)
