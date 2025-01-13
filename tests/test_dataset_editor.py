import pytest
import pandas as pd
from metabotk.metabolomic_dataset import MetabolomicDataset
from metabotk.dataset_manipulator import DatasetManipulator


@pytest.fixture
def dataset():
    dataset = MetabolomicDataset._setup(
        data=pd.read_csv("data/data.csv"),
        sample_metadata=pd.read_csv("data/sample_metadata.csv"),
        chemical_annotation=pd.read_csv("data/chemical_annotation.csv"),
        sample_id_column="PARENT_SAMPLE_NAME",
        metabolite_id_column="CHEM_ID",
    )
    return dataset


class TestDatasetManipulator:
    def test_subset_samples(self, dataset):
        samples = ["INTR-03208 [COPY 2]", "INTR-03200 [COPY 2]"]
        subsetted = DatasetManipulator.subset(dataset, what="samples", ids=samples)
        assert subsetted.chemical_annotation.equals(dataset.chemical_annotation)
        assert subsetted.data.equals(dataset.data.loc[samples])
        assert subsetted.sample_metadata.equals(dataset.sample_metadata.loc[samples])
        assert len(subsetted.data) == 2
        assert len(subsetted.sample_metadata) == 2
        assert len(subsetted.samples) == 2
        assert subsetted.samples == samples
        assert len(subsetted.metabolites) == len(dataset.metabolites)

    def test_subset_metabolites(self, dataset):
        metabolites = ["50", "100008998"]
        subsetted = DatasetManipulator.subset(
            dataset, what="metabolites", ids=metabolites
        )
        assert subsetted.chemical_annotation.equals(
            dataset.chemical_annotation.loc[metabolites]
        )
        assert subsetted.data.equals(dataset.data[metabolites])
        assert subsetted.chemical_annotation.equals(
            dataset.chemical_annotation.loc[metabolites]
        )
        assert len(subsetted.data) == len(dataset.data)
        assert len(subsetted.chemical_annotation) == 2
        assert len(subsetted.samples) == len(dataset.samples)
        assert subsetted.metabolites == metabolites
        assert len(subsetted.metabolites) == len(metabolites)
