from src.reader import MetabolonCDT
from src.missing import MissingDataHandler
from src.outliers import OutlierHandler
from src.utils import parse_input, split_data_from_metadata

import warnings

import pandas as pd

test=MetabolonCDT()

#test.read_metabolon_excel("data/cdt_demo.xlsx")

test.read_metabolon_flat_tables(chemical_annotation="/home/pelmo/work/workspace/pigphenomics_metabolomics/config/metabolites.tsv",
                                sample_metadata="/home/pelmo/work/workspace/pigphenomics_metabolomics/config/samples.tsv",
                                batch_normalized_data="/home/pelmo/work/workspace/pigphenomics_metabolomics/data/raw_data/data.tsv"
                                )
test.batch_normalized_data=test.batch_normalized_data[test.batch_normalized_data.columns[8::]]

class MetaboTK:
    """
    Class for working with metabolomics data
    """

    def __init__(self, data_provider='metabolon', sample_column='sample') -> None:
        """
        Initialize the class.
        """
        self.data_provider=data_provider
        if self.data_provider.lower()=='metabolon':
            self.parser=MetabolonCDT()
        else:
            raise NotImplementedError('This data provider is not supported yet')
        self.sample_column=sample_column
        self.sample_metadata=pd.DataFrame()
        self.metabolite_metadata=pd.DataFrame()
        self.data=pd.DataFrame()

    def setup_data(self):
        if sample_column in self.data:
            self.data=self.data.set_index(self.sample_column)
            self.validate_sample_order()
        elif self.data.index.name == self.sample_column:
            self.validate_sample_order()
        else:
            warning_message = "No sample column found in data, there is no way to confirm that the order of samples and data correspond"
            warnings.warn(warning_message, UserWarning)
            self.data.index = self.sample_metadata[self.sample_column]

    def import_excel(self, file_path, data_sheet='batch_normalized_data'):
        imported=self.parser.import_excel(file_path)
        self.sample_metadata=parser.sample_metadata
        self.metabolite_metadata=parser.sample_metadata
        self.data=getattr(imported, data_sheet)
        self.setup_data()
        self.validate_sample_order()

    def import_tables(self, data, chemical_annotation='config/metabolites.tsv', sample_metadata='config/samples.tsv'):
        imported=self.parser.import_tables(sample_metadata=sample_metadata, chemical_annotation=chemical_annotation, generic_data=data)
        self.sample_metadata=parser.sample_metadata
        self.metabolite_metadata=parser.sample_metadata
        self.data=self.generic_data
        self.setup_data()
        self.validate_sample_order()

    def validate_sample_order(self) -> None:
        """
        Confirm that the samples in sample_metadata and in the data are the same and in the same order.
        Raises:
        - ValueError: If sample_metadata has different samples or they are in different order from the data
        - ValueError: If the sample column can not be found in the data as index or in the columns
        """

        if self.data.index.name==self.sample_column:
            if (self.sample_metadata[self.sample_column]!=self.data.index).all():
                raise ValueError("Sample name discrepancy found; check the order and correspondence between the sample metadata and data")
        elif self.sample_column in self.data.columns:
            if (self.sample_metadata[self.sample_column]!=self.data[self.sample_column]).all():
                raise ValueError("Sample name discrepancy found; check the order and correspondence between the sample metadata and data")
        else:
            raise ValueError("Sample column name or index can not be found in the data")

    def merge_data_sample_metadata(self)-> pd.DataFrame:
        merged=pd.concat([self.sample_metadata.reset_index(drop=True), self.data.reset_index(drop=True)], axis=1)
        return merged

help(MetaboTK)

a=MetaboTK()
a.import_excel()
a.import_excel("data/cdt_demo.xlsx")

merged=a.merge_data_sample_metadata()
