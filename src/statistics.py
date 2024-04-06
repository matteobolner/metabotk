"""Module for obtaining some basic statistics about the data"""

import pandas as pd
import numpy as np
from src.outliers import detect_outliers


def coefficient_of_variation(data):
    """
    Compute the coefficient of variation in percentage
    NaN values are removed before computing
    Parameters:
    - data: list, array, or Series containing numerical data

    Returns:
    - Coefficient of Variation %

    """
    if len(data) == 0:
        raise ValueError("Empty data")
    data = np.array(data)  # convert to np array
    if not np.issubdtype(data.dtype, np.number):
        raise TypeError("Data must contain only numeric values")
    data = data[~np.isnan(data)]  # remove nan values
    cv = np.std(data) / np.mean(data)  # compute CV
    cv_pctg = cv * 100  # compute CV%
    return cv_pctg


def basic_stats(data, outlier_threshold=5):
    """
    Get some basic statistics from a collection

    Parameters:
    - data: list, array, or Series containing numerical data

    Returns:
    - Pandas series containing statistics

    """
    if len(data) == 0:
        raise ValueError("Input data is empty")
    data = np.array(data)
    if not np.issubdtype(data.dtype, np.number):
        raise TypeError("Data must contain only numeric values")
    data_series = pd.Series(data)
    if data_series.isnull().all():
        raise ValueError("Input data contains only NaN values")
    stats = data_series.describe()
    cv = coefficient_of_variation(data_series)
    stats["CV%"] = cv
    stats = stats.rename(index={"50%": "median"})
    stats["missing"] = (len(data) - stats["count"]).astype(int)
    stats["outliers"] = sum(detect_outliers(data_series, outlier_threshold))
    return stats


def dataframe_basic_stats(data_frame, axis=0, outlier_threshold=5):
    """
    Get basic statistics on the whole dataframe, either row-wise or column-wise

    Parameters:
    - data_frame: pandas DataFrame of numeric values
    - axis: {0 or ‘index’, apply to each column, 1 or ‘columns’, apply to each row}, default 0

    Returns:
    - Pandas DataFrame containing statistics for each row or column

    """
    if not isinstance(data_frame, pd.DataFrame):
        raise TypeError("Data must be a pandas DataFrame")
    stats = data_frame.apply(lambda x: basic_stats(x, outlier_threshold), axis=axis)
    if axis == 0:
        stats = stats.transpose()
    return stats
