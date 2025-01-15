import pytest
from metabotk.metabolomic_dataset import MetabolomicDataset
import pandas as pd
import numpy as np


@pytest.fixture
def dataset():
    dataset = MetabolomicDataset._setup(
        data=pd.read_csv("tests/test_data/data.csv"),
        sample_metadata=pd.read_csv("tests/test_data/sample_metadata.csv"),
        chemical_annotation=pd.read_csv("tests/test_data/chemical_annotation.csv"),
        sample_id_column="PARENT_SAMPLE_NAME",
        metabolite_id_column="CHEM_ID",
    )
    return dataset


class TestMetabolomicDataset:
    def test_setup(self, dataset):
        assert dataset._sample_id_column == "PARENT_SAMPLE_NAME"
        assert dataset._metabolite_id_column == "CHEM_ID"
        pd.testing.assert_index_equal(dataset.sample_metadata.index, dataset.data.index)
        assert list(dataset.data.columns) == list(dataset.chemical_annotation.index)

    def test_data_setter(self, dataset):
        new_data = pd.DataFrame(
            np.nan, index=dataset.data.index, columns=dataset.data.columns
        )
        dataset.data = new_data

    def test_sample_metadata_setter(self, dataset):
        new_sample_metadata = pd.DataFrame(
            np.nan,
            index=dataset.sample_metadata.index,
            columns=dataset.sample_metadata.columns,
        )
        dataset.sample_metadata = new_sample_metadata

    def test_chemical_annotation_setter(self, dataset):
        new_chemical_annotation = pd.DataFrame(
            np.nan,
            index=dataset.chemical_annotation.index,
            columns=dataset.chemical_annotation.columns,
        )
        dataset.chemical_annotation = new_chemical_annotation

    def test_samples(self, dataset):
        assert dataset.samples == list(dataset.sample_metadata.index)

    def test_samples_setter(self, dataset):
        new_samples = [np.nan for i in dataset.samples]
        dataset.samples = new_samples

    def test_samples_setter_diff_len(self, dataset):
        new_samples = [np.nan for i in dataset.samples[0:10]]
        with pytest.raises(ValueError):
            dataset.samples = new_samples

    def test_metabolites_setter(self, dataset):
        new_metabolites = [np.nan for i in dataset.metabolites]
        dataset.metabolites = new_metabolites

    def test_metabolites_setter_diff_len(self, dataset):
        new_metabolites = [np.nan for i in dataset.metabolites[0:10]]
        with pytest.raises(ValueError):
            dataset.metabolites = new_metabolites
