"""
Statistics module
"""

import pandas as pd
import numpy as np
from metabotk.outliers_handler import OutlierHandler
from metabotk.missing_handler import MissingDataHandler
from metabotk.utils import ensure_numeric_data


def compute_correlations(data_frame: pd.DataFrame, method: str) -> pd.DataFrame:
    """
    Computes correlations between columns in a pandas DataFrame.

    Parameters:
        data_frame (DataFrame): Pandas DataFrame containing numerical values.
        method (str): Method for computing correlations. Default is 'pearson'.

    Returns:
        DataFrame: Pandas DataFrame containing correlations between columns.
    """
    correlations = data_frame.corr(method=method)
    return correlations


def get_top_n_correlations(data_frame: pd.DataFrame, n=10, method="pearson"):
    """
    Get the top n correlations for each column in a pandas DataFrame.

    Parameters:
        data_frame (DataFrame): Pandas DataFrame containing numerical values.
        n (int): Number of top correlations to return. Default is 10.
        method (str): Method for computing correlations. Default is 'pearson'.

    Returns:
        DataFrame: Pandas DataFrame containing top n correlations
        for each id and their values.
    """
    correlations = compute_correlations(data_frame, method)
    top_correlations = []

    for id in correlations.columns:
        top_n_abs = (
            correlations[id].abs().sort_values(ascending=False).drop(id).iloc[0:n].index
        )
        top_n = correlations[id].loc[top_n_abs]
        top_n.index.name = "correlated_ids"
        top_n.name = "correlation"
        top_n = top_n.reset_index()
        top_n["id"] = id
        top_correlations.append(top_n)
    top_correlations = pd.concat(top_correlations)
    top_correlations = top_correlations[["id", "correlated_ids", "correlation"]]
    return top_correlations


class StatisticsHandler:
    """
    Class for obtaining basic statistics about the data.

    This class provides methods for computing basic statistics
    (mean, standard deviation, median, min, max, sum, CV%, missing, outliers)
    for a collection of numerical data or a pandas DataFrame.
    """

    def __init__(self, dataset_manager):
        """
        Initializes the StatisticsHandler.
        """
        self._outlier_handler = OutlierHandler()
        self._missing_handler = MissingDataHandler()
        self._dataset_manager = dataset_manager

    def coefficient_of_variation(self, data):
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

    def total_sum_abundance(self, data_frame, exclude_incomplete=True):
        """
        Computes total sum abundance (TSA) row-wise

        Parameters:
            data_frame (DataFrame): pandas DataFrame containing numerical data.
            exclude_incomplete (bool): option to exclude columns containing incomplete values
            from the computation

        Returns:
            Series: Pandas Series containing TSA values for each row.
        """
        if exclude_incomplete:
            data_frame = data_frame.dropna(axis=1).copy()
        else:
            data_frame = data_frame.copy()
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
        data_series = pd.Series(data)
        if len(data) == 0:
            raise ValueError("Input data is empty")
        stats = data_series.describe()
        cv = self.coefficient_of_variation(data)
        stats["CV%"] = cv
        stats = stats.rename(index={"50%": "median"})
        stats["missing"] = self._missing_handler._count_missing(data_series)
        stats["outliers"] = sum(
            self._outlier_handler.detect_outliers(
                data_series, threshold=outlier_threshold
            )
        )
        return stats

    def compute_dataframe_statistics(self, outlier_threshold, axis):
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
        stats = self._dataset_manager.data.apply(
            lambda x: self.compute_statistics(x, outlier_threshold=outlier_threshold),
            axis=axis,
        )
        if axis == 0:
            stats = stats.transpose()
        return stats

    def metabolite_stats(self, outlier_threshold=5):
        """
        Computes basic statistics for the metabolomics data metabolite-wise

        This function computes basic statistics for each metabolite in the data.
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

        Parameters:
        - outlier_threshold: Threshold for outlier detection (default=5).

        Returns:
            pandas DataFrame: DataFrame containing statistics for each metabolite.
            The index of the DataFrame is the metabolite names.

        """
        # Ensure that data is set up properly
        if self._dataset_manager.data.empty:
            raise ValueError(
                "No data available. Please import data before computing statistics."
            )

        # Compute statistics using StatisticsHandler
        metabolite_stats = self.compute_dataframe_statistics(outlier_threshold, axis=0)
        # self.metabolite_stats=metabolite_stats
        return metabolite_stats

    def sample_stats(self, outlier_threshold=5):
        """
        Computes basic statistics for the metabolomics data sample-wise

        This function computes statistics for each sample across all metabolites.

        Parameters:
            outlier_threshold (int): Threshold for identifying outliers.

        Returns:
             DataFrame containing statistics for each sample across all metabolites.
        """
        # Ensure that data is set up properly
        if self._dataset_manager.data.empty:
            raise ValueError(
                "No data available. Please import data before computing statistics."
            )
        sample_stats = self.compute_dataframe_statistics(outlier_threshold, axis=1)

        # Compute Total Sum of Abundance (TSA) for each sample across all metabolites
        tsa_complete_only = self.total_sum_abundance(
            self._dataset_manager.data, exclude_incomplete=True
        )
        tsa_complete_only.name = "TSA_complete_only"
        tsa_all = self.total_sum_abundance(
            self._dataset_manager.data, exclude_incomplete=False
        )
        tsa_all.name = "TSA_including_incomplete"
        tsa = pd.concat([tsa_complete_only, tsa_all], axis=1)

        # Merge TSA with sample statistics
        sample_stats = sample_stats.merge(tsa, left_index=True, right_index=True)
        # self.sample_stats=sample_stats
        return sample_stats
