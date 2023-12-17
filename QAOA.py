from qiskit.quantum_info.operators import Operator
from qiskit import *
from qiskit.visualization import plot_histogram
from qiskit.circuit import Gate
import numpy as np
from qiskit.providers.fake_provider import FakeManilaV2
import math
import time

def QAOA(seperator, n, beta, noise=False): 
    #QAOA to solve Max2SAT approximately
    #Here n represents the number of variables in the boolean expressions 
    #--> which also the number of primary qubits in the circuit (one qubit for each of x1,..., xn in the boolean expression)

    QAOA = QuantumCircuit(n + 1, n) #need a helper qubit for the seperator
    QAOA.reset(range(n + 1))

    for i in range(n):
        QAOA.h(i) #preparing for the application of Sep(gamma) and Mix(beta)
    QAOA.x(n) #inverting the last qubit because it is a helper qubit for the seperator

    QAOA.barrier()

    #append the seperator to the circuit -- the seperator represents the input boolean expression for the Max2SAT problem
    sep = seperator.to_instruction()
    QAOA.append(sep, [i for i in range(n + 1)])

    QAOA.barrier()
    
    #creating the mixer -- B = sum_{k = 0}^{n - 1} NOT_k, where NOT_k = I^{x{n - k}} NOT I^{k - 1}, and Mix(B) = e^{-i*beta*B}
    #This evaluates to B = R_x(2*beta)^{xn} -- applying R_x(2*beta) to each qubit in the primary circuit
    mixer = QuantumCircuit(n, name="Mixer")
    mixer.rx(2*beta, [i for i in range(n)])

    #append the mixer to the circuit
    mixer = mixer.to_instruction()
    QAOA.append(mixer, [i for i in range(n)])

    QAOA.barrier()

    #measure and output of the primary qubits
    QAOA.measure([i for i in range(n)], [i for i in range(n)])

    if (not(noise)):
        backend = Aer.get_backend("aer_simulator") #accurate simualtor using no noise
    else:
        backend = FakeManilaV2() #fake noise simnulator to prevent running on actual quantum computer (high queue times) if noise option is chosen
    job = backend.run(QAOA.decompose(), shots=1, memory=True)
    output = job.result().get_memory()[0] #no need to reverse b/c only 1 bit output

    return QAOA, output

def getSeperator(boolean_string, gamma):
    if (boolean_string == "x0"):
        sep = QuantumCircuit(2)
        sep.cp(-1*gamma, 0, 1)
        return sep
    if (boolean_string == "(x0 ^ x1)"): #1-bit boolean expression
        sep = QuantumCircuit(3, name="Seperator")
        sep.mcp(-1*gamma, [0,1], 2)
        return sep
    if (boolean_string == "(x0 ^ x1) ^ (x1 ^ x2)"): #3-bit boolean expression
        sep = QuantumCircuit(4, name="Seperator")
        sep.mcp(-1*gamma, [1,2], 3)
        sep.mcp(-1*gamma, [0,1], 3)
        sep.mcp(-1*gamma, [0,1,2], 3)
        return sep
    if (boolean_string == "(x_0 ^ x_1) ^ (x1 ^ x2) ^ (x2 ^ x3)"):
        sep = QuantumCircuit(5, name="Seperator")
        sep.mcp(-1*gamma, [0,1], 4)
        sep.mcp(-1*gamma, [1,2], 4)
        sep.cp(-1*gamma, [2,3], 4)
        return sep
    if (boolean_string == "(x_0 ^ x_1) ^ (x_1 ^ x_2) ^ (x_2 ^ x_3) ^ (x_3 ^ x_4)"):
        sep = QuantumCircuit(6, name="Seperator")
        sep.mcp(-1*gamma, [0,1], 5)
        sep.mcp(-1*gamma, [1,2], 5)
        sep.mcp(-1*gamma, [2,3], 5)
        sep.mcp(-1*gamma, [3,4], 5)
        return sep

#parameters -- gamma in [0, 2*pi], beta in [0, pi] for seperator, mixer.
gamma = math.pi/4
beta = math.pi/4
boolean_expression = "(x_0 ^ x_1) ^ (x_1 ^ x_2) ^ (x_2 ^ x_3) ^ (x_3 ^ x_4)"
num_qubits = 5 #number of qubits/the number of variables in the boolean expression

#For testing purposes
# n = 500 #iterations of QAOA
# all_outs = []
# for i in range(n):
#     #creating the seperator dependent on gamma
#     sep = getSeperator(boolean_expression, gamma)
    
#     #Applying QAOA for with beta
#     circ, out = QAOA(sep, num_qubits, beta, noise=True)

#     all_outs.append(out)
# print((all_outs.count('11111'))/len(all_outs))

noise = False
#output for mixer with pi/4
beta = math.pi/4
start_time = time.time()
sep = getSeperator(boolean_expression, gamma)
circ,out = QAOA(sep, num_qubits, beta, noise)
print("Time taken is", time.time() - start_time, end="")
print(", and the Output with mixer using beta = pi/4: ", out)

#outout for mixer with pi/2
beta = math.pi/2
start_time = time.time()
sep = getSeperator(boolean_expression, gamma)
circ,out = QAOA(sep, num_qubits, beta, noise)
print("Time taken is", time.time() - start_time, end="")
print(", and the Output with mixer using beta = pi/2: ", out)