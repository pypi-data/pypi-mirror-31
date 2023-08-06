# nr-common
[![Build Status](https://travis-ci.org/nitred/nr-common.svg?branch=master)](https://travis-ci.org/nitred/nr-common)

Common python functionalities aimed to be at least compatible with Python3.


#### Current Stable Version
```
0.1.6
```

#### Dependency Installation
This package is expected to contain common utility function covering a wide range of topics such as file system, web development, data science etc. This package is expected to be used with virtually any sized project. It may be unwise for this package to install all the dependencies in case the user wants to use this package for a small subset of the functionalities. Therefore this package does not install all the dependencies it requires and expects the user to install the dependencies manually wherever necessary.

Some dependencies that are not included but expects the user to install when necessary are:
* Flask
* Flask-SQLAlchemy
* opencv-python
* numpy
* Pillow

All the missing dependencies can be installed using:
```
pip install -r requirements_missing.txt
```


# Installation

### pip
```
pip install nr-common
```


### Development Installation

* Clone the project.
* Install in Anaconda3 environment
```
$ conda env create --force -f dev_environment.yml
$ source activate nr-common
$ pip install -e .
```


# Test
To run the tests:
```
make test
```


# Examples
```
$ python examples/simple.py
```


# License
MIT
