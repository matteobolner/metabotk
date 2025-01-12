import pytest
from metabotk.metabolomic_dataset import MetabolomicDataset
import pandas as pd
import numpy as np


def set_pandas_display_options() -> None:
    """Set pandas display options."""
    # Ref: https://stackoverflow.com/a/52432757/
    display = pd.options.display
    display.max_columns = 1000
    display.max_rows = 10_000
    display.max_colwidth = 199
    display.width = 1000
    # display.precision = 2  # set as needed
    # display.float_format = lambda x: '{:,.2f}'.format(x)  # set as needed


set_pandas_display_options()


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


class TestMetabolomicDataset:
    def test_setup(self):
        dataset = MetabolomicDataset._setup(
            data=pd.read_csv("data/data.csv"),
            sample_metadata=pd.read_csv("data/sample_metadata.csv"),
            chemical_annotation=pd.read_csv("data/chemical_annotation.csv"),
            sample_id_column="PARENT_SAMPLE_NAME",
            metabolite_id_column="CHEM_ID",
        )
        assert dataset._sample_id_column == "PARENT_SAMPLE_NAME"
        assert dataset._metabolite_id_column == "CHEM_ID"
        pd.testing.assert_index_equal(dataset.sample_metadata.index, dataset.data.index)
        assert list(dataset.data.columns) == list(dataset.chemical_annotation.index)

    def test_data_setter_working(self):
        dataset = MetabolomicDataset._setup(
            data=pd.read_csv("data/data.csv"),
            sample_metadata=pd.read_csv("data/sample_metadata.csv"),
            chemical_annotation=pd.read_csv("data/chemical_annotation.csv"),
            sample_id_column="PARENT_SAMPLE_NAME",
            metabolite_id_column="CHEM_ID",
        )
        new_data = pd.DataFrame(
            np.nan, index=dataset.data.index, columns=dataset.data.columns
        )
        dataset.data = new_data

    def test_sample_metadata_setter_working(self):
        dataset = MetabolomicDataset._setup(
            data=pd.read_csv("data/data.csv"),
            sample_metadata=pd.read_csv("data/sample_metadata.csv"),
            chemical_annotation=pd.read_csv("data/chemical_annotation.csv"),
            sample_id_column="PARENT_SAMPLE_NAME",
            metabolite_id_column="CHEM_ID",
        )

        new_sample_metadata = pd.DataFrame(
            np.nan,
            index=dataset.sample_metadata.index,
            columns=dataset.sample_metadata.columns,
        )
        dataset.sample_metadata = new_sample_metadata

    def test_chemical_annotation_setter_working(self):
        dataset = MetabolomicDataset._setup(
            data=pd.read_csv("data/data.csv"),
            sample_metadata=pd.read_csv("data/sample_metadata.csv"),
            chemical_annotation=pd.read_csv("data/chemical_annotation.csv"),
            sample_id_column="PARENT_SAMPLE_NAME",
            metabolite_id_column="CHEM_ID",
        )

        new_chemical_annotation = pd.DataFrame(
            np.nan,
            index=dataset.chemical_annotation.index,
            columns=dataset.chemical_annotation.columns,
        )
        dataset.chemical_annotation = new_chemical_annotation


"""
    def test_setter_getter_name(self):
        person = Person("Alice", 30)
        person.set_name("Bob")
        assert person.get_name() == "Bob"

    def test_setter_getter_age(self):
        person = Person("Alice", 30)
        person.set_age(35)
        assert person.get_age() == 35

    def test_getter_before_setter(self):
        person = Person("Alice", 30)
        assert person.get_name() == "Alice"
        assert person.get_age() == 30

    def test_setter_update_values(self):
        person = Person("Alice", 30)
        person.set_name("Charlie")
        person.set_age(40)
        assert person.get_name() == "Charlie"
        assert person.get_age() == 40
    """
