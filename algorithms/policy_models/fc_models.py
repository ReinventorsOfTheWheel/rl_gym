from keras.layers import *
from keras.models import *
from keras.regularizers import l2


class FCModel():
    INPUT_SHAPE = (7,)
    FC_SIZES=[64]
    NUM_ACTIONS = 1

    L2_REG_FULLY = 1e-3

    def __init__(self):
        # some parameters now belong to the model

        # build a model to predict action probabilities and values
        self.input_observation = Input(shape=(*self.INPUT_SHAPE,))

        # predicting policy
        layer = self.input_observation
        for fc_size in self.FC_SIZES:
            layer = Dense(fc_size, activation="tanh", kernel_regularizer=l2(self.L2_REG_FULLY))(layer)

        pred_policy = Dense(self.NUM_ACTIONS, activation='softmax', kernel_regularizer=l2(self.L2_REG_FULLY))(layer)

        # predicting value
        layer = self.input_observation
        for fc_size in self.FC_SIZES:
            layer = Dense(fc_size, activation="tanh", kernel_regularizer=l2(self.L2_REG_FULLY))(layer)
        pred_value = Dense(1, kernel_regularizer=l2(self.L2_REG_FULLY))(layer)

        model = Model(inputs=[self.input_observation], outputs=[pred_policy, pred_value])

        # the model is not compiled with any loss function
        # but the regularizers are still exposed as losses
        loss_regularization = sum(model.losses)

        # the model and its inputs
        self.model = model

        # the weights that can be updated
        self.trainable_weights = model.trainable_weights

        # tensors, these will be used for loss formulations
        self.pred_policy = pred_policy
        self.pred_value = pred_value
        self.loss_regularization = loss_regularization

    def preprocess(self, observation):
        return observation

    def get_initial_state(self):
        return []

    def predict(self, observation, state):
        # keras always needs a batch dimension
        if observation.shape == self.INPUT_SHAPE:
            observation = observation.reshape((-1, *self.INPUT_SHAPE))

        return [*self.model.predict(observation), []]

    def create_feed_dict(self, observation, state):
        return {self.input_observation: observation}

class FCCartPole(FCModel):
    INPUT_SHAPE = (4,)
    FC_SIZES = [16]
    NUM_ACTIONS = 2

    def __init__(self):
        FCModel.__init__(self)

import environments.obstacle_car.params
class FCRadialCar(FCModel):
    INPUT_SHAPE = (environments.obstacle_car.params.num_obstacles*2 + 2 + 1,)
    FC_SIZES = [64, 32, 16]

    NUM_ACTIONS = 4

    L2_REG_FULLY = 0

    def __init__(self):
        FCModel.__init__(self)