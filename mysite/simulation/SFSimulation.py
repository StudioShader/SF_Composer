import os
import math
from simulation import loqc
import numpy as np

# set the random seed
np.random.seed(42)

# import Strawberry Fields
import strawberryfields as sf
from strawberryfields.ops import *

class Circuit():
    name = "somename"
    backend = "fock"
    backend_options = {"cutoff_dim": 7}

    def simulate(self):
        print(self.backend)
        return None
    
    def initialize_circuit(self):
        return None
    
    def construct_circuit(self, n):
        # n - number of input modes
        boson_sampling = sf.Program(n)
        with boson_sampling.context as q:
            # prepare the input fock states
            Fock(1) | q[0]
            Fock(1) | q[1]
            Vac     | q[2]
            Fock(1) | q[3]

            # rotation gates
            Rgate(0.5719)  | q[0]
            Rgate(-1.9782) | q[1]
            Rgate(2.0603)  | q[2]
            Rgate(0.0644)  | q[3]

            # beamsplitter arrayp
            BSgate(0.7804, 0.8578)  | (q[0], q[1])
            BSgate(0.06406, 0.5165) | (q[2], q[3])
            BSgate(0.473, 0.1176)   | (q[1], q[2])
            BSgate(0.563, 0.1517)   | (q[0], q[1])
            BSgate(0.1323, 0.9946)  | (q[2], q[3])
            BSgate(0.311, 0.3231)   | (q[1], q[2])
            BSgate(0.4348, 0.0798)  | (q[0], q[1])
            BSgate(0.4368, 0.6157)  | (q[2], q[3])

        eng = sf.Engine(backend=self.backend, backend_options=self.backend_options)
        results = eng.run(boson_sampling)

        prog_unitary = sf.Program(4)
        prog_unitary.circuit = boson_sampling.circuit[4:]
        prog_compiled = prog_unitary.compile(compiler="gaussian_unitary")
        S = prog_compiled.circuit[0].op.p[0]
        U = S[:4, :4] + 1j*S[4:, :4]
        print(U)
        return U



