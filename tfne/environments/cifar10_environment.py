from __future__ import annotations

import numpy as np
import tensorflow as tf

from .base_environment import BaseEnvironment
from tfne.helper_functions import read_option_from_config


class CIFAR10Environment(BaseEnvironment):
    """
    TFNE compatible environment for the CIFAR10 dataset
    https://www.cs.toronto.edu/~kriz/cifar.html
    """

    def __init__(self, config):
        """
        Initializes CIFAR10 environment by downloading and setting up dataset and storing config. Config will be
        processed when the evaluation method will be set up.
        @param config: ConfigParser instance holding an 'Environment' section specifying the required environment
                       parameters for the chosen evaluation method.
        """
        print("Setting up CIFAR10 environment...")

        # Load test data, unpack it and normalize the pixel values
        cifar10_dataset = tf.keras.datasets.cifar10.load_data()
        (self.train_images, self.train_labels), (self.test_images, test_labels) = cifar10_dataset
        self.train_images, self.test_images = self.train_images / 255.0, self.test_images / 255.0
        self.squeezed_test_labels = np.squeeze(test_labels)

        # Initialize the accuracy metric, responsible for fitness determination
        self.accuracy_metric = tf.keras.metrics.Accuracy()

        # Register the supplied config, which will be evaluated once the method of evaluation is set up and set
        # verbosity to TF standard value
        self.config = config
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
            raise NotImplementedError("Non-Weight training evaluation not yet implemented for CIFAR10 Environment")

    def eval_genome_fitness(self, genome) -> float:
        # TO BE OVERRIDEN
        raise RuntimeError("CIFAR10 Environment not yet set up by calling 'set_up_evaluation'")

    def _eval_genome_fitness_weight_training(self, genome) -> float:
        """
        Evaluates the genome's fitness by obtaining the associated Tensorflow model and optimizer, compiling them and
        then training them for the config specified duration. The genomes fitness is then calculated and returned as
        the percentage of test images classified correctly.
        @param genome: TFNE compatible genome that is to be evaluated
        @return: genome calculated fitness that is the percentage of test images classified correctly
        """
        # Get model and optimizer required for compilation
        model = genome.get_model()
        optimizer = genome.get_optimizer()

        # Compile and train model
        model.compile(optimizer=optimizer, loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True))
        model.fit(x=self.train_images,
                  y=self.train_labels,
                  epochs=self.epochs,
                  batch_size=self.batch_size,
                  verbose=self.verbosity)

        # Determine fitness by creating model predictions with test images and then judging the fitness based on the
        # achieved model accuracy. Return this fitness
        self.accuracy_metric.reset_states()
        self.accuracy_metric.update_state(self.squeezed_test_labels, np.argmax(model(self.test_images), axis=-1))
        return round(self.accuracy_metric.result().numpy() * 100, 4)

    def _eval_genome_fitness_non_weight_training(self, genome) -> float:
        """"""
        raise NotImplementedError("Non-Weight training evaluation not yet implemented for CIFAR10 Environment")

    def replay_genome(self, genome):
        """
        Replay genome on environment by calculating its fitness and printing it. The fitness is the percentage of test
        images classified correctly.
        @param genome: TFNE compatible genome that is to be evaluated
        """
        print("Replaying Genome #{}:".format(genome.get_id()))

        # Determine fitness by creating model predictions with test images and then judging the fitness based on the
        # achieved model accuracy.
        model = genome.get_model()
        self.accuracy_metric.reset_states()
        self.accuracy_metric.update_state(self.squeezed_test_labels, np.argmax(model(self.test_images), axis=-1))
        evaluated_fitness = round(self.accuracy_metric.result().numpy() * 100, 4)
        print("Achieved Fitness:\t{}\n".format(evaluated_fitness))

    def duplicate(self) -> CIFAR10Environment:
        """"""
        return CIFAR10Environment(self.config)

    def get_input_shape(self) -> (int, int, int):
        """"""
        return 32, 32, 3

    def get_output_shape(self) -> (int,):
        """"""
        return (10,)
