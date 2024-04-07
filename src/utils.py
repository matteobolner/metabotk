import pandas as pd
import numpy as np

def validate_dataframe(data_frame):
    """
    Ensure that the input data is a pandas dataframe.

    Parameters:
    - data_frame: input to validate
    Returns:
    - TypeError if input is not a pandas dataframe
    """

    if not isinstance(data_frame, pd.DataFrame):
        raise TypeError("Data must be a pandas DataFrame")

def ensure_numeric_data(data):
    """
    Ensure that the input data is numeric.

    Parameters:
    - data: list, array, or Series containing numerical data

    Returns:
    - np.array: Input data converted to NumPy array
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
    """
    if isinstance(input_data, pd.DataFrame):
        data = input_data.reset_index(drop=True)
        return data
    if isinstance(input_data, str):
        if input_data.endswith(".tsv"):
            data = pd.read_table(input_data, sep="\t").reset_index(drop=True)
        elif input_data.endswith(".csv"):
            data = pd.read_csv(input_data).reset_index(drop=True)
        return data
    raise ValueError(
        "Input should be a Pandas DataFrame or a file path to a TSV or CSV file."
    )


def split_data_from_metadata(input_data, metabolites):
    """
    Split metabolite abundance data from sample metadata
    """
    # get all columns not corresponding to a metabolite name i.e. metadata columns
    metadata_columns = [col for col in input_data.columns if col not in metabolites]
    # get all columns corresponding to a metabolite name
    metabolite_names = [i for i in metabolites if i in input_data.columns]
    # get metadata
    if len(metadata_columns) > 0:
        metadata = input_data[metadata_columns]
    else:
        metadata = None
    # get metabolite abundance data and convert to float
    data = input_data[metabolite_names]
    data = data.astype(float)
    return data, metadata
