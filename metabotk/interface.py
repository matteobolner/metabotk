from metabotk.statistics_handler import StatisticsHandler
from metabotk.dataset_manager import DatasetManager
from metabotk.models_handler import ModelsHandler
from metabotk.visualization_handler import Visualization
from metabotk.dimensionality_reduction import DimensionalityReduction
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
    def feature_selection(self):
        """Lazy initialization of FeatureSelection instance."""
        if not hasattr(self, "_feature_selection_"):
            self._feature_selection_ = FeatureSelection(self)
        return self._feature_selection_
