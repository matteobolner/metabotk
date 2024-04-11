import argparse
from metabolomics_toolkit import MetaboTK


def main():
    """Metabolomics data analysis tool

    This tool allows users to perform various actions on metabolomics data,
    such as generating sample and metabolite statistics, and performing
    Principal Component Analysis (PCA) with different numbers of components.

    The tool can import data from an Excel file or separate tables. If the
    data is from an Excel file, the user must specify the sheet name. If the
    data is from separate tables, the user must specify the location of the
    data, sample metadata, and metabolite metadata files.

    The tool excludes by default xenobiotic metabolites from the analysis; the option --include_metabolites can be used to include them.

    The user must specify the action to perform using the --action argument.
    The valid actions are:

    * sample_stats: Print sample statistics
    * metabolite_stats: Print metabolite statistics
    * pca: Perform PCA analysis with the number of components specified by
      the --n_components argument

    The output is printed to stdout as a tab-delimited table.
    """

    # Create ArgumentParser instance
    parser = argparse.ArgumentParser(description=__doc__)

    # Add number of components argument
    parser.add_argument(
        "--sample_id_column",
        type=str,
        default="PARENT_SAMPLE_NAME",
        help="Name of the column containing the sample IDS",
    )
    parser.add_argument(
        "--metabolite_id_column",
        type=str,
        default="CHEM_ID",
        help="Name of the column containing the metabolite IDS",
    )

    # Add arguments
    parser.add_argument(
        "action",
        choices=["sample_stats", "metabolite_stats", "pca"],
        help="Action to perform",
    )
    group = parser.add_mutually_exclusive_group(required=True)

    # Add Excel file argument
    group.add_argument(
        "--excel",
        help="Path to the Excel file",
    )

    # Add tables argument
    group.add_argument(
        "--tables",
        nargs=3,
        metavar=("data", "samples", "metabolites"),
        help="Use separate tables for data, sample metadata, and metabolite metadata",
    )

    # Add sheet name argument
    parser.add_argument(
        "--sheet",
        help="Name of the sheet in Excel file (if applicable)",
        nargs="?",
    )

    # Add number of components argument
    parser.add_argument(
        "--n_components",
        type=int,
        default=3,
        help="Number of components for PCA",
    )

    parser.add_argument(
        "--exclude_xenobiotics",
        action="store_true",
        help="Exclude xenobiotics from analysis",
    )
    # Parse arguments
    args = parser.parse_args()

    # Create MetaboTK instance
    mt = MetaboTK(
        sample_id_column=args.sample_id_column,
        metabolite_id_column=args.metabolite_id_column,
    )
    # Import data based on provided options
    if args.excel:
        if args.sheet is None:
            print("Sheet name required for Excel file")
            return
        mt.import_excel(args.excel, args.sheet)
    elif args.tables:
        data, samples, metabolites = args.tables
        mt.import_tables(
            data=data,
            chemical_annotation=metabolites,
            sample_metadata=samples,
        )
    # Perform action based on user input
    if args.exclude_xenobiotics:
        mt.drop_xenobiotic_metabolites(inplace=True)
        # Drop xenobiotic metabolites if specified

    if args.action == "sample_stats":
        # Print sample statistics
        output = mt.sample_stats()
    elif args.action == "metabolite_stats":
        # Print metabolite statistics
        output = mt.metabolite_stats()
    elif args.action == "pca":
        # Perform PCA analysis with number of components specified
        output = mt.get_pca(n_components=args.n_components)
    else:
        print("Invalid action")
    # Print output to stdout as tab-delimited table
    print(output.to_csv(sep="\t"))


if __name__ == "__main__":
    main()
