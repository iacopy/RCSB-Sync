"""
RCSB query generator.

This module contains the functions to generate the advanced queries to be sent to the RCSB website.

The advanced query is a json string containing the search criteria.
The json string can be generated manually or using the functions in this module.
The advanced query can be used to retrieve the list of PDB IDs from the RCSB website.

Usage example:
    python rcsbquery.py -p Protein -o "Rattus norvegicus" -m "X-RAY DIFFRACTION" "SOLUTION NMR" --csm
"""
# Standard Library
import argparse
import json
import logging
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# 3rd party
import yaml
from yaml.loader import SafeLoader

# Default values for query generation
DEFAULT_POLYMER_TYPE = "Protein"
DEFAULT_METHODS = ["X-RAY DIFFRACTION", "SOLUTION NMR", "ELECTRON MICROSCOPY"]
DEFAULT_RESULTS_CONTENT_TYPE = ("experimental",)
DEFAULT_ROWS = 999999


def generate_request_options(
    results_content_type: tuple = ("experimental",), rows: int = 25
) -> dict:
    """
    Generate the request options.
    """
    return {
        "paginate": {"start": 0, "rows": rows},
        "results_content_type": results_content_type,
        "sort": [{"sort_by": "score", "direction": "desc"}],
        "scoring_strategy": "combined",
    }


def generate_terminal(
    attribute_str: str,
    value: str,
    operator: str = "exact_match",
    negation: bool = False,
) -> dict:
    """
    Generate a terminal query.
    """
    return {
        "type": "terminal",
        "service": "text",
        "parameters": {
            "attribute": attribute_str,
            "operator": operator,
            "negation": negation,
            "value": value,
        },
    }


def generate_organism(organism: str, negation: bool = False) -> dict:
    """
    Generate a query for the organism (taxon name).
    """
    return generate_terminal(
        "rcsb_entity_source_organism.taxonomy_lineage.name",
        organism,
        "contains_phrase",
        negation,
    )


def generate_method_extendend(value: str, negation: bool = False) -> dict:
    """
    Generate the terminal query for the method, including the CSMs.
    """
    if value == "AlphaFoldDB":
        attribute_str = "rcsb_comp_model_provenance.source_db"
    else:
        attribute_str = "exptl.method"
    return generate_terminal(attribute_str, value, "exact_match", negation)


def generate_methods(methods: List[str]) -> dict:
    """
    Generate a query for the experimental methods.
    """
    if len(methods) == 1:
        return generate_method_extendend(methods[0])
    return generate_group(
        [generate_method_extendend(method) for method in methods],
        "or",
    )


def generate_polymer_type(polymer_type: str, negation: bool = False) -> dict:
    """
    Generate a query about the polymer type.
    """
    if polymer_type in {"Nucleic acid (only)", "Protein (only)"}:
        attribute_str = "rcsb_entry_info.selected_polymer_entity_types"
    else:
        attribute_str = "entity_poly.rcsb_entity_polymer_type"
    return generate_terminal(attribute_str, polymer_type, "exact_match", negation)


def generate_group(
    queries: list,
    logical_operator: str = "and",
) -> Dict[str, Any]:
    """
    Generate a group query.
    """
    return {
        "type": "group",
        # no negation for groups
        "nodes": queries,
        "logical_operator": logical_operator,
    }


def generate_queries(
    polymer_type: Optional[str] = None,
    organism: Optional[str] = None,
    methods: Optional[List[str]] = None,
) -> Dict[Any, Any]:
    """
    Generate the advanced query string for the organism, methods and polymer type.
    """
    queries = []
    # NB: this is the order of the queries in the RCSB website
    if polymer_type is not None:
        queries.append(generate_polymer_type(polymer_type))
    if methods is not None:
        queries.append(generate_methods(methods))
    if organism is not None:
        queries.append(generate_organism(organism))
    return queries[0] if len(queries) == 1 else generate_group(queries)


def generate_advanced_query(  # pylint: disable=too-many-arguments
    polymer_type: Optional[str] = None,
    organism: Optional[str] = None,
    methods: Optional[list] = None,
    results_content_type: tuple = ("experimental",),
    rows: int = 999999,
    indent: int = 2,
) -> str:
    """
    Generate the advanced query string for the organism, methods and polymer type.
    """
    query = generate_queries(polymer_type, organism, methods)
    query["label"] = "text"
    request = {
        "query": query,
        "return_type": "entry",
        "request_options": generate_request_options(results_content_type, rows=rows),
    }
    return json.dumps(request, indent=indent)


def extend_parser(parser):  # pragma: no cover
    """
    Extend the parser with the arguments.
    """
    parser.add_argument("-o", "--organism", help="organism (taxon name)")
    parser.add_argument("-m", "--methods", nargs="+", help="experimental methods")
    parser.add_argument("-p", "--polymer-type", help="polymer type")
    parser.add_argument(
        "--csm",
        action="store_true",
        help="include Computed Structure Models (CSMs) in the search results",
    )
    parser.add_argument(
        "--no-experimental", action="store_true", help="exclude experimental structures"
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=999999,
        help="maximum number of structures to retrieve",
    )
    parser.add_argument(
        "-i", "--indent", type=int, default=2, help="indentation for the json string"
    )
    return parser


def prepare_queries(yaml_filename: str) -> None:
    """
    Load a yaml file and create the query files for the project directory.
    """
    project_dir = os.path.dirname(yaml_filename)
    with open(yaml_filename, "r", encoding="utf-8") as file:
        data = yaml.load(file, Loader=SafeLoader)

    queries_dir = os.path.join(project_dir, "queries")
    os.makedirs(queries_dir, exist_ok=True)

    project_name = data["name"]
    taxa = data.get("taxa", [])
    csm = data.get("csm", False)
    rc_types = [("computational",), ("experimental",)] if csm else [("experimental",)]
    for taxon in taxa:
        for results_content_type in rc_types:
            if results_content_type == ("experimental",):
                methods = DEFAULT_METHODS
            else:
                methods = ["AlphaFoldDB"]
            query_name = f"{taxon.replace(' ', '_')}__{results_content_type[0][:3]}"  # Copilot by itself
            adv_query = generate_advanced_query(
                polymer_type=data.get("polymer_type", DEFAULT_POLYMER_TYPE),
                organism=taxon,
                methods=methods,
                results_content_type=results_content_type,
                rows=data.get("rows", DEFAULT_ROWS),
            )
            query_filename = os.path.join(queries_dir, f"{query_name}.json")
            with open(query_filename, "w", encoding="utf-8") as file:
                file.write(adv_query)

    logging.info("Created %d queries for %s.", len(taxa) * len(rc_types), project_name)


def args_to_query(args):  # pragma: no cover
    """
    Generate the advanced query string from the arguments.
    """
    # prepare the results_content_type
    results_content_type = ["experimental"]
    if args.csm:
        results_content_type.append("computational")
    if args.no_experimental:
        assert args.csm, "Cannot exclude experimental structures without including CSMs"
        results_content_type = ["computational"]
    results_content_type = tuple(results_content_type)

    return generate_advanced_query(
        polymer_type=args.polymer_type,
        organism=args.organism,
        methods=args.methods,
        results_content_type=results_content_type,
        rows=args.rows,
        indent=args.indent,
    )


def main():  # pragma: no cover
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description="RCSB query generator")
    args = extend_parser(parser).parse_args()
    query = args_to_query(args)
    print(query)


if __name__ == "__main__":
    main()
