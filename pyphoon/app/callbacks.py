from keras.callbacks import TensorBoard
from keras.callbacks import ModelCheckpoint
from keras.callbacks import Callback
import matplotlib.pyplot as plt
from os.path import join
import os
import numpy as np


def _create_folder(folderpath):
    """
    Creates a folder if it does not exist.
    """
    if not os.path.exists(folderpath):
        # Create folder
        os.makedirs(folderpath)


class OurTensorBoard(TensorBoard):
    """ Keras modified callback of Tensorboard.

    :param folderpath: Folder to store the tensorboard log files.
    :type folderpath: str
    :param histogram_freq:
    :type histogram_freq: int
    :param write_graph:
    :type write_graph: bool
    :param write_images:
    :type write_images: bool
    """
    def __init__(self, folderpath, histogram_freq=0, write_graph=True,
                 write_images=True):
        log_dir = join(folderpath, 'tensorboard_log')
        _create_folder(log_dir)
        super().__init__(log_dir=log_dir, histogram_freq=histogram_freq,
                         write_graph=write_graph, write_images=write_images
                         )


class LossHistory(Callback):
    """
    Accumulates the losses and accuracies on training and validation sets.
    """
    def on_train_begin(self, logs={}):
        self.losses = []
        self.val_losses = []
        self.accuracies = []
        self.val_accuracies = []

    def on_batch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))
        self.val_losses.append(logs.get('val_loss'))
        self.accuracies.append(logs.get('acc'))
        self.val_accuracies.append(logs.get('val_acc'))


class StoreModelWeights(ModelCheckpoint):
    """ Keras callback used to store the model weights after each epoch. More
    details in `keras documentation`_.

    ..  _keras documentation:
        keras.io/callbacks


    :param folderpath: Folder to store the weights HDF5 files.
    :type folderpath: str
    :param monitor: Model metric to rely on when storing the weights.
    :type monitor: str, default 'val_loss'
    :param verbose: Set to 1 to display execution information
    :type verbose: int
    :param save_best_only: Set to True to only store weights when model
        performance (according to metric **monitor**) improves.
    :param save_weights_only: Set to True to only store the weights.
    :type save_weights_only: bool, default False
    :param mode:
    :type mode: str, default 'auto'
    :param period:
    :type period: int, default 1
    :param naming: Parameter to use in the naming of the weights HDF5 file.
    :type naming: str
    """
    def __init__(self, folderpath, monitor='val_loss', verbose=0,
                 save_best_only=False, save_weights_only=True, mode='auto',
                 period=1, naming="val_mean_error"):
        """ Constructor
        """
        # Create folder for storing weights
        weights_dir = join(folderpath, 'weights')
        _create_folder(weights_dir)
        # Define name for weights HDF5 files
        filepath = join(weights_dir, "weights-improvement-{epoch:02d}-{"
                                     ""+naming+":.4f}.hdf5")
        super().__init__(filepath, monitor=monitor, verbose=verbose,
                         save_best_only=save_best_only,
                         save_weights_only=save_weights_only, mode=mode,
                         period=period)


class PlotRegressionValidation(Callback):
    """
    Plot a scatterplot illustrating the ground truth values and the network
    predictions after each epoch. This callback should only be used in
    regression models, where output and target are real values.

    :param X: Batch of samples. Shape (N, W, H, C), where N: #samples,
        W: width, H: height and C: #channels.
    :type X: numpy.array
    :param Y: Target values.
    :type Y: numpy.array
    :param folderpath: Folder to store the plots
    :type folderpath: str
    :param crop: Define the cropping shape (number of pixels width and
        height). It crops the input image according to this shape. The crop
        is placed in the centre of the image.
    :type crop: int
    """
    def __init__(self, X, Y, folderpath, crop=None):
        """ Constructor
        """
        self.X = X
        self.Y = Y
        self.crop = crop
        self.regression_plot_dir = join(folderpath, 'regression_plots')
        # Create folder for storing regression plots
        _create_folder(self.regression_plot_dir)

    def plot_regression(self, y_true, y_pred, show=False, save=False,
                        filename='none'):
        """ Plot scatterplot with network estimation and ground truth values.

        :param y_true: Ground truth values.
        :type y_true: numpy.array
        :param y_pred: Network estimation values.
        :type y_pred: numpy.array
        :param show: Set to True to plot a figure.
        :type show: bool
        :param save: Set to True to store the image.
        :type save: bool
        :param filename: Name of the file if image is stored.
        :type filename: str
        """
        plt.figure(figsize=(12, 6))
        plt.scatter(y_true, y_pred)
        plt.plot(y_true, y_true, 'k--')

        plt.title("Pressure regression", fontsize=20)
        plt.xlabel("Ground truth (hPa)")
        plt.ylabel("Estimation (hPa)")
        plt.legend(["ground truth", "estimation"])
        if show:
            plt.show()
        if save:
            plt.savefig(filename)

    def on_epoch_end(self, epoch, logs={}):
        """ Executed after each epoch.

        :param epoch: Current epoch.
        :param logs:
        """
        y_pred = []

        if type(self.X) is list:
            for idx in range(len(self.X)):
                _X = self.X[idx]
                if self.crop:
                    base = int(self.crop/2)
                    _X = _X[:, base:+base+self.crop, base:base+self.crop]
                y_pred.append(self.model.predict(_X))
            y_pred = np.concatenate(y_pred)[:, 0]
        elif type(self.X) is np.ndarray:
            y_pred = self.model.predict(self.X)[:, 0]

        if type(self.Y) is list:
            y_true = np.concatenate(self.Y)
        elif type(self.Y) is np.ndarray:
            y_true = self.Y
        # Plot &, eventually, store figure
        filename = 'regression-' + str(epoch)
        self.plot_regression(y_true, y_pred, save=True,
                             filename=join(self.regression_plot_dir, filename))