import numpy as np

from qualang_tools.config.components import *
from qualang_tools.config.builder import ConfigBuilder
from qm.program._qua_config_schema import load_config
from qualang_tools.config.parameters import Parameter, ConfigVars

cb = ConfigBuilder()
c_vars = ConfigVars()

con1 = Controller("con1")

cb.add([con1])
zero_wf = ConstantWaveform("zero_wf", 0)


def raised_cos(a: float, duration: int):
    s = duration / 2
    t = np.arange(duration)
    return a * (1.0 / (2 * s)) * (1 + np.cos((t - s) * np.pi / s))


for i in range(2):
    qb_name = "qb" + str(i)
    cb.add(FluxTunableTransmon(
        qb_name,
        I=con1.analog_output(2 * i + 1),
        Q=con1.analog_output(2 * i + 2),
        flux_port=con1.analog_output(i + 5),
        intermediate_frequency=c_vars.parameter(qb_name + "_IF"),
    ))

    res_name = "qb" + str(i) + "_rr"
    cb.add(ReadoutResonator(
        res_name,
        outputs=[con1.analog_output(9), con1.analog_output(10)],
        inputs=[con1.analog_input(9), con1.analog_input(10)],
        intermediate_frequency=c_vars.parameter(res_name + "_IF"),
    ))

    cb.component(qb_name).add(
        ControlPulse(
            "x",
            [
                ArbitraryWaveform(
                    qb_name + "_x_I", c_vars.parameter(qb_name + "_x_I_samples")
                ),
                zero_wf,
            ],
            32,
        )
    )
    cb.component(qb_name).add(
        ControlPulse(
            "sx",
            [
                ArbitraryWaveform(
                    qb_name + "_sx_I", 0.5 * c_vars.parameter(qb_name + "_x_I_samples")
                ),
                zero_wf,
            ],
            32,
        )
    )
    cb.component(qb_name).add(
        ControlPulse(
            "net_zero",
            [
                ArbitraryWaveform(
                    qb_name + "_net_zero",
                    c_vars.parameter(qb_name + "_net_zero_samples"),
                )
            ],
            32,
        )
    )
    cb.component(qb_name).add(
        ControlPulse(
            "const",
            [
                ConstantWaveform(
                    qb_name + "_const_wf",
                    c_vars.parameter(qb_name + "_flux_line_const_wf_sample"),
                )
            ],
            32,
        )
    ).lo_frequency = c_vars.parameter(qb_name + "_LO")

    cb.component(res_name).add(
        MeasurePulse(
            "const",
            [
                ConstantWaveform(
                    res_name + "_const_wf",
                    c_vars.parameter(res_name + "_const_wf_sample"),
                ),
                zero_wf,
            ],
            200,
        )
    ).lo_frequency = c_vars.parameter(res_name + "_LO")

params = dict()
for i in range(2):
    params["qb{}_IF".format(i)] = 1e7
    params["qb{}_LO".format(i)] = 3e9
    params["qb{}_rr_IF".format(i)] = 1e7
    params["qb{}_rr_LO".format(i)] = 4e9
    params["qb{}_x_I_samples".format(i)] = raised_cos(1.0, 32)
    params["qb{}_net_zero_samples".format(i)] = np.random.rand(32)
    params["qb{}_flux_line_const_wf_sample".format(i)] = np.random.rand()
    params["qb{}_rr_const_wf_sample".format(i)] = np.random.rand()

c_vars.set(**params)

config = cb.build()
print(cb.build())
load_config(cb.build())