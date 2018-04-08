This task consists in estimating a phenomenon illustrated on an image is a 
*Tropical cyclone* or an *Extratropical cyclone*. 

## Architecture

![](../../assets/tcxtc_net)

## Results

Our model achieved nearly **94.4% accuracy** on the validation set.

## Using the model

### Download weights
You can download model's weights [here](https://mega.nz/#!rioSgAQD!7bzyh3tOfsi8y2th9lUwQa3BAC0Ap2Na4xeZ6NlDXYo).

### Prediction
Assuming you have stored the downloaded weights as `weights.h5` and that you 
have the image stored as `image_datafile.npy` simply execute:

```
python predict <weights.h5> <image_datafile.npy>
```

#### Remarks on the image
1. `<image_datafile.npy>` can be an image (shapes: (256, 256), (1, 256, 
256) and (256, 256, 1)) or a batch of images (shapes: (N, 256, 256) or (N, 
256, 256, 1))).

2. `<image_datafile.npy>` must have an aspect ratio of roughly 1 pixel/X KM.

### Further usages
You can use this model directly in your code.

#### Load model

```python
from predict import get_model
model = get_model()
model.load_weights('path/to/weights.h5')
```

#### Preprocess data

```python
import h5py

# Load preprocessing parameters
with h5py.File('preprocessing_params.h5.h5') as f:
    mean = f.get('image_mean_256').value
    scale_factor = f.get('max_value_256').value - f.get('min_value_256').value

X = ...
X = (X - mean )/scale_factor
```

#### Prediction

```python
Y = model.predict(X)
```