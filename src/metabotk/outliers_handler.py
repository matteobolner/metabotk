from typing import Literal
import numpy as np
import pandas as pd
from metabotk.utils import validate_dataframe

"""
Module containing functions to detect, count and remove outlier values
"""


def detect_outliers(data, threshold):
    """
    Detect outlier values in a single-column numerical array.

    Parameters:
    - data: single-column numerical array
    - threshold: a factor that determines the range from the IQR

    Returns:
    - Boolean array indicating outliers (True) and non-outliers (False)
    """
    if len(data) == 0:
        raise ValueError("Input is empty.")
    if isinstance(data, pd.DataFrame):
        raise TypeError("DataFrame input is not supported.")
    if np.isnan(data).all():
        return np.zeros(len(data), dtype=bool)
    median = np.nanmedian(data)
    q1 = np.nanquantile(data, 0.25)
    q3 = np.nanquantile(data, 0.75)
    iqr = q3 - q1
    cutoff_lower = median - (threshold * iqr)
    cutoff_upper = median + (threshold * iqr)
    is_outlier = (data < cutoff_lower) | (data > cutoff_upper)
    return is_outlier


def get_outliers_matrix(
    data_frame: pd.DataFrame, threshold: float, axis: Literal[0, 1] = 0
):
    """
    Get a matrix indicating outliers in each row or column of a dataframe.

    Parameters:
    - data_frame: pandas DataFrame containing only numeric values
    - threshold: a factor that determines the range from the IQR
    - axis: {0 or ‘index’, apply to each column, 1 or ‘columns’, apply to each row}, default 0

    Returns:
    - pandas DataFrame indicating outliers (True) and non-outliers (False)
    """
    validate_dataframe(data_frame)
    matrix = data_frame.apply(lambda x: detect_outliers(x, threshold), axis=axis)
    return matrix


def count_outliers(data_frame: pd.DataFrame, threshold: float, axis: Literal[0, 1] = 0):
    """
    Count number of outlier values in each row or column of a dataframe.

    Parameters:
    - data_frame: pandas DataFrame containing only numeric values
    - threshold: a factor that determines the range from the IQR
    - axis: {0 or ‘index’, apply to each column, 1 or ‘columns’, apply to each row}, default 0

    Returns:
    - pandas Series with the row/column index and the number of outliers
    """
    validate_dataframe(data_frame)
    outliers_matrix = get_outliers_matrix(data_frame, threshold)
    outlier_counts = outliers_matrix.sum(axis=axis)
    return outlier_counts


def remove_outliers(
    data_frame: pd.DataFrame, threshold: float, axis: Literal[0, 1] = 0
):
    """
    Replace outlier values with NAs in a dataframe, column-wise or row-wise.

    Parameters:
    - data_frame: pandas DataFrame containing only numeric values
    - threshold: a factor that determines the range from the IQR
    - axis: {0 or ‘index’, apply to each column, 1 or ‘columns’, apply to each row}, default 0

    Returns:
    - pandas DataFrame where the outlier values are replaced by NAs
    """
    validate_dataframe(data_frame)
    outliers = get_outliers_matrix(data_frame, threshold, axis=axis)
    data_frame_without_outliers = data_frame.where(~outliers, np.nan)
    return data_frame_without_outliers
