import pandas as pd
from src.reader import MetabolonCDT
from src.utils import parse_input

class DatasetManager:
    """
    Class for working with metabolomics data
    """

    def __init__(self, data_provider='metabolon', sample_id_column='PARENT_SAMPLE_NAME', metabolite_id_column='CHEM_ID') -> None:
        """
        Initialize the class.
        """
        self._data_provider=data_provider
        if self._data_provider.lower()=='metabolon':
            self.parser=MetabolonCDT()
        else:
            raise NotImplementedError('This data provider is not supported yet')
        self._sample_id_column=sample_id_column
        self.sample_metadata=pd.DataFrame()
        self.samples=[]
        self._metabolite_id_column=metabolite_id_column
        self.chemical_annotation=pd.DataFrame()
        self.metabolites=[]
        self.data=pd.DataFrame()

    ###
    #Functions to import, setup and write data and metadata
    ###

    def _setup_data(self, chemical_annotation, sample_metadata, data) -> None:
        """
        Setup the class with chemical annotation, sample metadata, and data.

        Parameters:
        chemical_annotation (DataFrame): DataFrame or path of file containing chemical annotation.
        sample_metadata (DataFrame): DataFrame or path of file containing sample metadata.
        data (DataFrame): DataFrame containing or path of file the main data.

        Raises:
        ValueError: If the sample ID column is not found in the data or the metabolite ID column is not found in chemical annotation.
        """
        try:

            parsed_chemical_annotation=parse_input(chemical_annotation)
            parsed_sample_metadata=parse_input(sample_metadata)
            parsed_data=parse_input(data)
            if (self._sample_id_column in parsed_data.columns) and (self._sample_id_column in parsed_sample_metadata.columns):
                self.sample_metadata=parsed_sample_metadata
                if self.sample_metadata is None:
                    raise ValueError("Sample metadata is not properly initialized.")
                self.sample_metadata[self._sample_id_column]=self.sample_metadata[self._sample_id_column].astype(str)
                self.sample_metadata.set_index(self._sample_id_column, inplace=True)

                self.data=parsed_data
                self.data.columns=[str(i) for i in self.data.columns]
                self.data.set_index(self._sample_id_column, inplace=True)
                self.samples=list(self.sample_metadata.index)
            else:
                raise ValueError("No sample ID column found in data")
            if self._metabolite_id_column in parsed_chemical_annotation.columns:
                self.chemical_annotation=parsed_chemical_annotation
                self.chemical_annotation[self._metabolite_id_column]=self.chemical_annotation[self._metabolite_id_column].astype(str)
                self.chemical_annotation.set_index(self._metabolite_id_column, inplace=True)
                self.metabolites=list(self.chemical_annotation.index)
            else:
                raise ValueError("No metabolite ID column found in chemical annotation")
        except ValueError as ve:
            raise ValueError(f"Error setting up data: {ve}")

    def import_excel(self, file_path, data_sheet) -> None:
        """
        Import data from an Excel file and set up the class.

        Parameters:
        file_path (str): Path to the Excel file.
        data_sheet (str): Name of the sheet containing the main data.

        """
        try:
            self.parser.import_excel(file_path)
            data=getattr(self.parser, data_sheet)
            self._setup_data(self.parser.chemical_annotation, self.parser.sample_metadata, data)
            self._remove_metadata_from_data()
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{file_path}' not found.")
        except AttributeError:
            raise AttributeError(f"Data sheet '{data_sheet}' not found in the Excel file.")
        except ValueError as ve:
            raise ValueError(f"Error importing data: {ve}")

    def import_tables(self, data, chemical_annotation='config/metabolites.tsv', sample_metadata='config/samples.tsv') -> None:
        """
        Import data from tables and set up the class.

        Parameters:
        data (DataFrame): DataFrame or path of file containing the main data.
        chemical_annotation (str): DataFrame or path to the file containing chemical annotation.
        sample_metadata (str): DataFrame or path to the file containing sample metadata.

        """
        try:
            self.parser.import_tables(sample_metadata=sample_metadata, chemical_annotation=chemical_annotation, generic_data=data)
            self._setup_data(self.parser.chemical_annotation, self.parser.sample_metadata, self.parser.generic_data)
            self._remove_metadata_from_data()
        except ValueError as ve:
            raise ValueError(f"Error importing data: {ve}")

    def merge_sample_metadata_data(self)-> pd.DataFrame:
        """
        Merge sample metadata and data into a single DataFrame.

        Returns:
        DataFrame: Merged DataFrame containing sample metadata and data.
        """
        merged=self.sample_metadata.merge(self.data, left_index=True, right_index=True)
        return merged

    def save_merged(self, data_path, chemical_annotation_path=None):
        """
        Save the merged sample data and metabolite abundance data to TSV files.
        Chemical annotation is saved optionally.

        Parameters:
        data_path (str): Path to save the merged sample data.
        chemical_annotation_path (str, optional): Path to save the chemical annotation data. Default is None.

        Raises:
        ValueError: If attempting to save an empty DataFrame.
        """
        merged = self.merge_sample_metadata_data()
        if len(merged)==0:
            raise ValueError("Trying to save an empty dataframe")
        merged.to_csv(data_path, sep="\t")
        if chemical_annotation_path:
            self.chemical_annotation.to_csv(chemical_annotation_path, sep='\t')

    def save(self, data_path=None, chemical_annotation_path=None, sample_metadata_path=None):
        """
        Save individual parts of the dataset to TSV files.

        Parameters:
        data_path (str, optional): Path to save the data. Default is None.
        chemical_annotation_path (str, optional): Path to save the chemical annotation data. Default is None.
        sample_metadata_path (str, optional): Path to save the sample metadata. Default is None.

        Raises:
        ValueError: If attempting to save an empty DataFrame.
        """
        if len(self.data)==0:
            raise ValueError("Trying to save an empty dataframe")
        if data_path:
            self.data.to_csv(data_path, sep='\t')
        if chemical_annotation_path:
            self.chemical_annotation.to_csv(chemical_annotation_path, sep='\t')
        if sample_metadata_path:
            self.sample_metadata_path.to_csv(sample_metadata_path, sep='\t')

    ###
    #Utility functions to manipulate the class attributes
    ###

    def replace_column_names(self, new_column) -> None:
        """
        Replace data column names with names from a column of the metabolite metadata.

        Parameters:
        new_column (str): Name of the column from metabolite metadata to use for renaming.

        Raises:
        ValueError: If the specified column does not exist in the metabolite metadata or if chemical annotation is missing for some features.
        """
        if new_column not in self.chemical_annotation.columns:
            raise ValueError(f"No column named {new_column} in the metabolite metadata")
        not_annotated=list(set(self.data.columns).difference(set(self.chemical_annotation.index)))
        if len(not_annotated)>0:
            raise ValueError(f"Missing chemical annotation for {not_annotated}")
        renaming_dict={old:new for old,new in zip(self.chemical_annotation.index,self.chemical_annotation[new_column])}
        self.data.columns=[renaming_dict[old] for old in self.data.columns]
        self._metabolite_id_column=new_column
        self.chemical_annotation=self.chemical_annotation.reset_index().set_index(new_column)
        self._update_chemical_annotation()

    def _update_chemical_annotation(self):
        """
        Update chemical annotation based on the current data columns.
        """
        self.chemical_annotation=self.chemical_annotation.loc[list(self.data.columns)]
        self.metabolites=list(self.chemical_annotation.index)

    def _update_sample_metadata(self):
        """
        Update sample metadata based on the current data index.
        """
        self.sample_metadata=self.sample_metadata.loc[self.data.index]
        self.samples=list(self.sample_metadata.index)

    def _remove_metadata_from_data(self):
        """
        Remove metadata columns from the data.
        """
        try:
            self.data=self.data[list(self.chemical_annotation.index)]
        except ValueError as ve:
            raise ValueError(f"Error removing metadata from data: {ve}")

    def split_by_sample_column(self, column):
        """
        Split the dataset (data and sample metadata) in multiple independent DataClass instances
        based on the values of a sample metadata column
        """
        split_data = {}
        for name, group in self.sample_metadata.groupby(by=column):
            tempdata=self.data.loc[group.index]
            tempclass=MetaboTK(data_provider=self._data_provider, sample_id_column=self._sample_id_column, metabolite_id_column=self._metabolite_id_column)
            tempclass.import_tables(data=tempdata.reset_index(), chemical_annotation=self.chemical_annotation.reset_index(), sample_metadata=group.reset_index())
            tempclass._update_chemical_annotation()
            tempclass._update_sample_metadata()
            tempclass._remove_metadata_from_data()
            split_data[name]=tempclass
        return split_data

    def split_by_metabolite_column(self, column):
        """
        Split the data in multiple independent DataClass instances
        based on the values of a metabolite metadata column
        """
        split_data = {}
        for name, group in self.chemical_annotation.groupby(by=column):
            tempdata=self.data[list(group.index)]
            tempclass=MetaboTK(data_provider=self._data_provider, sample_id_column=self._sample_id_column, metabolite_id_column=self._metabolite_id_column)
            tempclass.import_tables(data=tempdata.reset_index(), chemical_annotation=group.reset_index(), sample_metadata=self.sample_metadata.reset_index())
            tempclass._update_chemical_annotation()
            split_data[name]=tempclass
        return split_data

    def drop_samples(self, samples_to_drop, inplace=True):
        """
        Drop specified samples from the dataset.

        Parameters:
        samples_to_drop (list): List of sample IDs to drop.
        """
        if not isinstance(samples_to_drop, list):
            samples_to_drop=[samples_to_drop]
        remaining=self.data.drop(index=[str(i) for i in samples_to_drop])
        if inplace:
            self.data=remaining
            self._update_sample_metadata()
            return None
        else:
            return remaining

    def drop_metabolites(self, metabolites_to_drop, inplace=True):
        """
        Drop specified metabolites from the dataset.

        Parameters:
        metabolites_to_drop (list): List of metabolite IDs to drop.
        """
        if not isinstance(metabolites_to_drop, list):
            metabolites_to_drop=[metabolites_to_drop]
        remaining = self.data.drop(columns=[str(i) for i in metabolites_to_drop])
        if inplace:
            self.data=remaining
            self._update_chemical_annotation()
            return None
        else:
            return remaining

    def drop_xenobiotic_metabolites(self, inplace=True):
        """
        Drop xenobiotic metabolites from the dataset.
        """
        xenobiotic_metabolites=list(self.chemical_annotation[self.chemical_annotation["SUPER_PATHWAY"].str.lower()=='xenobiotics'].index)
        if inplace:
            self.drop_metabolites(xenobiotic_metabolites, inplace=True)
            return None
        else:
            return self.drop_metabolites(xenobiotic_metabolites, inplace=False)

    def extract_metabolites(self, metabolites_to_extract):
        """
        Extract data for specified metabolites.

        Parameters:
        metabolites_to_extract (str or list): Name(s) of metabolite(s) to extract.

        Returns:
        DataFrame: Extracted data for the specified metabolites merged with sample metadata
        """
        if not isinstance(metabolites_to_extract, list):
            metabolites_to_extract=[metabolites_to_extract]
        return self.sample_metadata.merge(self.data[[str(i) for i in metabolites_to_extract]], left_index=True, right_index=True)

    def extract_samples(self, samples_to_extract):
        """
        Extract data for specified samples.

        Parameters:
        samples_to_extract (str or list): ID(s) of sample(s) to extract.

        Returns:
        DataFrame: Extracted data and sample metadata for the specified samples.
        """
        if not isinstance(samples_to_extract, list):
            samples_to_extract=[samples_to_extract]
        return self.sample_metadata.loc[samples_to_extract].merge(self.data, left_index=True, right_index=True, how='left')

    def extract_chemical_annotations(self, metabolites_to_extract):
        """
        Extract chemical annotations for the specified metabolites.

        Parameters:
        metabolites_to_extract (str or list): Name(s) of metabolite(s) to extract annotations for.

        Returns:
        DataFrame: Extracted chemical annotations for the specified metabolites.
        """
        if not isinstance(metabolites_to_extract, list):
            metabolites_to_extract=[metabolites_to_extract]
        return self.chemical_annotation.loc[[str(i) for i in metabolites_to_extract]]
