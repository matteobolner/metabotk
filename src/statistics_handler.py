import pandas as pd
import numpy as np
from outliers_handler import OutlierHandler
from missing_handler import MissingDataHandler
from utils import ensure_numeric_data, validate_dataframe


def coefficient_of_variation(data):
    """
    Compute the coefficient of variation in percentage.

    The coefficient of variation (CV) is a measure of the dispersion of a dataset.
    It is calculated as the standard deviation (σ) divided by the mean (μ).
    The CV is expressed as a percentage (%).

    Parameters:
        data (list, array, or Series): Collection containing numerical data.

    Returns:
        float: Coefficient of Variation % (CV%).
    """
    data = ensure_numeric_data(data)
    # Remove any missing (nan) values.
    data = data[~np.isnan(data)]
    # Compute the standard deviation.
    std = np.std(data)
    # Compute the mean.
    mean = np.mean(data)
    # Compute the coefficient of variation.
    cv = std / mean
    # Convert coefficient of variation to a percentage.
    cv_pctg = cv * 100
    return cv_pctg


class StatisticsHandler:
    """
    Class for obtaining basic statistics about the data.

    This class provides methods for computing basic statistics
    (mean, standard deviation, median, min, max, sum, CV%, missing, outliers)
    for a collection of numerical data or a pandas DataFrame.
    """

    def __init__(self):
        """
        Initializes the StatisticsHandler.
        """
        self.outlier_handler = OutlierHandler()
        self.missing_handler = MissingDataHandler()

    def total_sum_abundance(self, data_frame, exclude_incomplete=True):
        """
        Computes total sum abundance (TSA) row-wise

        Parameters:
            data_frame (DataFrame): pandas DataFrame containing numerical data.
            exclude_incomplete (bool): option to exclude columns containing incomplete values from the computation

        Returns:
            Series: Pandas Series containing TSA values for each row.
        """
        if exclude_incomplete:
            data_frame = data_frame.dropna(axis=1)
        tsa = data_frame.sum(axis=1, skipna=True)
        tsa.name = "TSA"
        return tsa

    def compute_statistics(self, data, outlier_threshold):
        """
        Computes basic statistics for a collection of numerical data.

        Parameters:
            data (list, array, or Series): Collection containing numerical data.
            outlier_threshold (float): Threshold for outlier detection.

        Returns:
            Series: Pandas Series containing basic statistics.

        Notes:
            The statistics computed are:
            - Mean
            - Standard deviation
            - Median
            - Min
            - Max
            - Sum
            - Coefficient of Variation (CV%)
            - Number of missing values
            - Number of outliers
        """
        data = np.array(data)
        data_series = pd.Series(data)
        if len(data) == 0:
            raise ValueError("Input data is empty")
        stats = data_series.describe()
        cv = coefficient_of_variation(data)
        stats["CV%"] = cv
        stats = stats.rename(index={"50%": "median"})
        stats["missing"] = self.missing_handler.count_missing(data_series)
        stats["outliers"] = sum(
            self.outlier_handler.detect_outliers(
                data_series, threshold=outlier_threshold
            )
        )
        return stats

    def compute_dataframe_statistics(self, data_frame, outlier_threshold, axis=0):
        """
        Computes basic statistics for a pandas DataFrame.

        Parameters:
            data_frame (DataFrame): Pandas DataFrame containing numerical values.
            outlier_threshold (float): Threshold for outlier detection. Default is None.
            axis (int): Which axis to compute statistics on. Default is 0 (column-wise)

        Returns:
            DataFrame: Pandas DataFrame containing statistics for each column.

        Notes:
            The statistics computed are:
            - Mean
            - Standard deviation
            - Median
            - Min
            - Max
            - Sum
            - Coefficient of Variation (CV%)
            - Number of missing values
            - Number of outliers
        """
        validate_dataframe(data_frame)
        stats = data_frame.apply(
            lambda x: self.compute_statistics(x, outlier_threshold=outlier_threshold),
            axis=axis,
        )
        if axis == 0:
            stats = stats.transpose()
        return stats
