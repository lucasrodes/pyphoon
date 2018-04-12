This task consists in estimating a phenomenon illustrated on an image is a 
*Tropical cyclone* or an *Extratropical cyclone*.

Tropical Cyclone    |  Extra-Tropical Cyclone
:------------------:|:-------------------------:
![](../../assets/TC.gif)  |  ![](../../assets/xTC.gif)

## Architecture

![](../../assets/tcxtc_net.png)

## Results
Our model achieved nearly **96.27% accuracy** on the validation set and **94
.9% accuracy** on the test set. For more details refer to the examples in 
[notebooks](notebooks). 

## Using the model

We provide the weights of the model (`weights.hdf5`) and a script to do new 
predictions ([`predict.py`](predict.py)). Simply run

```
python predict weights.hdf5 <image_datafile.npy>
```

where `image_datafile.npy` is an image (or images) stored as a numpy array. 
Accepted shapes are (256, 256) for a single image and (N, 256, 256) for a 
batch of N images. In addition, you can use option `-p` to display 
probabilities instead of labels. Find more details using `--help`.

### On input images

Images should be in range of [0, 255], where 0 and 255 correspond to 160 Kelvin 
and 255 Kelvin, correspondingly.

### Use in code
Alternatively, you can use this model in your code.

#### Load model

```python
from predict import get_model
model = get_model()
model.load_weights('weights.hdf5')
```

#### Preprocess data

```python
import h5py

# Load preprocessing parameters
with h5py.File('preprocessing_year.h5.h5') as f:
    mean = f.get('image_mean').value
    scale_factor = f.get('max_value').value - f.get('min_value').value

X = ...  # Load (256, 256) image or (N, 256, 256) array of images
X = (X - mean )/scale_factor
```

#### Prediction

```python
Y = model.predict(X)
```