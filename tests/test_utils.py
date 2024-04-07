import pytest
import pandas as pd
import numpy as np

# Import your functions here
from src.utils import validate_dataframe, ensure_numeric_data

class TestValidateDataFrame:
    def test_valid_dataframe(self):
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        assert validate_dataframe(df) is None

    def test_invalid_dataframe(self):
        with pytest.raises(TypeError):
            validate_dataframe([])

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
            ensure_numeric_data(['a', 'b', 'c'])

    def test_valid_mixed_numeric_data(self):
        data = [1, 2, 3, '4']
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
        series = pd.Series(['a', 'b', 'c'])
        with pytest.raises(TypeError):
            ensure_numeric_data(series)
