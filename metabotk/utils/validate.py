import pandas as pd
import numpy as np


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


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
