import numpy as np
from copy import deepcopy
from .base import GRN


class StochasticGRN(GRN):
    """Stochastic CPU-based GRN

    Dynamics equations are written mostly in loop form
    """
    concentration = []
    next_concentration = []
    enhance_match = []
    inhibit_match = []
    total_t = 0
    max_dt = 10

    def __init__(self, max_dt = 10):
        self.max_dt = max_dt

    def reset(self):
        self.concentration = np.ones(
            len(self.identifiers)) * (1.0/len(self.identifiers))
        self.next_concentration = np.zeros(len(self.identifiers))
        return self

    def warmup(self, nsteps):
        self.set_input(np.zeros(self.num_input))
        for i in range(nsteps):
            self.step()

    def setup(self):
        self.inhibit_match = np.zeros(
            [len(self.identifiers), len(self.identifiers)])
        self.enhance_match = np.zeros(
            [len(self.identifiers), len(self.identifiers)])
        for k in range(len(self.identifiers)):
            for j in range(len(self.identifiers)):
                self.enhance_match[k, j] = np.abs(
                    self.enhancers[k] - self.identifiers[j])
                self.inhibit_match[k, j] = np.abs(
                    self.inhibitors[k] - self.identifiers[j])

        for k in range(len(self.identifiers)):
            for j in range(len(self.identifiers)):
                self.enhance_match[k, j] = np.exp(
                    - self.beta * self.enhance_match[k, j])
                self.inhibit_match[k, j] = np.exp(
                    - self.beta * self.inhibit_match[k, j])

        self.reset()

    def get_signatures(self):
        return self.enhance_match - self.inhibit_match

    def get_concentrations(self):
        return self.concentration

    def set_input(self, inputs):
        self.concentration[0:self.num_input] = inputs
        return self

    def get_output(self):
        return self.concentration[self.num_input:(
            self.num_output + self.num_input)]

    def step(self):
        if len(self.next_concentration) != len(self.concentration):
            self.next_concentration = np.zeros(len(self.concentration))
        r_total = 0
        for i in range(len(self.identifiers)):
            for j in range(len(self.identifiers)):
                r_total += abs(self.enhance_match[i, j] - self.inhibit_match[i, j]) * self.concentration[i]
        if r_total == 0:
            print(self.concentration)
        r_tot = 1/(r_total+0.0000001)
        self.dt = r_tot * np.log(1/np.random.rand())
        while self.dt > self.max_dt:
            self.dt = r_tot * np.log(1/np.random.rand())
        sum_concentration = 0.0
        for k in range(len(self.identifiers)):
            if k < self.num_input:
                self.next_concentration[k] = self.concentration[k]
            else:
                dConcentration = 0.0
                for j in range(len(self.identifiers)):
                    if not (j >= self.num_input and
                            j < (self.num_output + self.num_input)):
                        dConcentration += (self.concentration[j] * self.enhance_match[j, k]) - (self.concentration[j] * self.inhibit_match[j, k])
                diff = self.delta / len(self.identifiers) * dConcentration
                self.next_concentration[k] = max(0.0,
                                                 self.concentration[k] + diff) * self.dt
                sum_concentration += self.next_concentration[k]
        if sum_concentration > 0:
            for k in range(len(self.identifiers)):
                if k >= self.num_input:
                    self.next_concentration[k] = min(
                        1.0, self.next_concentration[k] / sum_concentration)

        self.concentration = self.next_concentration
        self.total_t+=self.dt
        return self

    def clone(self):
        return deepcopy(self)
