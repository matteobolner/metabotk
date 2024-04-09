from src.reader import MetabolonCDT
from src.statistics import StatisticsHandler
from src.utils import parse_input, split_data_from_metadata

import warnings

import pandas as pd

class MetaboTK:
    """
    Class for working with metabolomics data
    """

    def __init__(self, data_provider='metabolon', sample_id_column='PARENT_SAMPLE_NAME', metabolite_id_column='CHEM_ID') -> None:
        """
        Initialize the class.
        """
        self.stats_handler=StatisticsHandler()
        self.data_provider=data_provider
        if self.data_provider.lower()=='metabolon':
            self.parser=MetabolonCDT()
        else:
            raise NotImplementedError('This data provider is not supported yet')
        self.sample_id_column=sample_id_column
        self.sample_metadata=pd.DataFrame()
        self.samples=[]
        self.metabolite_id_column=metabolite_id_column
        self.chemical_annotation=pd.DataFrame()
        self.metabolites=[]
        self.data=pd.DataFrame()
        self.feature_stats=pd.DataFrame()
        self.sample_stats=pd.DataFrame()
    ###
    #Functions to import, setup and write data and metadata
    ###

    def setup_data(self, chemical_annotation, sample_metadata, data) -> None:
        """
        Setup data
        """
        parsed_chemical_annotation=parse_input(chemical_annotation)
        parsed_sample_metadata=parse_input(sample_metadata)
        parsed_data=parse_input(data)
        if (self.sample_id_column in parsed_data.columns) and (self.sample_id_column in parsed_sample_metadata.columns):
            self.sample_metadata=self.parser.sample_metadata
            self.sample_metadata[self.sample_id_column]=self.sample_metadata[self.sample_id_column].astype(str)
            self.sample_metadata.set_index(self.sample_id_column, inplace=True)
            self.data=parsed_data
            self.data.columns=[str(i) for i in self.data.columns]
            self.data.set_index(self.sample_id_column, inplace=True)
            self.samples=list(self.sample_metadata.index)
        else:
            raise ValueError("No sample ID column found in data")
        if self.metabolite_id_column in parsed_chemical_annotation.columns:
            self.chemical_annotation=self.parser.chemical_annotation
            self.chemical_annotation[self.metabolite_id_column]=self.chemical_annotation[self.metabolite_id_column].astype(str)
            self.chemical_annotation.set_index(self.metabolite_id_column, inplace=True)
            self.metabolites=list(self.chemical_annotation.index)
        else:
            raise ValueError("No metabolite ID column found in chemical annotation")

    def import_excel(self, file_path, data_sheet) -> None:#='batch_normalized_data'):
        self.parser.import_excel(file_path)
        data=getattr(self.parser, data_sheet)
        self.setup_data(self.parser.chemical_annotation, self.parser.sample_metadata, data)

    def import_tables(self, data, chemical_annotation='config/metabolites.tsv', sample_metadata='config/samples.tsv') -> None:
        self.parser.import_tables(sample_metadata=sample_metadata, chemical_annotation=chemical_annotation, generic_data=data)
        self.setup_data(self.parser.chemical_annotation, self.parser.sample_metadata, self.parser.generic_data)

    def merge_sample_metadata_data(self)-> pd.DataFrame:
        merged=self.sample_metadata.merge(self.data, left_index=True, right_index=True)
        return merged

    def split_sample_metadata_data(self)-> pd.DataFrame:
        self.data=self.data[self.chemical_annotation[self.metabolite_id_column]]

    def save_merged(self, data_path, chemical_annotation_path=None):
        """
        Save the merged sample data and metabolite abundance data to a TSV file
        """
        merged = self.merge_sample_metadata_data()
        if len(merged)==0:
            raise ValueError("Trying to save an empty dataframe")
        merged.to_csv(data_path, sep="\t")
        if chemical_annotation_path:
            self.chemical_annotation.to_csv(chemical_annotation_path, sep='\t')

    def save(self, data_path=None, chemical_annotation_path=None, sample_metadata_path=None):
        """
        Save the individual parts
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
        Replace the data column names with names from a columno of the metabolite metadata
        """
        if new_column not in self.chemical_annotation.columns:
            raise ValueError(f"No column named {new_column} in the metabolite metadata")
        not_annotated=list(set(self.data.columns).difference(set(self.chemical_annotation[self.metabolite_id_column])))
        if len(not_annotated)>0:
            raise ValueError(f"Missing chemical annotation for {not_annotated}")
        renaming_dict={old:new for old,new in zip(self.chemical_annotation[self.metabolite_id_column],self.chemical_annotation[new_column])}
        self.data.columns=[renaming_dict[old] for old in self.data.columns]
        self.metabolite_id_column=new_column

    def update_chemical_annotation(self):
        self.chemical_annotation=self.chemical_annotation.loc[list(self.data.columns)]
        self.metabolites=list(self.chemical_annotation.index)

    def update_sample_metadata(self):
        self.sample_metadata=self.sample_metadata.loc[self.data.index]
        self.samples=list(self.sample_metadata.index)

    def remove_outliers(self, axis=0, threshold=5):
        """
        Replace outlier values with NAs in the whole dataset, column-wise or row-wise.

        Parameters:
        - axis: {0 or ‘index’, apply to each column, 1 or ‘columns’, apply to each row}, default 0
        Returns:
        - pandas DataFrame where the outlier values are replaced by NAs
        """
        self.data=self.stats_handler.outlier_handler.remove_outliers(self.data,threshold=threshold, axis=axis)

    def drop_missing(self, axis=0, threshold=0.25):
        """
        Remove columns or rows with missing values above the threshold.

        Parameters:
            - threshold: missingness over which to remove the row/column
            - axis: {0 or ‘index’, remove columns, 1 or ‘columns’, remove rows}, default 0

        Returns:
            DataFrame: DataFrame containing the rows/columns dropped.
        """
        if axis==0:
            all=self.data.copy()
            self.data=self.stats_handler.missing_handler.drop_columns_with_missing(data_frame=self.data, threshold=threshold)
            remaining=set(self.data.columns)
            self.update_chemical_annotation()
            dropped=list(set(all.columns).difference(remaining))
            print(f"Removed {len(dropped)} features")
            dropped=all[dropped]
            return dropped
        elif axis==1:
            all=self.data.copy()
            self.data=self.stats_handler.missing_handler.drop_rows_with_missing(data_frame=self.data, threshold=threshold)
            self.update_sample_metadata()
            remaining=set(self.data.index)
            dropped=list(set(all.index).difference(remaining))
            print(f"Removed {len(dropped)} samples")
            dropped=all.loc[dropped]
            return dropped

    def remove_metadata_from_data(self):
        self.data=self.data[list(self.chemical_annotation.index)]

    def split_by_sample_column(self, column):
        """
        Split the dataset (data and sample metadata) in multiple independent DataClass instances
        based on the values of a sample metadata column
        """
        split_data = {}
        for name, group in self.sample_metadata.groupby(by=column):
            tempdata=self.data.loc[group.index]
            tempclass=MetaboTK(data_provider=self.data_provider, sample_id_column=self.sample_id_column, metabolite_id_column=self.metabolite_id_column)
            tempclass.import_tables(data=tempdata.reset_index(), chemical_annotation=self.chemical_annotation.reset_index(), sample_metadata=group.reset_index())
            tempclass.update_chemical_annotation()
            tempclass.update_sample_metadata()
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
            tempclass=MetaboTK(data_provider=self.data_provider, sample_id_column=self.sample_id_column, metabolite_id_column=self.metabolite_id_column)
            tempclass.import_tables(data=tempdata.reset_index(), chemical_annotation=group.reset_index(), sample_metadata=self.sample_metadata.reset_index())
            tempclass.update_chemical_annotation()
            split_data[name]=tempclass
        return split_data

    def drop_samples(self, samples_to_drop):
        self.data=self.data.drop(index=[str(i) for i in samples_to_drop])
        self.update_sample_metadata()

    def drop_metabolites(self, metabolites_to_drop):
        self.data=self.data.drop(columns=[str(i) for i in metabolites_to_drop])
        self.update_chemical_annotation()

    def drop_xenobiotic_metabolites(self):
        self.drop_metabolites(self.chemical_annotation[self.chemical_annotation["SUPER_PATHWAY"].str.lower()=='xenobiotics'])

    def extract_metabolites(self, metabolites_to_extract):
        if not isinstance(metabolites_to_extract, list):
            metabolites_to_extract=[metabolites_to_extract]
        return self.sample_metadata.merge(self.data[[str(i) for i in metabolites_to_extract]], left_index=True, right_index=True)

    def extract_samples(self, samples_to_extract):
        if not isinstance(samples_to_extract, list):
            samples_to_extract=[samples_to_extract]
        return self.sample_metadata.loc[samples_to_extract].merge(self.data, left_index=True, right_index=True, how='left')

    def extract_chemical_annotations(self, metabolites_to_extract):
        if not isinstance(metabolites_to_extract, list):
            metabolites_to_extract=[metabolites_to_extract]
        return self.chemical_annotation.loc[[str(i) for i in metabolites_to_extract]]


    ###
    #Statistics
    ###
    def TSA(self, exclude_xenobiotics=True, exclude_incomplete_metabolites=False):
        """
        Compute the Total Sum Abundance (TSA) values for each sample,
        either on all metabolites or only on the complete ones without missing data.
        Xenobiotics should be excluded as they usually are not considered for this calculation.
        """
        if exclude_xenobiotics:
            temp_data=self.chemical_annotation[self.chemical_annotation['SUPER_PATHWAY'].str.lower()!='xenobiotics']
        if exclude_incomplete_metabolites:
            temp_data=temp_data.dropna(axis=1)
        TSA=temp_data.apply(sum, axis=1)
        ERI QUI
        return TSA

    def compute_stats(self, outlier_threshold=5):
        """
        Computes basic statistics for the metabolomics data.

        Returns:
            pandas DataFrame: DataFrame containing statistics for each column of the data.
        """
        # Ensure that data is set up properly
        if self.data.empty:
            raise ValueError("No data available. Please import data before computing statistics.")

        # Compute statistics using StatisticsHandler
        feature_stats = self.stats_handler.compute_dataframe_statistics(self.data,outlier_threshold, axis=0)
        sample_stats = self.stats_handler.compute_dataframe_statistics(self.data,outlier_threshold, axis=1)

        self.feature_stats=feature_stats
        self.sample_stats=sample_stats



a=MetaboTK(sample_id_column='PARENT_SAMPLE_NAME')
a.import_excel("data/cdt_demo.xlsx", data_sheet='batch_normalized_data')

test=a.split_by_metabolite_column("PLATFORM")
a.sample_metadata.drop(["INTR-03233 [COPY 2]",'INTR-03212 [COPY 2]'])
a.data

a.sample_metadata

a.merge_sample_metadata_data().to_csv("test.tsv", sep='\t')
