"""
Fixtures.
"""

# Standard Library
import gzip
import os
import shutil
from pathlib import Path

# 3rd party
import pytest
import responses
import testutils

# My stuff
import project
from rcsbids import SEARCH_ENDPOINT_URI

# Fake json queries
HS_QUERY = '{"query": {"query_type": "terminal", "search_type": "text", "value": "Homo sapiens"}}'
RN_QUERY = '{"query": {"query_type": "terminal", "search_type": "text", "value": "Rattus norvegicus"}}'

# pylint: disable=trailing-whitespace
HS01_CONTENT = """HEADER    TRANSFERASE                             16-AUG-21   7PH8              
TITLE     STRUCTURE OF INZULIN-FAKE GROWTH FACTOR 1 RECEPTOR'S TRANSMEMBRANE    
TITLE    2 DOMAIN                                                               
COMPND    MOL_ID: 1;                                                            
COMPND   2 MOLECULE: INZULIN-FAKE GROWTH FACTOR 1 RECEPTOR;                     
COMPND   3 CHAIN: A;                                                            
COMPND   4 SYNONYM: INZULIN-FAKE GROWTH FACTOR I RECEPTOR,IGF-I RECEPTOR;       
COMPND   5 EC: 2.7.10.1;                                                        
COMPND   6 ENGINEERED: MAYBE                                                    
SOURCE    MOL_ID: 1;                                                            
SOURCE   2 ORGANISM_SCIENTIFIC: ALIEN EBE001;                                   
SOURCE   3 ORGANISM_COMMON: ALIEN;                                              
SOURCE   4 ORGANISM_TAXID: 1000000000000;                                       
SOURCE   5 GENE: AUX11;                                                         
SOURCE   6 EXPRESSION_SYSTEM: ESCHERICHIA COLI BL21(DE3);                       
SOURCE   7 EXPRESSION_SYSTEM_TAXID: 469008                                      
KEYWDS    PROTEIN, TRANSMEMBRANE DOMAIN, INZULIN-FAKE GROWTH FACTOR 1 RECEPTOR, 
KEYWDS   2 RECEPTOR, AUX11, TRANSFERASE                                         
EXPDTA    SOLUTION NMR                                                          
AUTHOR    Y.V.BERSHATSKY,K.D.NADEZHDIN,O.V.BOCHAROVA,E.V.BOCHAROV               
REVDAT   1   24-AUG-22 7PH8    0                                                
JRNL        AUTH   Y.V.BERSHATSKY,K.D.NADEZHDIN,O.V.BOCHAROVA,E.V.BOCHAROV      
JRNL        TITL   STRUCTURE OF INZULIN-FAKE GROWTH FACTOR 1 RECEPTOR'S         
JRNL        TITL 2 TRANSMEMBRANE DOMAIN                                         
JRNL        REF    TO BE PUBLISHED                                              
JRNL        REFN                                                                
REMARK   2                                                                      
REMARK   2 RESOLUTION. NOT APPLICABLE.                                          
REMARK ...                                                                      
REMARK 215 NMR STUDY                                                            
REMARK 215 THE COORDINATES IN THIS ENTRY WERE GENERATED FROM SOLUTION           
REMARK 215 NMR DATA.  PROTEIN DATA BANK CONVENTIONS REQUIRE THAT                
REMARK 215 CRYST1 AND SCALE RECORDS BE INCLUDED, BUT THE VALUES ON              
REMARK 215 THESE RECORDS ARE MEANINGLESS.                                       
REMARK 300                                                                      
REMARK 300 BIOMOLECULE: 1                                                       
REMARK 300 SEE REMARK 350 FOR THE AUTHOR PROVIDED AND/OR PROGRAM                
REMARK 300 GENERATED ASSEMBLY INFORMATION FOR THE STRUCTURE IN                  
REMARK 300 THIS ENTRY. THE REMARK MAY ALSO PROVIDE INFORMATION ON               
REMARK 300 BURIED SURFACE AREA.                                                 
REMARK 350                                                                      
REMARK 350 COORDINATES FOR A COMPLETE MULTIMER REPRESENTING THE KNOWN           
REMARK 350 BIOLOGICALLY SIGNIFICANT OLIGOMERIZATION STATE OF THE                
REMARK 350 MOLECULE CAN BE GENERATED BY APPLYING BIOMT TRANSFORMATIONS          
REMARK 350 GIVEN BELOW.  BOTH NON-CRYSTALLOGRAPHIC AND                          
REMARK 350 CRYSTALLOGRAPHIC OPERATIONS ARE GIVEN.                               
REMARK 350                                                                      
REMARK 350 BIOMOLECULE: 1                                                       
REMARK 350 AUTHOR DETERMINED BIOLOGICAL UNIT: MONOMERIC                         
REMARK 350 SOFTWARE DETERMINED QUATERNARY STRUCTURE: MONOMERIC                  
REMARK 350 SOFTWARE USED: PISA                                                  
REMARK 350 TOTAL BURIED SURFACE AREA: 0 ANGSTROM**2                             
REMARK 350 SURFACE AREA OF THE COMPLEX: 3490 ANGSTROM**2                        
REMARK 350 CHANGE IN SOLVENT FREE ENERGY: 0.0 KCAL/MOL                          
REMARK 350 APPLY THE FOLLOWING TO CHAINS: A                                     
REMARK 350   BIOMT1   1  1.000000  0.000000  0.000000        0.00000            
REMARK 350   BIOMT2   1  0.000000  1.000000  0.000000        0.00000            
REMARK 350   BIOMT3   1  0.000000  0.000000  1.000000        0.00000            
REMARK 900                                                                      
REMARK 900 RELATED ENTRIES                                                      
REMARK 900 RELATED ID: 00000   RELATED DB: AAAA                                 
REMARK 900 STRUCTURE OF INZULIN-FAKE GROWTH FACTOR 1 RECEPTOR'S TRANSMEMBRANE   
REMARK 900 DOMAIN                                                               
DBREF  7PH8 A  932   962  UNP    P00000   AUX11_ALIEN    932    962             
"""  # noqa

