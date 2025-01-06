import pandas as pd
from metabotk.parse_and_setup import (
    setup_data,
    setup_sample_metadata,
    setup_chemical_annotation,
)


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
        sample_id_column: str = "sample",
        metabolite_id_column: str = "CHEM_ID",
    ) -> None:
        """
        Initialize the class.

        Parameters:
            sample_id_column (str): name of the sample id column
            metabolite_id_column (str): name of the metabolite id column
        """
        self.sample_id_column: str = sample_id_column
        self.metabolite_id_column: str = metabolite_id_column
        self.data = data
        self.sample_metadata = sample_metadata
        self.chemical_annotation = chemical_annotation

        self._samples = list(sample_metadata.index)
        self._metabolites = list(self.chemical_annotation.index)

    @staticmethod
    def _setup(
        data: pd.DataFrame,
        sample_metadata: pd.DataFrame,
        chemical_annotation: pd.DataFrame,
        sample_id_column: str = "sample",
        metabolite_id_column: str = "CHEM_ID",
    ):
        data = setup_data(data, sample_id_column)
        sample_metadata = setup_sample_metadata(sample_metadata, sample_id_column)
        chemical_annotation = setup_chemical_annotation(
            chemical_annotation, metabolite_id_column
        )

        # TODO: check if the lines below are really necessary or complicate things
        #######
        sample_metadata = sample_metadata.loc[data.index]
        sample_metadata.index.name = sample_id_column
        chemical_annotation = chemical_annotation.loc[data.columns]
        chemical_annotation.index.name = metabolite_id_column
        #######
        return MetabolomicDataset(
            data=data,
            sample_metadata=sample_metadata,
            chemical_annotation=chemical_annotation,
            sample_id_column=sample_id_column,
            metabolite_id_column=metabolite_id_column,
        )

    @property
    def samples(self) -> list[str]:
        return self._samples

    @property
    def metabolites(self) -> list[str]:
        return self._metabolites
