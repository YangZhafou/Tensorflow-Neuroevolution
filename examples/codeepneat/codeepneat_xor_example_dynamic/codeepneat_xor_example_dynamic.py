from absl import app, flags, logging

import tfne

flags.DEFINE_string('logging_level',
                    default=None, help='TODO')
flags.DEFINE_string('config_file',
                    default=None, help='TODO')
flags.DEFINE_string('backup_dir',
                    default=None, help='TODO')
flags.DEFINE_integer('max_generations',
                     default=None, help='TODO')
flags.DEFINE_float('max_fitness',
                   default=None, help='TODO')


def codeepneat_xor_example(_):
    """"""
    # Set standard configuration specific to TFNE but not the neuroevolution process
    logging_level = logging.INFO
    config_file_path = './codeepneat_xor_example_dynamic_config.cfg'
    backup_dir_path = './tfne_backups/'
    max_generations = 100
    max_fitness = None

    # Read in optionally supplied flags, changing the just set standard configuration
    if flags.FLAGS.logging_level is not None:
        logging_level = flags.FLAGS.logging_level
    if flags.FLAGS.config_file is not None:
        config_file_path = flags.FLAGS.config_file
    if flags.FLAGS.backup_dir is not None:
        backup_dir_path = flags.FLAGS.backup_dir
    if flags.FLAGS.max_generations is not None:
        max_generations = flags.FLAGS.max_generations
    if flags.FLAGS.max_fitness is not None:
        max_fitness = flags.FLAGS.max_fitness

    # Set logging, parse config
    logging.set_verbosity(logging_level)
    config = tfne.parse_configuration(config_file_path)

    # Initialize the environment and the specific NE algorithm
    environment = tfne.environments.XOREnvironment(config)
    ne_algorithm = tfne.algorithms.CoDeepNEAT(config, environment)

    # Initialize evolution engine and supply config as well as initialized NE elements. As CoDeepNEAT currently only
    # supports single-instance evaluation, set num_cpus and num_gpus to 1
    engine = tfne.EvolutionEngine(ne_algorithm=ne_algorithm,
                                  backup_dir_path=backup_dir_path,
                                  num_cpus=1,
                                  num_gpus=1,
                                  max_generations=max_generations,
                                  max_fitness=max_fitness)

    # Start training process, returning the best genome when training ends
    best_genome = engine.train()

    # Serialize and save genotype and Tensorflow model to demonstrate serialization/deserialization
    genome_file_path = best_genome.save_genotype(save_dir_path='./')
    best_genome.save_model(save_dir_path='./')

    # Load and deserialize the saved genotype and apply it again to the chosen environment
    print("Best Genome returned by evolution:\n")
    deserialized_genome = tfne.load_genome(genome_file_path=genome_file_path)
    print(deserialized_genome)
    environment.replay_genome(deserialized_genome)


if __name__ == '__main__':
    app.run(codeepneat_xor_example)
