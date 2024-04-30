import pytest
import pandas as pd
from metabotk.providers_handler import MetabolonCDT
from metabotk.statistics_handler import StatisticsHandler
from metabotk.utils import parse_input
from metabotk.interface import MetaboTK


@pytest.fixture
def sample_metadata():
    # Path to sample metadata test data
    return pd.read_csv("data/sample_metadata.csv")


@pytest.fixture
def chemical_annotation():
    # Load chemical annotation test data
    return pd.read_csv("data/chemical_annotation.csv")


@pytest.fixture
def data():
    # Load main data test data
    return pd.read_csv("data/data.csv")


@pytest.fixture
def excel():
    # Load main data test data
    return "data/cdt_demo.xlsx"


@pytest.fixture
def metabotk_instance(data, sample_metadata, chemical_annotation):
    # Initialize MetaboTK instance for testing
    metabotk = MetaboTK()
    metabotk.import_tables(
        data=data,
        chemical_annotation=chemical_annotation,
        sample_metadata=sample_metadata,
    )
    return metabotk


class TestMetaboTK:

    def test_init(self):
        # Test MetaboTK initialization
        metabotk = MetaboTK()
        assert isinstance(metabotk.stats, StatisticsHandler)

    def test_setup_data(self, data, sample_metadata, chemical_annotation):
        # Test setup_data function
        metabotk = MetaboTK()
        metabotk._setup_data(
            data=data,
            chemical_annotation=chemical_annotation,
            sample_metadata=sample_metadata,
        )
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
        metabotk.import_tables(
            data=data,
            chemical_annotation=chemical_annotation,
            sample_metadata=sample_metadata,
        )
        assert not metabotk.data.empty
        assert not metabotk.sample_metadata.empty
        assert not metabotk.chemical_annotation.empty

    def test_merge_sample_metadata_data(self, metabotk_instance):
        # Test merge_sample_metadata_data function
        merged = metabotk_instance.merge_sample_metadata_data()
        assert not merged.empty

    def test_save_empty(self, metabotk_instance):
        # Test save_merged function
        metabotk_instance = MetaboTK()
        with pytest.raises(ValueError):
            metabotk_instance.save_merged("empty.tsv")

    def test_replace_column_names(self, metabotk_instance):
        # Test replace_column_names function
        with pytest.raises(ValueError):
            metabotk_instance.replace_column_names("nonexistent_column")

    def test_drop_missing(self, metabotk_instance):
        # Test drop_missing function
        dropped_columns = (
            metabotk_instance.stats.missing_handler.drop_missing_from_dataframe(
                metabotk_instance.data, axis=0
            )
        )
        assert isinstance(dropped_columns, pd.DataFrame)

    def test_split_by_sample_column(self, metabotk_instance):
        # Test split_by_sample_column function
        split_data = metabotk_instance.split_by_sample_column("SUPERGROUP")
        assert isinstance(split_data, dict)

    def test_total_sum_abundance(self, metabotk_instance):
        # Test total_sum_abundance function
        tsa = metabotk_instance.stats.total_sum_abundance(metabotk_instance.data)
        assert isinstance(tsa, pd.Series)

    def test_compute_stats(self, metabotk_instance):
        # Test compute_stats function
        sample_stats = metabotk_instance.stats.sample_stats()
        metabolite_stats = metabotk_instance.stats.metabolite_stats()
        assert not sample_stats.empty
        assert not metabolite_stats.empty

    def test_get_pca(self, metabotk_instance):
        # Test get_pca function
        pca = metabotk_instance.dimensionality_reduction.get_pca(
            n_components=3,
            get_pca_object=False,
        )
        print(pca.shape)
        assert isinstance(pca, pd.DataFrame)
        assert pca.shape == (
            metabotk_instance.data.shape[0],
            3 + len(metabotk_instance.sample_metadata.columns),
        )

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
        with_outliers = metabotk_instance.data.copy()
        removed_outliers = metabotk_instance.stats.outlier_handler.remove_outliers(
            with_outliers, threshold=5
        )
        # Check if any NaN values present, indicating removal of outliers
        assert not with_outliers.equals(removed_outliers)


class TestMetaboTKExtraction:

    @pytest.mark.parametrize("metabolites_to_extract", ["50", "171"])
    def test_extract_metabolites(self, metabotk_instance, metabolites_to_extract):
        # Test extract_metabolites function
        extracted_data = metabotk_instance.extract_metabolites(metabolites_to_extract)
        assert not extracted_data.empty

    @pytest.mark.parametrize(
        "samples_to_extract", ["INTR-03192 [COPY 2]", "INTR-03231 [COPY 2]"]
    )
    def test_extract_samples(self, metabotk_instance, samples_to_extract):
        # Test extract_samples function
        extracted_data = metabotk_instance.extract_samples(samples_to_extract)
        assert not extracted_data.empty

    @pytest.mark.parametrize("metabolites_to_extract", ["50", "171"])
    def test_extract_chemical_annotations(
        self, metabotk_instance, metabolites_to_extract
    ):
        # Test extract_chemical_annotations function
        extracted_annotations = metabotk_instance.extract_chemical_annotations(
            metabolites_to_extract
        )
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


def test_merge_data_sample_metadata():
    test_instance = MetaboTK(sample_id_column="PARENT_SAMPLE_NAME")
    test_instance.import_excel("data/cdt_demo.xlsx", data_sheet="batch_normalized_data")
    merged_data = test_instance.merge_sample_metadata_data()
    # Add assertions here to check if the merged data is as expected
    assert merged_data.shape[0] == 46  # Assuming 46 samples in the sample metadata
    assert merged_data.shape[1] == 91  # Assuming 91 columns in the metabolomic data
    assert (
        merged_data.index.name == "PARENT_SAMPLE_NAME"
    )  # Assuming 5 columns in the metabolomic data


def test_sample_id_column_warning():
    with pytest.raises(ValueError):
        # Initialize MetaboTK with a data file that doesn't contain the specified sample_id_column
        metabotk_instance = MetaboTK(sample_id_column="CLIENT_IDENTIFIER")
        metabotk_instance.import_excel(
            "data/cdt_demo.xlsx", data_sheet="batch_normalized_data"
        )


def test_unsupported_data_provider():
    with pytest.raises(NotImplementedError):
        # Initialize MetaboTK with a data provider not supported
        metabotk_instance = MetaboTK(data_provider="biocrates")
