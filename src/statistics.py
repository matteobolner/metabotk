"""Module for obtaining some basic statistics about the data"""

import pandas as pd
import numpy as np
from src.utils import validate_dataframe, ensure_numeric_data
from src.outliers import detect_outliers

OUTLIER_THRESHOLD=5


def coefficient_of_variation(data):
    """
    Compute the coefficient of variation in percentage
    NaN values are removed before computing
    Parameters:
    - data: list, array, or Series containing numerical data

    Returns:
    - Coefficient of Variation %

    """
    data=ensure_numeric_data(data)
    data = data[~np.isnan(data)]  # remove nan values
    cv = np.std(data) / np.mean(data)  # compute CV
    cv_pctg = cv * 100  # compute CV%
    return cv_pctg


def compute_statistics(data, outlier_threshold=OUTLIER_THRESHOLD):
    """
    Get some basic statistics from a collection

    Parameters:
    - data: list, array, or Series containing numerical data

    Returns:
    - Pandas series containing statistics

    """
    data=ensure_numeric_data(data)
    data_series = pd.Series(data)
    stats = data_series.describe()
    cv = coefficient_of_variation(data_series)
    stats["CV%"] = cv
    stats = stats.rename(index={"50%": "median"})
    stats["missing"] = (len(data) - stats["count"]).astype(int)
    stats["outliers"] = sum(detect_outliers(data_series, outlier_threshold))
    return stats


def compute_dataframe_statistics(data_frame, axis=0, outlier_threshold=OUTLIER_THRESHOLD):
    """
    Get basic statistics on the whole dataframe, either row-wise or column-wise

    Parameters:
    - data_frame: pandas DataFrame of numeric values
    - axis: {0 or ‘index’, apply to each column, 1 or ‘columns’, apply to each row}, default 0

    Returns:
    - Pandas DataFrame containing statistics for each row or column

    """
    validate_dataframe(data_frame)
    stats = data_frame.apply(lambda x: compute_statistics(x, outlier_threshold), axis=axis)
    if axis == 0:
        stats = stats.transpose()
    return stats
