# Configurable PySpark Pipeline
_A configurable PySpark pipeline library._

## Getting Started
* Requirements: 
    * Python 3.5
* install the package using pip:

``` bash
$ pip install sparkml-pipe
```

## Project Organization
```
├── README.md          <- The top-level README for developers using this project.
├── data               <- Data for testing the library.
│
├── docs               <- A default Sphinx project; see sphinx-doc.org for details
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── sparkmlpip         <- Source code for use in this project.
│   ├── conf           <- YAML config files for pyspark pipeline.
│   │
│   ├── pipeline       <- pyspark model pipelines.
│   │
│   ├── stat           <- pyspark stat pipelines.
│   │
│   ├── test           <- test code.
│   │
│   └── utils          <- util functions.
│
└── setup.py           <- Metadata about your project for easy distribution.
```



## Contributing
### checkout the codebase
``` bash
$ git checkout develop
```
### Update the PyPI version
* Update sparkmlpipe/\_\_version\_\_.py if needed
* Upload to PyPI
``` bash
$ python setup.py sdist
$ pip install twine
// upload to Test PyPI
$ twine upload --repository-url https://test.pypi.org/legacy/ dist/*
// upload to PyPI
$ twine upload dist/*
```
### Installing development requirements
``` bash
$ pip install -r requirements.txt
```