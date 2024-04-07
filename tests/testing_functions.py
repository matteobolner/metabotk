import pandas as pd
import numpy as np


##Create a test dataframe with outlier values
def create_test_dataframe_with_outliers():
    np.random.seed(42)
    test_data = {
        "A": np.random.normal(
            loc=10, scale=2, size=5
        ),  # Normal distribution without outliers
        "B": np.random.normal(
            loc=20, scale=3, size=5
        ),  # Normal distribution without outliers
        "C": np.random.normal(
            loc=30, scale=4, size=5
        ),  # Normal distribution without outliers
        "D": np.random.normal(
            loc=40, scale=5, size=5
        ),  # Normal distribution without outliers
    }
    test_data["B"][0] = 100  # Outlier in column B
    test_data["D"][1] = -50  # Outlier in column D
    test_dataframe = pd.DataFrame(test_data)
    return test_dataframe


def create_outlier_presence_matrix_from_dataframe():
    test_dataframe = create_test_dataframe_with_outliers()
    outliers_df = pd.DataFrame(
        False, index=test_dataframe.index, columns=test_dataframe.columns
    )
    outliers_df.loc[0, "B"] = True  # Outlier in column B
    outliers_df.loc[1, "D"] = True  # Outlier in column B
    return outliers_df


##Create a test dataframe with missing values
def create_test_dataframe_with_missing():
    np.random.seed(42)
    test_data = {
        "A": np.random.normal(
            loc=10, scale=2, size=5
        ),  # Normal distribution without missings
        "B": np.random.normal(
            loc=20, scale=3, size=5
        ),  # Normal distribution without missings
        "C": np.random.normal(
            loc=30, scale=4, size=5
        ),  # Normal distribution without missings
        "D": np.random.normal(
            loc=40, scale=5, size=5
        ),  # Normal distribution without missings
    }
    test_data["B"][0] = np.nan  # missing in column B
    test_data["B"][1] = np.nan  # missing in column B
    test_data["B"][2] = np.nan  # missing in column B
    test_data["D"][1] = np.nan  # missing in column D
    test_data["A"][1] = np.nan  # missing in column D
    test_data["D"][1] = np.nan  # missing in column D

    test_dataframe = pd.DataFrame(test_data)
    return test_dataframe
