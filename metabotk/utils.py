import pandas as pd
import numpy as np
from pathlib import Path


def validate_dataframe(data_frame):
    """
    Validates that the input is a pandas DataFrame.

    Parameters
    ----------
    data_frame : any
        Input to validate.

    Raises
    ------
    TypeError
        If the input is not a pandas DataFrame.
    """
    if not isinstance(data_frame, pd.DataFrame):
        raise TypeError("Data must be a pandas DataFrame.")


def ensure_numeric_data(data):
    """
    Ensure that the input data is numeric.

    This function checks that the input data is a non-empty NumPy array
    containing only numeric values. If the data is not numeric or empty,
    a TypeError is raised.

    Parameters
    ----------
    data : list, array, or Series
        Input data to validate.

    Returns
    -------
    np.array
        Input data converted to NumPy array.

    Raises
    ------
    ValueError
        If the input data is empty.
    TypeError
        If the input data is not numeric.
    """
    if len(data) == 0:
        raise ValueError("Empty data")
    data = np.array(data)  # convert to np array
    if not np.issubdtype(data.dtype, np.number):
        raise TypeError("Data must contain only numeric values")
    return data


def parse_input(input_data):
    """
    Parse input data as pandas dataframe or as file path to TSV or CSV file

    This function allows users to provide input data as a pandas DataFrame or
    as a file path to a TSV or CSV file. If the input is a DataFrame, it is
    returned as is. If the input is a file path, the function loads the data
    from the file and returns it as a DataFrame.

    Parameters
    ----------
    input_data : pandas.DataFrame or str
        Input data to be parsed.

    Returns
    -------
    pandas.DataFrame
        Input data as a pandas DataFrame.

    Raises
    ------
    TypeError
        If the input is not a pandas DataFrame or a file path.
    """
    if isinstance(input_data, pd.DataFrame):
        data = input_data.reset_index(drop=True)
        return data
    elif isinstance(input_data, str):
        if input_data.endswith((".tsv", ".csv")):
            if input_data.endswith(".tsv"):
                data = pd.read_table(input_data, sep="\t").reset_index(drop=True)
            elif input_data.endswith(".csv"):
                data = pd.read_csv(input_data).reset_index(drop=True)
            return data
        else:
            raise TypeError(
                "Input should be a Pandas DataFrame or a file path to a TSV or CSV file."
            )
    else:
        raise TypeError(
            "Input should be a Pandas DataFrame or a file path to a TSV or CSV file."
        )


def create_directory(directory_path):
    """
    Creates a directory at the given path.

    This function creates a directory at the given path and all parent directories
    if they do not already exist. If the directory already exists, nothing is done.

    Parameters
    ----------
    directory_path : str
        Path of the directory to be created.
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
