import numpy as np
import pandas as pd
from src.utils import validate_dataframe

class MissingDataHandler:
    """
    Class for detecting and counting missing values in data,
    as well as removing columns/rows based on their missing data content.

    Methods:
        detect_missing(data): Detects missing values in a collection.
        count_missing(data_frame, axis=0): Counts missing values in each row or column of a DataFrame.
        drop_columns_with_missing(data_frame): Removes columns with missing values above the threshold.
        drop_rows_with_missing(data_frame): Removes rows with missing values above the threshold.
    """

    def __init__(self):
        """
        Initializes the MissingDataHandler.
        """

    def validate_threshold(self, threshold):
        """
        Validates the threshold attribute.
        """
        if not isinstance(threshold, (int, float)):
            raise TypeError("Threshold must be a numeric value")
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")

    def detect_missing(self, data):
        """
        Detects missing values in a collection.

        Parameters:
            data (list, array, or Series): Collection containing data.

        Returns:
            Boolean array indicating missing (True) and non-missing data (False).
        """

        is_missing = np.isnan(data)
        return is_missing

    def count_missing(self, data):
        """
        Counts missing values in a collection.

        Parameters:
            data (list, array, or Series): Collection containing data.

        Returns:
            Number of missing values in collection
        """

        missing=self.detect_missing(data)
        n_missing=missing.sum()
        return n_missing

    def count_missing_in_dataframe(self, data_frame, axis=0):
        """
        Counts missing values in each row or column of a DataFrame.

        Parameters:
            data_frame (DataFrame): Pandas DataFrame containing only numeric values.
            axis (int, optional): Axis along which to count missing values.
                0 for columns, 1 for rows. Default is 0.

        Returns:
            Series: Pandas Series with the row/column index and the number of missing values.
        """
        validate_dataframe(data_frame)
        missing_values = data_frame.apply(self.detect_missing, axis=axis)
        n_missing_values = missing_values.sum(axis=axis)
        return n_missing_values

    def drop_columns_with_missing(self, data_frame, threshold=0.25):
        """
        Removes columns with missing values above the threshold.

        Parameters:
            data_frame (DataFrame): Pandas DataFrame containing only numeric values.

        Returns:
            DataFrame: DataFrame without columns with missingness higher than the threshold.
        """
        self.validate_threshold(threshold)
        validate_dataframe(data_frame)
        missing = self.count_missing_in_dataframe(data_frame, axis=0)
        to_drop = missing[missing / len(data_frame) > threshold]
        data_frame = data_frame.drop(columns=to_drop.index)
        return data_frame

    def drop_rows_with_missing(self, data_frame, threshold=0.25):
        """
        Removes rows with missing values above the threshold.

        Parameters:
            data_frame (DataFrame): Pandas DataFrame containing only numeric values.

        Returns:
            DataFrame: DataFrame without rows with missingness higher than the threshold.
        """
        self.validate_threshold(threshold)
        validate_dataframe(data_frame)
        missing = self.count_missing_in_dataframe(data_frame, axis=1)
        to_drop = missing[missing / len(data_frame.columns) > threshold]
        data_frame = data_frame.drop(index=to_drop.index)
        return data_frame

    def drop_missing_from_dataframe(self, data_frame, axis=0, threshold=0.25):
        """
        Remove columns or rows with missing values above the threshold.

        Parameters:
            - threshold: missingness over which to remove the row/column
            - axis: {0 or ‘index’, remove columns, 1 or ‘columns’, remove rows}, default 0

        Returns:
            DataFrame: DataFrame containing the rows/columns dropped.
        """
        if axis==0:
            all=data_frame.copy()
            data_frame=self.drop_columns_with_missing(data_frame=data_frame, threshold=threshold)
            remaining=set(data_frame.columns)
            #self._update_chemical_annotation()
            dropped=list(set(all.columns).difference(remaining))
            print(f"Removed {len(dropped)} elements")
            dropped=all[dropped]
            return dropped
        elif axis==1:
            all=data_frame.copy()
            data_frame=self.drop_rows_with_missing(data_frame=data_frame, threshold=threshold)
            #self._update_sample_metadata()
            remaining=set(data_frame.index)
            dropped=list(set(all.index).difference(remaining))
            print(f"Removed {len(dropped)} elements")
            dropped=all.loc[dropped]
            return dropped
