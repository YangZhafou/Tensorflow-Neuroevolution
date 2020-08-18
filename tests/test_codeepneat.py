import os
import tempfile

import tfne


def test_codeepneat():
    """"""
    # Initialize the environment and the specific NE algorithm
    config = tfne.parse_configuration(os.path.dirname(__file__) + '/test_codeepneat_config_1.cfg')
    environment = tfne.environments.XOREnvironment(config)
    ne_algorithm = tfne.algorithms.CoDeepNEAT(config, environment)

    # Initialize evolution engine and supply config as well as initialized NE elements. As CoDeepNEAT currently only
    # supports single-instance evaluation, set num_cpus and num_gpus to 1
    engine = tfne.EvolutionEngine(ne_algorithm=ne_algorithm,
                                  backup_dir_path=tempfile.gettempdir(),
                                  num_cpus=1,
                                  num_gpus=1,
                                  max_generations=10,
                                  max_fitness=None)

    # Start training process, returning the best genome when training ends
    best_genome = engine.train()

    best_genome_fitness = environment.eval_genome_fitness(best_genome)
    assert 100.0 >= best_genome_fitness > 0
