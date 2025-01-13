from metabotk.metabolomic_dataset import MetabolomicDataset
from metabotk.dataset_io import DatasetIO
from metabotk.dataset_operations import DatasetOperations
import pandas as pd


class MetaboTK(MetabolomicDataset):
    def __init__(
        self,
        data=pd.DataFrame(),
        sample_metadata=pd.DataFrame(),
        chemical_annotation=pd.DataFrame(),
        sample_id_column="sample",
        metabolite_id_column="CHEM_ID",
    ) -> None:
        super().__init__(
            data=data,
            sample_metadata=sample_metadata,
            chemical_annotation=chemical_annotation,
            sample_id_column=sample_id_column,
            metabolite_id_column=metabolite_id_column,
        )

    @property
    def io(self):
        """Lazy initialization of DatasetIO instance."""
        if not hasattr(self, "_io_"):
            self._io_ = DatasetIO(self)
        return self._io_

    @property
    def ops(self):
        """Lazy initialization of DatasetEditor instance."""
        if not hasattr(self, "_operations_"):
            self._operations_ = DatasetOperations(self)
        return self._operations_
