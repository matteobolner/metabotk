from typing import List, Dict

from metabotk.outliers_handler import OutlierHandler
from metabotk.missing_handler import MissingDataHandler
from metabotk.statistics_handler import StatisticsHandler
from metabotk.dataset_manager import DatasetManager
from metabotk.models_handler import ModelsHandler
from metabotk.visualization_handler import Visualization
from metabotk.dimensionality_reduction import DimensionalityReduction
from metabotk.imputation import ImputationHandler
from metabotk.feature_selection import FeatureSelection
from metabotk.normalization import NormalizationHandler
from metabotk.scaling import ScalingHandler


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
    def normalization(self):
        """Lazy initialization of NormalizationHandler instance."""
        if not hasattr(self, "_normalization_"):
            self._normalization_ = NormalizationHandler(self)
        return self._normalization_

    @property
    def scaling(self):
        """Lazy initialization of ScalingHandler instance."""
        if not hasattr(self, "_scaling_"):
            self._scaling_ = ScalingHandler(self)
        return self._scaling_

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

    def split_by_sample_column(self, columns: List[str]) -> Dict[str, "MetaboTK"]:
        """
        Split the data based on the sample column(s).

        Parameters:
            columns (list): List of column names containing the sample IDs.

        Returns:
            dict: Dictionary with the split data and sample metadata, as a MetaboTK instance.
        """
        split_data = self._split_by_sample_column(columns)
        split_data_instanced = {}
        for dataset_name, dataset_instance in split_data.items():
            temp_instance = MetaboTK(
                sample_id_column=self._sample_id_column,
                data_provider=self._data_provider,
                metabolite_id_column=self._metabolite_id_column,
            )
            temp_instance.import_tables(
                data=dataset_instance.data.reset_index(),
                sample_metadata=dataset_instance.sample_metadata.reset_index(),
                chemical_annotation=dataset_instance.chemical_annotation.reset_index(),
            )
            split_data_instanced[dataset_name] = temp_instance
        return split_data_instanced

    def split_by_metabolite_column(self, columns: List[str]) -> Dict[str, "MetaboTK"]:
        """
        Split the data based on the metabolite column(s).

        Parameters:
            columns (list): List of column names containing the sample IDs.

        Returns:
            dict: Dictionary with the split data and sample metadata as a MetaboTK instance.
        """
        split_data = self._split_by_metabolite_column(columns)
        split_data_instanced = {}
        for dataset_name, dataset_instance in split_data.items():
            temp_instance = MetaboTK(
                sample_id_column=self._sample_id_column,
                data_provider=self._data_provider,
                metabolite_id_column=self._metabolite_id_column,
            )
            temp_instance.import_tables(
                data=dataset_instance.data.reset_index(),
                sample_metadata=dataset_instance.sample_metadata.reset_index(),
                chemical_annotation=dataset_instance.chemical_annotation.reset_index(),
            )
            split_data_instanced[dataset_name] = temp_instance
        return split_data_instanced

    def subset_samples(self, samples_to_extract):
        """
        Extract a subset of the dataset containing only the specified samples.

        Parameters
        ----------
        samples_to_extract : str or list
            ID(s) of sample(s) to extract.

        Returns
        -------
        MetaboTK object containing the subset of the dataset.
        """
        subset = self._subset_samples(samples_to_extract)
        temp_instance = MetaboTK(
            sample_id_column=self._sample_id_column,
            data_provider=self._data_provider,
            metabolite_id_column=self._metabolite_id_column,
        )
        temp_instance.import_tables(
            data=subset.data.reset_index(),
            sample_metadata=subset.sample_metadata.reset_index(),
            chemical_annotation=subset.chemical_annotation.reset_index(),
        )
        return temp_instance
