import time
import os
from queue import Queue
from operator import itemgetter
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dotenv import load_dotenv
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit.transpiler import PassManager

load_dotenv()

maze = [
    [1, 0, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 1, 1, 0, 1, 1],
    [1, 0, 1, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1],
]

maze = np.array(maze)

# Qiskit init
# if os.getenv("Qiskit_API_Token"):
#     print("API Token Successfully Loaded")
# else:
#     raise Exception(
#         "Qiskit API Token not found. Please verify it is correctly declared in your .env file."
#     )

# try:
#     print("Establishing connection...")
#     service = QiskitRuntimeService(
#         channel="ibm_quantum",
#         token=os.getenv("Qiskit_API_Token"),
#     )
#     print("Connection Established.")
# except Exception as e:
#     print(e)
# backend = service.backend(name="ibm_brisbane")
# print(backend.num_qubits)


# Grover's
def phase_oracle(circuit, register):
    circuit.cz(register[0], register[1])


def inversion_about_average(circuit, register):
    circuit.h(register)
    circuit.x(register)
    circuit.h(register[1])
    circuit.cx(register[0], register[1])
    circuit.h(register[1])
    circuit.x(register)
    circuit.h(register)


qr = QuantumRegister(2)
cr = ClassicalRegister(2)
oracle = QuantumCircuit(qr)
phase_oracle(oracle, qr)
print(oracle.draw())
qaverage = QuantumCircuit(qr)
inversion_about_average(qaverage, qr)
print(qaverage.draw())

grovercircuit = QuantumCircuit(qr, cr)
grovercircuit.h(qr)
phase_oracle(grovercircuit, qr)
print(grovercircuit.draw())
inversion_about_average(grovercircuit, qr)
print(grovercircuit.draw())
grovercircuit.measure(qr, cr)
print(grovercircuit.draw())

backend = AerSimulator()
job = backend.run(grovercircuit, shots=1024)
results = job.result()
answer = results.get_counts()
print(answer)
print(plot_histogram(answer))
