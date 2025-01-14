import pandas as pd
from metabotk.parse_and_setup import (
    read_excel,
    read_prefix,
    dataset_from_prefix,
    read_tables,
)

"""
Setup dataset from file(s)
"""


class DatasetIO:
    def __init__(self, dataset):
        self.dataset = dataset

    def from_excel(
        self,
        file_path: str,
        sample_metadata_sheet: str = "Sample Meta Data",
        chemical_annotation_sheet: str = "Chemical Annotation",
        data_sheet: str = "Data",
        sample_id_column: str = "sample",
        metabolite_id_column: str = "CHEM_ID",
    ):
        parsed = read_excel(
            file_path, sample_metadata_sheet, chemical_annotation_sheet, data_sheet
        )
        return self.dataset._setup(
            data=parsed["data"],
            sample_metadata=parsed["sample_metadata"],
            chemical_annotation=parsed["chemical_annotation"],
            sample_id_column=sample_id_column,
            metabolite_id_column=metabolite_id_column,
        )

    def from_tables(
        self,
        sample_metadata,
        chemical_annotation,
        data,
        sample_id_column: str = "sample",
        metabolite_id_column: str = "CHEM_ID",
    ):
        parsed = read_tables(sample_metadata, chemical_annotation, data)
        return self.dataset._setup(
            data=parsed["data"],
            sample_metadata=parsed["sample_metadata"],
            chemical_annotation=parsed["chemical_annotation"],
            sample_id_column=sample_id_column,
            metabolite_id_column=metabolite_id_column,
        )

    def from_prefix(
        self,
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
        return self.dataset._setup(
            data=parsed["data"],
            sample_metadata=parsed["sample_metadata"],
            chemical_annotation=parsed["chemical_annotation"],
            sample_id_column=sample_id_column,
            metabolite_id_column=metabolite_id_column,
        )

    """
    Save dataset to file(s)
    """

    def save_prefix(self, prefix: str):
        """

        Args:
            prefix:
        """
        prefix_dict = dataset_from_prefix(prefix)
        self.dataset.data.to_csv(prefix_dict["data"], sep="\t", index=True)
        self.dataset.sample_metadata.to_csv(
            prefix_dict["sample_metadata"], sep="\t", index=True
        )
        self.dataset.chemical_annotation.to_csv(
            prefix_dict["chemical_annotation"], sep="\t", index=True
        )
        print(f"Saved to {prefix}")

    def save_excel(self, file_path, data_sheet="Data"):
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
            self.dataset.chemical_annotation.to_excel(
                writer, sheet_name="Chemical Annotation"
            )
            self.dataset.sample_metadata.to_excel(writer, sheet_name="Sample Meta Data")
            self.dataset.data.to_excel(writer, sheet_name=data_sheet)
