import pytest
from src.outliers import OutlierHandler
import numpy as np
import pandas as pd
import warnings
from tests.testing_functions import (
    create_test_dataframe_with_outliers,
    create_outlier_presence_matrix_from_dataframe,
)

outlier_handler=OutlierHandler(threshold=1)
high_thresh_outlier_handler=OutlierHandler(threshold=5)
medium_thresh_outlier_handler=OutlierHandler(threshold=1.2)

# detect_outliers

class TestDetectOutliers:
    def test_input_df(self):
        with pytest.raises(TypeError):
            outlier_handler.detect_outliers(create_test_dataframe_with_outliers())

    def test_input_list(self):
        data = [1, 2, 3, 4, 100]
        assert any(outlier_handler.detect_outliers(data))

    def test_input_series(self):
        data = pd.Series([1, 2, 3, 4, 100])
        assert any(outlier_handler.detect_outliers(data))

    def test_no_outliers(self):
        data = np.array([1, 2, 3, 4, 5])
        assert not any(outlier_handler.detect_outliers(data))

    def test_single_outlier(self):
        data = np.array([1, 2, 3, 10, 5])
        assert np.array_equal(
            outlier_handler.detect_outliers(data), [False, False, False, True, False]
        )

    def test_single_outlier_higher_threshold(self):
        data = np.array([1, 2, 3, 10, 5])
        assert np.array_equal(
            high_thresh_outlier_handler.detect_outliers(data), [False, False, False, False, False]
        )

    def test_multiple_outliers(self):
        data = np.array([1, 100, 1, 50, 1, 2, 3])
        assert np.array_equal(
            outlier_handler.detect_outliers(data), [False, True, False, True, False, False, False]
        )

    def test_negative_values(self):
        data = np.array([-1000, -5, 0, 5, 10])
        assert any(outlier_handler.detect_outliers(data))

    def test_empty_input(self):
        with pytest.raises(ValueError):
            outlier_handler.detect_outliers([])

    # def test_empty_input(self):
    #    with warnings.catch_warnings():
    #    # Filter out the specific warning related to nanmean on an empty slice
    #        warnings.filterwarnings("ignore", message="Mean of empty slice")
    #        data = np.array([])
    #        detected_outliers=detect_outliers(data, 1)
    #    assert not any(detected_outliers)


# get_outliers_matrix

class TestGetOutliersMatrix:
    data, outliers_df = (
        create_test_dataframe_with_outliers(),
        create_outlier_presence_matrix_from_dataframe(),
    )

    def test_outliers_matrix(self):
        assert high_thresh_outlier_handler.get_outliers_matrix(self.data).equals(self.outliers_df)


# count_outliers


class TestCountOutliers:

    data, outliers_df = (
        create_test_dataframe_with_outliers(),
        create_outlier_presence_matrix_from_dataframe(),
    )

    def test_count_outliers_column_wise(self):
        outlier_counts = outlier_handler.count_outliers(self.data, axis=0)
        outlier_counts_to_assert = pd.Series([1, 2, 1, 2])
        outlier_counts_to_assert.index = self.data.columns
        assert outlier_counts_to_assert.equals(outlier_counts)

    def test_count_outliers_row_wise(self):
        outlier_counts = outlier_handler.count_outliers(self.data, axis=1)
        outlier_counts_to_assert = pd.Series([1, 1, 1, 3, 0])
        outlier_counts_to_assert.index = self.data.index
        assert outlier_counts_to_assert.equals(outlier_counts)

    def test_count_outliers_column_wise_high_threshold(self):
        outlier_counts = high_thresh_outlier_handler.count_outliers(self.data, axis=0)
        outlier_counts_to_assert = pd.Series([0, 1, 0, 1])
        outlier_counts_to_assert.index = self.data.columns
        assert outlier_counts_to_assert.equals(outlier_counts)

    def test_count_outliers_row_wise_high_threshold(self):
        outlier_counts = high_thresh_outlier_handler.count_outliers(self.data, axis=1)
        outlier_counts_to_assert = pd.Series([1, 1, 0, 0, 0])
        outlier_counts_to_assert.index = self.data.index
        assert outlier_counts_to_assert.equals(outlier_counts)

    def test_count_outliers_column_wise_medium_threshold(self):
        outlier_counts = medium_thresh_outlier_handler.count_outliers(self.data, axis=0)
        outlier_counts_to_assert = pd.Series([1, 1, 0, 2])
        outlier_counts_to_assert.index = self.data.columns
        assert outlier_counts_to_assert.equals(outlier_counts)

    def test_count_outliers_row_wise_medium_threshold(self):
        outlier_counts = medium_thresh_outlier_handler.count_outliers(self.data, axis=1)
        outlier_counts_to_assert = pd.Series([1, 1, 1, 1, 0])
        outlier_counts_to_assert.index = self.data.index
        assert outlier_counts_to_assert.equals(outlier_counts)


# remove_outliers


class TestRemoveOutliers:
    data, outliers_df = (
        create_test_dataframe_with_outliers(),
        create_outlier_presence_matrix_from_dataframe(),
    )

    def test_outlier_removal(self):
        data_without_outliers = self.data.copy()
        data_without_outliers.loc[0, "B"] = np.nan  # Outlier in column B
        data_without_outliers.loc[1, "D"] = np.nan  # Outlier in column D
        assert high_thresh_outlier_handler.remove_outliers(self.data).equals(data_without_outliers)
