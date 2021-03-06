from pygrn.grns import ClassicGRN
from pygrn.problems import Random, Counter
from pygrn import evolution, config
import numpy as np


def test_init():
    problem = Counter()
    pop = evolution.Population(lambda: ClassicGRN(),
                               problem.nin, problem.nout)
    assert len(pop.offspring) == config.POPULATION_SIZE
    assert len(pop.species) == 0


def test_evaluation():
    problem = Counter()
    pop = evolution.Population(lambda: ClassicGRN(),
                               problem.nin, problem.nout)
    pop.evaluate(problem)
    assert problem.count == config.POPULATION_SIZE


def test_speciation():
    problem = Counter()
    config.INITIALIZATION_DUPLICATION = 8
    pop = evolution.Population(lambda: ClassicGRN(),
                               problem.nin, problem.nout)
    pop.evaluate(problem)
    pop.speciation()
    assert len(pop.offspring) == 0
    assert len(pop.species) > 0
    print([len(sp.individuals) for sp in pop.species])
    assert problem.count == config.POPULATION_SIZE


def test_best():
    problem = Counter()
    pop = evolution.Population(lambda: ClassicGRN(),
                               problem.nin, problem.nout)
    pop.evaluate(problem)
    assert problem.count == config.POPULATION_SIZE
    pop.speciation()
    best_fit, best_ind = pop.get_best()
    assert problem.count == config.POPULATION_SIZE
    assert best_fit > 0


def test_thresholds():
    problem = Random()
    config.INITIALIZATION_DUPLICATION = 8
    pop = evolution.Population(lambda: ClassicGRN(),
                               problem.nin, problem.nout)
    pop.evaluate(problem)
    pop.speciation()
    pop.adjust_thresholds()
    assert np.any([sp.species_threshold for sp in pop.species] !=
                  config.START_SPECIES_THRESHOLD)


def test_offspring_count():
    problem = Random()
    config.INITIALIZATION_DUPLICATION = 8
    pop = evolution.Population(lambda: ClassicGRN(),
                               problem.nin, problem.nout)
    pop.evaluate(problem)
    pop.speciation()
    pop.adjust_thresholds()
    pop.set_offspring_count()
    assert (np.sum([sp.num_offspring for sp in pop.species]) ==
            config.POPULATION_SIZE)


def test_make_offspring():
    problem = Counter()
    config.INITIALIZATION_DUPLICATION = 8
    pop = evolution.Population(lambda: ClassicGRN(),
                               problem.nin, problem.nout)
    pop.evaluate(problem)
    pop.speciation()
    pop.adjust_thresholds()
    pop.set_offspring_count()
    pop.make_offspring()
    assert problem.count == config.POPULATION_SIZE
    assert len(pop.offspring) == config.POPULATION_SIZE
    assert np.any([ind.evaluated for ind in pop.offspring])
    assert np.any([~ind.evaluated for ind in pop.offspring])
