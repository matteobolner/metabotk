import pandas as pd
import os
import warnings
from metabotk.utils import parse_input, reset_index_if_not_none


def read_excel(
    file_path: str | os.PathLike[str],
    sample_metadata_sheet: str = "Sample Meta Data",
    chemical_annotation_sheet: str = "Chemical Annotation",
    data_sheet: str = "Data",
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
    data = reset_index_if_not_none(data)
    if sample_id_column not in data.columns:
        raise ValueError(f"No sample ID column '{sample_id_column}' found in data")
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

    sample_metadata = reset_index_if_not_none(sample_metadata)
    # check that sample ID column is found in data
    if sample_id_column in sample_metadata.columns:
        # set metadata and data
        if sample_metadata[sample_id_column].duplicated().any():
            warnings.warn(
                "Warning: there are duplicate values in the chosen sample column.\
                        Consider choosing another column or renaming the duplicated samples"
            )
        # sample_metadata[sample_id_column] = sample_metadata[sample_id_column].astype(
        #    str
        # )
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

    chemical_annotation = reset_index_if_not_none(chemical_annotation)
    # check that metabolite ID column is found in chemical annotation
    if metabolite_id_column in list(chemical_annotation.columns):
        if chemical_annotation[metabolite_id_column].duplicated().any():
            warnings.warn(
                "Warning: there are duplicate values in the chosen metabolite column.\
                        Consider choosing another column or renaming the duplicated metabolites"
            )

        chemical_annotation[metabolite_id_column] = chemical_annotation[
            metabolite_id_column
        ]  # .astype(str)
        chemical_annotation.set_index(metabolite_id_column, inplace=True)
    else:
        raise ValueError("No metabolite ID column found in chemical annotation")
    return chemical_annotation
