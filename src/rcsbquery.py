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
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


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
        "logical_operator": logical_operator,
        # no negation for groups
        "nodes": queries,
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
        args.polymer_type,
        args.organism,
        args.methods,
        results_content_type,
        args.indent,
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
