import pytest
from src.missing import *
import numpy as np
import pandas as pd
import warnings


##Create a test dataframe with missing values
def create_test_dataframe():
    np.random.seed(42)
    test_data = {
        'A': np.random.normal(loc=10, scale=2, size=5),  # Normal distribution without missings
        'B': np.random.normal(loc=20, scale=3, size=5),  # Normal distribution without missings
        'C': np.random.normal(loc=30, scale=4, size=5),  # Normal distribution without missings
        'D': np.random.normal(loc=40, scale=5, size=5)   # Normal distribution without missings
    }
    test_data['B'][0] = np.nan  # missing in column B
    test_data['B'][1] = np.nan  # missing in column B
    test_data['B'][2] = np.nan  # missing in column B
    test_data['D'][1] = np.nan  # missing in column D
    test_data['A'][1] = np.nan  # missing in column D
    test_data['D'][1] = np.nan  # missing in column D

    test_dataframe=pd.DataFrame(test_data)
    return test_dataframe


###TESTS

#detect_missing_values

class TestDetectMissingValues:
    def test_input_list(self):
        data=[1,2,3,np.nan,100]
        assert any(detect_missing_values(data))

    def test_input_series(self):
        data=pd.Series([1,2,3,4,np.nan])
        assert any(detect_missing_values(data))

    def test_no_missing(self):
        data = np.array([1, 2, 3, 4, 5])
        assert not any(detect_missing_values(data))

    def test_single_missing(self):
        data = np.array([1, 2, 3, np.nan, 5])
        assert np.array_equal(detect_missing_values(data),[False, False, False, True, False])

    def test_multiple_missing(self):
        data = np.array([1, np.nan, 1, np.nan, 1, 2, 3])
        assert np.array_equal(detect_missing_values(data),[False, True, False, True, False, False, False])

    def test_empty_input(self):
        with warnings.catch_warnings():
        # Filter out the specific warning related to nanmean on an empty slice
            warnings.filterwarnings("ignore", message="Mean of empty slice")
            data = np.array([])
            detected_missing=detect_missing_values(data)
        assert not any(detected_missing)


#count_missing_values
class TestCountMissingValues:

    data=create_test_dataframe()

    def test_count_missing_values_column_wise(self):
        missing_counts=count_missing_values(self.data, axis=0)
        missing_counts_to_assert= pd.Series([1,3,0,1])
        missing_counts_to_assert.index=self.data.columns
        assert missing_counts_to_assert.equals(missing_counts)

    def test_count_missing_values_row_wise(self):
        missing_counts=count_missing_values(self.data, axis=1)
        missing_counts_to_assert= pd.Series([1,3,1,0,0])
        missing_counts_to_assert.index=self.data.index
        assert missing_counts_to_assert.equals(missing_counts)

#drop_columns_with_missing_over_threshold
class TestDropOverThreshold:
    data=create_test_dataframe()
    def test_drop_columns_with_missing_over_threshold_0(self):
        dropped=drop_columns_with_missing_over_threshold(self.data, 0)
        assert np.array_equal(list(dropped.columns), ['C'])

    def test_drop_rows_with_missing_over_threshold_0(self):
        dropped=drop_rows_with_missing_over_threshold(self.data, 0)
        print(dropped)
        assert np.array_equal(list(dropped.index), [3,4])

    def test_drop_columns_with_missing_over_threshold_1(self):
        dropped=drop_columns_with_missing_over_threshold(self.data, 1)
        assert dropped.equals(self.data)

    def test_drop_rows_with_missing_over_threshold_1(self):
        dropped=drop_rows_with_missing_over_threshold(self.data, 1)
        assert dropped.equals(self.data)

    def test_drop_columns_with_missing_over_threshold_half(self):
        dropped=drop_columns_with_missing_over_threshold(self.data, 0.5)
        assert np.array_equal(list(dropped.columns), ['A','C','D'])

    def test_drop_rows_with_missing_over_threshold_half(self):
        dropped=drop_rows_with_missing_over_threshold(self.data, 0.5)
        assert np.array_equal(list(dropped.index), [0,2,3,4])
