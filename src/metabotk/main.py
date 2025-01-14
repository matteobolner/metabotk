from metabotk.metabolomic_dataset import MetabolomicDataset
from metabotk.dataset_io import DatasetIO
from metabotk.dataset_operations import DatasetOperations
from metabotk.statistics_handler import Statistics
import pandas as pd


def set_pandas_display_options() -> None:
    """Set pandas display options."""
    # Ref: https://stackoverflow.com/a/52432757/
    display = pd.options.display
    display.max_columns = 1000
    display.max_rows = 10_000
    display.max_colwidth = 199
    display.width = 1000
    # display.precision = 2  # set as needed
    # display.float_format = lambda x: '{:,.2f}'.format(x)  # set as needed


set_pandas_display_options()


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

    @property
    def stats(self):
        """Lazy initialization of Statistics instance."""
        if not hasattr(self, "_statistics_"):
            self._statistics_ = Statistics(self.data)
        return self._statistics_
