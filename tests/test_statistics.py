import pytest
from src.metabotk.statistics_handler import (
    Statistics,
    compute_correlations,
    get_top_n_correlations,
    coefficient_of_variation,
    compute_statistics,
    compute_dataframe_statistics,
)
from metabotk.metabolomic_dataset import MetabolomicDataset
from tests.testing_functions import (
    create_test_dataframe_with_missing,
    create_test_dataframe_with_outliers,
)
import numpy as np
import pandas as pd


class TestCoefficientOfVariation:
    @pytest.mark.parametrize(
        "input_data, expected_output",
        [
            ([1, 2, 3, 4, 5], 47.14045207910317),
            ([5, 5, 5, 5, 5], 0),
            ([10, 20, 30, 40, 50], 47.14045207910317),
            ([1, 2, 3, 4, 5, np.nan], 47.14045207910317),
        ],
    )
    def test_correct_results(self, input_data, expected_output):
        result = coefficient_of_variation(input_data)
        assert result == expected_output

    def test_empty_or_wrong_input(self):
        with pytest.raises(ValueError):
            coefficient_of_variation([])
        with pytest.raises(TypeError):
            coefficient_of_variation([1, 2, "aa"])


class TestComputeStatistics:
    @pytest.mark.parametrize(
        "input_data, expected_output",
        [
            (
                [1, 2, 3, 4, 5],
                pd.Series(
                    {
                        "count": 5,
                        "mean": 3.0,
                        "std": 1.581139,
                        "min": 1.0,
                        "25%": 2.0,
                        "median": 3.0,
                        "75%": 4.0,
                        "max": 5.0,
                        "CV%": 47.140452,
                        "missing": 0,
                        "outliers": 0,
                    }
                ),
            ),
            (
                [5, 5, 5, 5, np.nan],
                pd.Series(
                    {
                        "count": 4,
                        "mean": 5.0,
                        "std": 0.0,
                        "min": 5.0,
                        "25%": 5.0,
                        "median": 5.0,
                        "75%": 5.0,
                        "max": 5.0,
                        "CV%": 0.0,
                        "missing": 1,
                        "outliers": 0,
                    }
                ),
            ),
            (
                [10, 20, 30, 40, 50],
                pd.Series(
                    {
                        "count": 5,
                        "mean": 30.0,
                        "std": 15.811388,
                        "min": 10.0,
                        "25%": 20.0,
                        "median": 30.0,
                        "75%": 40.0,
                        "max": 50.0,
                        "CV%": 47.140452,
                        "missing": 0,
                        "outliers": 0,
                    }
                ),
            ),
            (
                [1, 2, 3, 4, 100],
                pd.Series(
                    {
                        "count": 5,
                        "mean": 22.0,
                        "std": 43.617657,
                        "min": 1.0,
                        "25%": 2.0,
                        "median": 3.0,
                        "75%": 4,
                        "max": 100.0,
                        "CV%": 177.330993,
                        "missing": 0,
                        "outliers": 1,
                    }
                ),
            ),
        ],
    )
    def test_compute_statistics(self, input_data, expected_output):
        result = compute_statistics(input_data, outlier_threshold=5)
        pd.testing.assert_series_equal(result, expected_output)

    def test_input_validation(self):
        # Test with invalid input types
        with pytest.raises(TypeError):
            compute_statistics("invalid_input", outlier_threshold=5)

        with pytest.raises(TypeError):
            compute_statistics({"a": 1, "b": 2, "c": 3}, outlier_threshold=5)

        # Test with empty input
        with pytest.raises(ValueError):
            compute_statistics([], outlier_threshold=5)
        # Test with input containing non-numeric elements
        with pytest.raises(TypeError):
            compute_statistics([1, 2, "a", 4, 5], outlier_threshold=5)


