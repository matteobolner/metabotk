
Metabolomics Toolkit
====================

**Metabolomics Toolkit** is a Python package for working with metabolomics data.

It provides a set of utilities to process and analyze metabolomics data.
The tool includes methods for:

- Importing data from various file formats (currently only Excel and TSV are supported)
- Cleaning the data, including imputing missing values and removing outliers
- Generating sample and metabolite statistics, such as the median and mean of each metabolite across all samples
- Performing Principal Component Analysis (PCA) with different numbers of components, which can help to identify the most important features in the data

This tool allows users to perform various actions on metabolomics data, such as generating sample and metabolite statistics, and performing PCA with different numbers of components.

The tool can import data from an Excel file or separate tables. If the data is from an Excel file, the user must specify the sheet name. If the data is from separate tables, the user must specify the location of the data, sample metadata, and metabolite metadata files.

You can either import the class MetaboTK from metabolomics_toolkit or use the CLI 

The CLI is invoked by running the script cli.py from the command line.

The user can specify the following arguments:

    --input FILE                       Path to the Excel file or directory containing the data
    --sheet-name STRING                Name of the sheet in the Excel file (only used if importing from Excel)
    --data-file FILE                    Path to the file containing the metabolite abundance data
    --metabolites-file FILE            Path to the file containing the metabolite metadata
    --sample-metadata-file FILE        Path to the file containing the sample metadata
    --n-components INTEGER            Number of components to use in PCA (defaults to 3)
    --action {sample_stats,metabolite_stats,pca}
                                          Action to perform (defaults to sample_stats)
    --exclude_xenobiotics
                                          Exclude xenobiotic metabolites from the analysis
    --verbose / --quiet                    Print verbose output (defaults to quiet)

The user must specify the action to perform using the –action argument. The valid actions are:

    sample_stats: Print sample statistics for the entire dataset

    metabolite_stats: Print statistics for each metabolite across all samples

    pca: Perform PCA analysis with the number of components specified by the –n_components argument. The PCA is performed on the scaled data (mean centered and variance normalized). The resulting components are written to a separate CSV file.

Current documentation
--------------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   metabolomics_toolkit
   cli

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
