import os
import pandas as pd
from pathlib import Path


def parse_input(input_data: str | os.PathLike[str] | pd.DataFrame):
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
        data = input_data.reset_index()
        return data
    elif isinstance(input_data, str):
        if input_data.endswith((".tsv", ".csv")):
            if input_data.endswith(".tsv"):
                data = pd.read_table(input_data, sep="\t")
            elif input_data.endswith(".csv"):
                data = pd.read_csv(input_data)
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
