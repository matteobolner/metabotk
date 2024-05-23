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