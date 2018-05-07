from keras.layers import Input, Dense, Conv2D, MaxPooling2D, \
    Flatten, Activation, Dropout
from keras.layers.normalization import BatchNormalization
from keras.regularizers import l2
from keras.models import Model


def pressureRegressionModel():
    """ Defines the architecture of the pressure regression model.

    :return: Model instance.
    """
    input_img = Input(shape=(128, 128, 1), name="in")

    # Convolutional layers
    x = ConvBlock(64, '1', input_img)
    x = ConvBlock(128, '2', x)
    x = ConvBlock(128, '3', x)
    x = ConvBlock(256, '4', x)
    x = ConvBlock(256, '5', x)

    # Flatten
    x = Flatten()(x)

    # Dense layers
    x = Dense(1024, use_bias=False, name="fc1")(x)
    x = Activation('relu', name="fc_act1")(x)
    x = BatchNormalization(name="fc_bn1")(x)
    x = Dropout(0.2, name="drop1")(x)

    x = Dense(256, use_bias=False, name="fc2")(x)
    x = Activation('relu', name="fc_act2")(x)
    x = BatchNormalization(name="fc_bn2")(x)

    # Out
    x = Dense(1, use_bias=True, name="fc_end")(x)

    # Model
    return Model(input_img, x)


def ConvBlock(kernels, name, x):
    """ Conv block with: conv2d, relu, batch norm and max pooling.

    :param kernels: number of kernels to be used.
    :type kernels: int
    :param name: name for layers. For instance, conv layers will be named
        'conv_<name>', activation layers 'act_<name>' etc.
    :type name: str
    :param x: input sample to the block.
    :type x: numpy.array
    :return: output of the block
    :rtype: numpy.array
    """
    x = Conv2D(kernels, (3, 3), strides=(1, 1), padding='same',
               name='conv_'+name, kernel_regularizer=l2(0.01),
               use_bias=False)(x)
    x = Activation('relu', name='act_'+name)(x)
    x = BatchNormalization(name="bn_"+name)(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), padding='same',
                     name='pool_'+name)(x)
    return x