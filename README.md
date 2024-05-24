# MetabolomicsToolKit
MetabolomicsToolKit (metabotk) is a Python library for working with metabolomics data. It provides a variety of tools and methods for importing, exploring, manipulating and analyzing metabolomics data.

The library is designed to be easy to use and provides a simple interface for working with metabolomics data. It is also highly extensible and allows users to easily add new methods and tools.


### Features

* Import and export metabolomics data from various sources (e.g. Metabolon) and formats (e.g. excel files, tables)
* Explore and manipulate metabolomics data
* Impute missing values
* Normalize data
* Perform feature selection and dimensionality reduction
* Plot data (e.g. metabolite abundance, PCA)


## How to install ##

Install with `pip`:

```shell
pip install metabotk
```

## Dependencies ##

* pandas
* numpy
* math
* scikit-learn
* seaborn
* boruta_py for feature selection using Boruta
* skloess for normalization with LOESS
* pyserrf for normalization with SERRF


## Why metabotk? ##

Metabolomics data requires the following information:

- Peak values / abundance data for each metabolite over each sample
- Sample metadata
- Chemical annotation of the metabolites

Constantly coordinating these three sources of information is time consuming and prone to errors, especially for explorative analyses.  
Additionally, many analyses are repetitive and can benefit from a standardized procedure. For example, building and plotting a PCA or obtaining statistics about the metabolites/samples is something that is often done before and after modifying or removing data; updating the metadata or statistics after every modification can be automatized.  
With metabotk, the three sources are constantly updated based on changes to the dataset; for example, removing a metabolite or sample from the data will also remove it from the chemical annotation or sample metadata.  

metabotk provides a centralized interface for working with metabolomics data from the first to the last analysis step.

The following modules constitute metabotk:

- interface - the main point of access for the end user, with the MetaboTK class; all other modules can be accessed from here
- dataset manager - the main module for manipulating, importing and saving datasets
- providers - functions to read data from different providers into metabotk
- statistics - functions for obtaining statistics at the metabolite or sample level, from mean/std to total sum abundance (TSA) and coefficient of variation (CV), correlations, number of missing or outlier values.
- dimensionality reduction - functions to perform dimensionality reduction such as PCA
- imputation - functions to impute missing data
- normalization - functions to normalize data
- models - functions to build models from the data (i.e linear models) and remove variable effects
- feature selection - functions to perform feature selection and identify metabolites discriminating between groups
- visualization - functions to plot distribution of metabolites, PCA and other kinds of visualization.

All modules can be extended with different kind of analyses and methods; this is a work in progress aiming to provide a baseline which can be tailored based on the needs of the users.



## How to use ##

!!! Documentation is still a work in progress !!!

In-depth documentation about each module can be found here:   
https://metabolomics-toolkit.readthedocs.io/en/latest/



Import the library and initiate the class
```shell
from metabotk import MetaboTK

dataset = MetaboTK(data_provider="metabolon", sample_id_column='Sample', metabolite_id_column="CHEM_ID",)
```
Import the data in tabular or excel format
```shell
#TABLES
dataset.import_tables(data="data.tsv", sample_metadata="samples.tsv", chemical_annotation="config/metabolites.tsv")

#EXCEL -> the sheet names for data, sample metadata and chemical annotation must be specified
dataset.import_excel(file_path="dataset.xlsx", sample_metadata = "sample_metadata", chemical_annotation = "chemical_annotation", data_sheet = "peak_data",

```
Get some statistics about the dataset

```shell
#SAMPLE LEVEL STATS
sample_stats = dataset.stats.sample_stats()

#METABOLITE LEVEL STATS
metabolite_stats = dataset.stats.metabolite_stats()
```
Get a PCA from the data and plot it

```shell
pca=dataset.dimensionality_reduction.get_pca(n_components=3)

datset.visualization.plot_pca(pca=pca, hue='treatment')

```