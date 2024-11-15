from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli
from qiskit_aer.primitives import Estimator
from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime import EstimatorOptions
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()

# 2 Qubit Bell State
qc = QuantumCircuit(2)

qc.h(0)
qc.cx(0, 1)

print(qc.draw())

ZZ = Pauli("ZZ")
ZI = Pauli("ZI")
IZ = Pauli("IZ")
XX = Pauli("XX")
XI = Pauli("XI")
IX = Pauli("IX")

observables = [ZZ, ZI, IZ, XX, XI, IX]

estimator = Estimator()
job = estimator.run([qc] * len(observables), observables)
# print(job.result())

data = ["ZZ", "ZI", "IZ", "XX", "XI", "IX"]
values = job.result().values

plt.plot(data, values, "-o")
plt.xlabel("Observables")
plt.ylabel("Expectation Values")
# plt.show()


# n Qubit GHZ state

# n = 10
# for x in range(1, n + 1):
#     print(x)


def get_qc_for_n_qubit(n):
    qc = QuantumCircuit(n)
    qc.h(0)
    for x in range(n - 1):
        qc.cx(x, x + 1)
    return qc


n = 10
qc = get_qc_for_n_qubit(n)
print(qc.draw())

operator_strings = ["Z" + "I" * i + "Z" + "I" * (n - 2 - i) for i in range(n - 1)]
print(operator_strings)

operators = [SparsePauliOp(operator_string) for operator_string in operator_strings]

service = QiskitRuntimeService(
    channel="ibm_quantum", token=os.getenv("Qiskit_API_Token")
)
backend = service.backend("ibm_brisbane")

pass_manager = generate_preset_pass_manager(optimization_level=1, backend=backend)

qc_transpiled = pass_manager.run(qc)
operators_transpiled_list = [op.apply_layout(qc_transpiled.layout) for op in operators]

# Execute on the backend
options = EstimatorOptions()
options.resilience_level = 1
options.optimization_level = 0
options.dynamical_decoupling.enable = True
options.dynamical_decoupling.sequence_type = "XY4"

estimator = EstimatorV2(backend, options=options)
# job = estimator.run([(qc_transpiled, operators_transpiled_list)])
# job_id = job.job_id()
# print(job_id)

# Post process and plotting
job_id = "cvj93w7p7drg008m91yg"
job = service.job(job_id)
data = list(range(1, len(operators) + 1))
result = job.result()[0]
values = result.data.evs
values = [v / values[0] for v in values]

plt.scatter(data, values, marker="o", label="10 Qubit GHZ state")
plt.legend()
plt.show()
