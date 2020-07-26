from __future__ import annotations

import tensorflow as tf

from .base_environment import BaseEnvironment
from ..helper_functions import read_option_from_config


class CIFAR10Environment(BaseEnvironment):
    """"""

    def __init__(self, config):
        """"""
        print("Setting up CIFAR10 environment...")

        # Load test data, unpack it and normalize the pixel values
        cifar10_dataset = tf.keras.datasets.cifar10.load_data()
        (self.train_images, self.train_labels), (self.test_images, self.test_labels) = cifar10_dataset
        self.train_images, self.test_images = self.train_images / 255.0, self.test_images / 255.0

        # Register the supplied config, which will be evaluated once the method of evaluation is set up
        self.config = config
        self.verbosity = None

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
            raise NotImplementedError("Non-Weight training evaluation not yet implemented for CIFAR10 Environment")

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
        model.compile(optimizer=optimizer,
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True))
        model.fit(x=self.train_images,
                  y=self.train_labels,
                  epochs=self.epochs,
                  batch_size=self.batch_size,
                  verbose=self.verbosity)

        # Compile model again, this time considering accuracy, and evaluate and return its fitness being the accuracy
        # in percent
        model.compile(optimizer=optimizer,
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=['accuracy'])
        _, evaluated_fitness = model.evaluate(x=self.test_images,
                                              y=self.test_labels,
                                              verbose=self.verbosity)

        return round(evaluated_fitness * 100, 4)

    def _eval_genome_fitness_non_weight_training(self, genome) -> float:
        """"""
        raise NotImplementedError("Non-Weight training evaluation not yet implemented for CIFAR10 Environment")

    def replay_genome(self, genome):
        """"""
        raise NotImplementedError("CIFAR10 genome replay not yet implemented")

    def duplicate(self) -> CIFAR10Environment:
        """"""
        return CIFAR10Environment(self.config)

    def get_input_shape(self) -> (int, int, int):
        """"""
        return 32, 32, 3

    def get_output_shape(self) -> (int,):
        """"""
        return (10,)
