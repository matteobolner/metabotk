"""Module for detecting, counting and removing outlier values"""

import numpy as np
import pandas as pd
from src.utils import validate_dataframe

OUTLIER_THRESHOLD = 5



def detect_outliers(data, threshold):
    """
    Get outlier values in a list/array using the Interquartile Range (IQR) method.
    See https://github.com/MRCIEU/metaboprep for details on the method and threshold.
    Parameters:
    - data: list, array, or Series containing numerical data
    - threshold: multiplier for IQR to determine outliers

    Returns:
    - Boolean array indicating outliers (True) and non-outliers (False)
    """
    if len(data) == 0:
        raise ValueError("Input is empty.")
    if isinstance(data, pd.DataFrame):
        raise TypeError(
            "DataFrame input is not supported. Please provide a list, array, or Series. \
                        To apply the function on a whole dataframe, use get_outliers_matrix"
        )

    median = np.nanmedian(data)
    q1 = np.nanquantile(data, 0.25)
    q3 = np.nanquantile(data, 0.75)
    iqr = q3 - q1
    cutoff_lower = median - (threshold * iqr)
    cutoff_upper = median + (threshold * iqr)
    is_outlier = (data < cutoff_lower) | (data > cutoff_upper)
    return is_outlier


def get_outliers_matrix(data_frame, threshold):
    """
    Get a matrix of value outliers over the whole dataset column-wise
    Parameters:
    - data_frame: pandas DataFrame containing only numeric values
    - threshold: multiplier for IQR to determine outliers

    Returns:
    - pandas DataFrame indicating outliers (True) and non-outliers (False)

    """
    validate_dataframe(data_frame)
    matrix = data_frame.apply(lambda x: detect_outliers(x, threshold=threshold), axis=0)
    return matrix


def count_outliers(data_frame, axis=0, threshold=OUTLIER_THRESHOLD):
    """
    Count number of outlier values in each row or column of dataframe
    depending on the specified axis
    NOTE: if axis 1 is specified the outlier detection will still be computed column-wise,
    but the count will be row-wise

    Parameters:
    - data_frame: pandas DataFrame containing only numeric values
    - axis: {0 or ‘index’, apply to each column, 1 or ‘columns’, apply to each row}, default 0
    - threshold: multiplier for IQR to determine outliers

    Returns:
    - pandas Series with the row/column index and the number of outliers
    """
    validate_dataframe(data_frame)
    outliers_matrix = get_outliers_matrix(data_frame, threshold)
    outlier_counts = outliers_matrix.sum(axis=axis)
    return outlier_counts


def remove_outliers(data_frame, threshold=OUTLIER_THRESHOLD):
    """
    Replace outlier values with NAs in the whole dataset
    Parameters:
    - data_frame: pandas DataFrame containing only numeric values
    - threshold: multiplier for IQR to determine outliers

    Returns:
    - pandas DataFrame where the outlier values are replaced by NAs
    """
    validate_dataframe(data_frame)
    outliers = get_outliers_matrix(data_frame, threshold=threshold)
    data_frame_without_outliers = data_frame.where(~outliers, np.nan)
    return data_frame_without_outliers


# def count_outliers(data, threshold):
#    '''
#    Return the number of outliers contained in the input values
#    Parameters:
#    - data: list, array, or Series containing numerical data
#    - threshold: multiplier for IQR to determine outliers
#
#    Returns:
#    - Count of outliers in the input data (numeric)
#
#    '''
#    outliers_detected=detect_outliers(data, threshold=threshold)
#    n_outliers=sum(outliers_detected)
#    return n_outliers
