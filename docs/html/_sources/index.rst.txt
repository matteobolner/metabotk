metabotk Documentation
======================

This documentation provides an overview of the **metabotk** library, including its command-line interface (CLI) and core functionalities for working with metabolomics data.

CLI Documentation
-----------------

The metabotk CLI offers various functionalities for data import, analysis, manipulation, and more. For details on CLI usage and available options, refer to the `CLI Documentation <cli-docs>`_.

Class Documentation
-------------------

:class:`metabotk`
~~~~~~~~~~~~~~~~~

.. autoclass:: main.MetaboTK
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

    Class for working with metabolomics data.

    Initialization Parameters
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    - ``data_provider`` (str): Provider of the metabolomics data.
    - ``sample_id_column`` (str): Column name for sample IDs.
    - ``metabolite_id_column`` (str): Column name for metabolite IDs.

    Methods
    ~~~~~~~

    - ``sample_stats(outlier_threshold=5, exclude_xenobiotics=True)``: Computes basic statistics for the metabolomics data sample-wise.
    - ``metabolite_stats(outlier_threshold=5)``: Computes basic statistics for the metabolomics data metabolite-wise.

    Properties
    ~~~~~~~~~~

    - ``models``: Lazy initialization of ModelsHandler instance.
    - ``dimensionality_reduction``: Lazy initialization of DimensionalityReduction instance.
    - ``visualization``: Lazy initialization of Visualization instance.
    - ``feature_selection``: Lazy initialization of FeatureSelection instance.

    For detailed documentation on each method and property, refer to the function docstrings and the metabotk documentation.

    Statistics Handling
    ~~~~~~~~~~~~~~~~~~~

    metabotk provides functionality for computing statistics both sample-wise and metabolite-wise. These statistics include mean, standard deviation, median, minimum, maximum, sum, coefficient of variation (CV%), number of missing values, and number of outliers.

    .. note::
        Xenobiotic metabolites are usually excluded from sample-level statistics by default.

    For more details on the statistical methods and options, refer to the corresponding function docstrings and the metabotk documentation.

For more detailed documentation on specific methods and functionalities, please refer to the individual function docstrings and the metabotk documentation.

.. _cli-docs: metabotk Command Line Interface Documentation

metabotk Command Line Interface Documentation
=============================================

This documentation provides an overview of the metabotk Command Line Interface (CLI), offering various functionalities for metabolomics data analysis.

Installation
------------

Before using the metabotk CLI, ensure that metabotk is installed. You can install it via pip:

.. code-block:: bash

    pip install metabotk

Usage
-----

To use the metabotk CLI, execute the following command:

.. code-block:: bash

    metabotk [OPTIONS]

Options
-------
The metabotk CLI supports the following options:

- `-h, --help`: Display help message and exit.
- `--version`: Show the version number and exit.

Input Options
~~~~~~~~~~~~~

- `-ie, --excel`: Specify an Excel file and sheet from which to extract data.
- `-it, --tables`: Specify three TSV files for data, samples, and metabolites.
- `-sid, --sample_id`: Specify the column name for sample IDs.
- `-mid, --metabolite_id`: Specify the column name for metabolite IDs.

Output Options
~~~~~~~~~~~~~

- `-oe, --output-excel`: Save the dataset to an Excel file.
- `-ot, --output-tables`: Save the dataset to three TSV files.
- `-od, --output-data`: Save only the data to a TSV file.

Dataset Manipulation Options
~~~~~~~~~~~~~

- `-ss, --split-samples`: Split the dataset based on sample metadata.
- `-sm, --split-metabolites`: Split the dataset based on metabolite metadata.

Analysis Options
~~~~~~~~~~~~~

- `--exclude-xenobiotics`: Exclude xenobiotic metabolites from analysis.
- `--outlier-threshold`: Set a threshold for outlier detection.
- `--sample-stats`: Print sample statistics for the dataset.
- `--metabolite-stats`: Print metabolite statistics for the dataset.
- `--remove-outliers`: Remove outlier values from the dataset.
- `--fit-model`: Fit a linear model to each metabolite.
- `--PCA`: Perform Principal Component Analysis (PCA) on the dataset.

Feature Selection Options
~~~~~~~~~~~~~

- `--fs-method`: Specify the feature selection method.
- `-y, --y_column`: Column containing target values.
- `-t, --threads`: Number of threads to use.
- `-a, --alpha`: Alpha (p-value threshold) for feature selection.
- `-r, --random-state`: Random state seed for feature selection.

Feature Selection - Boruta Options
~~~~~~~~~~~~~
- `-d, --max-depth`: Max depth of the tree for Boruta feature selection.
- `-w, --class-weight`: Class weights for Boruta feature selection.
- `-n, --n-estimators`: Number of estimators for Boruta feature selection.
- `-i, --max-iterations`: Max iterations for Boruta feature selection.
- `-o, --output-dir`: Output directory for Boruta feature selection.

Examples
--------

1. Import data from an Excel file:

.. code-block:: bash

    metabotk --excel data.xlsx data_sheet

2. Perform sample-wise statistics analysis:

.. code-block:: bash

    metabotk --excel data.xlsx data_sheet --sample-stats

Current documentation
-------------------

.. toctree::
   :maxdepth: 3
   :caption: Contents:
   
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



