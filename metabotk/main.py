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
        self.stats = StatisticsHandler()

    ###
    # Statistics
    ###

    def sample_stats(self, outlier_threshold=5, exclude_xenobiotics=True):
        """
        Computes basic statistics for the metabolomics data sample-wise

        Xenobiotic metabolites are usually not considered in the calculations
        This function computes statistics for each sample across all metabolites.

        Parameters:
            outlier_threshold (int): Threshold for identifying outliers.
            exclude_xenobiotics (bool): If True, xenobiotic metabolites are excluded from the calculation.

        Returns:
            pandas DataFrame: DataFrame containing statistics for each sample across all metabolites.
        """
        # Ensure that data is set up properly
        if self.data.empty:
            raise ValueError(
                "No data available. Please import data before computing statistics."
            )

        # Compute statistics using StatisticsHandler
        if exclude_xenobiotics:
            data = self.drop_xenobiotic_metabolites(inplace=False)
        else:
            data = self.data
        sample_stats = self.stats.compute_dataframe_statistics(
            data, outlier_threshold, axis=1
        )

        # Compute Total Sum of Abundance (TSA) for each sample across all metabolites
        tsa_complete_only = self.stats.total_sum_abundance(
            data, exclude_incomplete=True
        )
        tsa_complete_only.name = "TSA_complete_only"
        tsa_all = self.stats.total_sum_abundance(data, exclude_incomplete=False)
        tsa_all.name = "TSA_including_incomplete"
        tsa = pd.concat([tsa_complete_only, tsa_all], axis=1)

        # Merge TSA with sample statistics
        sample_stats = sample_stats.merge(tsa, left_index=True, right_index=True)
        # self.sample_stats=sample_stats
        return sample_stats

    def metabolite_stats(self, outlier_threshold=5):
        """
        Computes basic statistics for the metabolomics data metabolite-wise

        This function computes basic statistics for each metabolite in the data.
        The statistics computed are:
        - Mean
        - Standard deviation
        - Median
        - Min
        - Max
        - Sum
        - Coefficient of Variation (CV%)
        - Number of missing values
        - Number of outliers

        Parameters:
        - outlier_threshold: Threshold for outlier detection (default=5).

        Returns:
            pandas DataFrame: DataFrame containing statistics for each metabolite.
            The index of the DataFrame is the metabolite names.

        """
        # Ensure that data is set up properly
        if self.data.empty:
            raise ValueError(
                "No data available. Please import data before computing statistics."
            )

        # Compute statistics using StatisticsHandler
        metabolite_stats = self.stats.compute_dataframe_statistics(
            self.data, outlier_threshold, axis=0
        )
        # self.metabolite_stats=metabolite_stats
        return metabolite_stats

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
