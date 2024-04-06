"""Module for detecting, counting and removing missing values"""

import numpy as np
import pandas as pd


def detect_missing_values(data):
    """
    Get missing values in a collection

    Parameters:
    - data: list, array, or Series containing numerical data

    Returns:
    - Boolean array indicating missing (True) and non-missing data (False)

    """
    is_missing = np.isnan(data)
    return is_missing


def count_missing_values(data_frame, axis=0):
    """
    Count number of missing values in each row or column of dataframe
    depending on the specified axis

    Parameters:
    - data_frame: pandas DataFrame containing only numeric values
    - axis: {0 or ‘index’, apply to each column, 1 or ‘columns’, apply to each row}, default 0

    Returns:
    - pandas Series with the row/column index and the number of missing values
    """
    if not isinstance(data_frame, pd.DataFrame):
        raise TypeError("Data must be a pandas DataFrame")
    missing_values = data_frame.apply(detect_missing_values, axis=axis)
    n_missing_values = missing_values.sum(axis=axis)
    return n_missing_values


def drop_columns_with_missing_over_threshold(data_frame, threshold=0.25):
    """
    Remove from the dataset all metabolites with a percentage of missing values
    greater than the threshold
    Parameters:
    - data_frame: pandas DataFrame containing only numeric values
    - threshold: maximum ratio of missingness
    Returns:
    - pandas DataFrame without columns with missingness higher than the threshold

    """
    if not isinstance(data_frame, pd.DataFrame):
        raise TypeError("Data must be a pandas DataFrame")
    missing = count_missing_values(data_frame, axis=0)
    to_drop = missing[missing / len(data_frame) > threshold]
    data_frame = data_frame.drop(columns=to_drop.index)
    return data_frame


def drop_rows_with_missing_over_threshold(data_frame, threshold=0.25):
    """
    Remove from the dataset all metabolites with a percentage of missing values
    greater than the threshold
    Parameters:
    - data_frame: pandas DataFrame containing only numeric values
    - threshold: maximum ratio of missingness
    Returns:
    - pandas DataFrame without columns with missingness higher than the threshold

    """
    if not isinstance(data_frame, pd.DataFrame):
        raise TypeError("Data must be a pandas DataFrame")
    missing = count_missing_values(data_frame, axis=1)
    to_drop = missing[missing / len(data_frame.columns) > threshold]
    data_frame = data_frame.drop(index=to_drop.index)
    return data_frame
