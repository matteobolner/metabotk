import polars as pl
from polars import meta
from metabotk.utils import validate_new_data, validate_new_metadata, check_duplicate_ids, check_all_ids_present


class MetabolomicDataset:
    """
    This class represents a metabolomic dataset, consisting of three main dataframes:
    data, sample_metadata, and chemical_annotation.
    Attributes:
        sample_id_column: name of the sample id column
        metabolite_id_column: name of the metabolite id column
        data: pl.DataFrame containing the metabolomic data, with samples as rows and metabolites as columns
        sample_metadata: pl.DataFrame containing the sample metadata, with samples as rows and sample metadata as columns
        chemical_annotation: pl.DataFrame containing the chemical annotation, with metabolites as rows and metabolite metadata as columns
        samples: list of sample ids
        metabolites: list of metabolite ids
    """

    def __init__(
        self,
        data: pl.DataFrame,
        sample_metadata: pl.DataFrame,
        chemical_annotation: pl.DataFrame,
        sample_id_column: str,
        metabolite_id_column: str,
    ) -> None:
        """
        Initialize the class.

        Parameters:
            sample_id_column (str): name of the sample id column
            metabolite_id_column (str): name of the metabolite id column
            data (pl.DataFrame): metabolomic data, with samples as rows and metabolites as columns
            sample_metadata (pl.DataFrame): sample metadata, with samples as rows and sample metadata as columns
            chemical_annotation (pl.DataFrame): chemical annotation, with metabolites as rows and metabolite metadata as columns
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
        data: pl.DataFrame,
        sample_metadata: pl.DataFrame,
        chemical_annotation: pl.DataFrame,
        sample_id_column: str,
        metabolite_id_column: str,
    ):
        """
        Setup the class.

        Parameters:
            sample_id_column (str): name of the sample id column
            metabolite_id_column (str): name of the metabolite id column
            data (pl.DataFrame): metabolomic data, with samples as rows and metabolites as columns
            sample_metadata (pl.DataFrame): sample metadata, with samples as rows and sample metadata as columns
            chemical_annotation (pl.DataFrame): chemical annotation, with metabolites as rows and metabolite metadata as columns
        Returns:
            MetabolomicDataset populated instance
        """
        #Initial checks for duplicate/missing sample and metabolite IDs
        if check_duplicate_ids(sample_metadata, sample_id_column):
            raise ValueError("Sample IDs must be unique")
        if check_duplicate_ids(chemical_annotation, metabolite_id_column):
            raise ValueError("Metabolite IDs must be unique")
        if sample_id_column not in data.columns:
            raise ValueError(f"No sample ID column '{sample_id_column}' found in data")
        if sample_id_column not in sample_metadata.columns:
            raise ValueError(f"No sample ID column '{sample_id_column}' found in data")
        if metabolite_id_column not in chemical_annotation.columns:
            raise ValueError(f"No metabolite ID column '{metabolite_id_column}' found in data")
        chemical_annotation=chemical_annotation.with_columns(pl.col(metabolite_id_column).cast(pl.String))
        metabolites = chemical_annotation[metabolite_id_column].to_list()
        sample_metadata=sample_metadata.with_columns(pl.col(sample_id_column).cast(pl.String))
        samples=data[sample_id_column].to_list()
        if not check_all_ids_present(metabolites, list(data.columns)):
            raise ValueError(f"Missing chemical annotation for {set(metabolites).difference(set(data.columns))}")
        if not check_all_ids_present(samples, sample_metadata[sample_id_column].to_list()):
            raise ValueError(f"Missing sample metadata for {set(samples).difference(set(sample_metadata[sample_id_column].to_list()))}")
        '''
        metabolites = [
            i
            for i in data.columns
            if i in chemical_annotation[metabolite_id_column].to_list()
        ]
        samples=[
            i
            for i in data.index
            if i in sample_metadata[sample_id_column].to_list()
        ]
        '''
        data = data.with_row_index()
        sample_id_column="PARENT_SAMPLE_NAME"
        metabolite_id_column="CHEM_ID"
        data=pl.read_csv("tests/test_data/data.csv")
        sample_metadata=pl.read_csv("tests/test_data/sample_metadata.csv")
        chemical_annotation=pl.read_csv("tests/test_data/chemical_annotation.csv")
        
        metabolite_order = pl.Enum(metabolites)
        sample_order=
        # chemical_annotation = chemical_annotation.with_row_index()
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
    def data(self, new_data: pl.DataFrame):
        """
        Set the data

        Args:
            new_data: pl.DataFrame
        """
        validate_new_data(self.data, new_data)
        self.__data = new_data

    @property
    def sample_metadata(self):
        return self.__sample_metadata

    @sample_metadata.setter
    def sample_metadata(self, new_sample_metadata: pl.DataFrame):
        """
        Set the sample metadata
        Args:
            new_sample_metadata: pl.DataFrame
        """
        validate_new_metadata(self.sample_metadata, new_sample_metadata)
        self.__sample_metadata = new_sample_metadata

    @property
    def chemical_annotation(self):
        return self.__chemical_annotation

    @chemical_annotation.setter
    def chemical_annotation(self, new_chemical_annotation: pl.DataFrame):
        """
        Set the chemical annotation.
        Args:
            new_chemical_annotation: pl.DataFrame
        """
        validate_new_metadata(self.chemical_annotation, new_chemical_annotation)
        self.__chemical_annotation = new_chemical_annotation

    @property
    def samples(self) -> list[str]:
        return self.__samples

    @samples.setter
    def samples(self, new_samples: list[str]):
        """
        Set the samples.

        Args:
            new_samples: list of sample ids

        Raises:
            ValueError: if the number of samples does not match the number of data rows
        """
        if len(new_samples) != len(self.data):
            raise ValueError("Number of samples must match number of data rows")
        self.__samples = new_samples

    @property
    def metabolites(self) -> list[str]:
        return list(self.chemical_annotation.index)

    @metabolites.setter
    def metabolites(self, new_metabolites: list[str]):
        """
        Set the metabolites

        Args:
            new_metabolites: list of metabolite ids

        Raises:
            ValueError: if the number of metabolites does not match the number of data columns
        """
        if len(new_metabolites) != len(self.data.columns):
            raise ValueError("Number of metabolites must match number of data columns")
        self.__metabolites = new_metabolites
