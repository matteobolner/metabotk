import numpy as np

import pandas as pd
from metabotk.utils import validate_dataframe


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

    def _validate_threshold(self, threshold):
        """
        Validates the threshold attribute.
        """
        if not isinstance(threshold, (int, float)):
            raise TypeError("Threshold must be a numeric value")
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")

    def _detect_missing(self, data) -> np.array:
        """
        Detects missing values in a collection.

        Parameters:
            data (list, array, or Series): Collection containing data.

        Returns:
            Boolean array indicating missing (True) and non-missing data (False).
        """

        is_missing = np.isnan(data)
        return is_missing

    def _count_missing(self, data):
        """
        Counts missing values in a collection.

        Parameters:
            data (list, array, or Series): Collection containing data.

        Returns:
            Number of missing values in collection
        """

        missing = self._detect_missing(data)
        n_missing = missing.sum()
        return n_missing

    def _count_missing_in_dataframe(self, data_frame, axis=0):
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
        missing_values = data_frame.apply(self._detect_missing, axis=axis)
        n_missing_values = missing_values.sum(axis=axis)
        return n_missing_values

    def _drop_columns_with_missing(self, data_frame, threshold=0.25):
        """
        Removes columns with missing values above the threshold.

        Parameters:
            data_frame (DataFrame): Pandas DataFrame containing only numeric values.

        Returns:
            DataFrame: DataFrame with columns with missingness higher than the threshold.
        """
        self._validate_threshold(threshold)
        validate_dataframe(data_frame)
        missing = self._count_missing_in_dataframe(data_frame, axis=0)
        to_drop = missing[missing / len(data_frame) > threshold]
        to_drop = data_frame[list(to_drop.index)]
        return to_drop

    def _drop_rows_with_missing(self, data_frame, threshold=0.25):
        """
        Removes rows with missing values above the threshold.

        Parameters:
            data_frame (DataFrame): Pandas DataFrame containing only numeric values.

        Returns:
            DataFrame: DataFrame with rows with missingness higher than the threshold.
        """
        self._validate_threshold(threshold)
        validate_dataframe(data_frame)
        missing = self._count_missing_in_dataframe(data_frame, axis=1)
        to_drop = missing[missing / len(data_frame.columns) > threshold]
        to_drop = data_frame.loc[to_drop.index]
        return to_drop

    def _drop_missing_from_dataframe(
        self, data_frame: pd.DataFrame, axis: int = 0, threshold: float = 0.25
    ) -> pd.DataFrame:
        """
        Remove columns or rows with missing values above the threshold.

        Parameters:
            - threshold: missingness over which to remove the row/column
            - axis: {0 or ‘index’, remove columns, 1 or ‘columns’, remove rows}, default 0

        Returns:
            DataFrame: DataFrame containing the rows/columns dropped.
        """
        if axis == 0:
            to_drop = self._drop_columns_with_missing(
                data_frame=data_frame, threshold=threshold
            )
            print(f"Removed {len(to_drop.columns)} columns")
            remaining_data = data_frame.drop(columns=to_drop.columns)
            return remaining_data

        if axis == 1:
            to_drop = self._drop_rows_with_missing(
                data_frame=data_frame, threshold=threshold
            )
            print(f"Removed {len(to_drop.index)} rows")
            remaining_data = data_frame.drop(index=to_drop.index)
            return remaining_data
