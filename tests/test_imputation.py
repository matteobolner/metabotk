# import miceforest as mf

# from sklearn.utils import check_random_state
from metabotk import MetaboTK

import pytest

from metabotk.statistics_handler import get_top_n_correlations


class TestImputationHandler:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.metabotk = MetaboTK().io.from_excel(
            "tests/test_data/cdt_demo.xlsx",
            data_sheet="Batch-normalized Data",
            sample_id_column="PARENT_SAMPLE_NAME",
        )

    def test_miceforest_returns_dict(self):
        imputed_data = self.metabotk.imp.miceforest(
            n_correlated_metabolites=10,
            n_imputed_datasets=1,
            n_iterations=1,
            random_state=42,
        )
        assert isinstance(imputed_data, dict)

    def test_miceforest_keys_start_from_1(self):
        imputed_data = self.metabotk.imp.miceforest(
            n_correlated_metabolites=10,
            n_imputed_datasets=2,
            n_iterations=1,
            random_state=42,
        )
        assert all(key >= 1 for key in imputed_data.keys())

    def test_miceforest_returns_correct_number_of_datasets(self):
        n_imputed_datasets = 3
        imputed_data = self.metabotk.imp.miceforest(
            n_correlated_metabolites=10,
            n_imputed_datasets=n_imputed_datasets,
            n_iterations=2,
            random_state=42,
        )
        assert len(imputed_data) == n_imputed_datasets

    def test_miceforest_returns_correct_shape_data(self):
        imputed_data = self.metabotk.imp.miceforest(
            n_correlated_metabolites=10,
            n_imputed_datasets=2,
            n_iterations=2,
            random_state=42,
        )
        for dataset in imputed_data.values():
            assert dataset.shape == self.metabotk.data.shape

    def test_no_nan_after_imputation(self):
        imputed_data = self.metabotk.imp.miceforest(
            n_correlated_metabolites=10,
            n_imputed_datasets=2,
            n_iterations=2,
            random_state=42,
        )

        for dataset in imputed_data.values():
            assert dataset.isnull().values.any() == False
