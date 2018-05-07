import math
import numpy
import os
import torch
import torch.utils.serialization
from pyphoon.io.h5 import read_source_image

arguments_strModel = 'F'

class Network(torch.nn.Module):
    def __init__(self):
        super(Network, self).__init__()

        class Preprocess(torch.nn.Module):
            def __init__(self):
                super(Preprocess, self).__init__()

            # end

            def forward(self, variableInput):
                variableBlue = variableInput[:, 0:1, :, :] - 0.406
                variableGreen = variableInput[:, 1:2, :, :] - 0.456
                variableRed = variableInput[:, 2:3, :, :] - 0.485

                variableBlue = variableBlue / 0.225
                variableGreen = variableGreen / 0.224
                variableRed = variableRed / 0.229

                return torch.cat([variableRed, variableGreen, variableBlue], 1)

        # end
        # end

        class Basic(torch.nn.Module):
            def __init__(self, intLevel):
                super(Basic, self).__init__()

                self.moduleBasic = torch.nn.Sequential(
                    torch.nn.Conv2d(in_channels=8, out_channels=32, kernel_size=7, stride=1, padding=3),
                    torch.nn.ReLU(inplace=False),
                    torch.nn.Conv2d(in_channels=32, out_channels=64, kernel_size=7, stride=1, padding=3),
                    torch.nn.ReLU(inplace=False),
                    torch.nn.Conv2d(in_channels=64, out_channels=32, kernel_size=7, stride=1, padding=3),
                    torch.nn.ReLU(inplace=False),
                    torch.nn.Conv2d(in_channels=32, out_channels=16, kernel_size=7, stride=1, padding=3),
                    torch.nn.ReLU(inplace=False),
                    torch.nn.Conv2d(in_channels=16, out_channels=2, kernel_size=7, stride=1, padding=3)
                )

                if intLevel == 5:
                    if arguments_strModel == '3' or arguments_strModel == '4':
                        intLevel = 4  # the models trained on the flying chairs dataset do not come with weights for the sixth layer
                # end
                # end
                base_dir = os.path.dirname(__file__)
                for intConv in range(5):
                    self.moduleBasic[intConv * 2].weight.data.copy_(torch.utils.serialization.load_lua(
                        os.path.join(base_dir, 'models/modelL' + str(intLevel + 1) + '_' + arguments_strModel + '-' + str(
                            intConv + 1) + '-weight.t7')))
                    self.moduleBasic[intConv * 2].bias.data.copy_(torch.utils.serialization.load_lua(
                        os.path.join(base_dir, 'models/modelL' + str(intLevel + 1) + '_' + arguments_strModel + '-' + str(
                            intConv + 1) + '-bias.t7')))

            # end
            # end

            def forward(self, variableInput):
                return self.moduleBasic(variableInput)

        # end
        # end

        class Backward(torch.nn.Module):
            def __init__(self):
                super(Backward, self).__init__()

            # end

            def forward(self, variableInput, variableFlow):
                if hasattr(self, 'tensorGrid') == False or self.tensorGrid.size(0) != variableInput.size(
                        0) or self.tensorGrid.size(2) != variableInput.size(2) or self.tensorGrid.size(
                        3) != variableInput.size(3):
                    torchHorizontal = torch.linspace(-1.0, 1.0, variableInput.size(3)).view(1, 1, 1, variableInput.size(
                        3)).expand(variableInput.size(0), 1, variableInput.size(2), variableInput.size(3))
                    torchVertical = torch.linspace(-1.0, 1.0, variableInput.size(2)).view(1, 1, variableInput.size(2),
                                                                                          1).expand(
                        variableInput.size(0), 1, variableInput.size(2), variableInput.size(3))

                    self.tensorGrid = torch.cat([torchHorizontal, torchVertical], 1).cuda()
                # end

                variableGrid = torch.autograd.Variable(data=self.tensorGrid, volatile=not self.training)

                variableFlow = torch.cat([variableFlow[:, 0:1, :, :] / ((variableInput.size(3) - 1.0) / 2.0),
                                          variableFlow[:, 1:2, :, :] / ((variableInput.size(2) - 1.0) / 2.0)], 1)

                return torch.nn.functional.grid_sample(input=variableInput,
                                                       grid=(variableGrid + variableFlow).permute(0, 2, 3, 1),
                                                       mode='bilinear', padding_mode='border')

        # end
        # end

        self.modulePreprocess = Preprocess()

        self.moduleBasic = torch.nn.ModuleList([Basic(intLevel) for intLevel in range(6)])

        self.moduleBackward = Backward()

    # end

    def forward(self, variableFirst, variableSecond):
        variableFlow = []

        variableFirst = [self.modulePreprocess(variableFirst)]
        variableSecond = [self.modulePreprocess(variableSecond)]

        for intLevel in range(5):
            if variableFirst[0].size(2) > 32 or variableFirst[0].size(3) > 32:
                variableFirst.insert(0, torch.nn.functional.avg_pool2d(input=variableFirst[0], kernel_size=2, stride=2))
                variableSecond.insert(0,
                                      torch.nn.functional.avg_pool2d(input=variableSecond[0], kernel_size=2, stride=2))
        # end
        # end

        variableFlow = torch.autograd.Variable(
            data=torch.zeros(variableFirst[0].size(0), 2, int(math.floor(variableFirst[0].size(2) / 2.0)),
                             int(math.floor(variableFirst[0].size(3) / 2.0))).cuda(), volatile=not self.training)

        for intLevel in range(len(variableFirst)):
            variableUpsampled = torch.nn.functional.upsample(input=variableFlow, scale_factor=2, mode='bilinear') * 2.0

            if variableUpsampled.size(2) != variableFirst[intLevel].size(
                2): variableUpsampled = torch.nn.functional.pad(input=variableUpsampled, pad=[0, 0, 0, 1],
                                                                mode='replicate')
            if variableUpsampled.size(3) != variableFirst[intLevel].size(
                3): variableUpsampled = torch.nn.functional.pad(input=variableUpsampled, pad=[0, 1, 0, 0],
                                                                mode='replicate')

            variableFlow = self.moduleBasic[intLevel](torch.cat(
                [variableFirst[intLevel], self.moduleBackward(variableSecond[intLevel], variableUpsampled),
                 variableUpsampled], 1)) + variableUpsampled
        # end

        return variableFlow


