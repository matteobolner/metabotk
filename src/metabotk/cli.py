#!/usr/bin/env python
from typing import Union
import os
import argparse
from metabotk.interface import MetaboTK
from metabotk.utils import create_directory


def cli():
    """
    Command line interface for MetaboTK.

    This function is the entry point for the command line interface of MetaboTK. It sets up
    the command line arguments and passes them to the main analysis function.

    """

    parser = argparse.ArgumentParser(description="Metabolomics data analysis tool")

    parser.add_argument_group()

    ###INPUT ARGUMENTS

    input_group = parser.add_argument_group(
        "Input", "Options for reading in input data"
    )
    input_options = input_group.add_mutually_exclusive_group()
    input_options.add_argument(
        "-ie",
        "--excel",
        dest="excel",
        nargs=2,
        metavar=("file", "data_sheet"),
        help="Specify the excel file and the sheet from which to extract data",
    )
    input_options.add_argument(
        "-it",
        "--tables",
        dest="tables",
        nargs=3,
        metavar=("data", "samples", "metabolites"),
        help="Specify three tsv files: data, samples, and metabolites, in this order",
    )
    input_group.add_argument(
        "-sid",
        "--sample_id",
        dest="sample_id",
        metavar=("colname"),
        help="Specify the column name for sample IDs (must be present in both sample metadata and data); if not specified, the program will try to use the name of the first column in the data table",
    )
    input_group.add_argument(
        "-mid",
        "--metabolite_id",
        dest="metabolite_id",
        metavar=("colname"),
        help="Specify the column name for metabolite IDs in the chemical annotation; the metabolite IDs\
            in the column must correspond to the column names of the data table.\
            If not specified, the program will try to use CHEM_ID",
    )

    ###OUTPUT ARGUMENTS

    output_group = parser.add_argument_group("Output", "Output options")
    output_options = output_group.add_mutually_exclusive_group()
    output_options.add_argument(
        "-oe",
        "--output-excel",
        dest="output_excel",
        nargs=2,
        metavar=("file", "data_sheet"),
        help="Save the dataset to an excel file; if the file already exists, only the data will be appended as a new sheet",
    )
    output_options.add_argument(
        "-ot",
        "--output-tables",
        dest="output_tables",
        nargs=3,
        metavar=("data", "metabolites", "samples"),
        help="Save the dataset to three tsv files: data, metabolites and samples, in this order",
    )

    output_options.add_argument(
        "-od",
        "--output-data",
        dest="output_data",
        nargs=1,
        metavar=("data"),
        help="Save only the data to a TSV file",
    )

    ###SPLIT DATASET

    manipulation_group = parser.add_argument_group(
        "Manipulation", "Dataset manipulation"
    )
    manipulation_options = manipulation_group.add_mutually_exclusive_group()
    manipulation_options.add_argument(
        "-ss",
        "--split-samples",
        dest="split_samples",
        nargs=3,
        metavar=("sample_column", "output_dir", "output_format"),
        default=None,
        help="Split the dataset into multiple DataClass instances based on the values of a sample metadata column, and save each instance to a separate file in the output directory",
    )
    manipulation_options.add_argument(
        "-sm",
        "--split-metabolites",
        dest="split_metabolites",
        nargs=3,
        metavar=("metabolite_column", "output_dir", "output_format"),
        default=None,
        help="Split the dataset into multiple DataClass instances based on the values of a metabolite metadata column, and save each instance to a separate file in the output directory",
    )
    manipulation_options.add_argument(
        "--stratified-kfold",
        dest="stratified_kfold",
        nargs=3,
        metavar=("n_splits", "stratification_column", "output_dir"),
        default=None,
        help="Split the dataset into n_splits folds, and save each training and validation group to a separate file in the output directory. The samples in the folds will be stratified on the specified column",
    )

    ###ANALYSIS ARGUMENTS

    analysis_group = parser.add_argument_group("Analysis", "Analysis options")
    analysis_options = analysis_group.add_mutually_exclusive_group()
    analysis_group.add_argument(
        "--exclude-xenobiotics",
        dest="exclude_xenobiotics",
        action="store_true",
        help="Exclude xenobiotic metabolites from the analysis",
    )
    analysis_group.add_argument(
        "--outlier-threshold",
        dest="outlier_threshold",
        nargs="?",
        default=5,
        type=float,
        help="Numeric threshold for the outlier detection; default value is 5",
    )

    analysis_options.add_argument(
        "--sample-stats",
        action="store_true",
        dest="sample_stats",
        help="Print to stdout the sample statistics for the entire dataset",
    )

    analysis_options.add_argument(
        "--metabolite-stats",
        dest="metabolite_stats",
        action="store_true",
        help="Print to stdout each metabolite's statistics for the entire dataset",
    )
    analysis_options.add_argument(
        "--remove-outliers",
        dest="remove_outliers",
        action="store_true",
        help="Remove metabolite outlier values from the dataset and replace them with NAs; \
            outliers are computed column-wise;the data without outliers will be printed to stdout",
    )

    analysis_options.add_argument(
        "--fit-model",
        dest="fit_model",
        nargs="+",
        metavar=("formula", "model_dir"),
        help="Fit a linear model to each metabolite and print the residuals to stdout; optionally, save the models as pickle files in a folder of choice",
    )

    analysis_options.add_argument(
        "--PCA",
        dest="PCA",
        nargs="?",
        default=None,
        help="Perform a PCA on the dataset and print the results to stdout; number of components must be specified",
    )
    ###FEATURE SELECTION
    fs_group = parser.add_argument_group(
        "Feature Selection", "Feature selection methods and options"
    )
    fs_group.add_argument(
        "--feature-selection",
        dest="fs_method",
        nargs="?",
        default=None,
        help="Which feature selection method to use, default is boruta",
    )

    fs_group.add_argument(
        "-y",
        "--y_column",
        dest="y_column",
        help="Column containing target values",
        default=None,
    )
    fs_group.add_argument(
        "-t",
        "--threads",
        dest="threads",
        help="Threads to use, default is 1",
        default=1,
        type=int,
    )
    fs_group.add_argument(
        "-a",
        "--alpha",
        dest="alpha",
        help="Alpha (p-value threshold), default is 0.01",
        default=0.01,
        type=float,
    )

    fs_group.add_argument(
        "-r",
        "--random-state",
        dest="random_state",
        help="Random state seed, default is 42",
        default=42,
        type=int,
    )
    fs_group.add_argument(
        "-d",
        "--max-depth",
        dest="max_depth",
        help="BORUTA:Max depth of the tree, default is None",
        default=None,
        type=Union[None, int],
    )
    fs_group.add_argument(
        "-w",
        "--class-weight",
        dest="class_weight",
        help="BORUTA: Class weights, default is balanced",
        default="balanced",
    )
    fs_group.add_argument(
        "-n",
        "--n-estimators",
        dest="n_estimators",
        help="BORUTA: Number of estimators, default is 1000",
        default="auto",
    )
    fs_group.add_argument(
        "-i",
        "--max-iterations",
        dest="max_iterations",
        help="BORUTA: Max iterations. default is 1000",
        default=1000,
        type=int,
    )
    fs_group.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        help="BORUTA: Output directory for saving rankings, model and importance history, default is None (print ranking only to stdout)",
        default=None,
    )

    args = parser.parse_args()

    ########SET UP METABOTK INSTANCE

    if args.sample_id:
        sample_id_column = args.sample_id
    else:
        sample_id_column = None

    if args.metabolite_id:
        metabolite_id_column = args.metabolite_id
    else:
        metabolite_id_column = "CHEM_ID"

    metabotk_instance = MetaboTK(
        sample_id_column=sample_id_column, metabolite_id_column=metabolite_id_column
    )

    ###READ INPUT DATA
    if args.excel:
        metabotk_instance.import_excel(
            file_path=args.excel[0],
            data_sheet=args.excel[1],
        )
    elif args.tables:
        metabotk_instance.import_tables(
            data=args.tables[0],
            sample_metadata=args.tables[1],
            chemical_annotation=args.tables[2],
        )

    ###ANALYZE DATA
    if args.sample_stats:
        sample_stats = metabotk_instance.sample_stats(
            outlier_threshold=args.outlier_threshold,
            exclude_xenobiotics=args.exclude_xenobiotics,
        )
        print(sample_stats.to_csv(sep="\t"))

    if args.metabolite_stats:
        metabolite_stats = metabotk_instance.metabolite_stats(
            outlier_threshold=args.outlier_threshold
        )
        print(metabolite_stats.to_csv(sep="\t"))

    if args.remove_outliers:
        outliers_removed = metabotk_instance.stats.outlier_handler.remove_outliers(
            data_frame=metabotk_instance.data,
            axis=0,
            threshold=args.outlier_threshold,
        )
        print(outliers_removed.to_csv(sep="\t"))

    ### FIT MODELS
    if args.fit_model:
        if len(args.fit_model) == 2:
            residuals = metabotk_instance.models.get_linear_model_residuals(
                formula=args.fit_model[0], models_path=args.fit_model[1]
            )
        else:
            residuals = metabotk_instance.models.get_linear_model_residuals(
                formula=args.fit_model[0], models_path=None
            )
        print(residuals.to_csv(sep="\t"))

    ### PCA

    if args.PCA:
        pca = metabotk_instance.dimensionality_reduction.get_pca(
            n_components=int(args.PCA), get_pca_object=False
        )
        print(pca.to_csv(sep="\t"))

    ### FEATURE SELECTION:
    if args.fs_method:
        if args.fs_method == "boruta":
            ranking = metabotk_instance.feature_selection.boruta(
                y_column=args.y_column,
                threads=args.threads,
                random_state=args.random_state,
                max_depth=args.max_depth,
                class_weight=args.class_weight,
                n_estimators=args.n_estimators,
                alpha=args.alpha,
                max_iterations=args.max_iterations,
                output_dir=args.output_dir,
            )
            print(ranking.to_csv(sep="\t"))

    ###SPLIT DATA
    if args.split_samples:
        if not args.split_samples[0]:
            raise ValueError("No column specified for splitting data")
        else:
            split_samples_dict = metabotk_instance.split_by_sample_column(
                column=args.split_samples[0]
            )
        outdir = args.split_samples[1]
        create_directory(outdir)
        for k, v in split_samples_dict.items():
            k = k.replace(" ", "_").replace("/", "_").replace("-", "_")
            if args.split_samples[2] == "excel":
                v.save_excel(f"{outdir}/{k}.xlsx")
            else:
                v.save_tables(
                    data_path=f"{outdir}/{k}_data.tsv",
                    chemical_annotation_path=f"{outdir}/{k}_metabolites.tsv",
                    sample_metadata_path=f"{outdir}/{k}_samples.tsv",
                )

    if args.split_metabolites:
        if not args.split_metabolites[0]:
            raise ValueError("No column specified for splitting data")
        else:
            split_metabolites_dict = metabotk_instance.split_by_metabolite_column(
                column=args.split_metabolites[0]
            )
        outdir = args.split_metabolites[1]
        create_directory(outdir)
        for k, v in split_metabolites_dict.items():
            k = k.replace(" ", "_").replace("/", "_").replace("-", "_")
            if args.split_metabolites[2] == "excel":
                v.save_excel(f"{outdir}/{k}.xlsx")
            else:
                v.save_tables(
                    data_path=f"{outdir}/{k}_data.tsv",
                    chemical_annotation_path=f"{outdir}/{k}_metabolites.tsv",
                    sample_metadata_path=f"{outdir}/{k}_samples.tsv",
                )
    if args.stratified_kfold:
        metabotk_instance.feature_selection.stratified_kfold(
            n_splits=args.stratified_kfold[0],
            stratification_column=args.stratified_kfold[1],
            output_dir=args.stratified_kfold[2],
        )

    ###SAVE DATA

    if args.output_excel:
        if os.path.exists(args.output_excel[0]):
            metabotk_instance.add_to_excel(
                file_path=args.output_excel[0],
                new_sheet=metabotk_instance.data,
                new_sheet_name=args.output_excel[1],
            )
        else:
            metabotk_instance.save_excel(
                file_path=args.output_excel[0], data_sheet=args.output_excel[1]
            )

    if args.output_tables:
        metabotk_instance.save_tables(
            args.output_tables[0], args.output_tables[1], args.output_tables[2]
        )


if __name__ == "__main__":
    cli()
