import os
import math
from simulation import loqc
import numpy as np
import json

# from simulation import data

# set the random seed
np.random.seed(42)

# import Strawberry Fields
import strawberryfields as sf
from strawberryfields.ops import *


class Circuit:
    name = "somename"
    backend = "fock"
    backend_options = {"cutoff_dim": 7}
    simulation_option = "gaussian_unitary"
    structured_devices = []
    cons = []
    probabilities = []

    def __init__(self, name, backend, simulation_option) -> None:
        self.name = name
        self.backend = backend
        self.simulation_option = simulation_option

    def simulate(self):
        return None

    def initialize_circuit(self):
        return None

    def check_modes(self, modes, id, port):
        n = len(modes)
        for i in range(n):
            mode = modes[i]
            if mode[0] == id and mode[1] == port:
                return i
        return -1

    def check_for_current_connections(self, modes, device):
        if device.type == "BS":
            ports = {"hybrid0": -1, "hybrid1": -1, "hybrid2": -1, "hybrid3": -1}
            for con in self.cons:
                if con[0]["node"] == device.id:
                    ports[con[0]["port"]] = self.check_modes(
                        modes, con[1]["node"], con[1]["port"]
                    )
            if ports["hybrid0"] != -1 and ports["hybrid2"] != -1:
                return [ports["hybrid0"], ports["hybrid2"]], [
                    [device.id, "hybrid1"],
                    [device.id, "hybrid3"],
                ]
            return None, None
        if device.type == "PS" or device.type == "S":
            ports = {"hybrid0": -1, "hybrid1": -1}
            for con in self.cons:
                if con[0]["node"] == device.id:
                    ports[con[0]["port"]] = self.check_modes(
                        modes, con[1]["node"], con[1]["port"]
                    )
            if ports["hybrid0"] != -1:
                return [ports["hybrid0"]], [[device.id, "hybrid1"]]
            return None, None
        if device.type == "OUT":
            ports = {"hybrid0": -1}
            for con in self.cons:
                if con[0]["node"] == device.id:
                    ports[con[0]["port"]] = self.check_modes(
                        modes, con[1]["node"], con[1]["port"]
                    )
            if ports["hybrid0"] != -1:
                return [ports["hybrid0"]], [[device.id, "endport"]]
            return None, None
        # returning number of modes in 'modes'
        # TODO: RAISE ERROR
        return None, None

    def beautify_matrix(self, U):
        result = "Scheme unitary matrix: <br />"
        for s in U:
            result += str(s)
            result += "<br />"
        return result

    def beautify_state_probs(self, photons, modes):
        all_states = []
        for i in range(photons + 3):
            all_states += self.get_all_perms(i, modes)
        result = ""
        results = []
        for state in all_states:
            results += [(state, self.get_prob_by_state(state))]
        results.sort(key=lambda a: a[1], reverse=True)
        print(results)
        for state, prob in results:
            result += str(state) + ": " + str(prob) + " <br />"
        return result

    def get_all_perms(self, photons, modes):
        if modes == 0:
            return [[]]
        if photons == 0:
            return [[0] * modes]
        if modes == 1:
            return [[photons]]
        result = []
        for i in range(photons + 1):
            rest = photons - i
            alls = self.get_all_perms(rest, modes - 1)
            for one in alls:
                one += [i]
            result += alls
        return result

    def get_prob_by_state(self, state):
        current = self.probabilities
        for i in range(len(state)):
            current = current[state[i]]
        return current

    def construct_circuit(self, project_key, devices, connections):
        modes = []
        number_of_input_modes = 0
        number_of_output_modes = 0
        number_of_photons = 0
        for dev in devices:
            if dev.type == "IN":
                modes += [[dev.id, "hybrid0", dev]]
                self.structured_devices.append([dev, [len(modes) - 1]])
                number_of_input_modes += 1
            if dev.type == "OUT":
                number_of_output_modes += 1

        if number_of_input_modes != number_of_output_modes:
            return "None circuit was constructed"

        for c in connections:
            con = json.loads(c.line_json)
            self.cons += [[con[0]["source"], con[0]["target"]]]
            self.cons += [[con[0]["target"], con[0]["source"]]]

        queue = []
        for dev in devices:
            if dev.type != "IN":
                queue.append(dev)
        max = 100
        iter = 0
        while len(queue) > 0 and iter < max:
            iter += 1
            current_device = queue.pop(0)
            device_modes, next_modes = self.check_for_current_connections(
                modes, current_device
            )
            if device_modes != None:
                self.structured_devices.append([current_device, device_modes])
                for i in range(len(device_modes)):
                    modes[device_modes[i]] = next_modes[i]
            else:
                queue.append(current_device)

        n = number_of_input_modes
        # n - number of input modes
        boson_sampling = sf.Program(n)
        with boson_sampling.context as q:
            # prepare the input states
            for dev_info in self.structured_devices:
                if dev_info[0].type == "IN":
                    number_of_photons += int(dev_info[0].n)
                    if self.simulation_option == "state_probabilities":
                        print("Fock", dev_info[0].n, "  ", dev_info[1][0])
                        Fock(int(dev_info[0].n)) | q[dev_info[1][0]]
                elif dev_info[0].type == "BS":
                    print(
                        "BS",
                        dev_info[0].theta,
                        "  ",
                        dev_info[1][0],
                        "  ",
                        dev_info[1][1],
                    )
                    BSgate(float(dev_info[0].theta), float(dev_info[0].phi)) | (
                        q[dev_info[1][0]],
                        q[dev_info[1][1]],
                    )
                elif dev_info[0].type == "PS":
                    print("Rgate", dev_info[0].phi, "  ", dev_info[1][0])
                    Rgate(float(dev_info[0].phi)) | q[dev_info[1][0]]
                elif dev_info[0].type == "S":
                    print("Sgate", dev_info[0].theta, "  ", dev_info[1][0])
                    Sgate(float(dev_info[0].theta), float(dev_info[0].phi)) | q[
                        dev_info[1][0]
                    ]
                elif dev_info[0].type == "OUT":
                    if (
                        self.simulation_option != "state_probabilities"
                        and self.simulation_option != "gaussian_unitary"
                    ):
                        MeasureFock() | q[dev_info[1][0]]
        if self.simulation_option == "state_probabilities":
            eng = sf.Engine(backend=self.backend, backend_options=self.backend_options)
            results = eng.run(boson_sampling)
            probs = results.state.all_fock_probs()
            self.probabilities = probs
            print(number_of_photons, number_of_input_modes)
            return self.beautify_state_probs(number_of_photons, number_of_input_modes)
        else:
            prog_unitary = sf.Program(number_of_input_modes)
            prog_unitary.circuit = boson_sampling.circuit
            prog_compiled = prog_unitary.compile(compiler="gaussian_unitary")
            S = prog_compiled.circuit[0].op.p[0]
            U = (
                S[:number_of_input_modes, :number_of_input_modes]
                + 1j * S[number_of_input_modes:, :number_of_input_modes]
            )
            print(self.beautify_matrix(U))
            return self.beautify_matrix(U)
        # return self.beautify_matrix(U), str(results.samples)
        return "The error on the backend occured"
