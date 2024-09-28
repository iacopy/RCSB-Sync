"""
Test module for querygenes.py
"""

# Standard Library
import json
import os

# 3rd party
import pytest

# My stuff
from querygenes import main


def load_json(file_path):
    """
    Load a JSON file from disk and return its content as a dictionary
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def assert_file_contains_gene_query(file_path, gene_name, node_index):
    """
    Assert that the content of the file at file_path contains a query for the gene_name.

    We test that the query is looking for the gene_name in the rcsb_gene_name attribute.

    Other attributes are not tested here, but they could be added in the future.

    Args:
        file_path (str): the path to the file to check
        gene_name (str): the gene name to look for in the query
        node_index (int): the index of the node in the query
    """
    content = load_json(file_path)
    assert content["query"]["nodes"][node_index]["parameters"] == {
        "attribute": "rcsb_entity_source_organism.rcsb_gene_name.value",
        "operator": "exact_match",
        "negation": False,
        "value": gene_name,
    }


def test_main_with_default_arguments(tmpdir):
    """main() should create the expected files"""
    name = "test_project"
    gene_names = ["gene1", "gene2"]
    output = str(tmpdir)
    types = ["experimental", "computational"]

    main(name, gene_names, output, types)

    expected_file = os.path.join(output, name, "experimental", "queries", "gene1.json")
    assert os.path.exists(expected_file), f"{expected_file} does not exist"
    assert_file_contains_gene_query(expected_file, "gene1", 2)

    expected_file = os.path.join(output, name, "experimental", "queries", "gene2.json")
    assert os.path.exists(expected_file), f"{expected_file} does not exist"
    assert_file_contains_gene_query(expected_file, "gene2", 2)

    expected_file = os.path.join(output, name, "computational", "queries", "gene1.json")
    assert os.path.exists(expected_file), f"{expected_file} does not exist"
    assert_file_contains_gene_query(expected_file, "gene1", 1)

    expected_file = os.path.join(output, name, "computational", "queries", "gene2.json")
    assert os.path.exists(expected_file), f"{expected_file} does not exist"
    assert_file_contains_gene_query(expected_file, "gene2", 1)


def test_main_with_empty_name():
    """main() should raise a ValueError if the name of the project is empty"""
    with pytest.raises(ValueError):
        main("", ["GENE1", "GENE2"])


def test_main_with_no_gene_names():
    """main() should raise a ValueError if no gene names are provided"""
    with pytest.raises(ValueError):
        main("project_name", [])


def test_main_with_no_types():
    """main() should raise a ValueError if no types are provided"""
    with pytest.raises(ValueError):
        main("project_name", ["GENE1", "GENE2"], types=[])
