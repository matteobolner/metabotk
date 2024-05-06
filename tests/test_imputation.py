# import miceforest as mf
import numpy as np
import pandas as pd

# from sklearn.utils import check_random_state
from metabotk.interface import MetaboTK

import pytest

from metabotk.statistics_handler import get_top_n_correlations


class TestImputationHandler:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.metabotk = MetaboTK(
            data_provider="metabolon",
            sample_id_column="PARENT_SAMPLE_NAME",
            metabolite_id_column="CHEM_ID",
        )
        self.metabotk.import_excel(
            "data/cdt_demo.xlsx", data_sheet="batch_normalized_data"
        )
        self.metabotk.data = self.metabotk.drop_missing_from_dataframe()
        self.metabotk._update_chemical_annotation()

    def test_miceforest_returns_dict(self):
        imputed_data = self.metabotk.imputation.miceforest(
            n_correlated_metabolites=10,
            n_imputed_datasets=1,
            n_iterations=1,
            random_state=42,
        )
        assert isinstance(imputed_data, dict)

    def test_miceforest_keys_start_from_1(self):
        imputed_data = self.metabotk.imputation.miceforest(
            n_correlated_metabolites=10,
            n_imputed_datasets=2,
            n_iterations=1,
            random_state=42,
        )
        assert all(key >= 1 for key in imputed_data.keys())

    def test_miceforest_returns_correct_number_of_datasets(self):
        n_imputed_datasets = 3
        imputed_data = self.metabotk.imputation.miceforest(
            n_correlated_metabolites=10,
            n_imputed_datasets=n_imputed_datasets,
            n_iterations=2,
            random_state=42,
        )
        assert len(imputed_data) == n_imputed_datasets

    def test_miceforest_returns_correct_shape_data(self):
        imputed_data = self.metabotk.imputation.miceforest(
            n_correlated_metabolites=10,
            n_imputed_datasets=2,
            n_iterations=2,
            random_state=42,
        )
        for dataset in imputed_data.values():
            assert dataset.shape == self.metabotk.data.shape

    def test_no_nan_after_imputation(self):
        imputed_data = self.metabotk.imputation.miceforest(
            n_correlated_metabolites=10,
            n_imputed_datasets=2,
            n_iterations=2,
            random_state=42,
        )

        for dataset in imputed_data.values():
            assert dataset.isnull().values.any() == False
