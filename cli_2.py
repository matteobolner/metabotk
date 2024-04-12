#!/usr/bin/env python

import os
import argparse
from metabolomics_toolkit import MetaboTK

parser = argparse.ArgumentParser(description="Metabolomics data analysis tool")

parser.add_argument_group()

###INPUT ARGUMENTS

input_group = parser.add_argument_group("Input", "Options for reading in input data")
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
    metavar=("data", "samples", "metabolites"),
    help="Save the dataset to three tsv files: data, samples, and metabolites, in this order",
)
output_options.add_argument(
    "-od",
    "--output-data",
    dest="output_data",
    nargs=1,
    metavar=("data"),
    help="Save only the data to a TSV file",
)

###ANALYSIS ARGUMENTS

analysis_group = parser.add_argument_group("Analysis", "Analysis options")
analysis_options = analysis_group.add_mutually_exclusive_group()
analysis_options.add_argument(
    "--exclude-xenobiotics",
    dest="exclude_xenobiotics",
    action="store_false",
    help="Exclude xenobiotic metabolites from the analysis",
)
analysis_options.add_argument(
    "--outlier-threshold",
    dest="outlier_threshold",
    nargs="?",
    const=5,
    type=float,
    help="Numeric threshold for the outlier detection; default value is 5",
)

analysis_options.add_argument(
    "--sample-stats",
    dest="sample_stats",
    help="Print to stdout the sample statistics for the entire dataset",
)

analysis_options.add_argument(
    "--metabolite-stats",
    dest="metabolite_stats",
    nargs="?",
    const=5,
    type=float,
    metavar="per_metabolite_or_sample",
    help="Print to stdout each metabolite's statistics for the entire dataset",
)
analysis_options.add_argument(
    "--remove-outliers",
    dest="remove_outliers",
    nargs="?",
    metavar="per_metabolite_or_sample",
    help="Remove metabolite outlier values from the dataset and replace them with NAs; \
        outliers can be computed per metabolite (over all samples, default) or per sample (over all metabolites)\
        the data without outliers will be printed to stdout",
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
    outliers_removed = metabotk_instance.remove_outliers(
        outlier_threshold=args.outlier_threshold,
    )
    print(metabolite_stats.to_csv(sep="\t"))


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
