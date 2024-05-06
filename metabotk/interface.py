from metabotk.outliers_handler import OutlierHandler
from metabotk.missing_handler import MissingDataHandler
from metabotk.statistics_handler import StatisticsHandler
from metabotk.dataset_manager import DatasetManager
from metabotk.models_handler import ModelsHandler
from metabotk.visualization_handler import Visualization
from metabotk.dimensionality_reduction import DimensionalityReduction
from metabotk.imputation import ImputationHandler
from metabotk.feature_selection import FeatureSelection
import pandas as pd


class MetaboTK(DatasetManager):
    """
    Class for working with metabolomics data
    """

    def __init__(
        self,
        data_provider="metabolon",
        sample_id_column=None,
        metabolite_id_column="CHEM_ID",
    ) -> None:
        """
        Initialize the class.
        """
        super().__init__(
            data_provider=data_provider,
            sample_id_column=sample_id_column,
            metabolite_id_column=metabolite_id_column,
        )

    @property
    def missing(self):
        """Lazy initialization of MissingDataHandler instance."""
        if not hasattr(self, "_missing_"):
            self._missing_ = MissingDataHandler()
        return self._missing_

    @property
    def outliers(self):
        """Lazy initialization of OutlierHandler instance."""
        if not hasattr(self, "_missing_"):
            self._outliers_ = OutlierHandler()
        return self._outliers_

    @property
    def stats(self):
        """Lazy initialization of StatisticsHandler instance."""
        if not hasattr(self, "_stats_"):
            self._stats_ = StatisticsHandler(self)
        return self._stats_

    @property
    def models(self):
        """Lazy initialization of ModelsHandler instance."""
        if not hasattr(self, "_models_"):
            self._models_ = ModelsHandler(self)
        return self._models_

    @property
    def dimensionality_reduction(self):
        """Lazy initialization of DimensionalityReduction instance."""
        if not hasattr(self, "_dimensionality_reduction_"):
            self._dimensionality_reduction_ = DimensionalityReduction(self)
        return self._dimensionality_reduction_

    @property
    def visualization(self):
        """Lazy initialization of Visualization instance."""
        if not hasattr(self, "_visualization_"):
            self._visualization_ = Visualization(self)
        return self._visualization_

    @property
    def imputation(self):
        """Lazy initialization of ImputationHandler instance."""
        if not hasattr(self, "_imputation_"):
            self._imputation_ = ImputationHandler(self)
        return self._imputation_

    @property
    def feature_selection(self):
        """Lazy initialization of FeatureSelection instance."""
        if not hasattr(self, "_feature_selection_"):
            self._feature_selection_ = FeatureSelection(self)
        return self._feature_selection_

    ###FUNCTIONS###
    def drop_missing_from_dataframe(self, axis=0, threshold=0.25, inplace=False):
        """
        Removes rows/columns from the data dataframe based on the threshold of missing
        values.

        Parameters:
            axis (int): Axis to drop missing values from (0: rows, 1: columns).
            threshold (float): Threshold of missing values to drop.
            inplace (bool): Whether to drop missing values inplace or return the remaining data.

        Returns:
            DataFrame: DataFrame with missing values over threshold removed.
        """
        remaining_data = self.missing._drop_missing_from_dataframe(
            data_frame=self.data, axis=axis, threshold=threshold
        )
        if inplace:
            self.data = remaining_data
            self._update_chemical_annotation()
            print("Removed inplace metabolites with missing data over threshold")
            return None
        else:
            return remaining_data