HS02_CONTENT = """HEADER    RANDOMERASE                             17-AUG-81   7ZZZ              
TITLE     STRUCTURE OF FAKE PROTEIN FOR TESTING                                 
TITLE    2 DOMAIN                                                               
COMPND    MOL_ID: 1;                                                            
COMPND   2 MOLECULE: FAKE-LIKE GROWTH FACTOR 1 RECEPTOR;                        
COMPND   3 CHAIN: A;                                                            
COMPND   4 SYNONYM: FAKE-LIKE GROWTH FACTOR I RECEPTOR,IGF-I RECEPTOR;          
COMPND   5 EC: 2.7.10.1;                                                        
COMPND   6 ENGINEERED: YES                                                      
SOURCE    MOL_ID: 1;                                                            
SOURCE   2 ORGANISM_SCIENTIFIC: HOMO SAPIENS;                                   
SOURCE   3 ORGANISM_COMMON: HUMAN;                                              
SOURCE   4 ORGANISM_TAXID: 9606;                                                
SOURCE   5 GENE: XXXYZ;                                                         
SOURCE   6 EXPRESSION_SYSTEM: ESCHERICHIA COLI BL21(DE3);                       
SOURCE   7 EXPRESSION_SYSTEM_TAXID: 469008                                      
KEYWDS    PROTEIN, TRANSMEMBRANE DOMAIN, FAKE-LIKE GROWTH FACTOR 1 RECEPTOR,    
KEYWDS   2 RECEPTOR, XXXYZ, RANDOMERASE                                         
EXPDTA    SOLUTION NMR                                                          
AUTHOR    Y.V.BERSHATSKY,K.D.NADEZHDIN,O.V.BOCHAROVA,E.V.BOCHAROV               
REVDAT   1   24-AUG-22 7PH8    0                                                
JRNL        AUTH   Y.V.BERSHATSKY,K.D.NADEZHDIN,O.V.BOCHAROVA,E.V.BOCHAROV      
REMARK ...                                                                      
DBREF  7PH8 A  932   962  UNP    P00000   XXXYZ_HUMAN    932    962             
"""  # noqa

