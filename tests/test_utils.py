import pandas as pd
import pytest
import numpy as np
from src.metabotk.utils import (
    validate_dataframe,
    ensure_numeric_data,
    parse_input,
    validate_new_data,
    reset_index_if_not_none,
)


class TestValidateNewShapeIndex:
    def test_validate_new_shape_index(self):
        data = pd.read_csv("tests/test_data/data.csv")
        data = data.set_index("PARENT_SAMPLE_NAME")
        new_data = pd.DataFrame(np.nan, index=data.index, columns=data.columns)
        validate_new_data(data, new_data)

    def test_different_shape(self):
        data = pd.read_csv("tests/test_data/data.csv")
        data = data.set_index("PARENT_SAMPLE_NAME")
        new_data = data.iloc[0:10]
        with pytest.raises(ValueError):
            validate_new_data(data, new_data)

    def test_different_index(self):
        data = pd.read_csv("tests/test_data/data.csv")
        data = data.set_index("PARENT_SAMPLE_NAME")
        new_data = data.copy()
        new_data.index.name = "INVALID_INDEX"
        with pytest.raises(ValueError):
            validate_new_data(data, new_data)


class TestValidateDataFrame:
    def test_valid_dataframe(self):
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        assert validate_dataframe(df) is None

    def test_invalid_dataframe(self):
        with pytest.raises(TypeError):
            validate_dataframe([])

    def test_validate_dataframe_valid(self):
        # Input is a pandas DataFrame
        data_frame = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        validate_dataframe(data_frame)
        # No error should be raised

    def test_validate_dataframe_invalid(self):
        # Input is not a pandas DataFrame
        data_frame = [1, 2, 3]
        with pytest.raises(TypeError):
            validate_dataframe(data_frame)


class TestEnsureNumericData:
    def test_valid_numeric_data(self):
        data = [1, 2, 3, 4]
        result = ensure_numeric_data(data)
        assert np.array_equal(result, np.array(data))

    def test_invalid_empty_data(self):
        with pytest.raises(ValueError):
            ensure_numeric_data([])

    def test_invalid_non_numeric_data(self):
        with pytest.raises(TypeError):
            ensure_numeric_data(["a", "b", "c"])

    def test_valid_mixed_numeric_data(self):
        data = [1, 2, 3, "4"]
        with pytest.raises(TypeError):
            ensure_numeric_data(data)

    def test_valid_series_input(self):
        series = pd.Series([1, 2, 3, 4])
        result = ensure_numeric_data(series)
        assert np.array_equal(result, np.array(series))

    def test_invalid_empty_series_input(self):
        series = pd.Series([])
        with pytest.raises(ValueError):
            ensure_numeric_data(series)

    def test_invalid_non_numeric_series_input(self):
        series = pd.Series(["a", "b", "c"])
        with pytest.raises(TypeError):
            ensure_numeric_data(series)


def test_reset_index_if_not_none():
    data = pd.read_csv("tests/test_data/sample_metadata.csv")
    data_after = reset_index_if_not_none(data)
    assert data.index.name is None
    data = data.set_index("PARENT_SAMPLE_NAME")
    assert data.index.name == "PARENT_SAMPLE_NAME"
    data_after = reset_index_if_not_none(data)
    assert data_after.index.name is None


class TestParseInput:
    def test_parse_input_pandas_dataframe(self):
        input_data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        assert parse_input(input_data).equals(input_data)

    def test_parse_input_tsv_file(self):
        tsv_file_path = "tests/test_data/data.tsv"
        assert isinstance(parse_input(tsv_file_path), pd.DataFrame)

    def test_parse_input_csv_file(self):
        csv_file_path = "tests/test_data/data.csv"
        assert isinstance(parse_input(csv_file_path), pd.DataFrame)

    def test_parse_input_invalid_input(self):
        invalid_input = 123  # Not a DataFrame or a file path
        with pytest.raises(TypeError):
            parse_input(invalid_input)

    def test_parse_input_invalid_extension(self):
        invalid_input = "tests/test_data/test.invalid"  # Not a DataFrame or a file path
        with pytest.raises(TypeError):
            parse_input(invalid_input)

    def test_parse_input_custom_prefix_ending(self):
        data = "tests/test_data/test.data"
        samples = "tests/test_data/test.samples"
        metabolites = "tests/test_data/test.metabolites"
        for i in [data, samples, metabolites]:
            assert isinstance(parse_input(i), pd.DataFrame)
