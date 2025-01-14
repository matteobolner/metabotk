import pytest
import pandas as pd
from metabotk.parse_and_setup import (
    read_excel,
    read_tables,
    dataset_from_prefix,
    read_prefix,
    setup_data,
    setup_sample_metadata,
    setup_chemical_annotation,
)
import numpy as np


class Helper:
    @staticmethod
    def test_parsed_dict(parsed):
        assert isinstance(parsed, dict)
        assert list(parsed.keys()) == [
            "sample_metadata",
            "chemical_annotation",
            "data",
        ]
        assert parsed["sample_metadata"].shape == (46, 10)
        assert parsed["data"].shape == (46, 83)
        assert parsed["chemical_annotation"].shape == (82, 20)


@pytest.fixture
def helper():
    return Helper


def test_read_excel(helper):
    file_path = "tests/test_data/cdt_demo.xlsx"
    parsed = read_excel(file_path, data_sheet="Batch-normalized Data")
    helper.test_parsed_dict(parsed)


def test_read_tables(helper):
    data_path = "tests/test_data/data.csv"
    sample_metadata_path = "tests/test_data/sample_metadata.csv"
    chemical_annotation_path = "tests/test_data/chemical_annotation.csv"
    parsed = read_tables(sample_metadata_path, chemical_annotation_path, data_path)
    helper.test_parsed_dict(parsed)


def test_dataset_from_prefix():
    prefix = "tests/test_data/test"
    expected_dict = {
        "sample_metadata": "tests/test_data/test.samples",
        "chemical_annotation": "tests/test_data/test.metabolites",
        "data": "tests/test_data/test.data",
    }
    output = dataset_from_prefix(prefix)
    assert output == expected_dict


def test_read_prefix(helper):
    parsed = read_prefix("tests/test_data/test")
    helper.test_parsed_dict(parsed)


class TestSetupData:
    def test_setup_data_already_indexed(self):
        data = pd.read_csv("tests/test_data/data.csv")
        data_with_index = data.set_index("PARENT_SAMPLE_NAME")
        ready_data = setup_data(data_with_index, "PARENT_SAMPLE_NAME")
        assert ready_data.index.name == "PARENT_SAMPLE_NAME"

    def test_setup_data_not_indexed(self):
        data = pd.read_csv("tests/test_data/data.csv")
        ready_data = setup_data(data, "PARENT_SAMPLE_NAME")
        assert ready_data.index.name == "PARENT_SAMPLE_NAME"

    def test_setup_data_invalid_sample_id_column(self):
        data = pd.read_csv("tests/test_data/data.csv")
        with pytest.raises(ValueError):
            setup_data(data, "INVALID_COLUMN_NAME")

    def test_setup_data_column_types(self):
        data = pd.read_csv("tests/test_data/data.csv")
        data_with_index = data.set_index("PARENT_SAMPLE_NAME")
        ready_data = setup_data(data_with_index, "PARENT_SAMPLE_NAME")
        ready_data.columns = [int(i) for i in ready_data.columns]
        assert type(ready_data.columns[1]) is np.int64
        ready_data = setup_data(ready_data, "PARENT_SAMPLE_NAME")
        assert type(ready_data.columns[1]) is str


class TestSetupSampleMetadata:
    def test_setup_metadata_already_indexed(self):
        data = pd.read_csv("tests/test_data/sample_metadata.csv")
        data_with_index = data.set_index("PARENT_SAMPLE_NAME")
        ready_data = setup_sample_metadata(data_with_index, "PARENT_SAMPLE_NAME")
        assert ready_data.index.name == "PARENT_SAMPLE_NAME"

    def test_setup_metadata_not_indexed(self):
        data = pd.read_csv("tests/test_data/sample_metadata.csv")
        ready_data = setup_sample_metadata(data, "PARENT_SAMPLE_NAME")
        assert ready_data.index.name == "PARENT_SAMPLE_NAME"

    def test_setup_metadata_invalid_sample_id_column(self):
        data = pd.read_csv("tests/test_data/sample_metadata.csv")
        with pytest.raises(ValueError):
            setup_sample_metadata(data, "INVALID_COLUMN_NAME")

    def test_setup_metadata_column_types(self):
        data = pd.read_csv("tests/test_data/sample_metadata.csv")
        data_with_index = data.set_index("PARENT_SAMPLE_NAME")
        ready_data = setup_sample_metadata(data_with_index, "PARENT_SAMPLE_NAME")
        assert type(ready_data.columns[1]) is str

    def test_setup_metadata_duplicated_values(self):
        data = pd.read_csv("tests/test_data/sample_metadata.csv")
        with pytest.warns():
            setup_sample_metadata(data, "SUBGROUP")


class TestSetupChemicalAnnotation:
    def test_setup_metadata_already_indexed(self):
        data = pd.read_csv("tests/test_data/chemical_annotation.csv")
        data_with_index = data.set_index("CHEM_ID")
        ready_data = setup_chemical_annotation(data_with_index, "CHEM_ID")
        assert ready_data.index.name == "CHEM_ID"

    def test_setup_metadata_not_indexed(self):
        data = pd.read_csv("tests/test_data/chemical_annotation.csv")
        ready_data = setup_chemical_annotation(data, "CHEM_ID")
        assert ready_data.index.name == "CHEM_ID"

    def test_setup_metadata_invalid_sample_id_column(self):
        data = pd.read_csv("tests/test_data/chemical_annotation.csv")
        with pytest.raises(ValueError):
            setup_chemical_annotation(data, "INVALID_COLUMN_NAME")

    def test_setup_metadata_column_types(self):
        data = pd.read_csv("tests/test_data/chemical_annotation.csv")
        data_with_index = data.set_index("CHEM_ID")
        ready_data = setup_chemical_annotation(data_with_index, "CHEM_ID")
        assert type(ready_data.columns[1]) is str

    def test_setup_metadata_duplicated_values(self):
        data = pd.read_csv("tests/test_data/chemical_annotation.csv")
        with pytest.warns():
            setup_chemical_annotation(data, "SUPER_PATHWAY")
