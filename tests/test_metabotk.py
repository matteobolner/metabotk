import pytest
from src.metabotk import MetaboTK
@pytest.fixture
def metabotk_instance():
    # Set up a sample instance of MetaboTK for testing
    return MetaboTK(metabolomic_data='data/cdt_demo.xlsx', sample_metadata='sample_metadata.csv')

def test_merge_data_sample_metadata(metabotk_instance):
    merged_data = metabotk_instance.merge_data_sample_metadata()
    # Add assertions here to check if the merged data is as expected
    assert merged_data.shape[0] == 10  # Assuming 10 samples in the sample metadata
    assert merged_data.shape[1] == 5   # Assuming 5 columns in the metabolomic data

def test_sample_column_warning():
    with pytest.warns(UserWarning):
        # Initialize MetaboTK with a data file that doesn't contain the specified sample_column
        metabotk_instance = MetaboTK(metabolomic_data='sample_data.csv', sample_column='non_existing_column')
