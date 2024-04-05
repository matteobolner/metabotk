import pytest
from src.outliers import *
import numpy as np
import pandas as pd

class TestDetectOutliers:
    def test_input_list(self):
        data=[1,2,3,4,100]
        assert any(detect_outliers(data, 1))

    def test_input_series(self):
        data=pd.Series([1,2,3,4,100])
        assert any(detect_outliers(data, 1))

    def test_no_outliers(self):
        data = np.array([1, 2, 3, 4, 5])
        assert not any(detect_outliers(data, 1))

    def test_single_outlier(self):
        data = np.array([1, 2, 3, 10, 5])
        assert np.array_equal(detect_outliers(data, 1),[False, False, False, True, False])

    def test_single_outlier_higher_threshold(self):
        data = np.array([1, 2, 3, 10, 5])
        assert np.array_equal(detect_outliers(data, 5),[False, False, False, False, False])

    def test_multiple_outliers(self):
        data = np.array([1, 100, 1, 50, 1, 2, 3])
        assert np.array_equal(detect_outliers(data, 1),[False, True, False, True, False, False, False])

    def test_negative_values(self):
        data = np.array([-1000, -5, 0, 5, 10])
        assert any(detect_outliers(data, 1))

    def test_empty_input(self):
        data = np.array([])
        assert not any(detect_outliers(data, 1))


class TestOutliersMatrix:
    def create_test_dataframe_and_outlier_results(self):
        np.random.seed(42)
        test_data = {
            'A': np.random.normal(loc=10, scale=2, size=5),  # Normal distribution without outliers
            'B': np.random.normal(loc=20, scale=3, size=5),  # Normal distribution without outliers
            'C': np.random.normal(loc=30, scale=4, size=5),  # Normal distribution without outliers
            'D': np.random.normal(loc=40, scale=5, size=5)   # Normal distribution without outliers
        }
        test_data['B'][0] = 100  # Outlier in column B
        test_data['D'][1] = -50  # Outlier in column D
        test_dataframe=pd.DataFrame(test_data)

        outliers_df = pd.DataFrame(False, index=test_dataframe.index, columns=test_dataframe.columns)
        outliers_df.loc[0,'B'] = True  # Outlier in column B
        outliers_df.loc[1,'D'] = True  # Outlier in column B
        return test_dataframe, outliers_df

    def test_generic(self):
        data, outliers_df=self.create_test_dataframe_and_outlier_results()
        assert outliers_matrix(data, threshold=5).equals(outliers_df)
