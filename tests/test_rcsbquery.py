"""
Unit tests for the rcsbquery module.
"""
# Standard Library
import json
import os

# My stuff
import rcsbquery


def load_test_query(file_name: str) -> str:
    """
    Load a test query from a file.

    :param file_name: name of the file containing the query.
    :return: query in json format.
    """
    file_path = os.path.join("tests", "data", file_name)
    with open(file_path, "r", encoding="utf-8") as file_pointer:
        return file_pointer.read()


def load_test_query_as_dict(file_name: str) -> dict:
    """
    Load a test query from a file and convert it to a dictionary.

    :param file_name: name of the file containing the query.
    :return: query in dictionary format.
    """
    return json.loads(load_test_query(file_name))


def test_minimal():
    """
    Test a minimal query (only the organism).
    """
    query = rcsbquery.generate_advanced_query(organism="Homo sapiens", rows=25)
    assert json.loads(query) == load_test_query_as_dict("query_homo_sapiens.json")


def test_dna_rattus_norvegicus():
    """
    Test the DNA query for Rattus norvegicus.
    """
    expected_query = load_test_query("query_dna_rattus_norvegicus.json")
    query = rcsbquery.generate_advanced_query(
        organism="Rattus norvegicus",
        polymer_type="DNA",
    )
    assert query == expected_query


def test_query_complete():
    """Test a complete query (all the parameters)."""
    query = rcsbquery.generate_advanced_query(
        polymer_type="Protein",
        organism="Homo sapiens",
        methods=[
            "X-RAY DIFFRACTION",
            "SOLUTION NMR",
            "ELECTRON MICROSCOPY",
            "AlphaFoldDB",
        ],
        results_content_type=("computational", "experimental"),
    )
    assert json.loads(query) == load_test_query_as_dict("query_complete.json")


def test_query_volvox_alphafolddb():
    """Test a query for Volvox including AlphaFoldDB results only.

    The expected JSON result is copy-pasted from RCSB, as is.
    NB: even if we ask also for experimental results, the query would return only computational results
    because there is only "AlphaFoldDB" in the methods list.
    """
    query = rcsbquery.generate_advanced_query(
        organism="Volvox",
        methods=["AlphaFoldDB"],
        results_content_type=("computational", "experimental"),
    )
    assert json.loads(query) == load_test_query_as_dict("query_volvox_alphafolddb.json")


def test_query_nucleid_acid_only():
    """Test a query for nucleic acids only."""
    query = rcsbquery.generate_advanced_query(polymer_type="Nucleic acid (only)")
    assert json.loads(query) == load_test_query_as_dict("query_nucleic_acid_only.json")
