We release our model and weights. 

## Architecture

## Loading pre-trained model

You can download model's weights [here](https://mega.nz/#!j7BRGJaI!vCLq9VBSR-Gyj_c7On5KCaMTe7AkwlfZx3DBG9EMl6M).
Once downloaded, you can load the model as

```python
from architecture import pressureRegressionModel

model = pressureRegressionModel()
model.load_weights('weights-improvement-09-8.02.hdf5')
```

## Results
