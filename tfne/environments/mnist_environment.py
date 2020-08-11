from __future__ import annotations

import numpy as np
import tensorflow as tf

from .base_environment import BaseEnvironment
from tfne.helper_functions import read_option_from_config


class MNISTEnvironment(BaseEnvironment):
    """"""

    def __init__(self, config):
        """"""
        print("Setting up MNIST environment...")

        # Load test data, unpack it and normalize the pixel values
        mnist_dataset = tf.keras.datasets.mnist.load_data()
        (self.train_images, self.train_labels), (self.test_images, self.test_labels) = mnist_dataset
        self.train_images, self.test_images = self.train_images / 255.0, self.test_images / 255.0

        # Initialize the accuracy metric, responsible for fitness determination
        self.accuracy_metric = tf.keras.metrics.Accuracy()

        # Register the supplied config, which will be evaluated once the method of evaluation is set up and set
        # verbosity to TF standard value
        self.config = config
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
            raise NotImplementedError("Non-Weight training evaluation not yet implemented for MNIST Environment")

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
        model.compile(optimizer=optimizer, loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True))
        model.fit(x=self.train_images,
                  y=self.train_labels,
                  epochs=self.epochs,
                  batch_size=self.batch_size,
                  verbose=self.verbosity)

        # Determine fitness by creating model predictions with test images and then judging the fitness based on the
        # achieved model accuracy. Return this fitness
        predictions = model.predict(self.test_images)
        self.accuracy_metric.reset_states()
        self.accuracy_metric.update_state(self.test_labels, np.argmax(predictions, axis=-1))
        return round(self.accuracy_metric.result().numpy() * 100, 4)

    def _eval_genome_fitness_non_weight_training(self, genome) -> float:
        """"""
        raise NotImplementedError("Non-Weight training evaluation not yet implemented for MNIST Environment")

    def replay_genome(self, genome):
        """"""
        print("Replaying Genome #{}:".format(genome.get_id()))

        # Determine fitness by creating model predictions with test images and then judging the fitness based on the
        # achieved model accuracy.
        model = genome.get_model()
        predictions = model.predict(self.test_images)
        self.accuracy_metric.reset_states()
        self.accuracy_metric.update_state(self.test_labels, np.argmax(predictions, axis=-1))
        evaluated_fitness = round(self.accuracy_metric.result().numpy() * 100, 4)
        print("Achieved Fitness:\t{}\n".format(evaluated_fitness))

    def duplicate(self) -> MNISTEnvironment:
        """"""
        return MNISTEnvironment(self.config)

    def get_input_shape(self) -> (int, int, int):
        """"""
        return 28, 28, 1

    def get_output_shape(self) -> (int,):
        """"""
        return (10,)