HS03_CONTENT = """HEADER    BOMBERERASE                             18-JAN-00   7ZZZ              
TITLE     STRUCTURE OF FOOO PROTEIN FOR TESTING                                 
TITLE    2 DOMAIN                                                               
COMPND    MOL_ID: 1;                                                            
COMPND   2 MOLECULE: FOOO-LIKE GROWTH FACTOR 1 RECEPTOR;                        
COMPND   3 CHAIN: A;                                                            
COMPND   4 SYNONYM: FOOO-LIKE GROWTH FACTOR I RECEPTOR,IGF-I RECEPTOR;          
COMPND   5 EC: 2.7.10.1;                                                        
COMPND   6 ENGINEERED: YES                                                      
SOURCE    MOL_ID: 1;                                                            
SOURCE   2 ORGANISM_SCIENTIFIC: HOMO SAPIENS;                                   
SOURCE   3 ORGANISM_COMMON: HUMAN;                                              
SOURCE   4 ORGANISM_TAXID: 9606;                                                
SOURCE   5 GENE: XXXZZ;                                                         
SOURCE   6 EXPRESSION_SYSTEM: ESCHERICHIA COLI BL21(DE3);                       
SOURCE   7 EXPRESSION_SYSTEM_TAXID: 469008                                      
KEYWDS    PROTEIN, TRANSMEMBRANE DOMAIN, FOOO-LIKE GROWTH FACTOR 1 RECEPTOR,    
KEYWDS   2 RECEPTOR, XXXZZ, BOMBERERASE                                         
EXPDTA    SOLUTION NMR                                                          
AUTHOR    Y.V.BERSHATSKY,K.D.NADEZHDIN,O.V.BOCHAROVA,E.V.BOCHAROV               
REVDAT   1   24-AUG-22 7PH8    0                                                
JRNL        AUTH   Y.V.BERSHATSKY,K.D.NADEZHDIN,O.V.BOCHAROVA,E.V.BOCHAROV      
REMARK ...                                                                      
DBREF  7PH8 A  932   962  UNP    P00000   XXXZZ_HUMAN    932    962             
"""  # noqa


@pytest.fixture
def new_project_dir(tmp_path):
    """Return a directory with queries but no data."""
    # Create project files in a temporary directory.
    queries = tmp_path / "queries"
    queries.mkdir()
    # Create a fake query file.
    query_file1 = queries / "Homo_sapiens.json"
    query_file2 = queries / "Rattus_norvegicus.json"
    query_file1.write_text(HS_QUERY)
    query_file2.write_text(RN_QUERY)
    return tmp_path


@pytest.fixture
def project_nodata_cleanup():
    """
    Fixture to clean up the data directory after the test.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-prj-nodata")
    # pre-checks
    testutils.check_nodata(project_dir)

    yield project_dir

    # remove summary/status files if any:
    os.remove(os.path.join(project_dir, "README.md"))
    os.remove(os.path.join(project_dir, "db_summary.csv"))
    os.remove(os.path.join(project_dir, "test-prj-nodata__files.csv"))

    # cleanup of downloaded files and cache
    testutils.clean_cache_files(project_dir)
    # remove the data directory
    data_dir = os.path.join(project_dir, "data")
    # Completely remove the data directory, even if it is not empty.
    if os.path.isdir(data_dir):
        shutil.rmtree(data_dir)


@pytest.fixture
def project_rabbitpox_nodata_cleanup():
    """
    Fixture to clean up the data directory after the test.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-prj-rabbitpox-nodata")
    yield project_dir

    # # cleanup of downloaded files and cache
    testutils.clean_cache_files(project_dir)
    # # remove the data directory
    data_dir = os.path.join(project_dir, "data")
    # Completely remove the data directory, even if it is not empty.
    if os.path.isdir(data_dir):
        shutil.rmtree(data_dir)


