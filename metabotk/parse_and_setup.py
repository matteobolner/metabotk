import pandas as pd
import os
import warnings


def parse_input(input_data: str | os.PathLike[str] | pd.DataFrame) -> pd.DataFrame:
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
        if input_data.endswith(".tsv"):
            data = pd.read_table(input_data, sep="\t")
            return data
        elif input_data.endswith(".csv"):
            data = pd.read_csv(input_data)
            return data
        else:
            raise TypeError(
                "Invalid file extension: input should be a Pandas DataFrame or a file path to a TSV or CSV file."
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
) -> dict[str, pd.DataFrame]:
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


def dataset_from_prefix(prefix: str) -> dict[str, str]:
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


"""
Functions to setup dataset files for the main class 
"""


def setup_data(data: pd.DataFrame, sample_id_column: str):
    """

    Args:
        data:
        sample_id_column:

    Returns:

    """
    data.columns = [str(i) for i in data.columns]
    data.set_index(sample_id_column, inplace=True)
    return data


def setup_sample_metadata(sample_metadata: pd.DataFrame, sample_id_column: str):
    """
    Args:
        sample_metadata:
        sample_id_column:
        data:

    Returns:


    Raises:
        ValueError:
    """
    # check that sample ID column is found in data
    if sample_id_column in sample_metadata.columns:
        # set metadata and data
        if len(sample_metadata) == 0:
            raise ValueError("Sample metadata is empty or not properly initialized.")
        if sample_metadata[sample_id_column].duplicated().any():
            warnings.warn(
                "Warning: there are duplicate values in the chosen sample column.\
                        Consider choosing another column or renaming the duplicated samples"
            )
        sample_metadata[sample_id_column] = sample_metadata[sample_id_column].astype(
            str
        )
        sample_metadata.set_index(sample_id_column, inplace=True)
    else:
        raise ValueError(f"No sample ID column '{sample_id_column}' found in data")
    return sample_metadata


def setup_chemical_annotation(
    chemical_annotation: pd.DataFrame, metabolite_id_column: str
):
    """

    Args:
        chemical_annotation:
        metabolite_id_column:

    Returns:


    Raises:
        ValueError:
    """
    # check that metabolite ID column is found in chemical annotation
    if metabolite_id_column in chemical_annotation.columns:
        chemical_annotation[metabolite_id_column] = chemical_annotation[
            metabolite_id_column
        ].astype(str)
        chemical_annotation.set_index(metabolite_id_column, inplace=True)
    else:
        raise ValueError("No metabolite ID column found in chemical annotation")
    return chemical_annotation
