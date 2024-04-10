import pytest
from metabolomics_toolkit import MetaboTK

def test_merge_data_sample_metadata():
    test_instance=MetaboTK(sample_id_column='PARENT_SAMPLE_NAME')
    test_instance.import_excel("data/cdt_demo.xlsx", data_sheet='batch_normalized_data')
    merged_data = test_instance.merge_sample_metadata_data()
    # Add assertions here to check if the merged data is as expected
    assert merged_data.shape[0] == 46  # Assuming 46 samples in the sample metadata
    assert merged_data.shape[1] == 91   # Assuming 91 columns in the metabolomic data
    assert merged_data.index.name == 'PARENT_SAMPLE_NAME'   # Assuming 5 columns in the metabolomic data

def test_sample_id_column_warning():
    with pytest.raises(ValueError):
        # Initialize MetaboTK with a data file that doesn't contain the specified sample_id_column
        metabotk_instance = MetaboTK(sample_id_column='CLIENT_IDENTIFIER')
        metabotk_instance.import_excel("data/cdt_demo.xlsx", data_sheet='batch_normalized_data')

def test_unsupported_data_provider():
    with pytest.raises(NotImplementedError):
        # Initialize MetaboTK with a data provider not supported
        metabotk_instance = MetaboTK(data_provider='biocrates')
