import os
import pyvisa

MOCK_FILE = os.path.join('marketplace', 'components', 'power_supply',
                         'keysight_n5700', 'visa_sim.yml')
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

    def teardown_method(self):
        """ teardown_method called for every method """
        self.visa_inst.close()

    def test_dialogues(self):
        assert self.visa_inst.query(
            '*IDN?') == 'Keysight Technologies,5700A,12345,A.11.22,A.33.44'

    def test_properties(self):
        self.visa_inst.write('*RST')

        assert self.visa_inst.query('CURR?') == '0'
        self.visa_inst.write('CURR 1')
        assert self.visa_inst.query('CURR?') == '1'

        assert self.visa_inst.query('VOLT?') == '0'
        self.visa_inst.write('VOLT 5')
        assert self.visa_inst.query('VOLT?') == '5'

        assert self.visa_inst.query('VOLT:PROT:LEV?') == '0'
        self.visa_inst.write('VOLT:PROT:LEV 10')
        assert self.visa_inst.query('VOLT:PROT:LEV?') == '10'

        assert self.visa_inst.query('OUTP:STAT?') == '0'
        self.visa_inst.write('OUTP:STAT 1')
        assert self.visa_inst.query('OUTP:STAT?') == '1'
