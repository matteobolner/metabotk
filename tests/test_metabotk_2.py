import pytest
import pandas as pd
from src.reader import MetabolonCDT
from src.statistics import StatisticsHandler
from src.utils import parse_input
from metabolomics_toolkit import MetaboTK


@pytest.fixture
def sample_metadata():
    # Path to sample metadata test data
    return pd.read_csv('data/sample_metadata.csv')

@pytest.fixture
def chemical_annotation():
    # Load chemical annotation test data
    return pd.read_csv('data/chemical_annotation.csv')

@pytest.fixture
def data():
    # Load main data test data
    return pd.read_csv('data/data.csv')

@pytest.fixture
def excel():
    # Load main data test data
    return 'data/cdt_demo.xlsx'

@pytest.fixture
def metabotk_instance(data, sample_metadata, chemical_annotation):
    # Initialize MetaboTK instance for testing
    metabotk = MetaboTK()
    metabotk.import_tables(data=data, chemical_annotation=chemical_annotation, sample_metadata=sample_metadata )
    return metabotk


class TestMetaboTK:

    def test_init(self):
        # Test MetaboTK initialization
        metabotk = MetaboTK()
        assert isinstance(metabotk.stats_handler, StatisticsHandler)

    def test_setup_data(self, data, sample_metadata, chemical_annotation):
        # Test setup_data function
        metabotk = MetaboTK()
        metabotk._setup_data(data=data, chemical_annotation=chemical_annotation, sample_metadata=sample_metadata)
        assert not metabotk.data.empty
        assert not metabotk.sample_metadata.empty
        assert not metabotk.chemical_annotation.empty

    def test_import_excel(self, data, sample_metadata, chemical_annotation):
        # Test import_excel function
        metabotk = MetaboTK()
        with pytest.raises(FileNotFoundError):
            metabotk.import_excel("nonexistent_file.xlsx", "data_sheet")

    def test_import_tables(self, data, sample_metadata, chemical_annotation):
        # Test import_tables function
        metabotk = MetaboTK()
        metabotk.import_tables(data=data, chemical_annotation=chemical_annotation, sample_metadata=sample_metadata)
        assert not metabotk.data.empty
        assert not metabotk.sample_metadata.empty
        assert not metabotk.chemical_annotation.empty

    def test_merge_sample_metadata_data(self, metabotk_instance):
        # Test merge_sample_metadata_data function
        merged = metabotk_instance.merge_sample_metadata_data()
        assert not merged.empty

    def test_save_empty(self, metabotk_instance):
        # Test save_merged function
        metabotk_instance=MetaboTK()
        with pytest.raises(ValueError):
            metabotk_instance.save_merged("empty.tsv")

    def test_replace_column_names(self, metabotk_instance):
        # Test replace_column_names function
        with pytest.raises(ValueError):
            metabotk_instance.replace_column_names("nonexistent_column")

    def test_drop_missing(self, metabotk_instance):
        # Test drop_missing function
        dropped_columns = metabotk_instance.drop_missing(axis=0)
        assert isinstance(dropped_columns, pd.DataFrame)

    def test_split_by_sample_column(self, metabotk_instance):
        # Test split_by_sample_column function
        split_data = metabotk_instance.split_by_sample_column("SUPERGROUP")
        assert isinstance(split_data, dict)

    def test_total_sum_abundance(self, metabotk_instance):
        # Test total_sum_abundance function
        tsa = metabotk_instance.total_sum_abundance()
        assert isinstance(tsa, pd.Series)

    def test_compute_stats(self, metabotk_instance):
        # Test compute_stats function
        metabotk_instance.compute_stats()
        assert not metabotk_instance.feature_stats.empty
        assert not metabotk_instance.sample_stats.empty

    def test_get_pca(self, metabotk_instance):
        # Test get_pca function
        metabotk_instance.get_pca()
        assert not metabotk_instance.PCA.empty
        assert metabotk_instance.PCA_object is not None

    # Add more tests for other methods of MetaboTK class
    # ...

@pytest.mark.parametrize("data_sheet", ["data", "other_sheet"])
def test_import_excel(data_sheet):
    # Test import_excel function
    metabotk = MetaboTK()
    with pytest.raises(FileNotFoundError):
        metabotk.import_excel("nonexistent_file.xlsx", data_sheet)

class TestMetaboTKReplaceColumnNames:

    def test_replace_column_names_nonexistent_column(self, metabotk_instance):
        # Test replace_column_names function when the specified column does not exist
        with pytest.raises(ValueError):
            metabotk_instance.replace_column_names("nonexistent_column")

class TestMetaboTKOutliers:

    def test_remove_outliers(self, metabotk_instance):
        # Test remove_outliers function
        with_outliers=metabotk_instance.data.copy()
        metabotk_instance.remove_outliers()
        # Check if any NaN values present, indicating removal of outliers
        assert not with_outliers.equals(metabotk_instance.data)

class TestMetaboTKExtraction:

    @pytest.mark.parametrize("metabolites_to_extract", ["50", "171"])
    def test_extract_metabolites(self, metabotk_instance, metabolites_to_extract):
        # Test extract_metabolites function
        extracted_data = metabotk_instance.extract_metabolites(metabolites_to_extract)
        assert not extracted_data.empty

    @pytest.mark.parametrize("samples_to_extract", ["INTR-03192 [COPY 2]", "INTR-03231 [COPY 2]"])
    def test_extract_samples(self, metabotk_instance, samples_to_extract):
        # Test extract_samples function
        extracted_data = metabotk_instance.extract_samples(samples_to_extract)
        assert not extracted_data.empty

    @pytest.mark.parametrize("metabolites_to_extract", ["50", "171"])
    def test_extract_chemical_annotations(self, metabotk_instance, metabolites_to_extract):
        # Test extract_chemical_annotations function
        extracted_annotations = metabotk_instance.extract_chemical_annotations(metabolites_to_extract)
        assert not extracted_annotations.empty

class TestMetaboTKSplit:

    @pytest.mark.parametrize("column", ["SUPERGROUP", "SUBGROUP"])
    def test_split_by_sample_column(self, metabotk_instance, column):
        # Test split_by_sample_column function
        split_data = metabotk_instance.split_by_sample_column(column)
        assert isinstance(split_data, dict)

    @pytest.mark.parametrize("column", ["SUPER_PATHWAY", "SUB_PATHWAY"])
    def test_split_by_metabolite_column(self, metabotk_instance, column):
        # Test split_by_metabolite_column function
        split_data = metabotk_instance.split_by_metabolite_column(column)
        assert isinstance(split_data, dict)

# Add more test classes for other classes if necessary

if __name__ == "__main__":
    pytest.main()
