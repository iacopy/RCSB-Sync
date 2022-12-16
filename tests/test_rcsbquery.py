"""
Unit tests for the rcsbquery module.
"""
# Standard Library
import filecmp
import json
import os
import shutil

# 3rd party
import pytest

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
    query = rcsbquery.generate_advanced_query(organism="Homo sapiens")
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


def test_prepare_query__dir():
    """Test that the prepare_query function works with a directory as input."""
    query_files = rcsbquery.prepare_queries("tests/test-prj-config--exp")
    assert query_files == [
        "tests/test-prj-config--exp/queries/Homo_sapiens__exp.json",
        "tests/test-prj-config--exp/queries/Mus_musculus__exp.json",
    ]


def test_prepare_query__file():
    """Test that the prepare_query function works with a file as input."""
    query_files = rcsbquery.prepare_queries("tests/test-prj-config--exp/project.yml")
    assert query_files == [
        "tests/test-prj-config--exp/queries/Homo_sapiens__exp.json",
        "tests/test-prj-config--exp/queries/Mus_musculus__exp.json",
    ]


# Test the project creation based on yaml configuration files.
@pytest.mark.parametrize(
    "project_dirname", ["test-prj-config--exp", "test-prj-config--exp-csm"]
)
def test_project_creation(tmp_path, project_dirname):
    """Test the creation of a project based on a yaml configuration file.

    Each test directory must contain a file named "project.yml" and a "queries" directory
    containing the expected queries to be generated (in json format) based on the project.yml file.

    :param tmp_path: temporary directory for the test.
    :param project_dirname: name of the directory containing the project configuration.
    """
    test_project_dir = os.path.join("tests", project_dirname)
    yaml_file = os.path.join(test_project_dir, "project.yml")
    # Copy the yaml file to the temporary directory.
    shutil.copy(yaml_file, tmp_path)
    dest_yml = os.path.join(tmp_path, "project.yml")
    rcsbquery.prepare_queries(dest_yml)

    # Compare the generated files with the expected ones.
    common = os.listdir(os.path.join(test_project_dir, "queries"))
    match, mismatch, errors = filecmp.cmpfiles(
        os.path.join(test_project_dir, "queries"),
        os.path.join(tmp_path, "queries"),
        common,
        shallow=False,
    )
    assert not errors
    if mismatch:
        for error in mismatch:
            wrong_file = tmp_path / "queries" / error
            assert os.path.exists(wrong_file)
            # copy the wrong file to the testdata directory for inspection.
            shutil.copy(wrong_file, test_project_dir)
            print(f"Copied {wrong_file} to {test_project_dir} for inspection.")
    assert not mismatch
    assert match == common
