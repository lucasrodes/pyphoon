# Content

Here you will find a folder for each of the experiments that we worked on. 

| **Section**                                   | **Description**                                                                                                                                                                                                   |
|-----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [tcxtc](tcxtc)                                | Binary image classification of *Tropical Cyclones* and *Extra-Tropical Cyclones*.                                                                                                                                 |                                                                                                                                                |
| [multiclas](multiclass)                       | Image classification of *Tropical Cyclones* (i.e. *Typhoons*) in categories 2-5, according to labeling in [JMA website](http://www.jma.go.jp/jma/jma-eng/jma-center/rsmc-hp-pub-eg/Besttracks/e_format_bst.html). |
| [pressure_regression](pressure_regression)    | Regression from *Tropical Cyclones* images -> centre pressure values.                                                                      |


## Folders content
In each of the folders, you will find the following content:

- **notebooks**: Folder containing some code snippets of the implemented 
experiment.
- **predict.py**: Script used to perform predictions on new data.
- **weights.hdf5**: Weights of the pre-trained model.
- **preprocessing_x.h5**: Parameters to preprocess the data (more details in 
folder).

## Usage

We provide the weights of the model (`weights.hdf5`) and a script to do new 
predictions ([`predict.py`](predict.py)). Simply run

```
$ python predict.py weights.hdf5 <image_datafile.npy>
```

where `image_datafile.npy` is an image (or images) stored as a numpy array. 
Accepted shapes are (256, 256) for a single image and (N, 256, 256) for a 
batch of N images. In addition, you can use option `-p` to display 
probabilities instead of labels. Find more details using `--help`.

## Remarks

Input image format for each of the experiments (i.e. models) may vary. Please 
review section **Image format** in the README file of the experiment you are 
interested in for more details.



