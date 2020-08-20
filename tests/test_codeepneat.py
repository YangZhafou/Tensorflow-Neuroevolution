import os
import tempfile

import tfne


def sanity_check_algorithm_state(ne_algorithm):
    """"""
    best_genome = ne_algorithm.get_best_genome()
    assert 100 >= best_genome.get_fitness() > 0


def test_codeepneat_1():
    """"""
    # Create test config
    config = tfne.parse_configuration(os.path.dirname(__file__) + '/test_codeepneat_1_config.cfg')
    environment = tfne.environments.XOREnvironment(config)
    ne_algorithm = tfne.algorithms.CoDeepNEAT(config, environment)

    # Start test
    engine = tfne.EvolutionEngine(ne_algorithm=ne_algorithm,
                                  backup_dir_path=tempfile.gettempdir(),
                                  num_cpus=1,
                                  num_gpus=1,
                                  max_generations=10,
                                  max_fitness=None)
    engine.train()

    # Sanity check state of the algorithm
    sanity_check_algorithm_state(ne_algorithm)


def test_codeepneat_2():
    """"""
    # Create test config
    config = tfne.parse_configuration(os.path.dirname(__file__) + '/test_codeepneat_2_config.cfg')
    environment = tfne.environments.XOREnvironment(config)
    ne_algorithm = tfne.algorithms.CoDeepNEAT(config, environment)

    # Start test
    engine = tfne.EvolutionEngine(ne_algorithm=ne_algorithm,
                                  backup_dir_path=tempfile.gettempdir(),
                                  num_cpus=1,
                                  num_gpus=1,
                                  max_generations=6,
                                  max_fitness=None)
    engine.train()

    # Sanity check state of the algorithm
    sanity_check_algorithm_state(ne_algorithm)


def test_codeepneat_3():
    """"""
    # Create test config
    config = tfne.parse_configuration(os.path.dirname(__file__) + '/test_codeepneat_3_config.cfg')
    environment = tfne.environments.XOREnvironment(config)
    ne_algorithm = tfne.algorithms.CoDeepNEAT(config, environment)

    # Start test
    engine = tfne.EvolutionEngine(ne_algorithm=ne_algorithm,
                                  backup_dir_path=tempfile.gettempdir(),
                                  num_cpus=1,
                                  num_gpus=1,
                                  max_generations=6,
                                  max_fitness=None)
    engine.train()

    # Sanity check state of the algorithm
    sanity_check_algorithm_state(ne_algorithm)


def test_codeepneat_4():
    """"""
    # Create test config
    config = tfne.parse_configuration(os.path.dirname(__file__) + '/test_codeepneat_4_config.cfg')
    environment = tfne.environments.MNISTEnvironment(config)
    ne_algorithm = tfne.algorithms.CoDeepNEAT(config, environment)

    # Start test
    engine = tfne.EvolutionEngine(ne_algorithm=ne_algorithm,
                                  backup_dir_path=tempfile.gettempdir(),
                                  num_cpus=1,
                                  num_gpus=1,
                                  max_generations=2,
                                  max_fitness=None)
    engine.train()

    # Sanity check state of the algorithm
    sanity_check_algorithm_state(ne_algorithm)


def test_codeepneat_5():
    """"""
    # Create test config
    config = tfne.parse_configuration(os.path.dirname(__file__) + '/test_codeepneat_4_config.cfg')
    environment = tfne.environments.CIFAR10Environment(config)
    ne_algorithm = tfne.algorithms.CoDeepNEAT(config, environment)

    # Start test
    engine = tfne.EvolutionEngine(ne_algorithm=ne_algorithm,
                                  backup_dir_path=tempfile.gettempdir(),
                                  num_cpus=1,
                                  num_gpus=1,
                                  max_generations=2,
                                  max_fitness=None)
    engine.train()

    # Sanity check state of the algorithm
    sanity_check_algorithm_state(ne_algorithm)
