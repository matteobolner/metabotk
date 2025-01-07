"""
Module for parsing input data
"""

import pandas as pd


"""
def save_dataset_to_prefix(dataset, prefix: str, extension: str = "tsv"):
    prefix_dict = dataset_from_prefix(prefix, extension)
    dataset.
    table.to_csv()
"""

'''
class MetabolonCDT:
    """
    A class for reading Metabolon Client Data Table files.

    Attributes:
    - data_key_and_explanation: DataFrame containing data key and explanation.
    - sample_metadata: DataFrame containing sample metadata (required).
    - chemical_annotation: DataFrame containing chemical annotation (required).
    - peak_area_data: DataFrame containing peak area data and a column with the sample names. (required)
    - batch_normalized_data: DataFrame containing batch-normalized data and a column with the sample names. (optional)
    - batch_normalized_imputed_data: DataFrame containing batch-norm imputed data and a column with the sample names. (optional)
    - log_transformed_data: DataFrame containing log-transformed data and a column with the sample names.(optional)
    """

    def __init__(self) -> None:
        """
        Initialize the class.
        """
        self.data_key_and_explanation: pd.DataFrame = pd.DataFrame()
        self.sample_metadata: pd.DataFrame = pd.DataFrame()
        self.chemical_annotation: pd.DataFrame = pd.DataFrame()
        self.data: pd.DataFrame = pd.DataFrame()
        self.peak_area_data: pd.DataFrame = pd.DataFrame()
        self.batch_normalized_data: pd.DataFrame = pd.DataFrame()
        self.batch_normalized_imputed_data: pd.DataFrame = pd.DataFrame()
        self.log_transformed_data: pd.DataFrame = pd.DataFrame()
        self.additional_data: pd.DataFrame = pd.DataFrame()

    def import_excel(
        self,
        file_path: str,
        sample_metadata: str = "Sample Meta Data",
        chemical_annotation: str = "Chemical Annotation",
        data: str = "Data",
    ) -> None:
        """
        Read the Metabolon Client Data Table Excel file and assign its sheets to class attributes.

        Args:
            file_path (str): The file path to the Metabolon Excel file.

        Raises:
            ValueError: If any required sheet ('Sample Meta Data', 'Chemical Annotation',
            'Peak Area Data') is missing from the Excel file.
        """

        # Read Excel file
        sheets = pd.read_excel(file_path, sheet_name=None)

        # Check if required sheets are missing
        missing_sheets = [
            sheet_name
            for sheet_name in [
                sample_metadata,
                chemical_annotation,
                data,
            ]
            if sheet_name not in sheets
        ]
        if missing_sheets:
            raise ValueError(
                "The following required sheets are missing: {}".format(missing_sheets)
            )

        # Assign sheets to attributes
        self.data_key_and_explanation = sheets.pop("Data Key & Explanation", None)
        self.sample_metadata = sheets.pop(sample_metadata)
        self.chemical_annotation = sheets.pop(chemical_annotation)
        self.generic_data = sheets.pop(data)
        self.peak_area_data = sheets.pop("Peak Area Data", None)
        self.batch_normalized_data = sheets.pop("Batch-normalized Data", None)
        self.batch_normalized_imputed_data = sheets.pop("Batch-norm Imputed Data", None)
        self.log_transformed_data = sheets.pop("Log Transformed Data", None)
        self.additional_data = sheets

    def import_tables(
        self,
        sample_metadata: pd.DataFrame | str,
        chemical_annotation: pd.DataFrame | str,
        data: pd.DataFrame | str,
    ) -> None:
        """
        Read flat tables for sample metadata, chemical annotation, and metabolite data.

        Args:
            sample_metadata: DataFrame or path of file containing sample metadata (required).
            chemical_annotation: DataFrame or path of file containing chemical annotation (required).
            data: DataFrame or path of file containing metabolite data (required).
        """
        # Read sample metadata
        self.sample_metadata = parse_input(sample_metadata)
        # Read chemical annotation
        self.chemical_annotation = parse_input(chemical_annotation)
        # Read data
        self.data = parse_input(data)
'''
