import os
import pyvisa

MOCK_FILE = os.path.join('marketplace', 'components', 'amplifier',
                         'keysight_33502a', 'visa_sim.yml')
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
            '*IDN?') == 'Agilent Technologies,33502A,MY12345678,1.00-01-01-01'

    def test_properties(self):
        assert self.visa_inst.query('ROUT1:PATH?') == 'DIR'
        self.visa_inst.write('ROUT1:PATH AMPL')
        assert self.visa_inst.query('ROUT1:PATH?') == 'AMPL'

        assert self.visa_inst.query('ROUT2:PATH?') == 'DIR'
        self.visa_inst.write('ROUT2:PATH AMPL')
        assert self.visa_inst.query('ROUT2:PATH?') == 'AMPL'

        assert self.visa_inst.query('OUTP1:STATe?') == '0'
        self.visa_inst.write('OUTP1 1')
        assert self.visa_inst.query('OUTP1:STATe?') == '1'

        assert self.visa_inst.query('OUTP2:STATe?') == '0'
        self.visa_inst.write('OUTP2 1')
        assert self.visa_inst.query('OUTP2:STATe?') == '1'

        assert self.visa_inst.query('INP1:COUP?') == 'DC'
        self.visa_inst.write('INP1:COUP AC')
        assert self.visa_inst.query('INP1:COUP?') == 'AC'

        assert self.visa_inst.query('INP2:COUP?') == 'DC'
        self.visa_inst.write('INP2:COUP AC')
        assert self.visa_inst.query('INP2:COUP?') == 'AC'

        assert self.visa_inst.query('INP1:IMP?') == '1000000'
        self.visa_inst.write('INP1:IMP 2000')
        assert self.visa_inst.query('INP1:IMP?') == '2000'

        assert self.visa_inst.query('INP2:IMP?') == '1000000'
        self.visa_inst.write('INP2:IMP 1000')
        assert self.visa_inst.query('INP2:IMP?') == '1000'