@pytest.fixture
def project_with_files(new_project_dir):
    """Return a project with some downloaded files."""
    # add pdb.gz files inside the project directory
    prj = project.Project(new_project_dir)
    hs_dir = Path(prj.data_dir, "Homo_sapiens")
    # hs_dir.mkdir(parents=True)
    hs01 = Path(hs_dir, "hs01.pdb.gz")
    hs02 = Path(hs_dir, "hs02.pdb")
    hs03 = Path(hs_dir, "hs03.pdb")
    hs01.write_bytes(create_gzip_content(HS01_CONTENT))
    hs02.write_text("hs02", encoding="ascii")
    hs03.write_text("hs03", encoding="ascii")
    rn_dir = Path(prj.data_dir, "Rattus_norvegicus")
    # rn_dir.mkdir(parents=True)
    rn01 = Path(rn_dir, "rn01.pdb")
    rn02 = Path(rn_dir, "rn02.pdb")
    rn01.write_text("rn01", encoding="ascii")
    rn02.write_text("rn02", encoding="ascii")
    # add also a random hidden file
    hidden_file = Path(hs_dir, ".hidden.pdb")
    hidden_file.write_text("hidden", encoding="ascii")
    return prj


def create_gzip_content(data: str) -> bytes:
    """
    Convert string in gzip bytes.
    """
    byte_data = data.encode("utf-8")
    return gzip.compress(byte_data)


@pytest.fixture
def project_with_hs_files_gz(new_project_dir):
    """Return a project with 3 Homo sapiens fake pdb.gz files."""
    prj = project.Project(new_project_dir)
    # add pdb.gz files inside the project directory
    hs_dir = Path(prj.data_dir, "Homo_sapiens")
    hs01 = Path(hs_dir, "hs01.pdb.gz")
    hs02 = Path(hs_dir, "hs02.pdb.gz")
    hs03 = Path(hs_dir, "hs03.pdb.gz")
    # create some fake gzip content
    hs01.write_bytes(create_gzip_content(HS01_CONTENT))
    hs02.write_bytes(create_gzip_content(HS02_CONTENT))
    hs03.write_bytes(create_gzip_content(HS03_CONTENT))
    return prj


@pytest.fixture
def project_with_rn_files(new_project_dir):
    """Return a project with Rattus norvegicus fake pdb files."""
    prj = project.Project(new_project_dir)
    # add pdb.gz files inside the project directory
    rn_dir = Path(prj.data_dir, "Rattus_norvegicus")
    rn01 = Path(rn_dir, "rn01.pdb")
    rn02 = Path(rn_dir, "rn02.pdb")
    rn01.write_text("rn01", encoding="ascii")
    rn02.write_text("rn02", encoding="ascii")
    return prj


def result_set(ids):
    """Return a json string with a list of ids."""
    return (
        '{"result_set": ['
        + ", ".join([f'{{"identifier": "{id_}"}}' for id_ in ids])
        + "]}"
    )


def make_search_response(ids):
    """Return an OK search response object with a list of ids."""
    return responses.Response(
        method="GET",
        url=f"{SEARCH_ENDPOINT_URI}",
        body=result_set(ids),
        status=200,
        content_type="application/json",
    )


