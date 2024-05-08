import miceforest as mf
import numpy as np
import pandas as pd
from sklearn.utils import check_random_state
from metabotk.statistics_handler import get_top_n_correlations


class ImputationHandler:
    """
    Class for performing missing data imputation on metabolomics data.

    This class provides a simple interface to perform missing value imputation on the data using various approaches.
    For now only miceforest is included.

    Attributes:
        stats (StatisticsHandler): StatisticsHandler instance containing the data.
    """

    def __init__(
        self,
        dataset_manager,
    ):
        """
        Initialize the class.

        Parameters:
            statistics_handler (StatisticsHandler): StatisticsHandler instance containing the data.
            n_imputed_datasets (int): Number of imputed datasets to generate (default: 5).
            n_iterations (int): Number of iterations of MICE to perform (default: 5).
            random_state (int): Random seed (default: None).
        """
        self._dataset_manager = dataset_manager

    def miceforest(
        self,
        n_correlated_metabolites,
        n_imputed_datasets=5,
        n_iterations=5,
        random_state=None,
        get_kernel=False,
    ):
        """
        Perform missing data imputation using MICE (Mixed-effects Imputation by Chained Equations).

        Parameters:
            n_correlated_metabolites (int): Number of metabolites to use for correlated imputation.

        Returns:
            dict: Dictionary with imputed datasets, keys are integers starting from 1.
        """
        corrs = get_top_n_correlations(
            data_frame=self._dataset_manager.data, n=n_correlated_metabolites
        )
        corrs_dict = {}
        for name, group in corrs.groupby(by="id"):
            corrs_dict[name] = group["correlated_ids"].tolist()
        kds = mf.ImputationKernel(
            data=self._dataset_manager.data,
            datasets=n_imputed_datasets,
            variable_schema=corrs_dict,
            save_all_iterations=True,
            random_state=random_state,
            train_nonmissing=False,
            mean_match_scheme=mf.mean_match_shap,
        )
        kds.mice(
            iterations=n_iterations,
            verbose=True,
        )

        imputed = {
            dataset + 1: kds.complete_data(dataset=dataset)
            for dataset in range(n_imputed_datasets)
        }
        if get_kernel == True:
            return kds, imputed
        else:
            return imputed
