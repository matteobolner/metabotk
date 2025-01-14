import warnings
import pytest
import numpy as np
import pandas as pd
import metabotk.missing_handler as missing

# setup test data
test_data = pd.read_csv("tests/test_data/data.csv")
test_data = test_data[test_data.columns[5:10]].iloc[10:20]
test_values_series = test_data["212"]
test_values_list = test_values_series.tolist()


class TestValidateThreshold:
    def test_string_threshold(self):
        with pytest.raises(TypeError):
            missing._validate_threshold("A")
        with pytest.raises(ValueError):
            missing._validate_threshold(12)


class TestDetectMissingValues:
    def test_input_list(self):
        data = test_values_list
        assert missing._detect_missing(data).sum() == 2

    def test_input_series(self):
        data = test_values_series
        assert missing._detect_missing(data).sum() == 2

    def test_no_missing(self):
        data = np.array([1, 2, 3, 4, 5])
        assert not any(missing._detect_missing(data))

    def test_single_missing(self):
        data = np.array([1, 2, 3, np.nan, 5])
        assert np.array_equal(
            missing._detect_missing(data), [False, False, False, True, False]
        )

    def test_multiple_missing(self):
        data = np.array([1, np.nan, 1, np.nan, 1, 2, 3])
        assert np.array_equal(
            missing._detect_missing(data),
            [False, True, False, True, False, False, False],
        )

    def test_empty_input(self):
        with warnings.catch_warnings():
            # Filter out the specific warning related to nanmean on an empty slice
            warnings.filterwarnings("ignore", message="Mean of empty slice")
            data = np.array([])
            detected_missing = missing._detect_missing(data)
        assert not any(detected_missing)


# count_missing_values
class TestCountMissingValues:
    data = test_data

    def test_count_missing_values_column_wise(self):
        missing_counts = missing.count_missing_in_dataframe(self.data, axis=0)
        missing_counts_to_assert = pd.Series([2, 0, 0, 0, 4])
        missing_counts_to_assert.index = self.data.columns
        assert missing_counts_to_assert.equals(missing_counts)

    def test_count_missing_values_row_wise(self):
        missing_counts = missing.count_missing_in_dataframe(self.data, axis=1)
        missing_counts_to_assert = pd.Series([0, 1, 0, 1, 2, 0, 0, 0, 1, 1])
        missing_counts_to_assert.index = self.data.index
        assert missing_counts_to_assert.equals(missing_counts)


# drop_columns_with_missing_over_threshold
class TestDropOverThreshold:
    data = test_data

    def test_drop_columns_with_missing_over_threshold_0(self):
        dropped = missing._drop_columns_with_missing(self.data, threshold=0)
        assert np.array_equal(
            list(dropped.columns),
            ["212", "273"],
        )

    def test_drop_rows_with_missing_over_threshold_0(self):
        dropped = missing._drop_rows_with_missing(self.data, threshold=0)
        assert np.array_equal(list(dropped.index), [11, 13, 14, 18, 19])

    def test_drop_columns_with_missing_over_threshold_1(self):
        dropped = missing._drop_columns_with_missing(self.data, threshold=1)
        assert len(dropped.columns) == 0

    def test_drop_rows_with_missing_over_threshold_1(self):
        dropped = missing._drop_rows_with_missing(self.data, threshold=1)
        assert len(dropped.index) == 0

    def test_drop_columns_with_missing_over_threshold_three(self):
        dropped = missing._drop_columns_with_missing(self.data, threshold=0.3)
        assert np.array_equal(list(dropped.columns), ["273"])

    def test_drop_rows_with_missing_over_threshold_three(self):
        dropped = missing._drop_rows_with_missing(self.data, threshold=0.3)
        assert np.array_equal(list(dropped.index), [14])


class TestDropOverThreshold2:
    data = test_data

    def test_drop_columns_with_missing_over_threshold_0(self):
        remaining = missing.drop_missing_from_dataframe(self.data, axis=0, threshold=0)
        assert np.array_equal(
            list(remaining.columns),
            ["229", "250", "254"],
        )

    def test_drop_rows_with_missing_over_threshold_0(self):
        remaining = missing.drop_missing_from_dataframe(self.data, axis=1, threshold=0)
        assert np.array_equal(
            list(remaining.index),
            [10, 12, 15, 16, 17],
        )

    def test_drop_columns_with_missing_over_threshold_1(self):
        remaining = missing.drop_missing_from_dataframe(self.data, axis=0, threshold=1)
        assert self.data.equals(remaining)

    def test_drop_rows_with_missing_over_threshold_1(self):
        remaining = missing.drop_missing_from_dataframe(self.data, axis=1, threshold=1)
        assert self.data.equals(remaining)
