import os
import pyvisa

MOCK_FILE = os.path.join('marketplace', 'components', 'switch_matrix',
                         'keysight_z2091c', 'visa_sim.yml')
INST_ADDRESS = 'TCPIP0::1.2.3.4::INSTR'


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        pass

    def teardown_class(self):
        """ teardown_class called once for the class """
        pass

    def setup_method(self):
        """ setup_method called for every method """
        mamba_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                 '..', '..', 'mamba')
        asd = os.path.join(mamba_dir, MOCK_FILE)
        self.visa_inst = pyvisa.ResourceManager(
            f"{os.path.join(mamba_dir, MOCK_FILE)}@sim").open_resource(
                INST_ADDRESS, write_termination='\n', read_termination='\n')

        self.visa_inst.encoding = 'utf-8'

    def teardown_method(self):
        """ teardown_method called for every method """
        self.visa_inst.close()

    def test_dialogues(self):
        assert self.visa_inst.query(
            '*IDN?'
        ) == 'Keysight Technologies,Z2091C-001,US56400131,1.1.6450.15113'

    def test_properties(self):
        assert self.visa_inst.query('SYST:ERR?') == '0, No Error'
        assert self.visa_inst.query('CONF:DIG:WIDTH? (@2001)') == 'BYTE'
        assert self.visa_inst.query('*OPC?') == '1'
