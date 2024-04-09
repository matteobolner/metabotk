import numpy as np
import pandas as pd
from src.utils import validate_dataframe

class OutlierHandler:
    def detect_outliers(self, data, threshold):
        """
        Get outlier values using the Interquartile Range (IQR) method.

        Parameters:
        - data: list, array, or Series containing numerical data

        Returns:
        - Boolean array indicating outliers (True) and non-outliers (False)
        """
        if len(data) == 0:
            raise ValueError("Input is empty.")
        if isinstance(data, pd.DataFrame):
            raise TypeError("DataFrame input is not supported.")

        median = np.nanmedian(data)
        q1 = np.nanquantile(data, 0.25)
        q3 = np.nanquantile(data, 0.75)
        iqr = q3 - q1
        cutoff_lower = median - (threshold * iqr)
        cutoff_upper = median + (threshold * iqr)
        is_outlier = (data < cutoff_lower) | (data > cutoff_upper)
        return is_outlier

    def get_outliers_matrix(self, data_frame, threshold, axis=0):
        """
        Get a matrix of value outliers over the whole dataset column-wise.

        Parameters:
        - data_frame: pandas DataFrame containing only numeric values

        Returns:
        - pandas DataFrame indicating outliers (True) and non-outliers (False)
        """
        validate_dataframe(data_frame)
        matrix = data_frame.apply(lambda x: self.detect_outliers(x,threshold), axis=axis)
        return matrix

    def count_outliers(self, data_frame, threshold, axis=0):
        """
        Count number of outlier values in each row or column of dataframe.

        Parameters:
        - data_frame: pandas DataFrame containing only numeric values
        - axis: {0 or ‘index’, apply to each column, 1 or ‘columns’, apply to each row}, default 0

        Returns:
        - pandas Series with the row/column index and the number of outliers
        """
        validate_dataframe(data_frame)
        outliers_matrix = self.get_outliers_matrix(data_frame, threshold)
        outlier_counts = outliers_matrix.sum(axis=axis)
        return outlier_counts

    def remove_outliers(self, data_frame, threshold, axis=0):
        """
        Replace outlier values with NAs in the whole dataset, column-wise or row-wise.

        Parameters:
        - data_frame: pandas DataFrame containing only numeric values
        - axis: {0 or ‘index’, apply to each column, 1 or ‘columns’, apply to each row}, default 0

        Returns:
        - pandas DataFrame where the outlier values are replaced by NAs
        """
        validate_dataframe(data_frame)
        outliers = self.get_outliers_matrix(data_frame,threshold, axis=axis)
        data_frame_without_outliers = data_frame.where(~outliers, np.nan)
        return data_frame_without_outliers