class TestDataFrameBasicStats:
    @pytest.fixture(
        params=(
            (
                create_test_dataframe_with_missing(),
                pd.DataFrame(
                    {
                        "A": {
                            "count": 4.0,
                            "mean": 11.216639586398308,
                            "std": 1.4424337098121411,
                            "min": 9.531693250553328,
                            "25%": 10.627994542155182,
                            "median": 11.144402691111924,
                            "75%": 11.73304773535505,
                            "max": 13.046059712816051,
                            "CV%": 11.136884860659604,
                            "missing": 1.0,
                            "outliers": 0.0,
                        },
                        "B": {
                            "count": 2.0,
                            "mean": 20.10962848647652,
                            "std": 2.1468492237254972,
                            "min": 18.591576842195146,
                            "25%": 19.35060266433583,
                            "median": 20.10962848647652,
                            "75%": 20.86865430861721,
                            "max": 21.627680130757895,
                            "CV%": 7.548879609099919,
                            "missing": 3.0,
                            "outliers": 0.0,
                        },
                        "C": {
                            "count": 5.0,
                            "mean": 26.539693398409987,
                            "std": 3.679348132720293,
                            "min": 22.346879021368807,
                            "25%": 23.10032866994787,
                            "median": 28.137080985718974,
                            "75%": 28.14632922875015,
                            "max": 30.96784908626414,
                            "CV%": 12.39995114358389,
                            "missing": 0.0,
                            "outliers": 0.0,
                        },
                        "D": {
                            "count": 4.0,
                            "mean": 36.78954003312224,
                            "std": 3.6342119804788555,
                            "min": 32.93848149332354,
                            "25%": 34.82953009012634,
                            "median": 36.32422098809454,
                            "75%": 38.28423093109044,
                            "max": 41.57123666297637,
                            "CV%": 8.554931360921774,
                            "missing": 1.0,
                            "outliers": 0.0,
                        },
                    }
                ).transpose(),
                0,
            ),
            (
                create_test_dataframe_with_outliers(),
                pd.DataFrame(
                    {
                        "A": {
                            "count": 5.0,
                            "mean": 10.918005948650173,
                            "std": 1.4164644377375784,
                            "min": 9.531693250553328,
                            "25%": 9.723471397657631,
                            "median": 10.993428306022466,
                            "75%": 11.295377076201385,
                            "max": 13.046059712816051,
                            "CV%": 11.603989905808133,
                            "missing": 0.0,
                            "outliers": 0.0,
                        },
                        "B": {
                            "count": 5.0,
                            "mean": 37.451839921386785,
                            "std": 35.03407354923386,
                            "min": 18.591576842195146,
                            "25%": 21.627680130757895,
                            "median": 22.302304187458727,
                            "75%": 24.737638446522176,
                            "max": 100.0,
                            "CV%": 83.6685942792137,
                            "missing": 0.0,
                            "outliers": 1.0,
                        },
                        "C": {
                            "count": 5.0,
                            "mean": 26.539693398409987,
                            "std": 3.679348132720293,
                            "min": 22.346879021368807,
                            "25%": 23.10032866994787,
                            "median": 28.137080985718974,
                            "75%": 28.14632922875015,
                            "max": 30.96784908626414,
                            "CV%": 12.39995114358389,
                            "missing": 0.0,
                            "outliers": 0.0,
                        },
                        "D": {
                            "count": 5.0,
                            "mean": 19.431632026497795,
                            "std": 38.94085867532299,
                            "min": -50.0,
                            "25%": 32.93848149332354,
                            "median": 35.45987962239394,
                            "75%": 37.188562353795135,
                            "max": 41.57123666297637,
                            "CV%": 179.24260192143672,
                            "missing": 0.0,
                            "outliers": 1.0,
                        },
                    }
                ).transpose(),
                0,
            ),
            (
                create_test_dataframe_with_missing(),
                pd.DataFrame(
                    {
                        "count": {0: 3.0, 1: 1.0, 2: 3.0, 3: 4.0, 4: 4.0},
                        "mean": {
                            0: 25.442773296189248,
                            1: 28.137080985718974,
                            2: 27.944820941813962,
                            3: 22.361098799693487,
                            4: 21.79954588614566,
                        },
                        "std": {
                            0: 13.305193458028285,
                            1: np.nan,
                            2: 15.362647649449363,
                            3: 9.53165795688867,
                            4: 9.59683399943225,
                        },
                        "min": {
                            0: 10.993428306022466,
                            1: 28.137080985718974,
                            2: 11.295377076201385,
                            3: 13.046059712816051,
                            4: 9.531693250553328,
                        },
                        "25%": {
                            0: 19.569878767386307,
                            1: 28.137080985718974,
                            2: 21.13161308123276,
                            3: 17.205197559850372,
                            4: 18.603683410706754,
                        },
                        "median": {
                            0: 28.14632922875015,
                            1: 28.137080985718974,
                            2: 30.96784908626414,
                            3: 20.469227931781976,
                            4: 22.364004400352883,
                        },
                        "75%": {
                            0: 32.66744579127264,
                            1: 28.137080985718974,
                            2: 36.26954287462026,
                            3: 25.62512917162509,
                            4: 25.55986687579179,
                        },
                        "max": {
                            0: 37.188562353795135,
                            1: 28.137080985718974,
                            2: 41.57123666297637,
                            3: 35.45987962239394,
                            4: 32.93848149332354,
                        },
                        "CV%": {
                            0: 42.69835226134397,
                            1: 0.0,
                            2: 44.88684792753065,
                            3: 36.91526076063319,
                            4: 38.125115462577256,
                        },
                        "missing": {0: 1.0, 1: 3.0, 2: 1.0, 3: 0.0, 4: 0.0},
                        "outliers": {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
                    }
                ),
                1,
            ),
        )
    )
    def test_data(self, request):
        return request.param

    def test_dataframe_stats(self, test_data):
        data, expected_output, axis = test_data
        result = compute_dataframe_statistics(data, axis=axis, outlier_threshold=5)
        pd.testing.assert_frame_equal(result, expected_output)

    def test_dataframe_stats_different_outlier_threshold(self, test_data):
        data, expected_output, axis = test_data

        result = compute_dataframe_statistics(data, axis=axis, outlier_threshold=100)
        assert result.iloc[-1, -1] == 0


test_data = pd.read_csv("tests/test_data/data.csv")
test_data = test_data[test_data.columns[5:10]].iloc[10:20]
test_values_series = test_data["212"]


class TestTopCorrelations:
    def test_top_1_correlations(self):
        assert get_top_n_correlations(test_data, n=1)["correlated_ids"].tolist() == [
            "250",
            "273",
            "212",
            "273",
            "254",
        ]
