'''
Written and collected by Duc Nguyen
Last Modified by Duc Nguyen (theano version >= 0.8.1 required)
Updates on Sep 2017: added BatchNormDNNLayer from Lasagne


'''
__author__ = 'Duc Nguyen'

import math
import time
import numpy as np
import abc
import theano
from theano import tensor as T
from theano.tensor.nnet import conv2d as conv
from theano.tensor.signal.pool import pool_2d as pool

from neuralnet import utils


def validate(func):
    """make sure output shape is a list of ints"""
    def func_wrapper(self):
        out = [int(x) if x is not None else x for x in func(self)]
        return tuple(out)
    return func_wrapper


class Layer(metaclass=abc.ABCMeta):
    def __init__(self):
        self.rng = np.random.RandomState(int(time.time()))
        self.params = []
        self.trainable = []
        self.regularizable = []
        self.layer_type = ''

    def __str__(self):
        return self.layer_type

    def __call__(self, *args, **kwargs):
        return self.get_output(*args, **kwargs)

    @abc.abstractclassmethod
    def get_output(self, input):
        return

    @property
    @abc.abstractclassmethod
    def output_shape(self):
        return

    def init_he(self, shape, activation, sampling='uniform', lrelu_alpha=0.1):
        # He et al. 2015
        if activation in ['relu', 'elu']:  # relu or elu
            gain = np.sqrt(2)
        elif activation == 'lrelu':  # lrelu
            gain = np.sqrt(2 / (1 + lrelu_alpha ** 2))
        else:
            gain = 1.0

        fan_in = shape[0] if len(shape) == 2 else np.prod(shape[1:])
        if sampling == 'normal':
            std = gain * np.sqrt(1. / fan_in)
            return np.asarray(self.rng.normal(0., std, shape), dtype=theano.config.floatX)
        elif sampling == 'uniform':
            bound = gain * np.sqrt(3. / fan_in)
            return np.asarray(self.rng.uniform(-bound, bound, shape), dtype=theano.config.floatX)
        else:
            raise NotImplementedError

    @staticmethod
    @abc.abstractclassmethod
    def reset():
        return


class ActivationLayer(Layer):
    def __init__(self, input_shape, activation='relu', layer_name='Activation'):
        super(ActivationLayer, self).__init__()
        self.input_shape = tuple(input_shape)
        self.activation = utils.function[activation]
        self.layer_name = layer_name
        self.layer_type = 'Activation Layer {}'.format(activation)
        print('{} Activation layer: {}'.format(self.layer_name, activation))

    def get_output(self, input):
        return self.activation(input)

    @property
    def output_shape(self):
        return tuple(self.input_shape)

    @staticmethod
    def reset():
        return


