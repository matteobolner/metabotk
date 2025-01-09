import pytest
import pandas as pd
from metabotk.parse_and_setup import (
    parse_input,
    read_excel,
    read_tables,
    dataset_from_prefix,
    read_prefix,
    setup_data,
    setup_sample_metadata,
    setup_chemical_annotation,
)


class Helper:
    @staticmethod
    def test_parsed_dict(parsed):
        assert isinstance(parsed, dict)
        assert list(parsed.keys()) == ["sample_metadata", "chemical_annotation", "data"]
        assert parsed["sample_metadata"].shape == (46, 10)
        assert parsed["data"].shape == (46, 83)
        assert parsed["chemical_annotation"].shape == (82, 20)


@pytest.fixture
def helper():
    return Helper


class TestParseInput:
    def test_parse_input_pandas_dataframe(self):
        input_data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        assert parse_input(input_data).equals(input_data)

    def test_parse_input_tsv_file(self):
        tsv_file_path = "data/data.tsv"
        assert isinstance(parse_input(tsv_file_path), pd.DataFrame)

    def test_parse_input_csv_file(self):
        csv_file_path = "data/data.csv"
        assert isinstance(parse_input(csv_file_path), pd.DataFrame)

    def test_parse_invalid_extension(self):
        file_path = "data/test.pls"
        with pytest.raises(TypeError):
            parse_input(file_path)

    def test_parse_input_invalid_input(self):
        invalid_input = 123  # Not a DataFrame or a file path
        with pytest.raises(TypeError):
            parse_input(invalid_input)


def test_read_excel(helper):
    file_path = "data/cdt_demo.xlsx"
    parsed = read_excel(file_path)
    helper.test_parsed_dict(parsed)


def test_read_tables(helper):
    data_path = "data/data.csv"
    sample_metadata_path = "data/sample_metadata.csv"
    chemical_annotation_path = "data/chemical_annotation.csv"
    parsed = read_tables(sample_metadata_path, chemical_annotation_path, data_path)
    helper.test_parsed_dict(parsed)


def test_dataset_from_prefix():
    prefix = "data/test"
    expected_dict = {
        "sample_metadata": "data/test.samples",
        "chemical_annotation": "data/test.metabolites",
        "data": "data/test.data",
    }
    output = dataset_from_prefix(prefix)
    assert output == expected_dict


def test_read_prefix(helper):
    parsed = read_prefix("data/test")
    helper.test_parsed_dict(parsed)
