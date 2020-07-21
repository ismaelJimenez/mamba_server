import os
import pyvisa

MOCK_FILE = os.path.join('marketplace', 'components', 'switch_matrix',
                         'keysight_34980a', 'visa_sim.yml')
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
            '*IDN?') == 'AGILENT TECHNOLOGIES,34980A,12345,1.11–2.22–3.33–4.44'

    def test_properties(self):
        assert self.visa_inst.query('SYST:ERR?') == '0, No Error'
        assert self.visa_inst.query('FETCh?') == 'some_value'
        assert self.visa_inst.query('MEAS:RES? (@1101)') == '100'
        assert self.visa_inst.query('SOUR:FUNC:ENAB? (@1101)') == '1'
        assert self.visa_inst.query('SOUR:FUNC:FREQ? (@1101)') == '1000'

        self.visa_inst.write('ROUT:CLOS (@1102)')
        assert self.visa_inst.query('ROUT:CLOSe? (@1101)') == '(@1102)'

        self.visa_inst.write('ROUT:OPEN (@1102)')
        assert self.visa_inst.query('ROUT:OPEN? (@1101)') == '(@1102)'

        self.visa_inst.write('CONF:VOLT:DC 1,0.003,(@4009)')
        assert self.visa_inst.query('MEAS:VOLT:DC? 1,0.001,(@4009)') == '1'
        self.visa_inst.write('CONF:VOLT:DC 0,0.003,(@4009)')
        assert self.visa_inst.query('MEAS:VOLT:DC? 1,0.001,(@4009)') == '0'