class PoolingLayer(Layer):
    def __init__(self, input_shape, ws=(2, 2), ignore_border=False, stride=(2, 2), pad='valid', mode='max', layer_name='Pooling', show=True):
        """

        :param input_shape:
        :param ws:
        :param ignore_border:
        :param stride:
        :param pad:
        :param mode: {'max', 'sum', 'average_inc_pad', 'average_exc_pad'}
        :param layer_name:
        """
        assert isinstance(input_shape, list) or isinstance(input_shape, tuple), \
            'input_shape must be list or tuple. Received %s' % type(input_shape)
        assert len(input_shape) == 4, 'input_shape must have 4 elements. Received %d' % len(input_shape)
        assert mode in ('max', 'sum', 'average_inc_pad', 'average_exc_pad'), 'Invalid pooling mode. ' \
                                                                             'Mode should be \'max\', \'sum\', ' \
                                                                             '\'average_inc_pad\' or \'average_exc_pad\', ' \
                                                                             'got %s' % mode
        super(PoolingLayer, self).__init__()

        self.layer_type = 'Pooling Layer mode {} size {} stride {}'.format(mode, ws, stride)
        self.input_shape = tuple(input_shape)
        self.ws = ws
        self.ignore_border = ignore_border
        self.stride = stride
        self.mode = mode
        self.layer_name = layer_name
        self.show = show
        if isinstance(pad, (list, tuple)):
            self.pad = tuple(pad)
        elif isinstance(pad, str):
            if pad == 'half':
                self.pad = (ws[0]//2, ws[1]//2)
            elif pad == 'valid':
                self.pad = (0, 0)
            elif pad == 'full':
                self.pad = (ws[0]-1, ws[1]-1)
            else:
                raise NotImplementedError
        else:
            raise TypeError

        if show:
            print('@ {} {} PoolingLayer: size: {}'.format(self.layer_name, self.mode, self.ws),
                  ' stride: {}'.format(self.stride), ' {} -> {}'.format(input_shape, self.output_shape))

    def get_output(self, input):
        return pool(input, self.ws, self.ignore_border, self.stride, self.pad, self.mode)

    @property
    @validate
    def output_shape(self):
        size = list(self.input_shape)
        if not self.ignore_border:
            size[2] = int(np.ceil((size[2] + 2 * self.pad[0] - self.ws[0]) / self.stride[0] + 1))
            size[3] = int(np.ceil((size[3] + 2 * self.pad[1] - self.ws[1]) / self.stride[1] + 1))
        else:
            size[2] = int(np.ceil((size[2] + 2 * self.pad[0] - self.ws[0]) / self.stride[0]))
            size[3] = int(np.ceil((size[3] + 2 * self.pad[1] - self.ws[1]) / self.stride[1]))
        return tuple(size)

    @staticmethod
    def reset():
        pass


class DropoutLayer(Layer):
    layers = []

    def __init__(self, input_shape, drop_prob=0.5, GaussianNoise=False, activation='relu', layer_name='Dropout', **kwargs):
        assert isinstance(input_shape, list) or isinstance(input_shape, tuple), \
            'input_shape must be list or tuple. Received %s' % type(input_shape)
        assert len(input_shape) == 2 or len(input_shape) == 4, \
            'input_shape must have 2 or 4 elements. Received %d' % len(input_shape)
        super(DropoutLayer, self).__init__()

        self.layer_type = 'Dropout Layer with prob {}'.format(drop_prob)
        self.input_shape = tuple(input_shape)
        self.GaussianNoise = GaussianNoise
        self.activation = utils.function[activation]
        self.layer_name = layer_name
        self.srng = T.shared_randomstreams.RandomStreams(self.rng.randint(1, int(time.time())))
        self.keep_prob = T.as_tensor_variable(np.float32(1. - drop_prob))
        self.training_flag = False
        self.kwargs = kwargs
        print('@ {} Dropout Layer: p={:.2f} activation: {}'.format(self.layer_name, 1. - drop_prob, activation))
        DropoutLayer.layers.append(self)

    def get_output(self, input):
        mask = self.srng.normal(input.shape) + 1. if self.GaussianNoise else self.srng.binomial(n=1, p=self.keep_prob, size=input.shape)
        output_on = mask * input if self.GaussianNoise else input * T.cast(mask, theano.config.floatX)
        output_off = input if self.GaussianNoise else input * self.keep_prob
        return self.activation(output_on if self.training_flag else output_off, **self.kwargs)

    @property
    @validate
    def output_shape(self):
        return tuple(self.input_shape)

    @staticmethod
    def set_training(training):
        for layer in DropoutLayer.layers:
            layer.training_flag = training

    @staticmethod
    def reset():
        pass


class FullyConnectedLayer(Layer):
    layers = []

    def __init__(self, input_shape, num_nodes, He_init=None, He_init_gain=None, W=None, b=None, no_bias=False, layer_name='fc',
                 activation='relu', maxout_size=4, target='dev0'):
        '''

        :param n_in:
        :param num_nodes:
        :param He_init: 'normal', 'uniform' or None (default)
        :param He_init_gain:
        :param W:
        :param b:
        :param no_bias:
        :param layer_name:
        :param activation:
        :param target:
        '''
        assert isinstance(input_shape, list) or isinstance(input_shape, tuple), \
            'input_shape must be list or tuple. Received %s' % type(input_shape)
        assert len(input_shape) == 2 or len(input_shape) == 4, \
            'input_shape must have 2 or 4 elements. Received %d' % len(input_shape)
        super(FullyConnectedLayer, self).__init__()

        self.input_shape = tuple(input_shape) if len(input_shape) == 2 else (input_shape[0], np.prod(input_shape[1:]))
        self.num_nodes = num_nodes
        self.He_init = He_init
        self.He_init_gain = He_init_gain if He_init_gain is not None else activation
        self.activation = utils.function[activation]
        self.maxout_size = maxout_size
        self.no_bias = no_bias
        self.layer_name = layer_name
        self.target = target
        self.layer_type = 'Fully Connected Layer {} nodes {}'.format(num_nodes, activation)

        if W is None:
            if self.He_init:
                self.W_values = self.init_he((self.input_shape[1], num_nodes), self.He_init_gain, self.He_init)
            else:
                W_bound = np.sqrt(6. / (self.input_shape[1] + num_nodes)) * 4 if self.activation is utils.function['sigmoid'] \
                    else np.sqrt(6. / (self.input_shape[1] + num_nodes))
                self.W_values = np.asarray(self.rng.uniform(low=-W_bound, high=W_bound, size=(self.input_shape[1], num_nodes)),
                                           dtype=theano.config.floatX) if W is None else W
        else:
            self.W_values = W
        self.W = theano.shared(value=self.W_values, name=self.layer_name + '_W', borrow=True)#, target=self.target)
        self.trainable.append(self.W)
        self.params.append(self.W)
        self.regularizable.append(self.W)

        if not self.no_bias:
            if b is None:
                self.b_values = np.zeros((num_nodes,), dtype=theano.config.floatX) if b is None else b
            else:
                self.b_values = b
            self.b = theano.shared(value=self.b_values, name=self.layer_name + '_b', borrow=True)
            self.trainable.append(self.b)
            self.params.append(self.b)

        self.regularizable.append(self.W)
        print('@ {} FC: in_shape = {} weight shape = {} -> {} activation: {}'
              .format(self.layer_name, self.input_shape, (self.input_shape[1], num_nodes), self.output_shape, activation))
        FullyConnectedLayer.layers.append(self)

    def get_output(self, input):
        output = T.dot(input.flatten(2), self.W) + self.b if not self.no_bias else T.dot(input.flatten(2), self.W)
        return self.activation(output) if self.activation != utils.maxout else self.activation(output, self.maxout_size)

    @property
    @validate
    def output_shape(self):
        return (self.input_shape[0], self.num_nodes//self.maxout_size) if self.activation is 'maxout' \
            else (self.input_shape[0], self.num_nodes)

    @staticmethod
    def reset():
        for layer in FullyConnectedLayer.layers:
            layer.W.set_value(layer.W_values)
            if not layer.no_bias:
                layer.b.set_value(layer.b_values)


class ConvolutionalLayer(Layer):
    layers = []

    def __init__(self, input_shape, num_filters, filter_size, He_init=None, He_init_gain=None, W=None, b=None, no_bias=True,
                 border_mode='half', stride=(1, 1), dilation=(1, 1), layer_name='conv', activation='relu', show=True, target='dev0', **kwargs):
        """

        :param input_shape: list or tuple
        :param num_filters: int
        :param filter_size: int or list or tuple
        :param He_init:
        :param He_init_gain:
        :param W:
        :param b:
        :param no_bias:
        :param border_mode:
        :param stride:
        :param dilation:
        :param layer_name:
        :param activation:
        :param maxout_size:
        :param show:
        :param target:
        """
        assert isinstance(input_shape, list) or isinstance(input_shape, tuple), \
            'input_shape must be list or tuple. Received %s' % type(input_shape)
        assert len(input_shape) == 2 or len(input_shape) == 4, \
            'input_shape must have 2 or 4 elements. Received %d' % len(input_shape)
        assert isinstance(num_filters, int) and isinstance(filter_size, (int, list, tuple))
        assert isinstance(border_mode, (int, list, tuple, str)), 'border_mode should be either \'int\', ' \
                                                                 '\'list\', \'tuple\' or \'str\', got {}'.format(type(border_mode))
        assert isinstance(stride, (int, list, tuple))
        super(ConvolutionalLayer, self).__init__()

        self.input_shape = tuple(input_shape)
        self.filter_shape = (num_filters, input_shape[1], filter_size[0], filter_size[1]) if isinstance(filter_size, (list, tuple)) \
            else (num_filters, input_shape[1], filter_size, filter_size)
        self.no_bias = no_bias
        self.activation = utils.function[activation]
        self.He_init = He_init
        self.He_init_gain = He_init_gain if He_init_gain is not None else activation
        self.layer_name = layer_name
        self.border_mode = border_mode
        self.subsample = tuple(stride) if isinstance(stride, (tuple, list)) else (stride, stride)
        self.dilation = dilation
        self.show = show
        self.target = target
        self.kwargs = kwargs
        self.layer_type = 'Convolutional Layer {} filters size {} stride {} dilation {} {} {}'.\
            format(num_filters, filter_size, stride, dilation, activation, ' '.join([' '.join((k, str(v))) for k, v in kwargs.items()]))

        if W is None:
            if He_init:
                self.W_values = self.init_he(self.filter_shape, self.He_init_gain, He_init)
            else:
                fan_in = np.prod(self.filter_shape[1:])
                fan_out = (self.filter_shape[0] * np.prod(self.filter_shape[2:]))
                W_bound = np.sqrt(6. / (fan_in + fan_out))
                self.W_values = np.asarray(self.rng.uniform(low=-W_bound, high=W_bound, size=self.filter_shape),
                                           dtype=theano.config.floatX)
        else:
            self.W_values = W
        self.W = theano.shared(self.W_values, name=self.layer_name + '_W', borrow=True)#, target=self.target)
        self.trainable.append(self.W)
        self.params.append(self.W)

        if not self.no_bias:
            if b is None:
                self.b_values = np.zeros(self.filter_shape[0], dtype=theano.config.floatX)
            else:
                self.b_values = b
            self.b = theano.shared(self.b_values, self.layer_name + '_b', borrow=True)
            self.trainable.append(self.b)
            self.params.append(self.b)

        self.regularizable += [self.W]
        if show:
            print('@ {} Conv Layer: '.format(self.layer_name), 'border mode: {} '.format(border_mode),
                  'subsampling: {} dilation {}'.format(stride, dilation), end=' ')
            print('shape: {} x '.format(input_shape), end=' ')
            print('filter shape: {} '.format(self.filter_shape), end=' ')
            print('-> {} '.format(self.output_shape), end=' ')
            print('activation: {} '.format(activation))
            ConvolutionalLayer.layers.append(self)

    def get_output(self, input):
        output = conv(input=input, filters=self.W, border_mode=self.border_mode, subsample=self.subsample)
        if not self.no_bias:
            output += self.b.dimshuffle(('x', 0, 'x', 'x'))
        return self.activation(output, **self.kwargs)

    @property
    @validate
    def output_shape(self):
        size = list(self.input_shape)
        assert len(size) == 4, "Shape must consist of 4 elements only"

        k1, k2 = self.filter_shape[2] + (self.filter_shape[2] - 1)*(self.dilation[0] - 1), \
                 self.filter_shape[3] + (self.filter_shape[3] - 1)*(self.dilation[1] - 1)

        if isinstance(self.border_mode, str):
            if self.border_mode == 'half':
                p = (k1 // 2, k2 // 2)
            elif self.border_mode == 'valid':
                p = (0, 0)
            elif self.border_mode == 'full':
                p = (k1 - 1, k2 - 1)
            else:
                raise NotImplementedError
        elif isinstance(self.border_mode, (list, tuple)):
            p = tuple(self.border_mode)
        elif isinstance(self.border_mode, int):
            p = (self.border_mode, self.border_mode)
        else:
            raise NotImplementedError

        size[2] = (size[2] - k1 + 2*p[0]) // self.subsample[0] + 1
        size[3] = (size[3] - k2 + 2*p[1]) // self.subsample[1] + 1

        size[1] = self.filter_shape[0] // self.maxout_size if self.activation == utils.maxout else self.filter_shape[0]
        return tuple(size)

    @staticmethod
    def reset():
        for layer in ConvolutionalLayer.layers:
            layer.W.set_value(layer.W_values)
            if not layer.no_bias:
                layer.b.set_value(layer.b_values)


class StackingConv(Layer):
    layers = []

    def __init__(self, input_shape, num_layers, num_filters, filter_size=3, batch_norm=False, layer_name='StackingConv', He_init=None,
                 He_init_gain=None, W=None, b=None, no_bias=True, border_mode='half', stride=1, dilation=(1, 1),
                 activation='relu', **kwargs):
        assert num_layers > 1, 'num_layers must be greater than 1, got %d' % num_layers
        super(StackingConv, self).__init__()
        self.input_shape = input_shape
        self.num_layers = num_layers
        self.batch_norm = batch_norm
        self.layer_name = layer_name
        self.layer_type = 'Stacking {} Convolutional Blocks {} filters size {} batchnorm {} ' \
                          'stride {} {} {}'.format(num_layers, num_filters, filter_size, batch_norm, stride, activation,
                                                ' '.join([' '.join((k, str(v))) for k, v in kwargs.items()]))
        self.block = []
        shape = tuple(self.input_shape)
        conv_layer = ConvBNAct if batch_norm else ConvolutionalLayer
        for num in range(num_layers - 1):
            self.block.append(conv_layer(shape, num_filters, filter_size, He_init=He_init, He_init_gain=He_init_gain, W=W,
                                         b=b, no_bias=no_bias, border_mode=border_mode, stride=(1, 1), dilation=dilation,
                                         layer_name=self.layer_name + '_conv_%d' % (num+1), activation=activation, **kwargs))
            shape = self.block[-1].output_shape
            self.params += self.block[-1].params
            self.trainable += self.block[-1].trainable
            self.regularizable += self.block[-1].regularizable
        self.block.append(conv_layer(shape, num_filters, filter_size, He_init=He_init, He_init_gain=He_init_gain, W=W,
                                     b=b, no_bias=no_bias, border_mode=border_mode, dilation=dilation, stride=stride,
                                     activation=activation, layer_name=self.layer_name + '_conv_%d' % num_layers, **kwargs))
        self.params += self.block[-1].params
        self.trainable += self.block[-1].trainable
        self.regularizable += self.block[-1].regularizable
        StackingConv.layers.append(self)

    def get_output(self, input):
        output = input
        for layer in self.block:
            output = layer(output)
        return output

    @property
    def output_shape(self):
        return self.block[-1].output_shape

    @staticmethod
    def reset():
        for layer in StackingConv.layers:
            layer.reset()


class StackingDeconv(Layer):
    layers = []

    def __init__(self, input_shape, num_layers, num_filters, stride_first=True, output_shape=None, He_init=None,
                 layer_name='transconv', padding='half', stride=(2, 2), activation='relu'):
        super(StackingDeconv, self).__init__()
        self.input_shape = input_shape
        self.num_layers = num_layers
        self.layer_name = layer_name
        self.stride_first = stride_first
        self.block = []

        if self.stride_first:
            o_shape = (input_shape[0], input_shape[1], stride[0] * input_shape[2], stride[1] * input_shape[3]) \
                if output_shape is not None else output_shape
            f_shape = (input_shape[1], num_filters, 3, 3)
            self.block.append(TransposedConvolutionalLayer(input_shape, f_shape, o_shape, He_init, stride=stride,
                                                           padding=padding, activation=activation, layer_name=layer_name+'_deconv0'))
            shape = self.block[-1].output_shape
            self.params += self.block[-1].params
            self.trainable += self.block[-1].trainable
            self.regularizable += self.block[-1].regularizable
        else:
            shape = tuple(self.input_shape)
        for num in range(num_layers - 1):
            o_shape = (input_shape[0], num_filters, shape[2], shape[3])
            f_shape = (shape[1], num_filters, 3, 3)
            self.block.append(TransposedConvolutionalLayer(shape, f_shape, o_shape, He_init, stride=(1, 1), padding=padding,
                                                           activation=activation, layer_name=layer_name+'_deconv%d' % (num+1)))
            shape = self.block[-1].output_shape
            self.params += self.block[-1].params
            self.trainable += self.block[-1].trainable
            self.regularizable += self.block[-1].regularizable
        if not stride_first:
            o_shape = (input_shape[0], num_filters, shape[2] * stride[0], shape[3] * stride[1])
            f_shape = (shape[1], num_filters, 3, 3)
            self.block.append(TransposedConvolutionalLayer(shape, f_shape, o_shape, He_init, layer_name+'_deconv_last',
                                                           stride=stride, activation=activation))
            self.params += self.block[-1].params
            self.trainable += self.block[-1].trainable
            self.regularizable += self.block[-1].regularizable
        StackingDeconv.layers.append(self)

    def get_output(self, input):
        output = input
        for layer in self.block:
            output = layer(output)
        return output

    @property
    def output_shape(self):
        return self.block[-1].output_shape

    @staticmethod
    def reset():
        for layer in StackingDeconv.layers:
            layer.reset()


class DilatedConvModule(Layer):
    def __init__(self, input_shape, num_filters, filter_size, dilation_scale=3, He_init=None, He_init_gain=None, W=None, b=None,
                 no_bias=True, border_mode='half', stride=(1, 1), layer_name='conv', activation='relu', target='dev0'):
        super(DilatedConvModule, self).__init__()
        self.input_shape = input_shape
        self.num_filters = num_filters
        self.filter_shape = filter_size
        self.dilation_scale = dilation_scale
        
        self.module = [[] for i in range(dilation_scale)]
        for i in range(dilation_scale):
            self.module[i].append(ConvBNAct(input_shape, num_filters, filter_size, 'normal', border_mode=border_mode,
                                            stride=(1, 1), dilation=(i+1, i+1), activation=activation, layer_name=layer_name+'_branch1'))
            self.module[i].append(ConvBNAct(self.module[i][-1].output_shape, num_filters, filter_size, 'normal',
                                            border_mode=border_mode, stride=(1, 1), dilation=(i+1, i+1), activation=activation,
                                            layer_name=layer_name+'_branch1_conv2'))
            self.module[i].append(ConvBNAct(self.module[i][-1].output_shape, num_filters, filter_size, 'normal',
                                            border_mode=border_mode, stride=stride, dilation=(i+1, i+1), activation=activation,
                                            layer_name=layer_name+'_branch1_conv3'))
        
        self.params += [p for block in self.module for layer in block for p in layer.params]
        self.trainable += [p for block in self.module for layer in block for p in layer.trainable]
        self.regularizable += [p for block in self.module for layer in block for p in layer.regularizable]

    def get_output(self, input):
        output = [utils.inference(input, block) for block in self.module]
        return T.concatenate(output, 1)
    
    @property
    def output_shape(self):
        shape = self.module[0][-1].output_shape
        return (self.input_shape[0], self.num_filters*self.dilation_scale, shape[2], shape[3])
    
    @staticmethod
    def reset():
        reset_training()
        

class InceptionModule1(Layer):
    def __init__(self, input_shape, num_filters=48, border_mode='half', stride=(1, 1), activation='relu',
                 layer_name='inception_mixed1', show=False):
        super(InceptionModule1, self).__init__()
        self.input_shape = input_shape
        self.border_mode = border_mode
        self.stride = stride
        self.activation = activation
        self.layer_name = layer_name
        self.show = show
        self.layer_type = 'Inception Module 1 {} filters stride {}'.format(num_filters, stride)

        self.module = [[], [], [], []]
        self.module[0].append(ConvBNAct(input_shape, num_filters, (1, 1), 'normal', border_mode=border_mode,
                                        stride=(1, 1), activation=activation, layer_name=layer_name+'_branch1_conv1x1', show=show))
        self.module[0].append(ConvBNAct(self.module[0][-1].output_shape, num_filters*4//3, 3,
                                        'normal', border_mode=border_mode, stride=(1, 1), activation=activation,
                                        layer_name=layer_name+'_branch1_conv3x3', show=show))
        self.module[0].append(ConvBNAct(self.module[0][-1].output_shape, num_filters*4//3, 3,
                                        'normal', border_mode=border_mode, stride=stride, activation=activation,
                                        layer_name=layer_name+'_branch1_conv3x3', show=show))

        self.module[1].append(ConvBNAct(input_shape, num_filters*4//3, 1, 'normal', border_mode=border_mode,
                                        stride=(1, 1), activation=activation, layer_name=layer_name+'_branch2_conv1x1', show=show))
        self.module[1].append(ConvBNAct(self.module[1][-1].output_shape, num_filters*2, 3,
                                        'normal', border_mode=border_mode, stride=stride, activation=activation,
                                        layer_name=layer_name+'_branch2_conv3x3', show=show))

        self.module[2].append(PoolingLayer(input_shape, (3, 3), stride=stride, mode='average_exc_pad', pad='half',
                                           ignore_border=True, layer_name=layer_name+'_branch3_pooling', show=show))
        self.module[2].append(ConvBNAct(self.module[2][-1].output_shape, num_filters*2//3, 1,
                                        'normal', border_mode=border_mode, stride=(1, 1), activation=activation,
                                        layer_name=layer_name+'_branch3_conv1x1', show=show))

        self.module[3].append(ConvBNAct(input_shape, num_filters*4//3, 1, 'normal', border_mode=border_mode,
                                        stride=stride, activation=activation, layer_name=layer_name+'_branch4_conv1x1', show=show))

        print('@{} Inception module 1: {} -> {}'.format(layer_name, input_shape, self.output_shape))

        self.params += [p for block in self.module for layer in block for p in layer.params]
        self.trainable += [p for block in self.module for layer in block for p in layer.trainable]
        self.regularizable += [p for block in self.module for layer in block for p in layer.regularizable]

    def get_output(self, input):
        output = [utils.inference(input, block) for block in self.module]
        return T.concatenate(output, 1)

    @property
    def output_shape(self):
        depth = 0
        for block in self.module:
            depth += block[-1].output_shape[1]
        return (self.module[0][-1].output_shape[0], depth, self.module[0][-1].output_shape[2], self.module[0][-1].output_shape[3])

    @staticmethod
    def reset():
        reset_training()


class InceptionModule2(Layer):
    def __init__(self, input_shape, num_filters=128, filter_size=7, border_mode='half', stride=(1, 1), activation='relu',
                 layer_name='inception_mixed1', show=False):
        super(InceptionModule2, self).__init__()
        self.input_shape = input_shape
        self.filter_size = filter_size
        self.border_mode = border_mode
        self.stride = stride
        self.activation = activation
        self.layer_name = layer_name
        self.show = show
        self.layer_type = 'Inception Module 2 {} filters size {} stride {}'.format(num_filters, filter_size, stride)

        self.module = [[], [], [], []]
        self.module[0].append(ConvBNAct(input_shape, num_filters, (1, 1), 'normal', border_mode=border_mode,
                                        stride=(1, 1), activation=activation, layer_name=layer_name+'_branch1_conv1x1', show=show))
        self.module[0].append(ConvBNAct(self.module[0][-1].output_shape, num_filters, (filter_size, 1),
                                        'normal', border_mode=border_mode, stride=(1, 1), activation=activation,
                                        layer_name=layer_name+'_branch1_conv7x1_1', show=show))
        self.module[0].append(ConvBNAct(self.module[0][-1].output_shape, num_filters, (1, filter_size),
                                        'normal', border_mode=border_mode, stride=(1, 1), activation=activation,
                                        layer_name=layer_name+'_branch1_conv1x7_1', show=show))
        self.module[0].append(ConvBNAct(self.module[0][-1].output_shape, num_filters, (filter_size, 1),
                                        'normal', border_mode=border_mode, stride=(1, 1), activation=activation,
                                        layer_name=layer_name+'_branch1_conv7x1_2', show=show))
        self.module[0].append(ConvBNAct(self.module[0][-1].output_shape, num_filters*3//2, (1, filter_size),
                                        'normal', border_mode=border_mode, stride=stride, activation=activation,
                                        layer_name=layer_name+'_branch1_conv1x7_2', show=show))

        self.module[1].append(ConvBNAct(input_shape, 64, (1, 1), 'normal', border_mode=border_mode,
                                        stride=(1, 1), activation=activation, layer_name=layer_name+'_branch2_conv1x1', show=show))
        self.module[1].append(ConvBNAct(self.module[1][-1].output_shape, num_filters, (filter_size, 1),
                                        'normal', border_mode=border_mode, stride=(1, 1), activation=activation,
                                        layer_name=layer_name+'_branch2_conv7x1', show=show))
        self.module[1].append(ConvBNAct(self.module[1][-1].output_shape, num_filters*3//2, (1, filter_size),
                                        'normal', border_mode=border_mode, stride=stride, activation=activation,
                                        layer_name=layer_name+'_branch2_conv1x7', show=show))

        self.module[2].append(PoolingLayer(input_shape, (3, 3), stride=stride, mode='average_exc_pad', pad='half',
                                           ignore_border=True, layer_name=layer_name+'_branch3_pooling', show=show))
        self.module[2].append(ConvBNAct(self.module[2][-1].output_shape, num_filters*3//2, (1, 1),
                                        'normal', border_mode=border_mode, stride=(1, 1), activation=activation,
                                        layer_name=layer_name+'_branch3_conv1x1', show=show))

        self.module[3].append(ConvBNAct(input_shape, num_filters*3//2, (1, 1), 'normal', border_mode=border_mode,
                                        stride=stride, activation=activation, layer_name=layer_name+'_branch4_conv1x1', show=show))

        print('@ {} Inception module 2: {} -> {}'.format(layer_name, input_shape, self.output_shape))

        self.params += [p for block in self.module for layer in block for p in layer.params]
        self.trainable += [p for block in self.module for layer in block for p in layer.trainable]
        self.regularizable += [p for block in self.module for layer in block for p in layer.regularizable]

    def get_output(self, input):
        output = [utils.inference(input, block) for block in self.module]
        return T.concatenate(output, 1)

    @property
    def output_shape(self):
        depth = 0
        for block in self.module:
            depth += block[-1].output_shape[1]
        return (self.module[0][-1].output_shape[0], depth, self.module[0][-1].output_shape[2], self.module[0][-1].output_shape[3])

    @staticmethod
    def reset():
        reset_training()


class InceptionModule3(Layer):
    def __init__(self, input_shape, num_filters=320, border_mode='half', stride=(1, 1), activation='relu',
                 layer_name='inception_mixed1', show=False):
        super(InceptionModule3, self).__init__()
        self.input_shape = input_shape
        self.border_mode = border_mode
        self.stride = stride
        self.activation = activation
        self.layer_name = layer_name
        self.show = show
        self.layer_type = 'Inception Module 3 {} filters stride {}'.format(num_filters, stride)

        self.module = [[], [], [], []]
        self.module[0].append(ConvBNAct(input_shape, num_filters*7//5, (1, 1), 'normal', border_mode=border_mode,
                                        stride=(1, 1), activation=activation, layer_name=layer_name+'_branch1_conv1x1', show=show))
        self.module[0].append(ConvBNAct(self.module[0][-1].output_shape, num_filters*6//5, (3, 3),
                                        'normal', border_mode=border_mode, stride=(1, 1), activation=activation,
                                        layer_name=layer_name+'_branch1_conv3x3', show=show))
        self.module[0].append([[], []])
        self.module[0][-1][0].append(ConvBNAct(self.module[0][1].output_shape, num_filters*6//5, (3, 1),
                                               'normal', border_mode=border_mode, stride=stride, activation=activation,
                                               layer_name=layer_name+'_branch1_conv3x1', show=show))
        self.module[0][-1][1].append(ConvBNAct(self.module[0][1].output_shape, num_filters*6//5, (3, 1),
                                               'normal', border_mode=border_mode, stride=stride, activation=activation,
                                               layer_name=layer_name+'_branch1_conv1x3', show=show))

        self.module[1].append(ConvBNAct(input_shape, num_filters*7//5, (1, 1), 'normal', border_mode=border_mode,
                                        stride=(1, 1), activation=activation, layer_name=layer_name+'_branch2_conv1x1', show=show))
        self.module[1].append([[], []])
        self.module[1][-1][0].append(ConvBNAct(self.module[1][0].output_shape, num_filters*6//5, (3, 1),
                                               'normal', border_mode=border_mode, stride=stride, activation=activation,
                                               layer_name=layer_name+'_branch2_conv3x1', show=show))
        self.module[1][-1][1].append(ConvBNAct(self.module[1][0].output_shape, num_filters*6//5, (3, 1),
                                               'normal', border_mode=border_mode, stride=stride, activation=activation,
                                               layer_name=layer_name+'_branch2_conv1x3', show=show))

        self.module[2].append(PoolingLayer(input_shape, (3, 3), stride=stride, mode='average_exc_pad', pad='half',
                                           ignore_border=True, layer_name=layer_name+'_branch3_pooling', show=show))
        self.module[2].append(ConvBNAct(self.module[2][-1].output_shape, num_filters*2//3, (1, 1),
                                        'normal', border_mode=border_mode, stride=(1, 1), activation=activation,
                                        layer_name=layer_name+'_branch3_conv1x1', show=show))

        self.module[3].append(ConvBNAct(input_shape, num_filters*4//3, (1, 1), 'normal', border_mode=border_mode,
                                        stride=stride, activation=activation, layer_name=layer_name+'_branch4_conv1x1', show=show))

        for block in self.module:
            for layer in block:
                if not isinstance(layer, (list, tuple)):
                    self.params += layer.params
                    self.trainable += layer.trainable
                    self.regularizable += layer.regularizable
                else:
                    for l in layer:
                        self.params += l[0].params
                        self.trainable += l[0].trainable
                        self.regularizable += l[0].regularizable

        if not show:
            print('@ {} Inception module 3: {} -> {}'.format(layer_name, input_shape, self.output_shape))

    def get_output(self, input):
        output = []
        for block in self.module:
            out = input
            for layer in block:
                if not isinstance(layer, (list, tuple)):
                    out = layer(out)
                else:
                    o = []
                    for l in layer:
                        o.append(l[0](out))
                    out = T.concatenate(o, 1)
            output.append(out)
        return T.concatenate(output, 1)

    @property
    def output_shape(self):
        depth = 0
        for block in self.module:
            if not isinstance(block[-1], (list, tuple)):
                depth += block[-1].output_shape[1]
            else:
                for l in block[-1]:
                    depth += l[0].output_shape[1]
        return (self.module[3][-1].output_shape[0], depth, self.module[3][-1].output_shape[2], self.module[3][-1].output_shape[3])

    @staticmethod
    def reset():
        reset_training()


class ConvBNAct(Layer):
    layers = []

    def __init__(self, input_shape, num_filters, filter_size, He_init=None, He_init_gain=None, W=None, b=None, no_bias=True,
                 border_mode='half', stride=(1, 1), layer_name='convbnact', activation='relu', dilation=(1, 1), epsilon=1e-4,
                 running_average_factor=1e-1, axes='spatial', no_scale=False, show=False, target='dev0', **kwargs):
        """

        :param input_shape:
        :param num_filters:
        :param filter_size:
        :param He_init:
        :param He_init_gain:
        :param W:
        :param b:
        :param no_bias:
        :param border_mode: int, list, tuple, or str
        :param stride:
        :param layer_name:
        :param activation:
        :param dilation:
        :param epsilon:
        :param running_average_factor:
        :param axes:
        :param no_scale:
        :param show:
        :param target:
        """
        super(ConvBNAct, self).__init__()
        self.layer_type = 'Conv BN Act Block {} filters size {} padding {} stride {} {} {}'.\
            format(num_filters, filter_size, border_mode, stride, activation, ' '.join([' '.join((k, str(v))) for k, v in kwargs.items()]))
        self.Conv = ConvolutionalLayer(input_shape, num_filters, filter_size, He_init=He_init, He_init_gain=He_init_gain, W=W, b=b,
                                       no_bias=no_bias, border_mode=border_mode, stride=stride, dilation=dilation,
                                       layer_name=layer_name + '_conv', activation='linear', show=show)
        self.BN = BatchNormLayer(self.Conv.output_shape, layer_name + 'bn', epsilon, running_average_factor, axes,
                                 activation, no_scale, show=show, **kwargs)
        self.block = [self.Conv, self.BN]
        self.trainable += self.Conv.trainable + self.BN.trainable
        self.regularizable += self.Conv.regularizable + self.BN.regularizable
        self.params += self.Conv.params + self.BN.params
        ConvBNAct.layers.append(self)
        if not show:
            print('@ {} Conv BN Act: {} -> {}'.format(layer_name, input_shape, self.output_shape))

    def get_output(self, input):
        output = utils.inference(input, self.block)
        return output

    @property
    @validate
    def output_shape(self):
        return self.block[-1].output_shape

    @staticmethod
    def reset():
        pass


class ConvolutionalZeroPhaseLayer(Layer):
    layers = []

    def __init__(self, input_shape, filter_shape, He_init=None, He_init_gain='relu', W1=None, W2=None, b=None, no_bias=True,
                 border_mode='half', stride=(1, 1), layer_name='conv', activation='relu', pool=False,
                 pool_size=(2, 2), pool_mode='max', pool_stride=(2, 2), pool_pad=(0, 0), target='dev0'):
        '''

        :param input_shape: (B, C, H, W)
        :param filter_shape: (num filters, num input channels, H, W)
        :param He_init:
        :param He_init_gain:
        :param W:
        :param b:
        :param no_bias: True (default) or False
        :param border_mode:
        :param stride:
        :param layer_name:
        :param activation:
        :param pool:
        :param pool_size:
        :param pool_mode:
        :param pool_stride:
        :param pool_pad:
        :param target:
        '''
        assert isinstance(input_shape, list) or isinstance(input_shape, tuple), \
            'input_shape must be list or tuple. Received %s' % type(input_shape)
        assert len(input_shape) == 2 or len(input_shape) == 4, \
            'input_shape must have 2 or 4 elements. Received %d' % len(input_shape)
        assert len(input_shape) == len(filter_shape) == 4, \
            'Filter shape and input shape must be 4-dimensional. Received %d and %d' % \
            (len(input_shape), len(filter_shape))
        super(ConvolutionalZeroPhaseLayer, self).__init__()

        self.input_shape = tuple(input_shape)
        self.filter_shape = tuple(filter_shape)
        self.no_bias = no_bias
        self.activation = utils.function[activation]
        self.He_init = He_init
        self.He_init_gain = He_init_gain
        self.layer_name = layer_name
        self.border_mode = border_mode
        self.subsample = stride
        self.pool = pool
        self.pool_size = pool_size
        self.pool_mode = pool_mode
        self.pool_stride = pool_stride
        self.pool_pad = pool_pad
        self.target = target

        filter_shape = list(self.filter_shape)
        filter_shape[3] = 1
        if W1 is None:
            if He_init:
                self.W_values1 = self.init_he(filter_shape, self.He_init_gain, He_init)
            else:
                fan_in = np.prod(self.filter_shape[1:])
                fan_out = (self.filter_shape[0] * np.prod(self.filter_shape[2:]))
                W_bound = np.sqrt(6. / (fan_in + fan_out))
                self.W_values1 = np.asarray(self.rng.uniform(low=-W_bound, high=W_bound, size=filter_shape),
                                           dtype=theano.config.floatX)
        else:
            self.W_values1 = W1
        self.W1 = theano.shared(self.W_values1, name=self.layer_name + '_W1', borrow=True)#, target=self.target)

        filter_shape[1] = filter_shape[0]
        if W2 is None:
            if He_init:
                self.W_values2 = self.init_he(filter_shape, self.He_init_gain, He_init)
            else:
                fan_in = np.prod(self.filter_shape[1:])
                fan_out = (self.filter_shape[0] * np.prod(self.filter_shape[2:]))
                W_bound = np.sqrt(6. / (fan_in + fan_out))
                self.W_values2 = np.asarray(self.rng.uniform(low=-W_bound, high=W_bound, size=filter_shape),
                                           dtype=theano.config.floatX)
        else:
            self.W_values2 = W2
        self.W2 = theano.shared(self.W_values2, name=self.layer_name + '_W2', borrow=True)#, target=self.target)
        self.scale = theano.shared(np.ones(self.filter_shape[0], dtype=theano.config.floatX),
                                   name=self.layer_name + '_scale', borrow=True)
        self.bias = theano.shared(np.zeros(self.filter_shape[0], dtype=theano.config.floatX),
                                  name=self.layer_name + '_bias', borrow=True)

        if not self.no_bias:
            if b is None:
                self.b_values = np.zeros(filter_shape[0], dtype=theano.config.floatX)
            else:
                self.b_values = b
            self.b = theano.shared(self.b_values, self.layer_name + '_b', borrow=True)
            self.trainable.append(self.b)
            self.params.append(self.b)

        self.params += [self.W1, self.W2, self.scale, self.bias]
        self.trainable += [self.W1, self.W2, self.scale, self.bias]
        self.regularizable += [self.W1, self.W2, self.scale]

        print('@ {} Conv Zero Phase Layer: '.format(self.layer_name), 'border mode: {} '.format(border_mode),
              'subsampling: {} '.format(stride), end=' ')
        print('shape: {} , '.format(input_shape), end=' ')
        print('filter shape: {} '.format(self.filter_shape), end=' ')
        print('-> {} '.format(self.output_shape), end=' ')
        print('activation: {} '.format(activation), end=' ')
        print('{} pool {}'.format(self.pool_mode, self.pool))
        ConvolutionalZeroPhaseLayer.layers.append(self)

    def get_output(self, input):
        W1 = (self.W1 + self.W1[:, :, ::-1]) / np.float32(2.)
        W2 = (self.W2 + self.W2[:, :, ::-1]) / np.float32(2.)
        output = conv(input=input, filters=W1, border_mode=self.border_mode, subsample=(self.subsample[0], 1))
        output = conv(input=output, filters=W2.dimshuffle((0, 1, 3, 2)), border_mode=self.border_mode, subsample=(1, self.subsample[1]))
        output = self.scale.dimshuffle(('x', 0, 'x', 'x')) * output + self.bias.dimshuffle(('x', 0, 'x', 'x'))

        if not self.no_bias:
            output += self.b.dimshuffle(('x', 0, 'x', 'x'))
        output = output if not self.pool else pool(input=output, ws=self.pool_size, ignore_border=False,
                                                   mode=self.pool_mode, pad=self.pool_pad, stride=self.pool_stride)
        return self.activation(T.clip(output, 1e-7, 1.0 - 1e-7)) if self.activation is utils.function['sigmoid'] \
            else self.activation(output)

    @property
    @validate
    def output_shape(self):
        size = list(self.input_shape)
        assert len(size) == 4, "Shape must consist of 4 elements only"

        if self.border_mode == 'half':

            p = (self.filter_shape[2] // 2, self.filter_shape[3] // 2)
        elif self.border_mode == 'valid':
            p = (0, 0)
        elif self.border_mode == 'full':
            p = (self.filter_shape[2] - 1, self.filter_shape[3] - 1)
        else:
            raise NotImplementedError

        size[2] = (size[2] - self.filter_shape[2] + 2 * p[0]) // self.subsample[0] + 1
        size[3] = (size[3] - self.filter_shape[3] + 2 * p[1]) // self.subsample[1] + 1
        if self.pool:
            size[2] = np.ceil((size[2] + 2 * self.pool_pad[0] - self.pool_size[0]) / self.pool_stride[0] + 1)
            size[3] = np.ceil((size[3] + 2 * self.pool_pad[1] - self.pool_size[1]) / self.pool_stride[1] + 1)

        size[1] = self.filter_shape[0] // 2 if self.activation is 'maxout' else self.filter_shape[0]
        return tuple(size)

    @staticmethod
    def reset():
        for layer in ConvolutionalLayer.layers:
            layer.W.set_value(layer.W_values)
            if not layer.no_bias:
                layer.b.set_value(layer.b_values)


class TransposedConvolutionalLayer(Layer):
    layers = []

    def __init__(self, input_shape, num_filters, filter_size, output_shape=None, He_init=None, layer_name='transconv', W=None,
                 b=None, padding='half', stride=(2, 2), activation='relu', target='dev0'):
        """

        :param input_shape:
        :param num_filters:
        :param filter_size:
        :param output_shape:
        :param He_init:
        :param layer_name:
        :param W:
        :param b:
        :param padding:
        :param stride:
        :param activation:
        :param target:
        """
        assert isinstance(num_filters, int) and isinstance(filter_size, (int, list, tuple))
        super(TransposedConvolutionalLayer, self).__init__()
        self.filter_shape = (input_shape[1], num_filters, filter_size[0], filter_size[1]) if isinstance(filter_size, (list, tuple)) \
            else (input_shape[1], num_filters, filter_size, filter_size)
        self.input_shape = tuple(input_shape)
        self.output_shape_tmp = (input_shape[0], num_filters, output_shape[0], output_shape[1]) \
            if output_shape is not None else output_shape
        self.padding = padding
        self.stride = stride
        self.activation = utils.function[activation]
        self.layer_name = layer_name
        self.target = target
        self.layer_type = 'Transposed Convolutional Layer {} filters size {} padding {} stride {} {}'.\
            format(num_filters, filter_size, padding, stride, activation)

        self.b_values = np.zeros((self.filter_shape[1],), dtype=theano.config.floatX) if b is None else b
        # self.W_values = self._get_deconv_filter() if W is None else W
        if W is None:
            if He_init:
                self.W_values = self.init_he(self.filter_shape, 'relu', He_init)
            else:
                fan_in = np.prod(self.filter_shape[1:])
                fan_out = (self.filter_shape[0] * np.prod(self.filter_shape[2:]))
                W_bound = np.sqrt(6. / (fan_in + fan_out))
                self.W_values = np.asarray(self.rng.uniform(low=-W_bound, high=W_bound, size=self.filter_shape),
                                           dtype=theano.config.floatX)
        else:
            self.W_values = W
        self.W = theano.shared(self.W_values, self.layer_name + '_W', borrow=True)#, target=self.target)
        self.b = theano.shared(value=self.b_values, name=self.layer_name + '_b', borrow=True)#, target=self.target)
        self.params += [self.W, self.b]
        self.trainable += [self.W, self.b]
        self.regularizable.append(self.W)
        print('@ {} Transposed Conv Layer: '.format(layer_name), end=' ')
        print('shape: {} '.format(input_shape), end=' ')
        print('filter shape: {} '.format(self.filter_shape), end=' ')
        print('-> {} '.format(self.output_shape), end=' ')
        print('padding: {}'.format(self.padding), end=' ')
        print('stride: {}'.format(self.stride), end=' ')
        print('activation: {}'.format(activation))
        TransposedConvolutionalLayer.layers.append(self)

    def _get_deconv_filter(self):
        """
        This function is collected
        :param f_shape: self.filter_shape
        :return: an initializer for get_variable
        """
        width = self.filter_shape[2]
        height = self.filter_shape[3]
        f = math.ceil(width/2.0)
        c = (2 * f - 1 - f % 2) / (2.0 * f)
        bilinear = np.zeros([self.filter_shape[2], self.filter_shape[3]])
        for x in range(width):
            for y in range(height):
                value = (1 - abs(x / f - c)) * (1 - abs(y / f - c))
                bilinear[x, y] = value
        weights = np.zeros(self.filter_shape)
        for j in range(self.filter_shape[1]):
            for i in range(self.filter_shape[0]):
                weights[i, j, :, :] = bilinear
        return weights.astype(theano.config.floatX)

    def get_output(self, output):
        if self.padding == 'half':
            p = (self.filter_shape[2] // 2, self.filter_shape[3] // 2)
        elif self.padding == 'valid':
            p = (0, 0)
        elif self.padding == 'full':
            p = (self.filter_shape[2] - 1, self.filter_shape[3] - 1)
        else:
            raise NotImplementedError
        if self.output_shape_tmp is None:
            in_shape = output.shape
            h = ((in_shape[2] - 1) * self.stride[0]) + self.filter_shape[2] + \
                T.mod(in_shape[2]+2*p[0]-self.filter_shape[2], self.stride[0]) - 2*p[0]
            w = ((in_shape[3] - 1) * self.stride[1]) + self.filter_shape[3] + \
                T.mod(in_shape[3]+2*p[1]-self.filter_shape[3], self.stride[1]) - 2*p[1]
            self.output_shape_tmp = [self.output_shape_tmp[0], self.filter_shape[1], h, w]

        op = T.nnet.abstract_conv.AbstractConv2d_gradInputs(imshp=self.output_shape_tmp, kshp=self.filter_shape,
                                                            subsample=self.stride, border_mode=self.padding)
        input = op(self.W, output, self.output_shape_tmp[-2:])
        input = input + self.b.dimshuffle('x', 0, 'x', 'x')
        return self.activation(input)

    @property
    @validate
    def output_shape(self):
        return tuple(self.output_shape_tmp)

    @staticmethod
    def reset():
        for layer in TransposedConvolutionalLayer.layers:
            layer.W.set_value(layer.W_values)
            layer.b.set_value(layer.b_values)


class UpsampleConvLayer(Layer):
    def __init__(self, input_shape, num_filters, filter_size, rate=(2, 2), activation='relu', he_init=True,
                 biases=True, layer_name='Upsample Conv'):
        super(UpsampleConvLayer, self).__init__()
        self.input_shape = tuple(input_shape)
        self.num_filters = num_filters
        self.filter_size = filter_size
        self.rate = rate
        self.activation = activation
        self.he_init = he_init
        self.biases = biases
        self.layer_name = layer_name
        self.layer_type = 'Upsample Convolutional Block'

        self.shape = (self.input_shape[0], self.input_shape[1], self.input_shape[2]*rate[0], self.input_shape[3]*rate[1])
        self.conv = ConvolutionalLayer(self.shape, num_filters, filter_size, 'uniform' if self.he_init else None, activation=self.activation,
                                       layer_name=self.layer_name, no_bias=not self.biases)
        self.params += self.conv.params
        self.trainable += self.conv.trainable
        self.regularizable += self.conv.regularizable
        print('@ {} Upsample Conv: {} -> {}'.format(layer_name, self.input_shape, self.output_shape))

    def get_output(self, input):
        output = input
        output = T.concatenate([output for i in range(np.sum(self.rate))], 1)
        output = T.transpose(output, (0, 2, 3, 1))
        output = T.reshape(output, (-1, self.shape[2], self.shape[3], self.shape[1]))
        output = T.transpose(output, (0, 3, 1, 2))
        return self.conv(output)

    @property
    def output_shape(self):
        return (self.shape[0], self.num_filters, self.shape[2], self.shape[3])

    @staticmethod
    def reset():
        reset_training()


class MeanPoolConvLayer(Layer):
    def __init__(self, input_shape, num_filters, filter_size, activation='relu', he_init=True, biases=True, layer_name='Mean Pool Conv'):
        assert input_shape[2] / 2 == input_shape[2] // 2 and input_shape[3] / 2 == input_shape[3] // 2, 'Input must have even shape.'
        super(MeanPoolConvLayer, self).__init__()
        self.input_shape = tuple(input_shape)
        self.num_filters = num_filters
        self.filter_size = filter_size
        self.activation = activation
        self.he_init = he_init
        self.biases = biases
        self.layer_name = layer_name

        self.shape = (self.input_shape[0], self.input_shape[1], self.input_shape[2]//2, self.input_shape[3]//2)
        self.conv = ConvolutionalLayer(self.shape, num_filters, filter_size, 'uniform' if self.he_init else None,
                                       activation=self.activation, layer_name=self.layer_name, no_bias=not self.biases)
        self.params += self.conv.params
        self.trainable += self.conv.trainable
        self.regularizable += self.conv.regularizable
        print('@ {} Mean Pool Conv layer: {} -> {}'.format(layer_name, self.input_shape, self.output_shape))

    def get_output(self, input):
        output = input
        output = (output[:, :, ::2, ::2] + output[:, :, 1::2, ::2] + output[:, :, ::2, 1::2] + output[:, :, 1::2, 1::2]) / 4.
        return self.conv(output)

    @property
    def output_shape(self):
        return (self.shape[0], self.num_filters, self.shape[2], self.shape[3])

    @staticmethod
    def reset():
        reset_training()


class ConvMeanPoolLayer(Layer):
    def __init__(self, input_shape, num_filters, filter_size, activation='relu', he_init=True, biases=True, layer_name='Mean Pool Conv'):
        assert input_shape[2] / 2 == input_shape[2] // 2 and input_shape[3] / 2 == input_shape[3] // 2, 'Input must have even shape.'
        super(ConvMeanPoolLayer, self).__init__()
        self.input_shape = tuple(input_shape)
        self.num_filters = num_filters
        self.filter_size = filter_size
        self.activation = activation
        self.he_init = he_init
        self.biases = biases
        self.layer_name = layer_name

        f_shape = (self.num_filters, self.input_shape[1], filter_size, filter_size)
        self.conv = ConvolutionalLayer(self.input_shape, num_filters, filter_size, 'uniform' if self.he_init else None,
                                       activation=self.activation, layer_name=self.layer_name, no_bias=not self.biases)
        self.params += self.conv.params
        self.trainable += self.conv.trainable
        self.regularizable += self.conv.regularizable
        print('@ {} Conv Mean Pool: {} -> {}'.format(layer_name, self.input_shape, self.output_shape))

    def get_output(self, input):
        output = input
        output = self.conv(output)
        return (output[:, :, ::2, ::2] + output[:, :, 1::2, ::2] + output[:, :, ::2, 1::2] + output[:, :, 1::2, 1::2]) / 4.

    @property
    def output_shape(self):
        return (self.input_shape[0], self.num_filters, self.input_shape[2]//2, self.input_shape[3]//2)

    @staticmethod
    def reset():
        reset_training()


class ResNetBlockWGAN(Layer):
    def __init__(self, input_shape, num_filters, filter_size, activation='relu', resample=None, he_init=True, layer_name='ResNet Block WGAN'):
        super(ResNetBlockWGAN, self).__init__()
        self.input_shape = tuple(input_shape)
        self.num_filters = num_filters
        self.filter_size = filter_size
        self.activation = activation
        self.resample = resample
        self.he_init = he_init
        self.layer_name = layer_name

        self.block = []
        self.proj = []
        if resample == 'down':
            self.proj.append(MeanPoolConvLayer(input_shape, num_filters, 1, 'linear', False, True, layer_name + '_shortcut'))

            self.block.append(LayerNormLayer(self.input_shape, layer_name + '_ln1', activation=activation))
            self.block.append(ConvolutionalLayer(self.block[-1].output_shape, input_shape[1], filter_size, 'uniform', no_bias=True,
                                                 layer_name=layer_name+'_conv1', activation='linear'))
            self.block.append(LayerNormLayer(self.block[-1].output_shape, layer_name + '_ln2', activation=activation))
            self.block.append(ConvMeanPoolLayer(self.block[-1].output_shape, num_filters, filter_size, 'linear',
                                                he_init, True, layer_name + '_ConvMeanPool'))
        elif resample == 'up':
            self.proj.append(UpsampleConvLayer(input_shape, num_filters, 1, 'linear', False, True, layer_name + '_shortcut'))

            self.block.append(BatchNormLayer(self.input_shape, layer_name + '_bn1', activation=activation))
            self.block.append(UpsampleConvLayer(self.block[-1].output_shape, num_filters, filter_size, 'linear',
                                                he_init, False, layer_name + '_UpConv'))
            self.block.append(BatchNormLayer(self.block[-1].output_shape, layer_name+'_bn2', activation=activation))
            self.block.append(ConvolutionalLayer(self.block[-1].output_shape, num_filters, filter_size, 'uniform', no_bias=False,
                                                 activation='linear', layer_name=layer_name+'_conv2'))
        elif resample is None:
            if input_shape[1] == num_filters:
                self.proj.append(IdentityLayer(input_shape, layer_name+'_shortcut'))
            else:
                f_shape = (num_filters, input_shape[1], 1, 1)
                self.proj.append(ConvolutionalLayer(input_shape, f_shape, None, activation='linear', no_bias=False,
                                                    layer_name=layer_name+'_shortcut'))

            f_shape = (input_shape[1], self.block[-1].output_shape[1], filter_size, filter_size)
            self.block.append(ConvolutionalLayer(self.block[-1].output_shape, f_shape, 'uniform', activation='linear',
                                                 layer_name=layer_name+'_conv1'))
            self.block.append(BatchNormLayer(self.block[-1].output_shape, layer_name+'_bn2', activation=activation))
            f_shape = (num_filters, self.block[-1].output_shape[1], filter_size, filter_size)
            self.block.append(ConvolutionalLayer(self.block[-1].output_shape, f_shape, 'uniform', activation='linear',
                                                 layer_name=layer_name+'_conv2'))
        else:
            raise NotImplementedError
        self.params += [p for layer in self.block for p in layer.params]
        self.params += [p for layer in self.proj for p in layer.params]
        self.trainable += [p for layer in self.block for p in layer.trainable]
        self.trainable += [p for layer in self.proj for p in layer.trainable]
        self.regularizable += [p for layer in self.block for p in layer.regularizable]
        self.regularizable += [p for layer in self.proj for p in layer.regularizable]

    @property
    def output_shape(self):
        return self.block[-1].output_shape

    def get_output(self, input):
        output = input
        for layer in self.block:
            output = layer(output)

        shortcut = input
        for layer in self.proj:
            shortcut = layer(shortcut)
        return shortcut + output

    @staticmethod
    def reset():
        reset_training()


class ResNetBlock(Layer):
    layers = []

    def __init__(self, input_shape, num_filters, stride=(1, 1), dilation=(1, 1), activation='relu', left_branch=False,
                 layer_name='ResBlock', **kwargs):
        '''

        :param input_shape: (
        :param down_dim:
        :param up_dim:
        :param stride:
        :param activation:
        :param layer_name:
        :param branch1_conv:
        :param target:
        '''
        assert left_branch or (input_shape[1] == num_filters), 'Cannot have identity branch when input dim changes.'
        super(ResNetBlock, self).__init__()

        self.input_shape = tuple(input_shape)
        self.num_filters = num_filters
        self.stride = stride
        self.dilation = dilation
        self.layer_name = layer_name
        self.activation = activation
        self.left_branch = left_branch
        self.kwargs = kwargs
        self.layer_type = 'ResNet Block 1 {} filters stride {} dilation {} left branch {} {} {}'.\
            format(num_filters, stride,dilation, left_branch, activation, ' '.join([' '.join((k, str(v))) for k, v in kwargs.items()]))

        self.block = []
        self.proj = []

        self.block += self._build_simple_block(block_name=layer_name + '_1', no_bias=True)
        self.params += [p for layer in self.block for p in layer.params]
        self.trainable += [p for layer in self.block for p in layer.trainable]
        self.regularizable += [p for layer in self.block for p in layer.regularizable]

        if self.left_branch:
            self.proj.append(ConvolutionalLayer(self.input_shape, num_filters, 3, 'normal',
                                                stride=stride, layer_name=layer_name+'_2', activation='linear'))
            self.proj.append(BatchNormLayer(self.proj[-1].output_shape, layer_name=layer_name+'_2_bn', activation='linear'))
            self.params += [p for layer in self.proj for p in layer.params]
            self.trainable += [p for layer in self.proj for p in layer.trainable]
            self.regularizable += [p for layer in self.proj for p in layer.regularizable]
        ResNetBlock.layers.append(self)

    def _build_simple_block(self, block_name, no_bias):
        layers = []
        layers.append(ConvolutionalLayer(self.input_shape, self.num_filters, 3, border_mode='half', stride=self.stride,
                                         dilation=self.dilation, layer_name=block_name + '_conv1', no_bias=no_bias,
                                         activation='linear'))
        layers.append(BatchNormLayer(layers[-1].output_shape, activation=self.activation,
                                     layer_name=block_name + '_conv1_bn', **self.kwargs))

        layers.append(ConvolutionalLayer(layers[-1].output_shape, self.num_filters, 3, border_mode='half', dilation=self.dilation,
                                         layer_name=block_name + '_conv2', no_bias=no_bias, activation='linear'))
        layers.append(BatchNormLayer(layers[-1].output_shape, layer_name=block_name + '_conv2_bn', activation='linear'))
        return layers

    def get_output(self, input):
        output = input
        for layer in self.block:
            output = layer(output)

        res = input
        if self.left_branch:
            for layer in self.proj:
                res = layer(res)
        return utils.function[self.activation](output + res, **self.kwargs)

    @property
    @validate
    def output_shape(self):
        return self.block[-1].output_shape

    @staticmethod
    def reset():
        reset_training()


class ResNetBlock2(Layer):
    layers = []

    def __init__(self, input_shape, ratio_n_filter=1.0, stride=1, upscale_factor=4, dilation=(1, 1),
                 activation='relu', left_branch=False, layer_name='ResBlock'):
        '''

        :param input_shape: (
        :param down_dim:
        :param up_dim:
        :param stride:
        :param activation:
        :param layer_name:
        :param branch1_conv:
        :param target:
        '''
        super(ResNetBlock2, self).__init__()

        self.input_shape = tuple(input_shape)
        self.ratio_n_filter = ratio_n_filter
        self.stride = stride
        self.upscale_factor = upscale_factor
        self.dilation = dilation
        self.layer_name = layer_name
        self.activation = activation
        self.left_branch = left_branch
        self.layer_type = 'ResNet Block 2 ratio {} stride {} upscale {} dilation {} left branch {} {}'.\
            format(ratio_n_filter, stride, upscale_factor, dilation, left_branch, activation)

        self.block = []
        self.proj = []

        self.block += self._build_simple_block(block_name=layer_name + '_1', no_bias=True)
        self.params += [p for layer in self.block for p in layer.params]
        self.trainable += [p for layer in self.block for p in layer.trainable]
        self.regularizable += [p for layer in self.block for p in layer.regularizable]

        if self.left_branch:
            self.proj.append(ConvBNAct(self.input_shape, int(input_shape[1]*4*ratio_n_filter), 1, 'normal',
                                       stride=stride, layer_name=layer_name+'_2', activation='linear'))
            self.params += [p for layer in self.proj for p in layer.params]
            self.trainable += [p for layer in self.proj for p in layer.trainable]
            self.regularizable += [p for layer in self.proj for p in layer.regularizable]
        ResNetBlock.layers.append(self)

    def _build_simple_block(self, block_name, no_bias):
        layers = []
        layers.append(ConvBNAct(self.input_shape, int(self.input_shape[1]*self.ratio_n_filter), 1, 'normal',
                                stride=self.stride, no_bias=no_bias, activation=self.activation, layer_name=block_name+'_conv_bn_act_1'))

        layers.append(ConvBNAct(layers[-1].output_shape, layers[-1].output_shape[1], 3, stride=(1, 1), border_mode='half',
                                activation=self.activation, layer_name=block_name+'_conv_bn_act_2', no_bias=no_bias))

        layers.append(ConvBNAct(layers[-1].output_shape, layers[-1].output_shape[1]*self.upscale_factor, 1, stride=1,
                                activation='linear', layer_name=block_name+'_conv_bn_act_3', no_bias=no_bias))
        return layers

    def get_output(self, input):
        output = input
        for layer in self.block:
            output = layer(output)

        res = input
        if self.left_branch:
            for layer in self.proj:
                res = layer(res)
        return utils.function[self.activation](output + res)

    @property
    @validate
    def output_shape(self):
        return self.block[-1].output_shape

    @staticmethod
    def reset():
        reset_training()


class DenseBlock(Layer):
    layers = []

    def __init__(self, input_shape, transit=False, num_conv_layer=6, growth_rate=32, dropout=False, activation='relu',
                 layer_name='DenseBlock', pool_transition=True, target='dev0', **kwargs):
        '''

        :param input_shape: (int, int, int, int)
        :param transit:
        :param num_conv_layer:
        :param growth_rate:
        :param activation:
        :param dropout:
        :param layer_name: str
        :param target:
        '''
        super(DenseBlock, self).__init__()

        self.input_shape = tuple(input_shape)
        self.transit = transit
        self.num_conv_layer = num_conv_layer
        self.growth_rate = growth_rate
        self.activation = activation
        self.dropout = dropout
        self.pool_transition = pool_transition
        self.layer_name = layer_name
        self.target = target
        self.kwargs = kwargs
        self.layer_type = 'Dense Block {} conv layers growth rate {} transit {} dropout {} {}'.\
            format(num_conv_layer, growth_rate, transit, dropout, activation)

        if not self.transit:
            self.block = self._dense_block(self.input_shape, self.num_conv_layer, self.growth_rate, self.dropout,
                                           self.activation, self.layer_name)
            pass
        else:
            self.block = self._transition(self.input_shape, self.dropout, self.activation,
                                          self.layer_name + '_transition')
        DenseBlock.layers.append(self)

    def _bn_act_conv(self, input_shape, num_filters, filter_size, dropout, activation, stride=1, layer_name='bn_re_conv'):
        block = [
            BatchNormLayer(input_shape, activation=activation, layer_name=layer_name + '_bn', **self.kwargs),
            ConvolutionalLayer(input_shape, num_filters, filter_size, He_init='normal', stride=stride,
                               activation='linear', layer_name=layer_name + '_conv')
        ]
        for layer in block:
            self.params += layer.params
            self.trainable += layer.trainable
            self.regularizable += layer.regularizable
        if dropout:
            block.append(DropoutLayer(block[-1].output_shape, dropout, activation='linear',
                                      layer_name=layer_name + 'dropout'))
        return block

    def _transition(self, input_shape, dropout, activation, layer_name='transition'):
        if self.pool_transition:
            block = self._bn_act_conv(input_shape, input_shape[1], 1, dropout, activation, layer_name=layer_name)
            block.append(PoolingLayer(block[-1].output_shape, (2, 2), mode='average_inc_pad', ignore_border=False,
                                      layer_name=layer_name + 'pooling'))
        else:
            block = self._bn_act_conv(input_shape, input_shape[1], 1, dropout, activation, stride=2, layer_name=layer_name)
        return block

    def _dense_block(self, input_shape, num_layers, growth_rate, dropout, activation, layer_name='dense_block'):
        block, input_channels = [], input_shape[1]
        i_shape = list(input_shape)
        for n in range(num_layers):
            block.append(self._bn_act_conv(i_shape, growth_rate, 3, dropout, activation, layer_name=layer_name + '_%d' % n))
            input_channels += growth_rate
            i_shape[1] = input_channels
        return block

    def get_output(self, input):
        feed = input
        if not self.transit:
            for layer in self.block:
                output = utils.inference(feed, layer)
                feed = T.concatenate((feed, output), 1)
        else:
            feed = utils.inference(feed, self.block)
        return feed

    @property
    @validate
    def output_shape(self):
        if not self.transit:
            shape = (self.input_shape[0], self.input_shape[1] + self.growth_rate * self.num_conv_layer,
                     self.input_shape[2], self.input_shape[3])
        else:
            shape = self.block[-1].output_shape
        return tuple(shape)

    @staticmethod
    def reset():
        pass


class DenseBlockBRN(Layer):
    def __init__(self, input_shape, transit=False, num_conv_layer=6, growth_rate=32, dropout=False,
                 layer_name='DenseBlock', target='dev0'):
        '''

        :param input_shape: (int, int, int, int)
        :param num_conv_layer: int
        :param growth_rate: int
        :param layer_name: str
        :param target: str
        '''
        super(DenseBlockBRN, self).__init__()

        self.input_shape = tuple(input_shape)
        self.transit = transit
        self.num_conv_layer = num_conv_layer
        self.growth_rate = growth_rate
        self.dropout = dropout
        self.layer_name = layer_name
        self.target = target

        if not self.transit:
            self.block = self._dense_block(self.input_shape, self.num_conv_layer, self.growth_rate, self.dropout, self.layer_name)
            pass
        else:
            self.block = self._transition(self.input_shape, self.dropout, self.layer_name + '_transition')

    def _brn_relu_conv(self, input_shape, filter_shape, dropout, layer_name='bn_re_conv'):
        block = [
            BatchRenormLayer(input_shape, activation='relu', layer_name=layer_name + '_bn'),
            ConvolutionalLayer(input_shape, filter_shape, He_init='normal', He_init_gain=None, activation='linear',
                               layer_name=layer_name + '_conv')
        ]
        for layer in block:
            self.params += layer.params
            self.trainable += layer.trainable
            self.regularizable += layer.regularizable
        if dropout:
            block.append(DropoutLayer(block[-1].output_shape, dropout, activation='linear',
                                      layer_name=layer_name + 'dropout'))
        return block

    def _transition(self, input_shape, dropout, layer_name='transition'):
        filter_shape = (input_shape[1], input_shape[1], 1, 1)
        block = self._brn_relu_conv(input_shape, filter_shape, dropout, layer_name)
        block.append(PoolingLayer(block[-1].output_shape, (2, 2), mode='average_inc_pad',
                                  layer_name=layer_name + 'pooling'))
        return block

    def _dense_block(self, input_shape, num_layers, growth_rate, dropout, layer_name='dense_block'):
        block, input_channels = [], input_shape[1]
        i_shape = list(input_shape)
        for n in range(num_layers):
            filter_shape = (growth_rate, input_channels, 3, 3)
            block.append(self._brn_relu_conv(i_shape, filter_shape, dropout, layer_name + '_%d' % n))
            input_channels += growth_rate
            i_shape[1] = input_channels
        return block

    def get_output(self, input):
        feed = input
        if not self.transit:
            for layer in self.block:
                output = utils.inference(feed, layer)
                feed = T.concatenate((feed, output), 1)
        else:
            feed = utils.inference(feed, self.block)
        return feed

    @property
    @validate
    def output_shape(self):
        if not self.transit:
            shape = (self.input_shape[0], self.input_shape[1] + self.growth_rate * self.num_conv_layer,
                     self.input_shape[2], self.input_shape[3])
        else:
            shape = self.block[-1].output_shape
        return tuple(shape)


class BatchNormLayer(Layer):
    layers = []

    def __init__(self, input_shape, layer_name='BN', epsilon=1e-4, running_average_factor=1e-1, axes='spatial',
                 activation='relu', no_scale=False, show=True, **kwargs):
        '''

        :param input_shape: (int, int, int, int) or (int, int)
        :param layer_name: str
        :param epsilon: float
        :param running_average_factor: float
        :param axes: 'spatial' or 'per-activation'
        '''
        super(BatchNormLayer, self).__init__()

        self.layer_name = layer_name
        self.input_shape = tuple(input_shape)
        self.epsilon = np.float32(epsilon)
        self.running_average_factor = running_average_factor
        self.activation = utils.function[activation]
        self.no_scale = no_scale
        self.show = show
        self.training_flag = False
        self.axes = (0,) + tuple(range(2, len(input_shape))) if axes == 'spatial' else (0,)
        self.shape = (self.input_shape[1],) if axes == 'spatial' else self.input_shape[1:]
        self.kwargs = kwargs
        self.layer_type = 'Batch Normalization Layer axes {} epsilon {} running average factor {} {} {}'.\
            format(axes, epsilon, running_average_factor, activation, ' '.join([' '.join((k, str(v))) for k, v in kwargs.items()]))

        self.gamma_values = np.ones(self.shape, dtype=theano.config.floatX)
        self.gamma = theano.shared(self.gamma_values, name=layer_name + '_gamma', borrow=True)

        self.beta_values = np.zeros(self.shape, dtype=theano.config.floatX)
        self.beta = theano.shared(self.beta_values, name=layer_name + '_beta', borrow=True)

        self.running_mean = theano.shared(np.zeros(self.shape, dtype=theano.config.floatX),
                                          name=layer_name + '_running_mean', borrow=True)
        self.running_var = theano.shared(np.zeros(self.shape, dtype=theano.config.floatX),
                                         name=layer_name + '_running_var', borrow=True)

        self.params += [self.gamma, self.beta, self.running_mean, self.running_var]
        self.trainable += [self.beta] if self. no_scale else [self.beta, self.gamma]
        self.regularizable += [self.gamma] if not self.no_scale else []

        if self.show:
            print('@ {} BatchNorm Layer: shape: {} -> {} running_average_factor = {:.4f} activation: {}'
                  .format(layer_name, self.input_shape, self.output_shape, self.running_average_factor, activation))
        BatchNormLayer.layers.append(self)

    def batch_normalization_train(self, input):
        out, _, _, mean_, var_ = T.nnet.bn.batch_normalization_train(input, self.gamma, self.beta, self.axes,
                                                                     self.epsilon, self.running_average_factor,
                                                                     self.running_mean, self.running_var)

        # Update running mean and variance
        # Tricks adopted from Lasagne implementation
        # http://lasagne.readthedocs.io/en/latest/modules/layers/normalization.html
        running_mean = theano.clone(self.running_mean, share_inputs=False)
        running_var = theano.clone(self.running_var, share_inputs=False)
        running_mean.default_update = mean_
        running_var.default_update = var_
        out += 0 * (running_mean + running_var)
        return out

    def batch_normalization_test(self, input):
        out = T.nnet.bn.batch_normalization_test(input, self.gamma, self.beta, self.running_mean, self.running_var,
                                                 axes=self.axes, epsilon=self.epsilon)
        return out

    def get_output(self, input):
        return self.activation(self.batch_normalization_train(input) if self.training_flag
                               else self.batch_normalization_test(input), **self.kwargs)

    @property
    @validate
    def output_shape(self):
        return tuple(self.input_shape)

    @staticmethod
    def set_training(training):
        for layer in BatchNormLayer.layers:
            layer.training_flag = training

    @staticmethod
    def reset():
        for layer in BatchNormLayer.layers:
            layer.gamma.set_value(layer.gamma_values)
            layer.beta.set_value(layer.beta_values)


class LayerNormLayer(Layer):
    layers = []

    def __init__(self, input_shape, layer_name='LN', epsilon=1e-4, axes='all-nodes', activation='relu'):
        super(LayerNormLayer, self).__init__()
        self.layer_name = layer_name
        self.input_shape = tuple(input_shape)
        self.epsilon = np.float32(epsilon)
        self.activation = utils.function[activation]
        if axes == 'all-nodes':
            self.axes = [i for i in range(1, len(self.input_shape))]
        else:
            raise NotImplementedError
        self.gamma_values = np.ones(self.input_shape[1], dtype=theano.config.floatX)
        self.gamma = theano.shared(self.gamma_values, name=layer_name + '_gamma', borrow=True)

        self.beta_values = np.zeros(self.input_shape[1], dtype=theano.config.floatX)
        self.beta = theano.shared(self.beta_values, name=layer_name + '_beta', borrow=True)

        self.params += [self.gamma, self.beta]
        self.trainable += [self.gamma, self.beta]
        self.regularizable += [self.gamma]
        print('@ {} LayerNorm Layer: shape: {} -> {} activation: {}'
              .format(layer_name, self.input_shape, self.output_shape, activation))
        LayerNormLayer.layers.append(self)

    def get_output(self, input):
        mean = T.mean(input, self.axes).dimshuffle((0, 'x', 'x', 'x'))
        var = T.var(input, self.axes).dimshuffle((0, 'x', 'x', 'x'))
        gamma = self.gamma.dimshuffle(('x', 0, 'x', 'x'))
        beta = self.beta.dimshuffle(('x', 0, 'x', 'x'))
        output = gamma * (input - mean) / T.sqrt(var + self.epsilon) + beta
        return self.activation(output)

    @property
    def output_shape(self):
        return tuple(self.input_shape)

    @staticmethod
    def reset():
        for layer in LayerNormLayer.layers:
            layer.gamma.set_value(layer.gamma_values)
            layer.beta.set_value(layer.beta_values)


class BatchRenormLayer(Layer):
    layers = []

    def __init__(self, input_shape, layer_name='BN', epsilon=1e-4, r_max=1, d_max=0, running_average_factor=0.1,
                 axes='spatial', activation='relu'):
        '''

        :param input_shape: (int, int, int, int) or (int, int)
        :param layer_name: str
        :param epsilon: float
        :param running_average_factor: float
        :param axes: 'spatial' or 'per-activation'
        '''
        super(BatchRenormLayer, self).__init__()

        self.layer_name = layer_name
        self.input_shape = tuple(input_shape)
        self.epsilon = epsilon
        self.running_average_factor = running_average_factor
        self.activation = utils.function[activation]
        self.training_flag = False
        self.r_max = theano.shared(np.float32(r_max), name=layer_name + 'rmax')
        self.d_max = theano.shared(np.float32(d_max), name=layer_name + 'dmax')
        self.axes = (0,) + tuple(range(2, len(input_shape))) if axes == 'spatial' else (0,)
        self.shape = (self.input_shape[1],) if axes == 'spatial' else self.input_shape[1:]

        self.gamma_values = np.ones(self.shape, dtype=theano.config.floatX)
        self.beta_values = np.zeros(self.shape, dtype=theano.config.floatX)
        self.gamma = theano.shared(self.gamma_values, name=layer_name + '_gamma', borrow=True)
        self.beta = theano.shared(self.beta_values, name=layer_name + '_beta', borrow=True)
        self.running_mean = theano.shared(np.zeros(self.shape, dtype=theano.config.floatX),
                                          name=layer_name + '_running_mean', borrow=True)
        self.running_var = theano.shared(np.zeros(self.shape, dtype=theano.config.floatX),
                                         name=layer_name + '_running_var', borrow=True)
        self.params += [self.gamma, self.beta, self.running_mean, self.running_var]
        self.trainable += [self.gamma, self.beta]
        self.regularizable.append(self.gamma)
        print('@ {} Batch Renorm Layer: running_average_factor = {:.4f}'.format(layer_name, self.running_average_factor))
        BatchNormLayer.layers.append(self)

    def get_output(self, input):
        batch_mean = T.mean(input, axis=self.axes)
        batch_std = T.sqrt(T.var(input, axis=self.axes) + 1e-10)
        r = T.clip(batch_std / T.sqrt(self.running_var + 1e-10), -self.r_max, self.r_max)
        d = T.clip((batch_mean - self.running_mean) / T.sqrt(self.running_var + 1e-10), -self.d_max, self.d_max)
        out = T.nnet.bn.batch_normalization_test(input, self.gamma, self.beta, batch_mean - d * batch_std / (r + 1e-10),
                                                 T.sqr(batch_std / (r + 1e-10)), axes=self.axes, epsilon=self.epsilon)
        if self.training_flag:
            # Update running mean and variance
            # Tricks adopted from Lasagne implementation
            # http://lasagne.readthedocs.io/en/latest/modules/layers/normalization.html
            m = T.cast(T.prod(input.shape) / T.prod(self.gamma.shape), 'float32')
            running_mean = theano.clone(self.running_mean, share_inputs=False)
            running_var = theano.clone(self.running_var, share_inputs=False)
            running_mean.default_update = running_mean + self.running_average_factor * (batch_mean - running_mean)
            running_var.default_update = running_var * (1. - self.running_average_factor) + \
                                         self.running_average_factor * (m / (m - 1)) * T.sqr(batch_std)
            out += 0 * (running_mean + running_var)
        return self.activation(out)

    @property
    @validate
    def output_shape(self):
        return tuple(self.input_shape)

    @staticmethod
    def set_training(training):
        for layer in BatchRenormLayer.layers:
            layer.training_flag = training

    @staticmethod
    def reset():
        for layer in BatchRenormLayer.layers:
            layer.gamma.set_value(layer.gamma_values)
            layer.beta.set_value(layer.beta_values)


class IdentityLayer(Layer):
    def __init__(self, input_shape, layer_name='Identity'):
        super(IdentityLayer, self).__init__()
        self.input_shape = tuple(input_shape)
        self.layer_name = layer_name
        self.layer_type = 'Identity Layer'
        print('%s Identity layer.' % layer_name)

    @property
    def output_shape(self):
        return tuple(self.input_shape)

    def get_output(self, input):
        return input

    @staticmethod
    def reset():
        return


class ResizingLayer(Layer):
    def __init__(self, input_shape, ratio=None, frac_ratio=None, layer_name='Upsampling'):
        super(ResizingLayer, self).__init__()
        if ratio / 2 != ratio // 2:
            raise NotImplementedError
        self.input_shape = tuple(input_shape)
        self.ratio = ratio
        self.frac_ratio = frac_ratio
        self.layer_name = layer_name
        self.layer_type = 'Resizing Layer ratio {} fraction ratio {}'.format(ratio, frac_ratio)
        print('@ {} x{} Resizing Layer {} -> {}'.format(layer_name, self.ratio, self.input_shape, self.output_shape))

    def get_output(self, input):
        return T.nnet.abstract_conv.bilinear_upsampling(input, ratio=self.ratio) #if self.frac_ratio is None \
            # else T.nnet.abstract_conv.bilinear_upsampling(input, frac_ratio=self.frac_ratio)

    @property
    @validate
    def output_shape(self):
        return (self.input_shape[0], self.input_shape[1], self.input_shape[2] * self.ratio, self.input_shape[3] * self.ratio)

    @staticmethod
    def reset():
        pass


class ReshapingLayer(Layer):
    def __init__(self, input_shape, new_shape, layer_name='reshape'):
        super(ReshapingLayer, self).__init__()
        self.input_shape = tuple(input_shape)
        self.new_shape = tuple(new_shape)
        self.layer_name = layer_name
        self.layer_type = 'Reshaping Layer -> {}'.format(new_shape)
        print('@ Reshaping Layer: {} -> {}'.format(self.input_shape, self.output_shape))

    def get_output(self, input):
        return T.reshape(input, self.new_shape)

    @property
    @validate
    def output_shape(self):
        if self.new_shape[0] == -1:
            output = list(self.new_shape)
            output[0] = None
            return tuple(output)
        else:
            prod_shape = np.prod(self.input_shape[1:])
            prod_new_shape = np.prod(self.new_shape) * -1
            shape = [x if x != -1 else prod_shape // prod_new_shape for x in self.input_shape]
            return tuple(shape)

    @staticmethod
    def reset():
        pass


class SlicingLayer(Layer):
    def __init__(self, input_shape, to_idx, from_idx=(0, 0), axes=(2, 3), layer_name='Slicing Layer'):
        '''

        :param input_shape: (int, int, int, int)
        :param to_idx:
        :param from_idx:
        :param axes:
        :param layer_name:
        '''
        assert isinstance(to_idx, (int, list, tuple)) and isinstance(to_idx, (int, list, tuple)) and isinstance(to_idx, (int, list, tuple))
        super(SlicingLayer, self).__init__()
        self.input_shape = tuple(input_shape)
        self.from_idx = from_idx
        self.to_idx = to_idx
        self.axes = axes
        self.layer_name = layer_name
        self.layer_type = 'Slicing Layer from {} to {} at {}'.format(from_idx, to_idx, axes)
        print('{} Slicing Layer: {} slice from {} to {} at {} -> {}'.format(layer_name, input_shape, from_idx,
                                                                            to_idx, axes, self.output_shape))

    def get_output(self, input):
        assign = dict({0: lambda x, fr, to: x[fr:to], 1: lambda x, fr, to: x[:, fr:to],
                       2: lambda x, fr, to: x[:, :, fr:to], 3: lambda x, fr, to: x[:, :, :, fr:to]})
        if isinstance(self.from_idx, (tuple, list)) and isinstance(self.to_idx, (tuple, list)) \
                and isinstance(self.axes, (tuple, list)):
            assert len(self.from_idx) == len(self.to_idx) == len(self.axes), \
                "Numbers of elements in from_idx, to_idx, and axes must match"
            output = input
            for idx, axis in enumerate(self.axes):
                output = assign[axis](output, self.from_idx[idx], self.to_idx[idx])
        elif isinstance(self.from_idx, int) and isinstance(self.to_idx, int) and isinstance(self.axes, int):
            output = assign[self.axes](input, self.from_idx, self.to_idx)
        else:
            raise NotImplementedError
        return output

    @property
    @validate
    def output_shape(self):
        shape = list(self.input_shape)
        for idx, axis in enumerate(self.axes):
            shape[axis] = self.to_idx[idx] - self.from_idx[idx]
        return shape

    @staticmethod
    def reset():
        pass


class ConcatLayer(Layer):
    def __init__(self, input_shapes, axis=1, layer_name='ConcatLayer'):
        super(ConcatLayer, self).__init__()
        self.input_shapes = tuple(input_shapes)
        self.axis = axis
        self.layer_name = layer_name
        self.layer_type = 'Concatenating Layer at {}'.format(axis)
        print('%s Concat Layer: axis %d' % (layer_name, axis), ' '.join([str(x) for x in input_shapes]),
              '-> {}'.format(self.output_shape))

    def get_output(self, input):
        return T.concatenate(input, self.axis)

    @property
    def output_shape(self):
        shape = np.array(self.input_shapes)
        depth = np.sum(shape[:, 1])
        return (self.input_shapes[0][0], depth, self.input_shapes[0][2], self.input_shapes[0][3])

    @staticmethod
    def reset():
        pass


class SumLayer(Layer):
    def __init__(self, input_shapes, weight=1., layer_name='SumLayer'):
        super(SumLayer, self).__init__()
        self.input_shapes = tuple(input_shapes)
        self.weight = weight
        self.layer_name = layer_name
        self.layer_type = 'Summing Layer weight {}'.format(weight)
        print('%s Sum Layer: weight %d' % (layer_name, weight))

    def get_output(self, input):
        assert isinstance(input, (list, tuple)), 'Input must be a list or tuple of same-sized tensors.'
        return sum(input) * np.float32(self.weight)

    @property
    def output_shape(self):
        return tuple(self.input_shapes[0])

    @staticmethod
    def reset():
        pass


class ScalingLayer(Layer):
    """
    Adapted from Lasagne
    lasagne.layers.ScaleLayer(incoming, scales=lasagne.init.Constant(1),
    shared_axes='auto', **kwargs)

    A layer that scales its inputs by learned coefficients.

    Parameters
    ----------
    incoming : a :class:`Layer` instance or a tuple
        The layer feeding into this layer, or the expected input shape

    scales : Theano shared variable, expression, numpy array, or callable
        Initial value, expression or initializer for the scale.  The scale
        shape must match the incoming shape, skipping those axes the scales are
        shared over (see the example below).  See
        :func:`lasagne.utils.create_param` for more information.

    shared_axes : 'auto', int or tuple of int
        The axis or axes to share scales over. If ``'auto'`` (the default),
        share over all axes except for the second: this will share scales over
        the minibatch dimension for dense layers, and additionally over all
        spatial dimensions for convolutional layers.

    Notes
    -----
    The scales parameter dimensionality is the input dimensionality minus the
    number of axes the scales are shared over, which matches the bias parameter
    conventions of :class:`DenseLayer` or :class:`Conv2DLayer`. For example:

    >>> layer = ScalingLayer((20, 30, 40, 50), shared_axes=(0, 2))
    >>> layer.scales.get_value().shape
    (30, 50)
    """
    def __init__(self, input_shape, scales=1, shared_axes='auto', layer_name='ScaleLayer'):
        super(ScalingLayer, self).__init__()

        self.input_shape = tuple(input_shape)
        if shared_axes == 'auto':
            # default: share scales over all but the second axis
            shared_axes = (0,) + tuple(range(2, len(self.input_shape)))
        elif isinstance(shared_axes, int):
            shared_axes = (shared_axes,)
        self.shared_axes = shared_axes
        self.layer_name = layer_name
        # create scales parameter, ignoring all dimensions in shared_axes
        shape = [size for axis, size in enumerate(self.input_shape)
                 if axis not in self.shared_axes]
        if any(size is None for size in shape):
            raise ValueError("ScaleLayer needs specified input sizes for "
                             "all axes that scales are not shared over.")
        self.scales = theano.shared(scales * np.ones(shape, theano.config.floatX), name=layer_name + 'scales', borrow=True)
        self.params.append(self.scales)
        self.trainable.append(self.scales)

    def get_output(self, input):
        axes = iter(list(range(self.scales.ndim)))
        pattern = ['x' if input_axis in self.shared_axes
                   else next(axes) for input_axis in range(input.ndim)]
        return input * self.scales.dimshuffle(*pattern)

    @property
    @validate
    def output_shape(self):
        return tuple(self.input_shape)

    @staticmethod
    def reset():
        pass


class Gate(object):
    def __init__(self, n_in, n_hid, use_peephole=False, W_hid=None, W_cell=False, bias_init_range=(-.5, .5),
                 layer_name='gate'):
        super(Gate, self).__init__()

        self.n_in = n_in
        self.n_hid = n_hid
        self.bias_init_range = bias_init_range
        self.layer_name = layer_name
        self.use_peephole = use_peephole
        if not use_peephole:
            self.W_hid = theano.shared(self.sample_weights(n_in + n_hid, n_hid), name=layer_name + '_Whid') if W_hid is None else W_hid
        else:
            self.W_hid = theano.shared(self.sample_weights(n_hid, n_hid), name=layer_name + '_Whid_ph') if isinstance(W_cell, int) else W_cell
        self.b = theano.shared(np.cast[theano.config.floatX](np.random.uniform(bias_init_range[0], bias_init_range[1],
                                                                               size=n_hid)), name=layer_name + '_b')

        self.trainable = [self.W_in, self.W_hid, self.W_cell, self.b] if W_cell else [self.W_in, self.W_hid, self.b]
        self.regularizable = [self.W_in, self.W_hid, self.W_cell, self.b] if W_cell else [self.W_in, self.W_hid, self.b]

    def sample_weights(self, sizeX, sizeY):
        values = np.ndarray([sizeX, sizeY], dtype=theano.config.floatX)
        for dx in range(sizeX):
            vals = np.random.uniform(low=-1., high=1., size=(sizeY,))
            # vals_norm = np.sqrt((vals**2).sum())
            # vals = vals / vals_norm
            values[dx, :] = vals
        _, svs, _ = np.linalg.svd(values)
        # svs[0] is the largest singular value
        values = values / svs[0]
        return values


class LSTMcell(Layer):
    def __init__(self, n_in, n_hid, use_peephole=False, tensordot=False, gradien_clipping=False, layer_name='lstmcell'):
        super(LSTMcell, self).__init__()

        self.n_in = n_in
        self.n_hid = n_hid
        self.use_peephole = False
        self.tensordot = tensordot
        self.gradient_clipping = gradien_clipping
        self.layer_name = layer_name
        self.in_gate = Gate(n_in, n_hid, W_cell=True, layer_name='in_gate')
        self.forget_gate = Gate(n_hid, n_hid, W_cell=True, bias_init_range=(0., 1.), layer_name='forget_gate')
        self.cell_gate = Gate(n_hid, n_hid, W_cell=False, layer_name='cell_gate')
        self.out_gate = Gate(n_hid, n_hid, W_cell=True, layer_name='out_gate')
        self.c0 = theano.shared(np.zeros((n_hid, ), dtype=theano.config.floatX), 'first_cell_state')
        self.h0 = utils.function['tanh'](self.c0)
        self.trainable += self.in_gate.trainable + self.forget_gate.trainable + self.cell_gate.trainable + self.out_gate.trainable + \
                          [self.c0]
        self.regularizable += self.in_gate.regularizable + self.forget_gate.regularizable + \
                              self.cell_gate.regularizable + self.out_gate.regularizable + [self.c0]
        print('@ %s LSTMCell: shape = (%d, %d)' % (self.layer_name, n_in, n_hid))

    def get_output_onestep(self, x_t, h_tm1, c_tm1, W_i, b_i, W_f, b_f, W_c, b_c, W_o, b_o):
        from theano import dot
        inputs = T.concatenate((x_t, h_tm1), 1)
        W = T.concatenate((W_i, W_f, W_c, W_o), 1)


        def slice_w(x, n):
            s = x[:, n*self.n_hid:(n+1)*self.n_hid]
            if self.n_hid == 1:
                s = T.addbroadcast(s, 1)  # Theano cannot infer this by itself
            return s

        xt_dot_W = dot(x_t, W_x)
        htm1_dot_W = dot(h_tm1, W_htm1)
        ctm1_dot_W = dot(c_tm1, W_ctm1)
        i_t = utils.function['sigmoid'](_slice(xt_dot_W, 0, self.n_hid) + dot(h_tm1, W_hi) + dot(c_tm1, W_ci) + b_i)
        f_t = utils.function['sigmoid'](dot(x_t, W_xf) + dot(h_tm1, W_hf) + dot(c_tm1, W_cf) + b_f)
        c_t = f_t * c_tm1 + i_t * utils.function['tanh'](dot(x_t, W_xc) + dot(h_tm1, W_hc) + b_c)
        o_t = utils.function['sigmoid'](dot(x_t, W_xo) + dot(h_tm1, W_ho) + dot(c_t, W_co) + b_o)
        h_t = o_t * utils.function['tanh'](c_t)
        return h_t, c_t

    def get_output(self, input):
        non_sequences = list(self.trainable)
        non_sequences.pop()
        [h_vals, _], _ = theano.scan(LSTMcell.get_output_onestep, sequences=dict(input=input, taps=[0]),
                                     outputs_info=[self.h0, self.c0], non_sequences=non_sequences)
        return h_vals

    def output_shape(self):
        return None, self.n_in


def reset_training():
    FullyConnectedLayer.reset()
    ConvolutionalLayer.reset()
    TransposedConvolutionalLayer.reset()
    BatchNormLayer.reset()
    BatchRenormLayer.reset()
    LayerNormLayer.reset()


def set_training_status(training):
    DropoutLayer.set_training(training)
    BatchNormLayer.set_training(training)
    BatchRenormLayer.set_training(training)