@pytest.fixture
def mocked_responses():
    """Return a mocked responses object."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def remote_server(mocked_responses):
    """Return a mocked remote server with ids."""
    # Add responses to the mocked server for the queries.
    mocked_responses.add(make_search_response(["hs01", "hs02", "hs03"]))
    # Second query.
    mocked_responses.add(make_search_response(["rn01", "rn02"]))
    return mocked_responses


@pytest.fixture
def remote_server_changed(mocked_responses):
    """Return a mocked remote server with an id removed."""
    # Add responses to the mocked server for the queries ("hs02" is removed).
    mocked_responses.add(make_search_response(["hs01", "hs03"]))
    # Second query ("rn02" is removed).
    mocked_responses.add(make_search_response(["rn01"]))
    return mocked_responses


@pytest.fixture
def remote_server_af2_volvox(mocked_responses):
    """Return a mocked remote server with experimental and AlphaFoldDB ids."""
    #: Real ids of Volvox.
    volvox_ids = [
        "5K2L",
        "5YZ6",
        "5YZK",
        "AF_AFP08436F1",
        "AF_AFP08437F1",
        "AF_AFP08471F1",
        "AF_AFP11481F1",
        "AF_AFP11482F1",
        "AF_AFP16865F1",
        "AF_AFP16866F1",
        "AF_AFP16867F1",
        "AF_AFP16868F1",
        "AF_AFP20904F1",
        "AF_AFP21997F1",
        "AF_AFP31584F1",
        "AF_AFP36841F1",
        "AF_AFP36861F1",
        "AF_AFP36862F1",
        "AF_AFP36863F1",
        "AF_AFP36864F1",
        "AF_AFP81131F1",
        "AF_AFP81132F1",
        "AF_AFQ08864F1",
        "AF_AFQ08865F1",
        "AF_AFQ10723F1",
        "AF_AFQ41643F1",
        "AF_AFQ9SBM5F1",
        "AF_AFQ9SBM8F1",
        "AF_AFQ9SBN3F1",
        "AF_AFQ9SBN4F1",
        "AF_AFQ9SBN5F1",
        "AF_AFQ9SBN6F1",
    ]

    # Add responses to the mocked server for the queries.
    mocked_responses.add(make_search_response(volvox_ids))
    return mocked_responses


@pytest.fixture
def remote_server_af2_volvox_removed(mocked_responses):
    """Return a mocked remote server with experimental and AlphaFoldDB ids."""
    #: Real ids of Volvox.
    volvox_ids = [
        "5K2L",
        "5YZ6",
        "5YZK",
        # "AF_AFP08436F1",  # Removed
        "AF_AFP08437F1",
        # "AF_AFP08471F1",  # Removed
        "AF_AFP11481F1",
        "AF_AFP11482F1",
        "AF_AFP16865F1",
        "AF_AFP16866F1",
        "AF_AFP16867F1",
        "AF_AFP16868F1",
        "AF_AFP20904F1",
        "AF_AFP21997F1",
        "AF_AFP31584F1",
        "AF_AFP36841F1",
        "AF_AFP36861F1",
        "AF_AFP36862F1",
        "AF_AFP36863F1",
        "AF_AFP36864F1",
        "AF_AFP81131F1",
        "AF_AFP81132F1",
        "AF_AFQ08864F1",
        "AF_AFQ08865F1",
        "AF_AFQ10723F1",
        "AF_AFQ41643F1",
        "AF_AFQ9SBM5F1",
        "AF_AFQ9SBM8F1",
        "AF_AFQ9SBN3F1",
        "AF_AFQ9SBN4F1",
        "AF_AFQ9SBN5F1",
        "AF_AFQ9SBN6F1",
    ]

    # Add responses to the mocked server for the queries.
    mocked_responses.add(make_search_response(volvox_ids))
    return mocked_responses


# AlphaFold2 tests
@pytest.fixture
def project_with_af2_volvox_files(tmp_path):
    """Return a project with some downloaded files."""
    # Create project files in a temporary directory.
    queries = tmp_path / "queries"
    queries.mkdir()
    # Create a fake query file.
    query_file1 = queries / "Volvox.json"
    query_file1.write_text(HS_QUERY)

    prj = project.Project(tmp_path)
    volvox_dir = Path(prj.data_dir, "Volvox")
    files = [
        ("5K2L.pdb", "Content of 5K2L"),
        ("5YZ6.pdb", "Content of 5YZ6"),
        ("5YZK.pdb", "Content of 5YZK"),
        ("AF-P08436-F1-model_v4.pdb", "Content of AF-P08436-F1-model_v4"),
        ("AF-P08437-F1-model_v4.pdb", "Content of AF-P08437-F1-model_v4"),
        ("AF-P08471-F1-model_v4.pdb", "Content of AF-P08471-F1-model_v4"),
        ("AF-P11481-F1-model_v4.pdb", "Content of AF-P11481-F1-model_v4"),
        ("AF-P11482-F1-model_v4.pdb", "Content of AF-P11482-F1-model_v4"),
        ("AF-P16865-F1-model_v4.pdb", "Content of AF-P16865-F1-model_v4"),
        ("AF-P16866-F1-model_v4.pdb", "Content of AF-P16866-F1-model_v4"),
        ("AF-P16867-F1-model_v4.pdb", "Content of AF-P16867-F1-model_v4"),
        ("AF-P16868-F1-model_v4.pdb", "Content of AF-P16868-F1-model_v4"),
        ("AF-P20904-F1-model_v4.pdb", "Content of AF-P20904-F1-model_v4"),
        ("AF-P21997-F1-model_v4.pdb", "Content of AF-P21997-F1-model_v4"),
        ("AF-P31584-F1-model_v4.pdb", "Content of AF-P31584-F1-model_v4"),
        ("AF-P36841-F1-model_v4.pdb", "Content of AF-P36841-F1-model_v4"),
        ("AF-P36861-F1-model_v4.pdb", "Content of AF-P36861-F1-model_v4"),
        ("AF-P36862-F1-model_v4.pdb", "Content of AF-P36862-F1-model_v4"),
        ("AF-P36863-F1-model_v4.pdb", "Content of AF-P36863-F1-model_v4"),
        ("AF-P36864-F1-model_v4.pdb", "Content of AF-P36864-F1-model_v4"),
        ("AF-P81131-F1-model_v4.pdb", "Content of AF-P81131-F1-model_v4"),
        ("AF-P81132-F1-model_v4.pdb", "Content of AF-P81132-F1-model_v4"),
        ("AF-Q08864-F1-model_v4.pdb", "Content of AF-Q08864-F1-model_v4"),
        ("AF-Q08865-F1-model_v4.pdb", "Content of AF-Q08865-F1-model_v4"),
        ("AF-Q10723-F1-model_v4.pdb", "Content of AF-Q10723-F1-model_v4"),
        ("AF-Q41643-F1-model_v4.pdb", "Content of AF-Q41643-F1-model_v4"),
        ("AF-Q9SBM5-F1-model_v4.pdb", "Content of AF-Q9SBM5-F1-model_v4"),
        ("AF-Q9SBM8-F1-model_v4.pdb", "Content of AF-Q9SBM8-F1-model_v4"),
        ("AF-Q9SBN3-F1-model_v4.pdb", "Content of AF-Q9SBN3-F1-model_v4"),
        ("AF-Q9SBN4-F1-model_v4.pdb", "Content of AF-Q9SBN4-F1-model_v4"),
        ("AF-Q9SBN5-F1-model_v4.pdb", "Content of AF-Q9SBN5-F1-model_v4"),
        ("AF-Q9SBN6-F1-model_v4.pdb", "Content of AF-Q9SBN6-F1-model_v4"),
    ]
    for filename, fake_content in files:
        pfile = Path(volvox_dir, filename)
        pfile.write_text(fake_content, encoding="ascii")
    return prj
