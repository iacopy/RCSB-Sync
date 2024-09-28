# pylint: disable=duplicate-code
"""
Generate a JSON query for each gene.
Useful to obtain protein structures for a list of genes, e.g for the GABA receptor family.

Usage:
    $ python querygenes.py --types experimental computational GENE1 GENE2
"""

# Standard Library
import argparse
import os

TEMPLATE_EXP = """
{
  "query": {
    "type": "group",
    "logical_operator": "and",
    "nodes": [
      {
        "type": "terminal",
        "service": "text",
        "parameters": {
          "attribute": "entity_poly.rcsb_entity_polymer_type",
          "operator": "exact_match",
          "negation": false,
          "value": "Protein"
        }
      },
      {
        "type": "group",
        "nodes": [
          {
            "type": "terminal",
            "service": "text",
            "parameters": {
              "attribute": "exptl.method",
              "operator": "exact_match",
              "negation": false,
              "value": "X-RAY DIFFRACTION"
            }
          },
          {
            "type": "terminal",
            "service": "text",
            "parameters": {
              "attribute": "exptl.method",
              "operator": "exact_match",
              "negation": false,
              "value": "SOLUTION NMR"
            }
          },
          {
            "type": "terminal",
            "service": "text",
            "parameters": {
              "attribute": "exptl.method",
              "operator": "exact_match",
              "negation": false,
              "value": "ELECTRON MICROSCOPY"
            }
          }
        ],
        "logical_operator": "or"
      },
      {
        "type": "terminal",
        "service": "text",
        "parameters": {
          "attribute": "rcsb_entity_source_organism.rcsb_gene_name.value",
          "operator": "exact_match",
          "negation": false,
          "value": "$gene_name"
        }
      }
    ],
    "label": "text"
  },
  "return_type": "entry",
  "request_options": {
    "return_all_hits": true,
    "results_content_type": [
      "experimental"
    ],
    "sort": [
      {
        "sort_by": "score",
        "direction": "desc"
      }
    ],
    "scoring_strategy": "combined"
  }
}
""".strip()

TEMPLATE_COM = """
{
  "query": {
    "type": "group",
    "logical_operator": "and",
    "nodes": [
      {
        "type": "terminal",
        "service": "text",
        "parameters": {
          "attribute": "entity_poly.rcsb_entity_polymer_type",
          "operator": "exact_match",
          "negation": false,
          "value": "Protein"
        }
      },
      {
        "type": "terminal",
        "service": "text",
        "parameters": {
          "attribute": "rcsb_entity_source_organism.rcsb_gene_name.value",
          "operator": "exact_match",
          "negation": false,
          "value": "$gene_name"
        }
      }
    ],
    "label": "text"
  },
  "return_type": "entry",
  "request_options": {
    "return_all_hits": true,
    "results_content_type": [
      "computational"
    ],
    "sort": [
      {
        "sort_by": "score",
        "direction": "desc"
      }
    ],
    "scoring_strategy": "combined"
  }
}
""".strip()


TEMPLATES = {"experimental": TEMPLATE_EXP, "computational": TEMPLATE_COM}


def main(
    name: str,
    gene_names: list,
    output: str = "templates",
    types: tuple = ("experimental",),
):
    """
    Create queries for genes.

    Args:
        name (str): the name of the directory that will be created
        gene_names (list): the list of genes
        output (str): the root directory path
        types (tuple): the types of protein structures (experimental and/or computational)
    """
    if not name:
        raise ValueError("The name of the project must be provided")
    if not gene_names:
        raise ValueError("At least one gene name must be provided")
    if not types:
        raise ValueError("At least one type of protein structure must be provided")

    project_dir = f"{output}/{name}"
    for type_ in types:
        sub_dir = f"{project_dir}/{type_}/queries"
        os.makedirs(sub_dir, exist_ok=True)
        template = TEMPLATES[type_]
        for gene_name in gene_names:
            query = template.replace("$gene_name", gene_name)
            file_name = f"{sub_dir}/{gene_name}.json"
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(query)
            print(f"{type_} query for gene {gene_name} saved to {file_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "name", help="Name of the project/group (protein family or similar)"
    )
    parser.add_argument("gene_names", nargs="+", help="Gene names to search for")
    parser.add_argument("--output", default="templates", help="Output directory")
    parser.add_argument(
        "--types",
        nargs="+",
        default=["experimental", "computational"],
        help="Types of queries to generate",
    )
    args = parser.parse_args()

    main(args.name, args.gene_names, args.output, args.types)
