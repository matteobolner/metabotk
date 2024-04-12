from src.manager import DatasetManager
from src.statistics import StatisticsHandler
from src.models import ModelsHandler
from src.dimensionality_reduction import DimensionalityReduction
from src.visualization import Visualization
from src.feature_selection import FeatureSelection
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
        self.dimensionality_reduction = DimensionalityReduction(self)
        self.visualization = Visualization(self)
        self.models = ModelsHandler(self)
        self.feature_selection = FeatureSelection(self)

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

    def remove_outliers(self, axis=0, threshold=5):
        """
        Replace outlier values with NAs in the whole dataset, column-wise or row-wise.

        This function replaces outlier values with NAs in the whole dataset,
        column-wise or row-wise. Outliers are determined using the interquartile
        range method, which is considered more robust than the standard
        deviation method.

        Parameters:
        - axis: {0 or ‘index’, apply to each column, 1 or ‘columns’, apply to each row}, default 0
        - threshold: a factor that determines the range from the IQR (default=5)

        Returns:
        - pandas DataFrame where the outlier values are replaced by NAs
        """
        data_without_outliers = self.stats.outlier_handler.remove_outliers(
            self.data, threshold=threshold, axis=axis
        )
        return data_without_outliers
