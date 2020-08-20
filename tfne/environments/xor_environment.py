from __future__ import annotations

import numpy as np
import tensorflow as tf

from .base_environment import BaseEnvironment
from tfne.helper_functions import read_option_from_config


class XOREnvironment(BaseEnvironment):
    """"""

    def __init__(self, config):
        """"""
        print("Setting up XOR environment...")

        # Initialize corresponding input and output mappings
        self.x = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        self.y = np.array([[0], [1], [1], [0]])

        # Register the supplied config, which will be evaluated once the method of evaluation is set up
        self.config = config

        # Initialize loss function to evaluate performance on either evaluation method and set verbosity to TF standard
        # value
        self.loss_function = tf.keras.losses.BinaryCrossentropy()
        self.verbosity = 1

    def set_up_evaluation(self, weight_training, verbosity):
        """"""
        # Set the verbosity level
        self.verbosity = verbosity

        # If environment is set to be weight training then set eval_genome_function accordingly and save the supplied
        # weight training parameters
        if weight_training:
            # Register the weight training variant as the genome eval function
            self.eval_genome_fitness = self._eval_genome_fitness_weight_training

            # Read the required evaluation parameters for a weight training XOR environment
            self.epochs = read_option_from_config(self.config, 'EVALUATION', 'epochs')
            self.batch_size = read_option_from_config(self.config, 'EVALUATION', 'batch_size')
        else:
            # Register the NON weight training variant as the genome eval function
            self.eval_genome_fitness = self._eval_genome_fitness_non_weight_training

    def eval_genome_fitness(self, genome) -> float:
        """"""
        # TO BE OVERRIDEN
        pass

    def _eval_genome_fitness_weight_training(self, genome) -> float:
        """"""
        # Get model and optimizer required for compilation
        model = genome.get_model()
        optimizer = genome.get_optimizer()

        # Compile and train model
        model.compile(optimizer=optimizer, loss=self.loss_function)
        model.fit(x=self.x, y=self.y, epochs=self.epochs, batch_size=self.batch_size, verbose=self.verbosity)

        # Evaluate and return its fitness
        evaluated_fitness = float(100 * (1 - self.loss_function(self.y, model(self.x))))

        # FIXME Tensorflow arbitrary NaN loss when using float16 datatype. Confirmed by TF.
        # Github TF issue: https://github.com/tensorflow/tensorflow/issues/38457
        if tf.math.is_nan(evaluated_fitness):
            evaluated_fitness = 0

        return round(evaluated_fitness, 4)

    def _eval_genome_fitness_non_weight_training(self, genome) -> float:
        """"""
        # Evaluate and return its fitness by calling genome directly with input
        evaluated_fitness = float(100 * (1 - self.loss_function(self.y, genome(self.x))))
        return round(evaluated_fitness, 4)

    def replay_genome(self, genome):
        """"""
        print("Replaying Genome #{}:".format(genome.get_id()))
        evaluated_fitness = round(float(100 * (1 - self.loss_function(self.y, genome(self.x)))), 4)
        print("Solution Values: \t{}\n".format(self.y))
        print("Predicted Values:\t{}\n".format(genome(self.x)))
        print("Achieved Fitness:\t{}\n".format(evaluated_fitness))

    def duplicate(self) -> XOREnvironment:
        """"""
        return XOREnvironment(self.config)

    def get_input_shape(self) -> (int,):
        """"""
        return (2,)

    def get_output_shape(self) -> (int,):
        """"""
        return (1,)
