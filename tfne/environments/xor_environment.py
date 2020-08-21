from __future__ import annotations

import numpy as np
import tensorflow as tf

from .base_environment import BaseEnvironment
from tfne.helper_functions import read_option_from_config


class XOREnvironment(BaseEnvironment):
    """
    TFNE compatible environment for the XOR problem
    """

    def __init__(self, config):
        """
        Initializes XOR environment by setting up the associated correct input and output pairs and storing the supplied
        config. Config will be processed when the evaluation method will be set up.
        @param config: ConfigParser instance holding an 'Environment' section specifying the required environment
                       parameters for the chosen evaluation method.
        """
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
        """
        Setting up the evaluation method to either the weight training or non-weight training variant. Possible
        parameters for each weight training variant are drawn from the config.
        @param weight_training: bool flag, indicating wether evaluation should be weight training or not
        @param verbosity: integer specifying the verbosity of the evaluation
        """
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
        # TO BE OVERRIDEN
        raise RuntimeError("XOR Environment not yet set up by calling 'set_up_evaluation'")

    def _eval_genome_fitness_weight_training(self, genome) -> float:
        """
        Evaluates the genome's fitness by obtaining the associated Tensorflow model and optimizer, compiling them and
        then training them for the config specified duration. The genomes fitness is then calculated and returned as
        the binary cross entropy in percent of the predicted to the actual results
        @param genome: TFNE compatible genome that is to be evaluated
        @return: genome calculated fitness
        """
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
        """
        Evaluates genome's fitness by calculating and returning the binary cross entropy in percent of the predicted to
        the actual results
        @param genome: TFNE compatible genome that is to be evaluated
        @return: genome calculated fitness
        """
        # Evaluate and return its fitness by calling genome directly with input
        evaluated_fitness = float(100 * (1 - self.loss_function(self.y, genome(self.x))))
        return round(evaluated_fitness, 4)

    def replay_genome(self, genome):
        """
        Replay genome on environment by calculating its fitness and printing it.
        @param genome: TFNE compatible genome that is to be evaluated
        """
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
