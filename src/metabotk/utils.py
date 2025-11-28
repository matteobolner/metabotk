import polars as pl
import numpy as np
from pathlib import Path
import os
from typing import List


def create_directory(directory_path: str):
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


def validate_dataframe(data_frame):
    """
    Validates that the input is a polars DataFrame.

    Parameters
    ----------
    data_frame : any
        Input to validate.

    Raises
    ------
    TypeError
        If the input is not a polars DataFrame.
    """
    if not isinstance(data_frame, pl.DataFrame):
        raise TypeError("Data must be a polars DataFrame.")


def check_duplicate_ids(input_data: pl.DataFrame, id_column: str) -> bool:
    if input_data[id_column].is_duplicated().any():
        return True
    else:
        return False


def check_all_ids_present(ids: List, to_check: List):
    if set(ids).issubset(set(to_check)):
        return True
    else:
        return False


def parse_input(input_data: str | os.PathLike[str] | pl.DataFrame) -> pl.DataFrame:
    """
    Parse input data as polars dataframe or as file path to TSV or CSV file

    This function allows users to provide input data as a polars DataFrame or
    as a file path to a TSV or CSV file. If the input is a DataFrame, it is
    returned as is. If the input is a file path, the function loads the data
    from the file and returns it as a DataFrame.

    Parameters
    ----------
    input_data : polars.DataFrame or str
        Input data to be parsed.

    Returns
    -------
    polars.DataFrame
        Input data as a polars DataFrame.

    Raises
    ------
    TypeError
        If the input is not a polars DataFrame or a file path.
    """
    if isinstance(input_data, pl.DataFrame):
        # data = input_data.reset_index()
        return input_data
    elif isinstance(input_data, str):
        if input_data.endswith((".tsv", ".data", ".samples", ".metabolites")):
            data = pl.read_csv(input_data, sep="\t")
            return data
        elif input_data.endswith(".csv"):
            data = pd.read_csv(input_data, sep=",")
            return data
        else:
            raise TypeError(
                "Invalid file extension: input should be a Polars DataFrame or a file path to a TSV or CSV file."
            )
    else:
        raise TypeError(
            "Input should be a Polars DataFrame or a file path to a TSV or CSV file."
        )


def reset_index_if_not_none(df: pd.DataFrame):
    """

    Args:
        df:

    Returns:

    """
    if df.index.name is not None:
        return df.reset_index()
    else:
        return df


def validate_new_data(old, new):
    if old.shape != new.shape:
        raise ValueError("New dataframe must have the same shape")
    if old.index.name != new.index.name:
        raise ValueError("New index name must be the same as the previous one")


def validate_new_metadata(old, new):
    if len(old) != len(new):
        raise ValueError("New dataframe must have the same length")
    if old.index.name != new.index.name:
        raise ValueError("New index name must be the same as the previous one")


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
