This task consists in estimating the class of a *Tropical Cyclone*. Classes 
are defined based on intensity level, which is provided by meteorological 
agencies. 


## Architecture

[Architecture image]

## Results
Our model achieved nearly **X% accuracy** on the validation set and **Y% 
accuracy** on the test set. For more details refer to the examples in 
[notebooks](notebooks). 


## Image format

Images must be in range of [0, 255], where 0 and 255 correspond to 160 Kelvin 
and 255 Kelvin, correspondingly.

The model accepts 256x256 images with resolution 1 pixel ≈ 5 Km. Note that 
images are assumed to have the typhoon eye in the image centre (i.e. position
[128, 128]).

![](../../assets/crop_multiclass.png)

## Use in code
Alternatively, you can use this model in your code.

### Load model

```python
from pyphoon.app.models.tc_multiclass import tcNet
model = tcNet('weights.hdf5')
```

### Preprocess data

```python
import h5py

# Load preprocessing parameters
with h5py.File('preprocessing_year.h5.h5') as f:
    mean = f.get('image_mean').value
    scale_factor = f.get('max_value').value - f.get('min_value').value

X = ...  # Load (256, 256) image or (N, 256, 256) array of images
X = (X - mean )/scale_factor
```

### Prediction

```python
Y = model.predict(X)
```