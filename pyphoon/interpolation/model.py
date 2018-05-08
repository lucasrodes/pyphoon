from keras.layers import Layer, Input, Conv2D, MaxPooling2D, UpSampling2D, merge, BatchNormalization, Activation, \
    Dropout
from keras.models import Sequential, Model
from keras.optimizers import Adam


def get_model(input_shape):
    inputs = Input(input_shape)
    conv1 = Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding='same')(inputs)
    bn1 = BatchNormalization()(conv1)
    conv1 = Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding='same')(bn1)
    bn1 = BatchNormalization()(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(bn1)

    conv2 = Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same')(pool1)
    bn2 = BatchNormalization()(conv2)
    conv2 = Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same')(bn2)
    bn2 = BatchNormalization()(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(bn2)

    conv3 = Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same')(pool2)
    bn3 = BatchNormalization()(conv3)
    conv3 = Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same')(bn3)
    bn3 = BatchNormalization()(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(bn3)

    conv4 = Conv2D(filters=256, kernel_size=(3, 3), activation='relu', padding='same')(pool3)
    bn4 = BatchNormalization()(conv4)
    conv4 = Conv2D(filters=256, kernel_size=(3, 3), activation='relu', padding='same')(bn4)
    bn4 = BatchNormalization()(conv4)
    pool4 = MaxPooling2D(pool_size=(2, 2))(bn4)

    conv5 = Conv2D(filters=512, kernel_size=(3, 3), activation='relu', padding='same')(pool4)
    bn5 = BatchNormalization()(conv5)
    conv5 = Conv2D(filters=512, kernel_size=(3, 3), activation='relu', padding='same')(bn5)
    bn5 = BatchNormalization()(conv5)
    pool5 = MaxPooling2D(pool_size=(2, 2))(bn5)

    conv5_2 = Conv2D(filters=512, kernel_size=(3, 3), activation='relu', padding='same')(pool5)
    bn5_2 = BatchNormalization()(conv5_2)
    conv5_2 = Conv2D(filters=512, kernel_size=(3, 3), activation='relu', padding='same')(bn5_2)
    bn5_2 = BatchNormalization()(conv5_2)

    up5_2 = merge([UpSampling2D(size=(2, 2))(bn5_2), bn5], mode='concat', concat_axis=3)
    conv6_2 = Conv2D(filters=512, kernel_size=(3, 3), activation='relu', padding='same')(up5_2)
    bn6_2 = BatchNormalization()(conv6_2)
    conv6_2 = Conv2D(filters=512, kernel_size=(3, 3), activation='relu', padding='same')(bn6_2)
    bn6_2 = BatchNormalization()(conv6_2)

    up6 = merge([UpSampling2D(size=(2, 2))(bn6_2), bn4], mode='concat', concat_axis=3)
    conv6 = Conv2D(filters=256, kernel_size=(3, 3), activation='relu', padding='same')(up6)
    bn6 = BatchNormalization()(conv6)
    conv6 = Conv2D(filters=256, kernel_size=(3, 3), activation='relu', padding='same')(bn6)
    bn6 = BatchNormalization()(conv6)

    up7 = merge([UpSampling2D(size=(2, 2))(bn6), bn3], mode='concat', concat_axis=3)
    conv7 = Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same')(up7)
    bn7 = BatchNormalization()(conv7)
    conv7 = Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same')(bn7)
    bn7 = BatchNormalization()(conv7)

    up8 = merge([UpSampling2D(size=(2, 2))(bn7), bn2], mode='concat', concat_axis=3)
    conv8 = Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same')(up8)
    bn8 = BatchNormalization()(conv8)
    conv8 = Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same')(bn8)
    bn8 = BatchNormalization()(conv8)

    up9 = merge([UpSampling2D(size=(2, 2))(bn8), bn1], mode='concat', concat_axis=3)
    conv9 = Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding='same')(up9)
    bn9 = BatchNormalization()(conv9)
    conv9 = Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding='same')(bn9)
    bn9 = BatchNormalization()(conv9)

    conv10 = Conv2D(filters=int(input_shape[2]/2), kernel_size=(1, 1), activation='sigmoid')(bn9)

    model = Model(input=inputs, output=conv10)

    return model


def get_model2(input_shape):
    inputs = Input(input_shape)

    conv1 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(inputs)
    conv1 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

    conv2 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool1)
    conv2 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

    conv3 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool2)
    conv3 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

    conv4 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool3)
    conv4 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv4)
    drop4 = Dropout(0.5)(conv4)
    pool4 = MaxPooling2D(pool_size=(2, 2))(drop4)

    conv5 = Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool4)
    conv5 = Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv5)
    drop5 = Dropout(0.5)(conv5)

    up6 = Conv2D(512, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(drop5))
    merge6 = merge([drop4, up6], mode='concat', concat_axis=3)
    conv6 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge6)
    conv6 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv6)

    up7 = Conv2D(256, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(conv6))
    merge7 = merge([conv3, up7], mode='concat', concat_axis=3)
    conv7 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge7)
    conv7 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv7)

    up8 = Conv2D(128, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(conv7))
    merge8 = merge([conv2, up8], mode='concat', concat_axis=3)
    conv8 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge8)
    conv8 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv8)

    up9 = Conv2D(64, 2, activation='relu', padding='same', kernel_initializer='he_normal')(UpSampling2D(size=(2, 2))(conv8))
    merge9 = merge([conv1, up9], mode='concat', concat_axis=3)
    conv9 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge9)
    conv9 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
    conv9 = Conv2D(2, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
    conv10 = Conv2D(1, 1, activation='tanh')(conv9)

    # final = merge([inputs, conv10], mode='concat', concat_axis=3)
    # finalconv = Conv2D(kernel_size=input_shape[0], filters=1, activation='tanh')(final)
    model = Model(input=inputs, output=conv10)

    return model


def get_model3(input_shape):
    inputs = Input(input_shape)

    conv1 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(inputs)
    conv1 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

    conv2 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool1)
    conv2 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

    conv3 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool2)
    conv3 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

    conv4 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool3)
    conv4 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv4)
    drop4 = Dropout(0.5)(conv4)
    pool4 = MaxPooling2D(pool_size=(2, 2))(drop4)

    conv5 = Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool4)
    conv5 = Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv5)
    drop5 = Dropout(0.5)(conv5)

    up6 = Conv2D(512, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(drop5))
    merge6 = merge([drop4, up6], mode='concat', concat_axis=3)
    conv6 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge6)
    conv6 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv6)

    up7 = Conv2D(256, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(conv6))
    merge7 = merge([conv3, up7], mode='concat', concat_axis=3)
    conv7 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge7)
    conv7 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv7)

    up8 = Conv2D(128, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(conv7))
    merge8 = merge([conv2, up8], mode='concat', concat_axis=3)
    conv8 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge8)
    conv8 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv8)

    up9 = Conv2D(64, 2, activation='relu', padding='same', kernel_initializer='he_normal')(UpSampling2D(size=(2, 2))(conv8))
    merge9 = merge([conv1, up9], mode='concat', concat_axis=3)
    conv9 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge9)
    conv9 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
    conv9 = Conv2D(2, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
    conv10 = Conv2D(1, 1, activation='tanh')(conv9)

    # final = merge([inputs, conv10], mode='concat', concat_axis=3)
    # finalconv = Conv2D(kernel_size=input_shape[0], filters=1, activation='tanh')(final)
    model = Model(input=inputs, output=conv10)

    return model


def get_unet(input_shape):
    inputs = Input(input_shape)

    conv1 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(inputs)
    conv1 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

    conv2 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool1)
    conv2 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

    conv3 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool2)
    conv3 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

    conv4 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool3)
    conv4 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv4)
    drop4 = Dropout(0.5)(conv4)
    pool4 = MaxPooling2D(pool_size=(2, 2))(drop4)

    conv5 = Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool4)
    conv5 = Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv5)
    drop5 = Dropout(0.5)(conv5)

    up6 = Conv2D(512, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(drop5))
    merge6 = merge([drop4, up6], mode='concat', concat_axis=3)
    conv6 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge6)
    conv6 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv6)

    up7 = Conv2D(256, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(conv6))
    merge7 = merge([conv3, up7], mode='concat', concat_axis=3)
    conv7 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge7)
    conv7 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv7)

    up8 = Conv2D(128, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(conv7))
    merge8 = merge([conv2, up8], mode='concat', concat_axis=3)
    conv8 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge8)
    conv8 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv8)

    up9 = Conv2D(64, 2, activation='relu', padding='same', kernel_initializer='he_normal')(UpSampling2D(size=(2, 2))(conv8))
    merge9 = merge([conv1, up9], mode='concat', concat_axis=3)
    conv9 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge9)
    conv9 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
    conv9 = Conv2D(2, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
    conv10 = Conv2D(1, 1, activation='sigmoid')(conv9)

    model = Model(input=inputs, output=conv10)
    return model

