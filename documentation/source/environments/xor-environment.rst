XOR Environment
===============

Overview
--------

foobar


--------------------------------------------------------------------------------

Specifications
--------------

+-----------------------------------+-----------+
| supports weight-training eval     |      True |
+-----------------------------------+-----------+
| supports non-weight-training eval |      True |
+-----------------------------------+-----------+

foobar


--------------------------------------------------------------------------------

[EVALUATION] Config Parameters
------------------------------

``epochs``
  **Value Range**: int > 0

  **Description**: Specifies the amount of epochs a genome phenotype is to be trained on the environment before evaluating its fitness.


``batch_size``
  **Value Range**: int > 0 | None

  **Description**: Supplied batch_size value for the model.fit function. batch_size is the number of training examples used for a single iteration of backpropagating the gradient of the loss function.


``preprocessing``
  **Value Range**: -

  **Description**: <FEATURE STILL IN DEVELOPMENT>

