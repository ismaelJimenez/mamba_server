import os
import pyvisa

MOCK_FILE = os.path.join('marketplace', 'components', 'signal_generator',
                         'rs_smb100b', 'visa_sim.yml')
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
                INST_ADDRESS, read_termination='\n')

    def teardown_method(self):
        """ teardown_method called for every method """
        self.visa_inst.close()

    def test_dialogues(self):
        assert self.visa_inst.query(
            '*IDN?') == 'Rohde&Schwarz,SMB100B,11400.1000K02/0,4.00.033'

    def test_properties(self):
        assert self.visa_inst.query('OUTP?') == '0'
        self.visa_inst.write('OUTP 1')
        assert self.visa_inst.query('OUTP?') == '1'

        assert self.visa_inst.query('FREQuency:MODE?') == 'CW'
        self.visa_inst.write('FREQuency:MODE FIX')
        assert self.visa_inst.query('FREQuency:MODE?') == 'FIX'

        assert self.visa_inst.query('FREQuency:CW?') == '100000000'
        self.visa_inst.write('FREQuency:CW 200000000')
        assert self.visa_inst.query('FREQuency:CW?') == '200000000'

        assert self.visa_inst.query('POWer?') == '-30'
        self.visa_inst.write('POWer 0')
        assert self.visa_inst.query('POWer?') == '0'

        assert self.visa_inst.query('SOURce:ROSCillator:SOURce?') == 'INT'
        self.visa_inst.write('SOURce:ROSCillator:SOURce EXT')
        assert self.visa_inst.query('SOURce:ROSCillator:SOURce?') == 'EXT'
