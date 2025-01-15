import pandas as pd
import pytest
from metabotk.providers_handler import MetabolonCDT
import os


# Fixture to create a sample MetabolonCDT instance
@pytest.fixture
def metabolon_instance():
    return MetabolonCDT()


# Test case to check if required sheets are missing
def test_read_metabolon_excel_missing_sheets(metabolon_instance):
    # Create a mock Excel file with missing sheets
    mock_excel_path = "tests/mock_missing_sheets.xlsx"
    pd.DataFrame().to_excel(mock_excel_path)  # Empty Excel file

    # Test that ValueError is raised if required sheets are missing
    with pytest.raises(ValueError):
        metabolon_instance.import_excel(mock_excel_path)
    os.remove(mock_excel_path)


# Test case to check if sheets are correctly assigned
def test_read_metabolon_excel(metabolon_instance):
    test_excel_path = "data/cdt_demo.xlsx"
    # Test that sheets are correctly assigned to attributes
    metabolon_instance.import_excel(test_excel_path)
    assert metabolon_instance.sample_metadata is not None
    assert metabolon_instance.chemical_annotation is not None
    assert metabolon_instance.peak_area_data is not None


# Test case to check reading flat tables
def test_read_metabolon_flat_tables(metabolon_instance):
    # Mock data frames for sample metadata and chemical annotation
    sample_metadata_df = pd.DataFrame({"ID": [1, 2, 3], "Name": ["A", "B", "C"]})
    chemical_annotation_df = pd.DataFrame(
        {"Compound": ["X", "Y", "Z"], "Mass": [100, 200, 300]}
    )

    # Test reading flat tables
    metabolon_instance.import_tables(sample_metadata_df, chemical_annotation_df)
    assert metabolon_instance.sample_metadata.shape == (3, 2)
    assert metabolon_instance.chemical_annotation.shape == (3, 2)
