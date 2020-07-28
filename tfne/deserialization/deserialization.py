import json

import tensorflow as tf

from tfne.encodings.base_genome import BaseGenome
from tfne.populations.base_population import BasePopulation
from tfne.deserialization.codeepneat.codeepneat_deserialization import deserialize_codeepneat_genome
from tfne.deserialization.codeepneat.codeepneat_deserialization import deserialize_codeepneat_population


def load_genome(genome_file_path=None, serialized_genome=None, dtype=None, **kwargs) -> BaseGenome:
    """"""
    if genome_file_path is not None and serialized_genome is not None:
        # Either a file path or an already loaded genome are to be supplied. Not both.
        raise RuntimeError("load_genome function either requires the path to a genome file that is to be loaded and"
                           "deserialized or an already loaded but still serialized genome. Currently both "
                           "'genome_file_path' and 'serialized_genome' arguments are supplied. Aborting.")
    elif serialized_genome is None:
        # Load file, determine the type of genome, then deserialize and return it
        with open(genome_file_path) as genome_file:
            serialized_genome = json.load(genome_file)

    # If no dtype supplied, use default one
    if dtype is None:
        dtype = tf.keras.backend.floatx()

    if serialized_genome['genome_type'] == 'CoDeepNEAT':
        return deserialize_codeepneat_genome(serialized_genome, dtype, **kwargs)
    else:
        raise NotImplementedError("Deserialization of a TFNE genome of type '{}' not yet implemented"
                                  .format(serialized_genome['genome_type']))


def load_population(population_file_path=None, serialized_population=None, dtype=None, **kwargs) -> BasePopulation:
    """"""
    if population_file_path is not None and serialized_population is not None:
        # Either a file path or an already loaded population are to be supplied. Not both.
        raise RuntimeError("load_population function either requires the path to a population file that is to be "
                           "loaded and deserialized or an already loaded but still serialized population. Currently "
                           "both 'population_file_path' and 'serialized_population' arguments are supplied. Aborting.")
    elif serialized_population is None:
        # Load file, determine the type of population, then deserialize and return it
        with open(population_file_path) as population_file:
            serialized_population = json.load(population_file)

    # If no dtype supplied, use default one
    if dtype is None:
        dtype = tf.keras.backend.floatx()

    if serialized_population['population_type'] == 'CoDeepNEAT':
        return deserialize_codeepneat_population(serialized_population, dtype, **kwargs)
    else:
        raise NotImplementedError("Deserialization of a TFNE population of type '{}' not yet implemented"
                                  .format(serialized_population['population_type']))


def load_population_from_state(state_file_path=None, serialized_state=None, dtype=None, **kwargs) -> BasePopulation:
    """"""
    if state_file_path is not None and serialized_state is not None:
        # Either a file path or an already loaded state are to be supplied. Not both.
        raise RuntimeError("load_population_from_state function either requires the path to a state file that is to be "
                           "loaded and deserialized or an already loaded but still serialized state. Currently "
                           "both 'state_file_path' and 'serialized_state' arguments are supplied. Aborting.")
    elif serialized_state is None:
        # Load file, determine the type of state, then deserialize its population and return it
        with open(state_file_path) as state_file:
            serialized_state = json.load(state_file)

    if serialized_state['type'] == 'CoDeepNEAT':
        serialized_pop = serialized_state['population']
        return load_population(serialized_population=serialized_pop, dtype=dtype, **kwargs)
    else:
        raise NotImplementedError("Deserialization of a TFNE state of type '{}' not yet implemented"
                                  .format(serialized_state['type']))
