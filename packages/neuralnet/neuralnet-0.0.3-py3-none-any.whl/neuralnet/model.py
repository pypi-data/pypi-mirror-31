import numpy
import abc

from neuralnet import layers
from neuralnet import Training
from neuralnet import Optimization


class Model(Optimization, Training, metaclass=abc.ABCMeta):
    def __init__(self, config_file, **kwargs):
        super(Model, self).__init__(config_file, **kwargs)
        self.model = []
        self.params = []
        self.trainable = []
        self.regularizable = []
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.model) == 0 or self.index == len(self.model):
            self.index = 0
            raise StopIteration
        else:
            self.index += 1
            return self.model[self.index - 1]

    def __len__(self):
        return len(self.model)

    def add(self, layer):
        assert isinstance(layer, layers.Layer), 'Expect \'layer\' to belong to {}, got {}'.format(type(layers.Layer), type(layer))
        self.model.append(layer)

    def load_pretrained_params(self):
        return

    @abc.abstractclassmethod
    def inference(self, input):
        return

    def get_all_params(self):
        for layer in self.model:
            self.params += layer.params

    def get_trainable(self):
        for layer in self.model:
            self.trainable += layer.trainable

    def get_regularizable(self):
        for layer in self.model:
            self.regularizable += layer.regularizable

    def save_params(self):
        numpy.savez(self.param_file, **{p.name: p.get_value() for p in self.params})
        print('Model weights dumped to %s' % self.param_file)

    def load_params(self):
        weights = numpy.load(self.param_file)
        for p in self.params:
            try:
                p.set_value(weights[p.name])
            except:
                NameError('There is no saved weight for %s' % p.name)
        print('Model weights loaded from %s' % self.param_file)

    def reset(self):
        layers.reset_training()

    @staticmethod
    def set_training_status(training):
        layers.set_training_status(training)
