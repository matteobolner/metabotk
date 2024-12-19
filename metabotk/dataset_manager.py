from typing import Union, Optional, Dict
import pandas as pd
from metabotk.providers_handler import MetabolonCDT
from metabotk.utils import parse_input
import warnings


class DatasetManager:
    """
    Class for working with metabolomics data.

    This class provides an interface for loading and processing
    metabolomics data from different sources.

    Attributes:
        _data_provider (str): name of the data provider
        parser (object): parser for the data provider
        _sample_id_column (str): name of the sample id column
    """

    def __init__(
        self,
        data_provider: str = "metabolon",
        sample_id_column: str = None,
        metabolite_id_column: str = "CHEM_ID",
    ) -> None:
        """
        Initialize the class.

        Parameters:
            data_provider (str): name of the data provider
            sample_id_column (str): name of the sample id column
            metabolite_id_column (str): name of the metabolite id column
        """
        self._data_provider = data_provider.lower()
        if self._data_provider == "metabolon":
            self.parser = MetabolonCDT()
        else:
            raise NotImplementedError("This data provider is not supported yet")
        self._sample_id_column = sample_id_column
        self.sample_metadata = pd.DataFrame()
        # list of sample names
        self.samples = []
        self._metabolite_id_column = metabolite_id_column
        self.chemical_annotation = pd.DataFrame()
        # list of metabolite IDs
        self.metabolites = []
        # dataframe with sample x metabolite data
        self.data = pd.DataFrame()

    ###
    # Functions to import, setup and write data and metadata
    ###

    def _setup_data(self, chemical_annotation, sample_metadata, data) -> None:
        """
        Setup the class with chemical annotation, sample metadata, and data.

        This function loads the data and sets up the class instance.
        It checks that the sample ID column is found in the data and the
        metabolite ID column is found in the chemical annotation.
        If any of these checks fail, a ValueError is raised.

        Parameters:
            chemical_annotation (DataFrame or str): DataFrame or path of file containing chemical annotation.
            sample_metadata (DataFrame or str): DataFrame or path of file containing sample metadata.
            data (DataFrame or str): DataFrame containing or path of file the main data.

        Raises:
            ValueError: If the sample ID column is not found in the data or the metabolite ID column is not found in chemical annotation.
        """
        try:
            # parse input data
            parsed_chemical_annotation = parse_input(chemical_annotation)
            parsed_sample_metadata = parse_input(sample_metadata)
            parsed_data = parse_input(data)
            if not self._sample_id_column:
                if parsed_data.columns[0] in parsed_sample_metadata.columns:
                    self._sample_id_column = parsed_data.columns[0]
                else:
                    raise ValueError(
                        "No sample ID column found in data with correspondence in sample metadata"
                    )
            # check that sample ID column is found in data
            if (self._sample_id_column in parsed_data.columns) and (
                self._sample_id_column in parsed_sample_metadata.columns
            ):
                # set metadata and data
                self.sample_metadata = parsed_sample_metadata
                if self.sample_metadata is None:
                    raise ValueError("Sample metadata is not properly initialized.")
                if self.sample_metadata[self._sample_id_column].duplicated().any():
                    warnings.warn(
                        "Warning: there are duplicate values in the chosen sample column.\
                        Consider choosing another column or renaming the duplicated samples"
                    )
                self.sample_metadata[self._sample_id_column] = self.sample_metadata[
                    self._sample_id_column
                ].astype(str)
                self.sample_metadata.set_index(self._sample_id_column, inplace=True)
                self.data = parsed_data
                self.data.columns = [str(i) for i in self.data.columns]
                self.data.set_index(self._sample_id_column, inplace=True)
                # Drop samples not in data
                self.sample_metadata = self.sample_metadata.loc[self.data.index]
                self.samples = list(self.sample_metadata.index)
            else:
                raise ValueError("No sample ID column found in data")

            # check that metabolite ID column is found in chemical annotation
            if self._metabolite_id_column in parsed_chemical_annotation.columns:
                self.chemical_annotation = parsed_chemical_annotation
                self.chemical_annotation[self._metabolite_id_column] = (
                    self.chemical_annotation[self._metabolite_id_column].astype(str)
                )
                self.chemical_annotation.set_index(
                    self._metabolite_id_column, inplace=True
                )
                # Cleanup data from metadata
                self._remove_metadata_from_data()
                # Update the chemical annotation data in the class
                self._update_chemical_annotation()

            else:
                raise ValueError("No metabolite ID column found in chemical annotation")
        except ValueError as ve:
            raise ValueError(f"Error setting up data: {ve}")

    def import_excel(
        self,
        file_path: str,
        sample_metadata: str = "sample_metadata",
        chemical_annotation: str = "chemical_annotation",
        data_sheet: str = "data",
    ) -> None:
        """
        Import data from an Excel file and set up the class.

        Parameters
        ----------
        file_path : str
            Path to the Excel file.
        data_sheet : str
            Name of the sheet containing the main data.

        Raises
        ------
        FileNotFoundError
            If the Excel file is not found.
        AttributeError
            If the data sheet is not found in the Excel file.
        ValueError
            If there is an error importing the data.
        """
        try:
            self.parser.import_excel(
                file_path, sample_metadata, chemical_annotation, data_sheet
            )
            self._setup_data(
                self.parser.chemical_annotation,
                self.parser.sample_metadata,
                self.parser.generic_data,
            )
            self._remove_metadata_from_data()
        except FileNotFoundError as fnfe:
            raise FileNotFoundError(f"File '{file_path}' not found.") from fnfe
        except AttributeError as ae:
            raise AttributeError(
                f"Data sheet '{data_sheet}' not found in the Excel file."
            ) from ae
        except ValueError as ve:
            raise ValueError(f"Error importing data: {ve}") from ve

    def import_tables(
        self,
        data: Union[pd.DataFrame, str],
        chemical_annotation: Union[pd.DataFrame, str] = "config/metabolites.tsv",
        sample_metadata: Union[pd.DataFrame, str] = "config/samples.tsv",
    ) -> None:
        """
        Import data from tables and set up the class.

        Parameters:
            data: DataFrame or path of file containing the main data.
            chemical_annotation: DataFrame or path to the file containing chemical annotation.
            sample_metadata: DataFrame or path to the file containing sample metadata.

        """
        try:
            self.parser.import_tables(
                sample_metadata=sample_metadata,
                chemical_annotation=chemical_annotation,
                generic_data=data,
            )
            self._setup_data(
                self.parser.chemical_annotation,
                self.parser.sample_metadata,
                self.parser.generic_data,
            )
            self._remove_metadata_from_data()
        except ValueError as ve:
            raise ValueError("Error importing data: {}".format(ve)) from ve

    def merge_sample_metadata_data(self) -> pd.DataFrame:
        """
        Merge sample metadata and metabolite abundance data into a single DataFrame.

        This method merges the sample metadata and the metabolite abundance data
        by matching the sample IDs in both dataframes. The resulting DataFrame
        contains all the columns from both the sample metadata and the data.

        The sample IDs in the data are used as the index for the merge, and the
        resulting dataframe will have the same index as the data.

        Returns:
            DataFrame: Merged DataFrame containing sample metadata and data.

        """
        # Merge sample metadata and data by matching sample IDs
        merged = self.sample_metadata.merge(
            self.data, left_index=True, right_index=True, how="inner"
        )
        return merged

    def save_merged(self, data_path, chemical_annotation_path=None):
        """
        Save the merged sample data and metabolite abundance data to TSV files.

        This function merges the sample metadata and metabolite abundance data
        and saves the resulting DataFrame to a TSV file. The chemical
        annotation is saved optionally.

        Parameters:
        data_path (str): Path to save the merged sample data.
        chemical_annotation_path (str, optional): Path to save the chemical annotation data. Default is None.

        Raises:
        ValueError: If attempting to save an empty DataFrame.
        """
        merged = self.merge_sample_metadata_data()
        if len(merged) == 0:
            raise ValueError("Trying to save an empty dataframe")
        merged.to_csv(data_path, sep="\t")
        if chemical_annotation_path:
            self.chemical_annotation.to_csv(chemical_annotation_path, sep="\t")

    def save_tables(
        self,
        data_path: Optional[str] = None,
        chemical_annotation_path: Optional[str] = None,
        sample_metadata_path: Optional[str] = None,
    ) -> None:
        """
        Save individual parts of the dataset to TSV files.

        This function saves the individual parts of the dataset to TSV files. The
        parts that can be saved are:

        * `data`: The metabolite quantification data.
        * `chemical_annotation`: The chemical annotation data.
        * `sample_metadata`: The sample metadata.

        All parameters are optional, and the function will only save the parts
        for which a path was provided.

        Parameters:
            data_path (str, optional): Path to save the data. Default is None.
            chemical_annotation_path (str, optional): Path to save the chemical
                annotation data. Default is None.
            sample_metadata_path (str, optional): Path to save the sample metadata.
                Default is None.

        Raises:
            ValueError: If attempting to save an empty DataFrame.
        """
        if len(self.data) == 0:
            raise ValueError("Trying to save an empty dataframe")
        if data_path:
            self.data.to_csv(data_path, sep="\t")
        if chemical_annotation_path:
            self.chemical_annotation.to_csv(chemical_annotation_path, sep="\t")
        if sample_metadata_path:
            self.sample_metadata.to_csv(sample_metadata_path, sep="\t")

    def save_excel(self, file_path, data_sheet="data"):
        """
        Save the dataset to an Excel file.

        This function saves the dataset to an Excel file. The data, chemical
        annotation, and sample metadata are saved to separate sheets in the
        Excel file. The name of the sheet containing the data is specified by
        the `data_name` parameter.

        Parameters:
            file_path (str): Path to save the Excel file.
            data_name (str): Name of the sheet containing the data. Default is
                "data".

        Returns:
            None
        """
        with pd.ExcelWriter(file_path) as writer:
            self.chemical_annotation.to_excel(writer, sheet_name="chemical_annotation")
            self.sample_metadata.to_excel(writer, sheet_name="sample_metadata")
            self.data.to_excel(writer, sheet_name=data_sheet)

    def add_to_excel(self, file_path, new_sheet, new_sheet_name):
        """
        Add a new sheet to an Excel file.
        This function adds a new sheet to an Excel file.
        The new sheet is specified by the `new_sheet` parameter, and the name of
        the new sheet is specified by the `new_sheet_name` parameter.

        Parameters:
            file_path (str): Path of the Excel file to add the new sheet to.
            new_sheet (DataFrame): DataFrame to add as a new sheet.
            new_sheet_name (str): Name of the new sheet.

        Returns:
            None
        """
        with pd.ExcelWriter(file_path, mode="a") as writer:
            new_sheet.to_excel(writer, sheet_name=new_sheet_name)

    ###
    # Utility functions to manipulate the class attributes
    ###

    def replace_column_names(self, new_column: str) -> None:
        """
        Replace data column names with names from a column of the metabolite metadata.

        Replaces the names of the columns in the data with the names from the specified
        column of the metabolite metadata. The metabolite metadata is expected to
        have a column with the specified name. Additionally, this function checks
        that the chemical annotation is complete for all features in the dataset.

        Parameters:
            new_column (str): Name of the column from metabolite metadata to use for renaming.

        Raises:
            ValueError: If the specified column does not exist in the metabolite metadata or if
                chemical annotation is missing for some features.
        """
        # Check that the column exists in the metabolite metadata
        if new_column not in self.chemical_annotation.columns:
            raise ValueError(f"No column named {new_column} in the metabolite metadata")

        # Check that all features have annotation
        not_annotated = list(
            set(self.data.columns).difference(set(self.chemical_annotation.index))
        )
        if len(not_annotated) > 0:
            raise ValueError(f"Missing chemical annotation for {not_annotated}")

        # Create dictionary for renaming
        renaming_dict = {
            old: new
            for old, new in zip(
                self.chemical_annotation.index, self.chemical_annotation[new_column]
            )
        }

        # Perform the renaming
        self.data.columns = [renaming_dict[old] for old in self.data.columns]

        # Update the name of the column used for feature identification in the data
        self._metabolite_id_column = new_column

        # Reset the index of the chemical annotation to match the new column name and update
        self.chemical_annotation = self.chemical_annotation.reset_index().set_index(
            new_column
        )

        # Update the chemical annotation data in the class
        self._update_chemical_annotation()

    def _update_chemical_annotation(self):
        """
        Update the chemical annotation based on the current data columns.

        This function ensures that the chemical annotation DataFrame only contains
        the columns present in the data, and update the metabolites attribute with the
        new list of metabolites.
        """
        self.chemical_annotation = self.chemical_annotation.loc[list(self.data.columns)]
        self.metabolites = list(self.chemical_annotation.index)

    def _update_sample_metadata(self):
        """
        This function updates the sample metadata based on the current data index.

        It ensures that the sample metadata DataFrame only contains
        the rows present in the data, and updates the `samples` attribute with the
        new list of samples.
        """
        # Update the sample metadata DataFrame to only contain the rows present in the
        # data
        self.sample_metadata = self.sample_metadata.loc[self.data.index]

        # Update the samples attribute with the new list of samples
        self.samples = list(self.sample_metadata.index)

    def _remove_metadata_from_data(self):
        """
        Remove metadata columns from the data.

        This function removes the metadata columns from the data by using the columns
        present in the chemical annotation DataFrame.

        Raises:
            ValueError: If there is an error removing the metadata from the data.
        """
        metabolites_in_data = [
            i for i in self.chemical_annotation.index if i in self.data.columns
        ]
        try:
            self.data = self.data[metabolites_in_data]
        except ValueError as ve:
            raise ValueError("Error removing metadata from data: {}".format(ve))

    def _split_by_sample_column(self, column: list) -> Dict[str, "DatasetManager"]:
        """
        Split the dataset (data and sample metadata) in multiple independent DataClass instances
        based on the values of one or more sample metadata columns.

        This function splits the dataset into multiple independent DataClass instances, each
        containing a subset of the data based on the values of a sample metadata column. The
        function returns a dictionary containing the split data, where the dictionary keys are
        the unique values of the sample metadata column and the values are the DataClass instances
        containing the split data.

        Args:
            column: The name of the column in the sample metadata DataFrame to use for splitting.

        Returns:
            A dictionary containing the split data, where the dictionary keys are the unique
            values of the sample metadata column and the values are the DataClass instances
            containing the split data.
        """
        split_data: Dict[str, DatasetManager] = {}
        for name, group in self.sample_metadata.groupby(by=column):
            tempdata = self.data.loc[group.index]
            tempclass = DatasetManager(
                data_provider=self._data_provider,
                sample_id_column=self._sample_id_column,
                metabolite_id_column=self._metabolite_id_column,
            )
            tempclass.import_tables(
                data=tempdata.reset_index(),
                chemical_annotation=self.chemical_annotation.reset_index(),
                sample_metadata=group.reset_index(),
            )
            tempclass._update_chemical_annotation()
            tempclass._update_sample_metadata()
            tempclass._remove_metadata_from_data()
            split_data[name] = tempclass
        return split_data

    def _split_by_metabolite_column(self, column: str) -> Dict[str, "DatasetManager"]:
        """
        Split the data in multiple independent DataClass instances
        based on the values of a metabolite metadata column

        Parameters:
        column (str): Name of the column in the metabolite metadata table to use for splitting

        Returns:
        Dict[str, DatasetManager]: dictionary where keys are the unique values present in the column and values are the corresponding DataClass instances
        """
        split_data: Dict[str, "DatasetManager"] = {}
        for name, group in self.chemical_annotation.groupby(by=column):
            tempdata = self.data[list(group.index)]
            tempclass = DatasetManager(
                data_provider=self._data_provider,
                sample_id_column=self._sample_id_column,
                metabolite_id_column=self._metabolite_id_column,
            )
            tempclass.import_tables(
                data=tempdata.reset_index(),
                chemical_annotation=group.reset_index(),
                sample_metadata=self.sample_metadata.reset_index(),
            )
            tempclass._update_chemical_annotation()
            split_data[name] = tempclass
        return split_data

    def drop_samples(self, samples_to_drop, inplace=True):
        """
        Drop specified samples from the dataset.

        Parameters
        ----------
        samples_to_drop : list
            List of sample IDs to drop.
        inplace : bool, optional
            If True, drop the samples from the existing data and metadata tables, by default True

        Returns
        -------
        pandas.DataFrame or None
            If `inplace` is False, the resulting data after dropping the samples, otherwise None
        """
        if not isinstance(samples_to_drop, list):
            samples_to_drop = [samples_to_drop]
        remaining = self.data.drop(index=[str(i) for i in samples_to_drop])
        if inplace:
            self.data = remaining
            self._update_sample_metadata()
            return None
        else:
            return remaining

    def drop_metabolites(self, metabolites_to_drop, inplace=True):
        """
        Drop specified metabolites from the dataset.

        Parameters
        ----------
        metabolites_to_drop : list
            List of metabolite IDs to drop.
        inplace : bool, optional
            If True, drop the metabolites from the existing data and chemical annotation tables, by default True

        Returns
        -------
        pandas.DataFrame or None
            If `inplace` is False, the resulting data after dropping the metabolites, otherwise None
        """
        if not isinstance(metabolites_to_drop, list):
            metabolites_to_drop = [metabolites_to_drop]
        remaining = self.data.drop(columns=[str(i) for i in metabolites_to_drop])
        if inplace:
            self.data = remaining
            self._update_chemical_annotation()
            return None
        else:
            return remaining

    def drop_xenobiotic_metabolites(self, inplace=True):
        """
        Drop metabolites of xenobiotic origin from the dataset.

        Xenobiotics are metabolites that are not found in the human body and are
        considered as foreign substances.

        Parameters
        ----------
        inplace : bool, optional
            If True, drop the metabolites from the existing data and chemical annotation tables, by default True

        Returns
        -------
        pandas.DataFrame or None
            If `inplace` is False, the resulting data after dropping the metabolites, otherwise None
        """
        xenobiotic_metabolites = list(
            self.chemical_annotation[
                self.chemical_annotation["SUPER_PATHWAY"].str.lower() == "xenobiotics"
            ].index
        )
        if inplace:
            self.drop_metabolites(xenobiotic_metabolites, inplace=True)
            return None
        else:
            return self.drop_metabolites(xenobiotic_metabolites, inplace=False)

    def extract_metabolites(self, metabolites_to_extract):
        """
        Extract data for specified metabolites.

        This function extracts the abundance data for the specified metabolites
        and merges the resulting data with the sample metadata.

        Parameters
        ----------
        metabolites_to_extract : str or list
            Name(s) of metabolite(s) to extract.

        Returns
        -------
        pandas.DataFrame
            Extracted data for the specified metabolites merged with sample metadata
        """
        if not isinstance(metabolites_to_extract, list):
            metabolites_to_extract = [metabolites_to_extract]
        return self.sample_metadata.merge(
            self.data[[str(i) for i in metabolites_to_extract]],
            left_index=True,
            right_index=True,
        )

    def extract_samples(self, samples_to_extract):
        """
        Extract data for specified samples.

        This function extracts the sample metadata and abundance data
        for the specified samples.

        Parameters
        ----------
        samples_to_extract : str or list
            ID(s) of sample(s) to extract.

        Returns
        -------
        pandas.DataFrame
            Extracted sample metadata and abundance data for the specified samples.
        """
        if not isinstance(samples_to_extract, list):
            samples_to_extract = [samples_to_extract]
        return self.sample_metadata.loc[samples_to_extract].merge(
            self.data,
            left_index=True,
            right_index=True,
            how="left",
        )

    def extract_chemical_annotations(self, metabolites_to_extract):
        """
        Extract chemical annotations for the specified metabolites.

        This method extracts the chemical annotations for the specified metabolites.

        Parameters
        ----------
        metabolites_to_extract : str or list
            Name(s) of metabolite(s) to extract annotations for.

        Returns
        -------
        pandas.DataFrame
            Extracted chemical annotations for the specified metabolites.
        """
        if not isinstance(metabolites_to_extract, list):
            metabolites_to_extract = [metabolites_to_extract]
        # convert to string to match the CHEM_ID column in chemical_annotation
        return self.chemical_annotation.loc[[str(i) for i in metabolites_to_extract]]

    def sort_samples(self, by, ascending=True):
        """
        Sort samples in the dataset.

        Parameters
        ----------
        by : str
            Column name to sort by.
        ascending : bool, optional
            If True, sort in ascending order, by default True

        Returns
        -------
        pandas.DataFrame
            Sorted dataset
        """
        self.sample_metadata = self.sample_metadata.sort_values(
            by=by, ascending=ascending
        )
        self.data = self.data.loc[self.sample_metadata.index]
        self.samples = self.sample_metadata.index

    def _subset_samples(self, samples_to_extract):
        """
        Extract a subset of the dataset containing only the specified samples.

        Parameters
        ----------
        samples_to_extract : str or list
            ID(s) of sample(s) to extract.

        Returns
        -------
        MetaboTK object containing the subset of the dataset.
        """
        temp_instance = DatasetManager(
            sample_id_column=self._sample_id_column,
            data_provider=self._data_provider,
            metabolite_id_column=self._metabolite_id_column,
        )
        temp_instance.import_tables(
            data=self.data.loc[samples_to_extract].reset_index(),
            sample_metadata=self.sample_metadata.loc[samples_to_extract].reset_index(),
            chemical_annotation=self.chemical_annotation.reset_index(),
        )
        return temp_instance
