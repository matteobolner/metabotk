from metabotk.metabolomic_dataset import MetabolomicDataset
import pandas as pd
from typing import Literal


class DatasetProcessor(MetabolomicDataset):
    def merge_sample_metadata_data(self) -> pd.DataFrame:
        """
        Merge sample metadata and metabolite abundance data into a single DataFrame.
        This method merges the sample metadata and the metabolite abundance data
        by matching the sample IDs in both dataframes. The resulting DataFrame
        contains all the columns from both the sample metadata and the data.
        The sample IDs in the data are used as the index for the merge, and the
        resulting dataframe will have the same index as the data.
        Returns:
            DataFrame: Merged DataFrame containing sample metadata and data.
        """
        # Merge sample metadata and data by matching sample IDs
        merged = self.sample_metadata.merge(
            self.data, left_index=True, right_index=True, how="inner"
        )
        return merged

    def replace_metabolite_names_in_data(self, new_column: str) -> None:
        # Check that the column exists in the metabolite metadata
        if new_column not in self.chemical_annotation.columns:
            raise ValueError(f"No column named {new_column} in the metabolite metadata")

        # Create dictionary for renaming
        renaming_dict = {
            old: new
            for old, new in zip(
                self.chemical_annotation.index, self.chemical_annotation[new_column]
            )
        }

        # Perform the renaming
        self.data.columns = [renaming_dict[old] for old in self.data.columns]

        # Update the name of the column used for feature identification in the data
        self.metabolite_id_column = new_column

        # Reset the index of the chemical annotation to match the new column name and update
        self.chemical_annotation = self.chemical_annotation.reset_index().set_index(
            new_column
        )

    def replace_sample_names_in_data(self, new_index: str):
        # Check that the column exists in the sample metadata
        if new_index not in self.sample_metadata.columns:
            raise ValueError(f"No column named {new_index} in the metabolite metadata")

        renaming_dict = {
            old: new
            for old, new in zip(
                self.sample_metadata.index, self.sample_metadata[new_index]
            )
        }

        # Perform the renaming
        # TODO: check if line below works or index name gets lost after setting new index
        self.data.index.rename_axis(new_index, axis="index")
        self.data.index = [renaming_dict[old] for old in self.data.index]
        # Update the name of the column used for feature identification in the data
        self.sample_id_column = new_index

        # Reset the index of the sample metadata to match the new index name and update
        self.sample_metadata = self.sample_metadata.reset_index().set_index(new_index)

    def _split_by_sample_column(
        self, sample_columns: list
    ) -> dict[str, MetabolomicDataset]:
        """
        Split the dataset (data and sample metadata) in multiple independent DataClass instances
        based on the values of one or more sample metadata columns.

        This function splits the dataset into multiple independent DataClass instances, each
        containing a subset of the data based on the values of a sample metadata column. The
        function returns a dictionary containing the split data, where the dictionary keys are
        the unique values of the sample metadata column and the values are the DataClass instances
        containing the split data.

        Args:
            column: The name of the column in the sample metadata DataFrame to use for splitting.

        Returns:
            A dictionary containing the split data, where the dictionary keys are the unique
            values of the sample metadata column and the values are the DataClass instances
            containing the split data.
        """
        split_datasets = {}
        for name, group in self.sample_metadata.groupby(by=sample_columns):
            temp_data = self.data.loc[group.index]
            temp_dataset = MetabolomicDataset._setup(
                data=temp_data,
                sample_metadata=group.reset_index(),
                chemical_annotation=self.chemical_annotation.reset_index(),
                sample_id_column=self.sample_id_column,
                metabolite_id_column=self.metabolite_id_column,
            )
            split_datasets[name] = temp_dataset
        return split_datasets

    def _split_by_metabolite_column(
        self, metabolite_columns: list
    ) -> dict[str, MetabolomicDataset]:
        """
        Split the data in multiple independent DataClass instances
        based on the values of a metabolite metadata column

        Parameters:
        column (str): Name of the column in the metabolite metadata table to use for splitting

        Returns:
        dict[str, DatasetManager]: dictionary where keys are the unique values present in the column and values are the corresponding DataClass instances
        """
        split_dataset = {}
        for name, group in self.chemical_annotation.groupby(by=metabolite_columns):
            temp_data = self.data[list(group.index)]
            temp_dataset = MetabolomicDataset._setup(
                data=temp_data,
                sample_metadata=self.sample_metadata.reset_index(),
                chemical_annotation=group.reset_index(),
                sample_id_column=self.sample_id_column,
                metabolite_id_column=self.metabolite_id_column,
            )
            split_dataset[name] = temp_dataset
        return split_dataset

    def split(
        self, by: Literal["samples", "metabolites"] = "samples", columns: list[str] = []
    ):
        if by == "samples":
            return self._split_by_sample_column(columns)
        elif by == "metabolites":
            return self._split_by_metabolite_column(columns)

    def _subset_samples(self, samples_to_subset: list[str] | str) -> MetabolomicDataset:
        if not isinstance(samples_to_subset, list):
            samples_to_subset = [samples_to_subset]
        remaining_data = self.data.loc[samples_to_subset]
        remaining_sample_metadata = self.sample_metadata.loc[samples_to_subset]
        return MetabolomicDataset._setup(
            data=remaining_data,
            sample_metadata=remaining_sample_metadata,
            chemical_annotation=self.chemical_annotation,
            sample_id_column=self.sample_id_column,
            metabolite_id_column=self.metabolite_id_column,
        )

    def _subset_metabolites(
        self, metabolites_to_subset: list[str] | str
    ) -> MetabolomicDataset:
        """

        Args:
            metabolites_to_subset:

        Returns:

        """
        if not isinstance(metabolites_to_subset, list):
            metabolites_to_subset = [metabolites_to_subset]

        remaining_data = self.data[metabolites_to_subset]

        remaining_chemical_annotation = self.chemical_annotation.loc[
            metabolites_to_subset
        ]
        return MetabolomicDataset._setup(
            data=remaining_data,
            sample_metadata=self.sample_metadata,
            chemical_annotation=remaining_chemical_annotation,
            sample_id_column=self.sample_id_column,
            metabolite_id_column=self.metabolite_id_column,
        )

    def subset(
        self,
        what: Literal["samples", "metabolites"] = "samples",
        ids: list[str] | str = [],
    ) -> MetabolomicDataset:
        if what == "samples":
            return self._subset_samples(ids)
        elif what == "metabolites":
            return self._subset_metabolites(ids)

    def _drop_samples(self, samples_to_drop: list[str] | str) -> MetabolomicDataset:
        """
        Drop specified samples from the dataset.
        Args:
            samples_to_drop:

        Returns:

        """
        if not isinstance(samples_to_drop, list):
            samples_to_drop = [samples_to_drop]
        remaining_samples = list(set(self.samples).difference(set(samples_to_drop)))
        return self._subset_samples(remaining_samples)

    def _drop_metabolites(
        self, metabolites_to_drop: list[str] | str
    ) -> MetabolomicDataset:
        """
        Drop specified metabolites from the dataset.
        Args:
            metabolites_to_drop:

        Returns:

        """
        remaining_metabolites = list(
            set(self.metabolites).difference(metabolites_to_drop)
        )
        return self._subset_metabolites(remaining_metabolites)

    def drop(
        self,
        what: Literal["samples", "metabolites"] = "samples",
        ids: list[str] | str = [],
    ):
        if what == "samples":
            return self._drop_samples(ids)
        elif what == "metabolites":
            return self._drop_metabolites(ids)

    def _sort_samples(
        self, by: list[str] | str, ascending: bool = True
    ) -> MetabolomicDataset:
        """

        Args:
            by:
            ascending:
        """
        self.sample_metadata = self.sample_metadata.sort_values(
            by=by, ascending=ascending
        )
        return self.subset(what="samples", ids=list(self.sample_metadata.index))

    def _sort_metabolites(
        self, by: list[str] | str, ascending: bool = True
    ) -> MetabolomicDataset:
        """

        Args:
            by:
            ascending:
        """
        self.chemical_annotation = self.chemical_annotation.sort_values(
            by=by, ascending=ascending
        )
        self.data = self.data[self.chemical_annotation.index]

        return self.subset(what="metabolites", ids=list(self.chemical_annotation.index))

    def sort(
        self,
        on: Literal["samples", "metabolites"] = "samples",
        by: list[str] = [],
        ascending: bool = True,
    ) -> MetabolomicDataset:
        if on == "samples":
            return self._sort_samples(by, ascending)
        elif on == "metabolites":
            return self._sort_metabolites(by, ascending)
