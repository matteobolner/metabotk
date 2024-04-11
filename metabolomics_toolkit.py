from src.manager import DatasetManager
from src.statistics import StatisticsHandler
from src.effects_models import EffectsHandler
from src.dimensionality_reduction import DimensionalityReduction
from src.utils import parse_input
from src.visualization import Visualization
import pandas as pd
from src.reader import MetabolonCDT


class MetaboTK(DatasetManager):
    """
    Class for working with metabolomics data
    """

    def __init__(
        self,
        data_provider="metabolon",
        sample_id_column="PARENT_SAMPLE_NAME",
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
        self.data = self.stats.outlier_handler.remove_outliers(
            self.data, threshold=threshold, axis=axis
        )

    def get_pca(self, n_components=3, output_pca_object=False):
        """
        Perform Principal Component Analysis (PCA) on the data.

        This function performs PCA on the data and returns the transformed data
        as a DataFrame. The number of components can be specified using the
        n_components parameter. By default, 3 components are used.

        Parameters:
            n_components (int, optional): Number of components for the PCA. Default is 3.
            output_pca_object (bool, optional): Whether to return the PCA object from scikit-learn. Default is False.

        Raises:
            ValueError: If the data contains NaN values or not all columns contain numeric data.

        Returns:
            pca_transformed (DataFrame): DataFrame containing the PCA-transformed data.
            pca (PCA): sklearn PCA object. Only returned if output_pca_object is True.
        """
        PCA, PCA_object = self.dimensionality_reduction.get_pca(
            n_components=n_components
        )
        if output_pca_object == True:
            return PCA, PCA_object
        else:
            return PCA

    def effect_residuals(self, formula, models_path=None):
        """
        Fit linear models for each metabolite and extract residuals.

        Fit a linear model for each metabolite using the formula specified,
        and extract the residuals from the fitted models. The residuals are
        returned as a DataFrame with the same index as the original data.

        Parameters:
        - formula: a formula used to fit the linear models
        - models_path: path to directory where models will be saved

        Returns:
        - residuals (DataFrame): DataFrame of residuals with same index as data
        """
        effect_handler = EffectsHandler(data_manager=self, formula=formula)
        self.residuals = effect_handler.get_all_residuals()
