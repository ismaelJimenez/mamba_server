import os
import pyvisa

MOCK_FILE = os.path.join('mock', 'visa', 'digitizer', 'ks_m8131a.yaml')
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
        mamba_dir = os.path.join(os.path.dirname(__file__), '..',
                                 '..', 'mamba')
        asd = os.path.join(mamba_dir, MOCK_FILE)
        self.visa_inst = pyvisa.ResourceManager(
            f"{os.path.join(mamba_dir, MOCK_FILE)}@sim").open_resource(
            INST_ADDRESS,
            read_termination='\n')

    def teardown_method(self):
        """ teardown_method called for every method """
        self.visa_inst.close()

    def test_dialogues(self):
        assert self.visa_inst.query('*IDN?') == 'Keysight Technologies, M8131A, SN XXXX'

    def test_properties(self):
        assert self.visa_inst.query(':TIMebase:REFClock?') == 'INT'
        self.visa_inst.write(':TIMebase:REFClock EXT')
        assert self.visa_inst.query(':TIMebase:REFClock?') == 'EXT'

        assert self.visa_inst.query('STAT:OPER:MEMC:COND?') == '0'

        assert self.visa_inst.query(':DIAG:SYNC:TSTamp:VALue? CHAN1') == '123456'
