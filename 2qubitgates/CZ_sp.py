
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from qm import SimulationConfig

from configuration import config
print(config)
qmManager = QuantumMachinesManager(host='192.168.116.125', port='80')
QM = qmManager.open_qm(config)  # Generate a Quantum Machine based on the configuration described above


N_avg = 100
t_min = 0
t_max = 100
dt = 4
sweet0 = 0.5
sweet2 = 0.5

with program() as CZ_sp:
    I = declare(fixed)
    t = declare(int)
    n = declare(int)
    detune = declare(fixed)
    set_dc_offset('qb0_flux_line', 'single', sweet0)
    set_dc_offset('qb1_flux_line', 'single', sweet2)
    with for_(n, 0, n < N_avg, n + 1):
        with for_(detune, 0.1, detune < 2.0, detune + 0.1):
            with for_(t, t_min, t < t_max, t+dt):
                set_dc_offset()
                play('pi', 'qb0')
                play('pi', 'qb1')
                play('const' * amp(detune), 'qb1_flux_line', duration=t)

                measure('readout', 'q2_rr', None, demod.full('integW_cos', I, 'out1'))

job = QM.simulate(CZ_sp, SimulationConfig(1000))
samples = job.get_simulated_samples()
