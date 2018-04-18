import sys
sys.path.insert(0, '../..')

import pandas as pd
import time
from keras.optimizers import adam
from keras.callbacks import ModelCheckpoint, TensorBoard, ReduceLROnPlateau
from keras import backend as K
from os.path import exists

from pyphoon.app.preprocess import DefaultImagePreprocessor
from pyphoon.interpolation.model import get_model2
from pyphoon.interpolation.triplets_generator import generator_from_df

LEARNING_RATE = 0.0001
BATCH_SIZE = 16
NUM_EPOCHS = 1000
NUM_CHANNELS = 1
NWORKERS = 1

train_dir = '/root/fs9/grishin/datasets/triplets/train/'
test_dir = '/root/fs9/grishin/datasets/triplets/test/'
tensorboard_path = '/root/fs9/grishin/datasets/triplets/tensorboard/'
train_dataset = '/root/fs9/grishin/database/triplets_training_set.csv'
model_path = '/root/fs9/grishin/datasets/triplets/model/weights_model2.hdf5'


def charbonnier(y_true, y_pred):
    return K.sqrt(K.square(y_true - y_pred) + 0.001**2)

# def charbonnier(y_true, y_pred):
#     return K.square(y_true - y_pred)

def main():
    img_width, img_height = 128, 128
    target_size = (img_width, img_height)

    model = get_model2(input_shape=(img_width, img_height, 2))
    if exists(model_path):
        model.load_weights(model_path)
        print('weights file loaded.')

    optimizer = adam(lr=LEARNING_RATE, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
    loss = charbonnier
    model.compile(loss=loss, optimizer=optimizer)
    preprocessor = DefaultImagePreprocessor(mean=269.15, std=150,
                                            resize_factor=1, reshape_mode='keras')
    callbacks = [
        ModelCheckpoint(filepath=model_path, monitor='loss',
                        save_best_only=True, verbose=1),
        ReduceLROnPlateau(monitor="loss", factor=0.5, patience=20, verbose=1),
        TensorBoard(log_dir=tensorboard_path, histogram_freq=0,
                    write_graph=True, write_images=True)
    ]
    t_start = time.time()

    training_data_df = pd.read_csv(train_dataset)
    df_train = training_data_df.loc[training_data_df['test'] == False]
    df_valid = training_data_df.loc[training_data_df['test'] == True]


    # print("\nTest basic generator.\n")
    # for df in (df_train, df_valid):
    #     i = 0
    #     for X, Y in generator_from_df(df, BATCH_SIZE, target_size):
    #         print(X[:3, :3, 0])
    #         print(Y[:3])
    #         i += 1
    #         if i > 1:
    #             break

    train_data = {}
    val_data = {}
    train_generator = generator_from_df(df_train, BATCH_SIZE, target_size, train_data)
    # train_generator = threadsafe_generator(train_generator)
    validation_generator = generator_from_df(df_valid, BATCH_SIZE, target_size, val_data)
    # validation_generator = threadsafe_generator(validation_generator)

    nbatches_train, mod = divmod(df_train.shape[0], BATCH_SIZE)
    nbatches_valid, mod = divmod(df_valid.shape[0], BATCH_SIZE)

    model.fit_generator(
        generator=train_generator,
        steps_per_epoch=nbatches_train,
        epochs=NUM_EPOCHS,
        validation_data=validation_generator,
        validation_steps=nbatches_valid,
        workers=NWORKERS,
        callbacks=callbacks)

    # model.fit(x=X, y=Y, validation_split=0.1, batch_size=BATCH_SIZE,
    #           callbacks=callbacks, validation_data=(test_X, test_Y))

    # while(True):
    #     for f in os.listdir(train_dir):
    #         # if f in ['0_chunk.h5', '1_chunk.h5', '2_chunk.h5', '3_chunk.h5', '4_chunk.h5']:
    #         #     continue
    #         t0 = time.time()
    #         print('Reading train batch file {}'.format(f))
    #         X, Y = read_chunk(join(train_dir, f), preprocessor)
    #         t1 = time.time()
    #         print('Done in {} seconds'.format(t1 - t0))
    #         rnd_test_file = random.sample(os.listdir(test_dir), 1)[0]
    #         print('Reading test batch file {}'.format(rnd_test_file))
    #         test_X, test_Y = read_chunk(join(test_dir, rnd_test_file), preprocessor)
    #         t2 = time.time()
    #         print('Done in {} seconds'.format(t2 - t1))
    #
    #         print('Start training...')
    #         model.fit(x=X, y=Y, validation_split=0.1, batch_size=BATCH_SIZE,
    #                   callbacks=callbacks, validation_data=(test_X, test_Y))
    #         t3 = time.time()
    #         print('Epoch trained in {} seconds, total time: {}'.format(t3-t2, t3-t_start))

if __name__ == '__main__':
    main()
