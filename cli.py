import argparse
from metabolomics_toolkit import MetaboTK


def main():
    """Metabolomics data analysis tool"""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample-id-column",
        default="PARENT_SAMPLE_NAME",
        help="Name of the column containing sample IDs",
    )
    parser.add_argument(
        "--metabolite-id-column",
        default="CHEM_ID",
        help="Name of the column containing metabolite IDs",
    )
    parser.add_argument(
        "action",
        choices=["sample_stats", "metabolite_stats", "pca"],
        help="Action to perform",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--excel", help="Path to Excel file")
    group.add_argument(
        "--tables",
        help="Use separate tables for data, sample metadata, and metabolite metadata",
    )

    args = parser.parse_args()

    mt = MetaboTK(
        sample_id_column=args.sample_id_column,
        metabolite_id_column=args.metabolite_id_column,
    )

    if args.excel:
        mt.import_excel(args.excel)
    else:
        data, samples, metabolites = args.tables.split()
        mt.import_tables(data, metabolites, samples)

    if args.action == "sample_stats":
        output = mt.sample_stats()
    elif args.action == "metabolite_stats":
        output = mt.metabolite_stats()
    elif args.action == "pca":
        output = mt.get_pca()

    print(output.to_csv(sep="\t"))


if __name__ == "__main__":
    main()
