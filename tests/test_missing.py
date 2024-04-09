import warnings
from tests.testing_functions import create_test_dataframe_with_missing
import pytest
import numpy as np
import pandas as pd
from src.missing import MissingDataHandler

missing_handler = MissingDataHandler()

# missing_handler.detect_missing

class TestValidateThreshold:
    def test_string_threshold(self):
        with pytest.raises(TypeError):
            MissingDataHandler().validate_threshold('A')
        with pytest.raises(ValueError):
            MissingDataHandler().validate_threshold(12)

class TestDetectMissingValues:
    def test_input_list(self):
        data = [1, 2, 3, np.nan, 100]
        assert any(missing_handler.detect_missing(data))

    def test_input_series(self):
        data = pd.Series([1, 2, 3, 4, np.nan])
        assert any(missing_handler.detect_missing(data))

    def test_no_missing(self):
        data = np.array([1, 2, 3, 4, 5])
        assert not any(missing_handler.detect_missing(data))

    def test_single_missing(self):
        data = np.array([1, 2, 3, np.nan, 5])
        assert np.array_equal(
            missing_handler.detect_missing(data), [False, False, False, True, False]
        )

    def test_multiple_missing(self):
        data = np.array([1, np.nan, 1, np.nan, 1, 2, 3])
        assert np.array_equal(
            missing_handler.detect_missing(data), [False, True, False, True, False, False, False]
        )

    def test_empty_input(self):
        with warnings.catch_warnings():
            # Filter out the specific warning related to nanmean on an empty slice
            warnings.filterwarnings("ignore", message="Mean of empty slice")
            data = np.array([])
            detected_missing = missing_handler.detect_missing(data)
        assert not any(detected_missing)

# count_missing_values
class TestCountMissingValues:

    data = create_test_dataframe_with_missing()

    def test_count_missing_values_column_wise(self):
        missing_counts = missing_handler.count_missing_in_dataframe(self.data, axis=0)
        missing_counts_to_assert = pd.Series([1, 3, 0, 1])
        missing_counts_to_assert.index = self.data.columns
        assert missing_counts_to_assert.equals(missing_counts)

    def test_count_missing_values_row_wise(self):
        missing_counts = missing_handler.count_missing_in_dataframe(self.data, axis=1)
        missing_counts_to_assert = pd.Series([1, 3, 1, 0, 0])
        missing_counts_to_assert.index = self.data.index
        assert missing_counts_to_assert.equals(missing_counts)


# drop_columns_with_missing_over_threshold
class TestDropOverThreshold:
    data = create_test_dataframe_with_missing()

    def test_drop_columns_with_missing_over_threshold_0(self):
        dropped = missing_handler.drop_columns_with_missing(self.data, threshold=0)
        assert np.array_equal(list(dropped.columns), ["C"])

    def test_drop_rows_with_missing_over_threshold_0(self):
        dropped = missing_handler.drop_rows_with_missing(self.data, threshold=0)
        print(dropped)
        assert np.array_equal(list(dropped.index), [3, 4])

    def test_drop_columns_with_missing_over_threshold_1(self):
        dropped = missing_handler.drop_columns_with_missing(self.data, threshold=1)
        assert dropped.equals(self.data)

    def test_drop_rows_with_missing_over_threshold_1(self):
        dropped = missing_handler.drop_rows_with_missing(self.data, threshold=1)
        assert dropped.equals(self.data)

    def test_drop_columns_with_missing_over_threshold_half(self):
        dropped = missing_handler.drop_columns_with_missing(self.data, threshold=0.5)
        assert np.array_equal(list(dropped.columns), ["A", "C", "D"])

    def test_drop_rows_with_missing_over_threshold_half(self):
        dropped = missing_handler.drop_rows_with_missing(self.data, threshold=0.5)
        assert np.array_equal(list(dropped.index), [0, 2, 3, 4])
