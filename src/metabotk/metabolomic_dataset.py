import pandas as pd
from metabotk.parse_and_setup import (
    setup_data,
    setup_sample_metadata,
    setup_chemical_annotation,
)

from metabotk.utils import validate_new_data, validate_new_metadata


class MetabolomicDataset:
    """

    Attributes:
        sample_id_column:
        metabolite_id_column:
        data:
        sample_metadata:
        chemical_annotation:
        samples:
        metabolites:
    """

    def __init__(
        self,
        data: pd.DataFrame,
        sample_metadata: pd.DataFrame,
        chemical_annotation: pd.DataFrame,
        sample_id_column: str,
        metabolite_id_column: str,
    ) -> None:
        """
        Initialize the class.

        Parameters:
            sample_id_column (str): name of the sample id column
            metabolite_id_column (str): name of the metabolite id column
        """
        self._sample_id_column: str = sample_id_column
        self._metabolite_id_column: str = metabolite_id_column
        self.__data = data
        self.__sample_metadata = sample_metadata
        self.__chemical_annotation = chemical_annotation
        self.__samples = list(sample_metadata.index)
        self.__metabolites = list(chemical_annotation.index)

    @classmethod
    def _setup(
        cls,
        data: pd.DataFrame,
        sample_metadata: pd.DataFrame,
        chemical_annotation: pd.DataFrame,
        sample_id_column: str,
        metabolite_id_column: str,
    ):
        data = setup_data(data, sample_id_column)
        sample_metadata = setup_sample_metadata(sample_metadata, sample_id_column)
        chemical_annotation = setup_chemical_annotation(
            chemical_annotation, metabolite_id_column
        )
        chemical_annotation.index = chemical_annotation.index.map(str)
        sample_metadata.index = sample_metadata.index.map(str)
        data.columns = data.columns.map(str)
        data.index = data.index.map(str)
        metabolites = [i for i in data.columns if i in list(chemical_annotation.index)]
        data = data[metabolites]
        sample_metadata = sample_metadata.loc[data.index]
        sample_metadata.index.name = sample_id_column
        chemical_annotation = chemical_annotation.loc[data.columns]
        chemical_annotation.index.name = metabolite_id_column

        return cls(
            data=data,
            sample_metadata=sample_metadata,
            chemical_annotation=chemical_annotation,
            sample_id_column=sample_id_column,
            metabolite_id_column=metabolite_id_column,
        )

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, new_data):
        validate_new_data(self.data, new_data)
        self.__data = new_data

    @property
    def sample_metadata(self):
        return self.__sample_metadata

    @sample_metadata.setter
    def sample_metadata(self, new_sample_metadata):
        validate_new_metadata(self.sample_metadata, new_sample_metadata)
        self.__sample_metadata = new_sample_metadata

    @property
    def chemical_annotation(self):
        return self.__chemical_annotation

    @chemical_annotation.setter
    def chemical_annotation(self, new_chemical_annotation):
        validate_new_metadata(self.chemical_annotation, new_chemical_annotation)
        self.__chemical_annotation = new_chemical_annotation

    @property
    def samples(self) -> list[str]:
        return self.__samples

    @samples.setter
    def samples(self, new_samples):
        if len(new_samples) != len(self.data):
            raise ValueError("Number of samples must match number of data rows")
        self.__samples = new_samples

    @property
    def metabolites(self) -> list[str]:
        return list(self.chemical_annotation.index)

    @metabolites.setter
    def metabolites(self, new_metabolites):
        if len(new_metabolites) != len(self.data.columns):
            raise ValueError("Number of metabolites must match number of data columns")
        self.__metabolites = new_metabolites
