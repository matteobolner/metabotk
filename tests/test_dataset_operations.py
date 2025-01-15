import pytest
import pandas as pd
from metabotk.metabolomic_dataset import MetabolomicDataset
from metabotk.dataset_operations import DatasetOperations


@pytest.fixture
def ops():
    dataset = MetabolomicDataset._setup(
        data=pd.read_csv("tests/test_data/data.csv"),
        sample_metadata=pd.read_csv("tests/test_data/sample_metadata.csv"),
        chemical_annotation=pd.read_csv("tests/test_data/chemical_annotation.csv"),
        sample_id_column="PARENT_SAMPLE_NAME",
        metabolite_id_column="CHEM_ID",
    )
    ops = DatasetOperations(dataset)
    return ops


class TestOperations:
    def test_subset_samples(self, ops):
        samples = ["INTR-03208 [COPY 2]", "INTR-03200 [COPY 2]"]
        subsetted = ops.subset(what="samples", ids=samples)
        assert subsetted.chemical_annotation.equals(ops.dataset.chemical_annotation)
        assert subsetted.data.equals(ops.dataset.data.loc[samples])
        assert subsetted.sample_metadata.equals(
            ops.dataset.sample_metadata.loc[samples]
        )
        assert len(subsetted.data) == 2
        assert len(subsetted.sample_metadata) == 2
        assert len(subsetted.samples) == 2
        assert subsetted.samples == samples
        assert len(subsetted.metabolites) == len(ops.dataset.metabolites)

    def test_subset_metabolites(self, ops):
        metabolites = ["50", "100008998"]
        subsetted = ops.subset(what="metabolites", ids=metabolites)
        assert subsetted.chemical_annotation.equals(
            ops.dataset.chemical_annotation.loc[metabolites]
        )
        assert subsetted.data.equals(ops.dataset.data[metabolites])
        assert subsetted.chemical_annotation.equals(
            ops.dataset.chemical_annotation.loc[metabolites]
        )
        assert len(subsetted.data) == len(ops.dataset.data)
        assert len(subsetted.chemical_annotation) == 2
        assert len(subsetted.samples) == len(ops.dataset.samples)
        assert subsetted.metabolites == metabolites
        assert len(subsetted.metabolites) == len(metabolites)
