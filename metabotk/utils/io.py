import os
import pandas as pd
from pathlib import Path


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


def read_excel(
    file_path: str | os.PathLike[str],
    sample_metadata_sheet: str = "Sample Meta Data",
    chemical_annotation_sheet: str = "Chemical Annotation",
    data_sheet: str = "Batch-normalized Data",
) -> dict[str, pd.DataFrame]:
    sheets = pd.read_excel(file_path, sheet_name=None)
    dataset_dict = {
        "sample_metadata": sheets.pop(sample_metadata_sheet),
        "chemical_annotation": sheets.pop(chemical_annotation_sheet),
        "data": sheets.pop(data_sheet),
    }
    return dataset_dict


def read_tables(
    sample_metadata: str | os.PathLike[str] | pd.DataFrame,
    chemical_annotation: str | os.PathLike[str] | pd.DataFrame,
    data: str | os.PathLike[str] | pd.DataFrame,
):
    """

    Args:
        sample_metadata:
        chemical_annotation:
        data:

    Returns:

    """
    dataset_dict = {
        "sample_metadata": parse_input(sample_metadata),
        "chemical_annotation": parse_input(chemical_annotation),
        "data": parse_input(data),
    }
    return dataset_dict


def dataset_from_prefix(prefix: str):
    """

    Args:
        prefix:
    Returns:

    """
    prefix_dict = {
        "sample_metadata": f"{prefix}.samples",
        "chemical_annotation": f"{prefix}.metabolites",
        "data": f"{prefix}.data",
    }
    return prefix_dict


def read_prefix(prefix: str) -> dict[str, pd.DataFrame]:
    """
    Parse files from prefix
    Args:
        prefix: prefix valid for all three dataset files
    Returns:
        Dict of dataframes
    """
    prefix_dict = dataset_from_prefix(prefix)
    return read_tables(
        sample_metadata=prefix_dict["sample_metadata"],
        chemical_annotation=prefix_dict["chemical_annotation"],
        data=prefix_dict["data"],
    )


class DatasetIO:
    def __init__(self) -> None:
        pass
