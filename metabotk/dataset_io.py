import pandas as pd
from metabotk.metabolomic_dataset import MetaboTK
from metabotk.parse_and_setup import read_excel, read_prefix, dataset_from_prefix

"""
Setup dataset from file(s)
"""


def from_excel(
    file_path: str,
    sample_metadata_sheet: str = "Sample Meta Data",
    chemical_annotation_sheet: str = "Chemical Annotation",
    data_sheet: str = "Batch-normalized Data",
    sample_id_column: str = "sample",
    metabolite_id_column: str = "CHEM_ID",
):
    parsed = read_excel(
        file_path, sample_metadata_sheet, chemical_annotation_sheet, data_sheet
    )
    return MetaboTK._setup(
        data=parsed["data"],
        sample_metadata=parsed["sample_metadata"],
        chemical_annotation=parsed["chemical_annotation"],
        sample_id_column=sample_id_column,
        metabolite_id_column=metabolite_id_column,
    )


def from_prefix(
    prefix: str,
    sample_id_column: str = "sample",
    metabolite_id_column: str = "CHEM_ID",
):
    """

    Args:
        prefix:
        sample_id_column:
        metabolite_id_column:

    Returns:

    """
    parsed = read_prefix(prefix)
    return MetaboTK._setup(
        data=parsed["data"],
        sample_metadata=parsed["sample_metadata"],
        chemical_annotation=parsed["chemical_annotation"],
        sample_id_column=sample_id_column,
        metabolite_id_column=metabolite_id_column,
    )


"""
Save dataset to file(s)
"""


def save_prefix(dataset: MetaboTK, prefix: str):
    """

    Args:
        prefix:
    """
    prefix_dict = dataset_from_prefix(prefix)
    dataset.data.to_csv(prefix_dict["data"], sep="\t", index=True)
    dataset.sample_metadata.to_csv(prefix_dict["sample_metadata"], sep="\t", index=True)
    dataset.chemical_annotation.to_csv(
        prefix_dict["chemical_annotation"], sep="\t", index=True
    )
    print(f"Saved to {prefix}")


def save_excel(dataset: MetaboTK, file_path, data_sheet="data"):
    """
    Save the dataset to an Excel file.

    This function saves the dataset to an Excel file. The data, chemical
    annotation, and sample metadata are saved to separate sheets in the
    Excel file. The name of the sheet containing the data is specified by
    the `data_name` parameter.

    Args:
        file_path (str): Path to save the Excel file.
        data_name (str): Name of the sheet containing the data. Default is
            "data".

    """
    with pd.ExcelWriter(file_path) as writer:
        dataset.chemical_annotation.to_excel(writer, sheet_name="chemical_annotation")
        dataset.sample_metadata.to_excel(writer, sheet_name="sample_metadata")
        dataset.data.to_excel(writer, sheet_name=data_sheet)
