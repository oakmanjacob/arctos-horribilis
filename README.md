# Data Analysis for Arctos
Jacob Oakman
Tokay Alberts

## Overview
This project is meant to provide data visualizations and analysis for museum data retrieved from Arctos DB (https://arctos.database.museum/) using Python Jupyter Notebooks.

## Notebooks
### Species Report - `species_report.ipynb`
Species level overview showing collecting history, locality information and attributes for an individual species or subspecies.

### Museum Report - `museum_report.ipynb`
Museum level overview displaying broad information regarding a specific collection.

### Ranges Report - `ranges_report.ipynb`
Dashboard for visualizing progress on the ranges digitization project.


### Data
Currently data is stored in the /data directory. This data was retrieved from arctos using the SQL queries in the /queries directory.

## Setup
Install python 3 (https://www.python.org/downloads/)

From this directory, install all required pip packages.
```shell
pip install -r requirements.txt
```

## Usage
### Jupyter Notebook
Start the Jupyter Kernel
```shell
jupyter lab
```

This should open a browser window to `localhost:8888/lab` showing this directory in jupyter. From here, navigate to the notebooks directory and open the .ipynb file you wish to access.

## References
- Jupyter Notebook documentation (https://docs.jupyter.org/en/latest/)
- Jupyter Notebook widgets (https://ipywidgets.readthedocs.io/en/8.1.5/_static/notebooks/index.html?path=Widget+List.ipynb)


## Future Work
- [ ] Deployment as an interactive website using Mercury (https://runmercury.com/)  
- [ ] Arctos API Integration so we can pull and cache information dynamically