"""Module for detecting, counting and removing missing values"""

import numpy as np
import pandas as pd
from src.utils import validate_dataframe


MISSING_THRESHOLD=0.25

def validate_threshold(threshold):
    if not isinstance(threshold, (int, float)):
        raise TypeError("Threshold must be a numeric value")
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1")

def detect_missing(data):
    """
    Get missing values in a collection

    Parameters:
    - data: list, array, or Series containing numerical data

    Returns:
    - Boolean array indicating missing (True) and non-missing data (False)

    """
    is_missing = np.isnan(data)
    return is_missing


def count_missing(data_frame, axis=0):
    """
    Count number of missing values in each row or column of dataframe
    depending on the specified axis

    Parameters:
    - data_frame: pandas DataFrame containing only numeric values
    - axis: {0 or ‘index’, apply to each column, 1 or ‘columns’, apply to each row}, default 0

    Returns:
    - pandas Series with the row/column index and the number of missing values
    """
    validate_dataframe(data_frame)
    missing_values = data_frame.apply(detect_missing, axis=axis)
    n_missing_values = missing_values.sum(axis=axis)
    return n_missing_values


def drop_columns_with_missing(data_frame, threshold=MISSING_THRESHOLD):
    """
    Remove from the dataset all metabolites with a percentage of missing values
    greater than the threshold
    Parameters:
    - data_frame: pandas DataFrame containing only numeric values
    - threshold: maximum ratio of missingness
    Returns:
    - pandas DataFrame without columns with missingness higher than the threshold

    """
    validate_threshold(threshold)
    validate_dataframe(data_frame)
    missing = count_missing(data_frame, axis=0)
    to_drop = missing[missing / len(data_frame) > threshold]
    data_frame = data_frame.drop(columns=to_drop.index)
    return data_frame


def drop_rows_with_missing(data_frame, threshold=MISSING_THRESHOLD):
    """
    Remove from the dataset all metabolites with a percentage of missing values
    greater than the threshold
    Parameters:
    - data_frame: pandas DataFrame containing only numeric values
    - threshold: maximum ratio of missingness
    Returns:
    - pandas DataFrame without columns with missingness higher than the threshold

    """
    validate_threshold(threshold)
    validate_dataframe(data_frame)
    missing = count_missing(data_frame, axis=1)
    to_drop = missing[missing / len(data_frame.columns) > threshold]
    data_frame = data_frame.drop(index=to_drop.index)
    return data_frame