# end
# end

moduleNetwork = Network().cuda()


##########################################################

def estimate(tensorInputFirst, tensorInputSecond):
    tensorOutput = torch.FloatTensor()

    # assert (tensorInputFirst.size(1) == tensorInputSecond.size(1))
    # assert (tensorInputFirst.size(2) == tensorInputSecond.size(2))

    intWidth = tensorInputFirst.size(2)
    intHeight = tensorInputFirst.size(1)

    if True:
        tensorInputFirst = tensorInputFirst.cuda()
        tensorInputSecond = tensorInputSecond.cuda()
        tensorOutput = tensorOutput.cuda()
    # end

    if True:
        variableInputFirst = torch.autograd.Variable(data=tensorInputFirst.view(1, 3, intHeight, intWidth),
                                                     volatile=True)
        variableInputSecond = torch.autograd.Variable(data=tensorInputSecond.view(1, 3, intHeight, intWidth),
                                                      volatile=True)

        tensorOutput.resize_(2, intHeight, intWidth).copy_(
            moduleNetwork(variableInputFirst, variableInputSecond).data[0])
    # end

    if True:
        tensorInputFirst = tensorInputFirst.cpu()
        tensorInputSecond = tensorInputSecond.cpu()
        tensorOutput = tensorOutput.cpu()
    # end

    return tensorOutput
# end


def scale_to_tensor_input(filename):
    """
    Converts image to tensor input format.

    :param filename: Input filename.
    :return: torch FloatTensor
    """
    im = read_source_image(filename)
    im3 = numpy.ndarray(shape=(3, *im.shape))
    im3[:, :, :] = im / 255
    return torch.FloatTensor(im3)


def calc_flow(filename1, filename2):
    """
    Calculates optical flow for two consecutive frames.

    :param filename1: First frame.
    :param filename2: Second frame.
    :return: Optical flow.
    """
    tensorInputFirst = scale_to_tensor_input(filename1)
    tensorInputSecond = scale_to_tensor_input(filename2)
    tensorOutput = estimate(tensorInputFirst, tensorInputSecond)
    output_array = numpy.array(tensorOutput.permute(1, 2, 0), numpy.float32)
    return output_array


def get_flow_filename(im1_filename, im2_filename):
    return os.path.basename(os.path.splitext(im1_filename)[0]) + '_' + \
        os.path.basename(os.path.splitext(im2_filename)[0]) + '.h5'

