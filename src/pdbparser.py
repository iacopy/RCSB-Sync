"""
Parse PDB file content.
"""
# Standard Library
import re
from typing import Dict
from typing import Optional

# pylint: disable=trailing-whitespace
TESTDATA = """HEADER    TRANSFERASE                             11-AUG-05   2AN4              
TITLE     STRUCTURE OF PNMT COMPLEXED WITH S-ADENOSYL-L-HOMOCYSTEINE AND THE    
TITLE    2 ACCEPTOR SUBSTRATE OCTOPAMINE                                        
COMPND    MOL_ID: 1;                                                            
COMPND   2 MOLECULE: PHENYLETHANOLAMINE N-METHYLTRANSFERASE;                    
COMPND   3 CHAIN: A, B;                                                         
COMPND   4 SYNONYM: PNMTASE, NORADRENALINE N-METHYLTRANSFERASE;                 
COMPND   5 EC: 2.1.1.28;                                                        
COMPND   6 ENGINEERED: YES                                                      
SOURCE    MOL_ID: 1;                                                            
SOURCE   2 ORGANISM_SCIENTIFIC: HOMO SAPIENS;                                   
SOURCE   3 ORGANISM_COMMON: HUMAN;                                              
SOURCE   4 ORGANISM_TAXID: 9606;                                                
SOURCE   5 GENE: PNMT;                                                          
SOURCE   6 EXPRESSION_SYSTEM: ESCHERICHIA COLI;                                 
SOURCE   7 EXPRESSION_SYSTEM_TAXID: 562;                                        
SOURCE   8 EXPRESSION_SYSTEM_STRAIN: BL21(DE3)PLYSS;                            
SOURCE   9 EXPRESSION_SYSTEM_VECTOR_TYPE: PLASMID;                              
SOURCE  10 EXPRESSION_SYSTEM_PLASMID: PET17PNMT-HIS                             
KEYWDS    METHYLTRANSFERASE, SUBSTRATE STRUCTURE, S-ADENOSYL-L-METHIONINE,      
KEYWDS   2 ADRENALINE SYNTHESIS, TRANSFERASE                                    
EXPDTA    X-RAY DIFFRACTION                                                     
AUTHOR    C.L.GEE,J.D.A.TYNDALL,G.L.GRUNEWALD,Q.WU,M.J.MCLEISH,J.L.MARTIN       
REVDAT   3   13-JUL-11 2AN4    1       VERSN                                    
REVDAT   2   24-FEB-09 2AN4    1       VERSN                                    
REVDAT   1   14-MAR-06 2AN4    0                                                
JRNL        AUTH   C.L.GEE,J.D.A.TYNDALL,G.L.GRUNEWALD,Q.WU,M.J.MCLEISH,        
JRNL        AUTH 2 J.L.MARTIN                                                   
JRNL        TITL   MODE OF BINDING OF METHYL ACCEPTOR SUBSTRATES TO THE         
JRNL        TITL 2 ADRENALINE-SYNTHESIZING ENZYME PHENYLETHANOLAMINE            
JRNL        TITL 3 N-METHYLTRANSFERASE: IMPLICATIONS FOR CATALYSIS              
JRNL        REF    BIOCHEMISTRY                  V.  44 16875 2005              
JRNL        REFN                   ISSN 0006-2960                               
JRNL        PMID   16363801                                                     
JRNL        DOI    10.1021/BI051636B                                            
REMARK   2                                                                      
REMARK   2 RESOLUTION.    2.20 ANGSTROMS.                                       
... qui sotto c'e' un'altra proteina (DNA-PK complessata con altre)
DBREF  7Z87 A    1  4128  UNP    P78527   PRKDC_HUMAN      1   4128             
DBREF  7Z87 B    1   609  UNP    P12956   XRCC6_HUMAN      1    609             
DBREF  7Z87 C    1   732  UNP    P13010   XRCC5_HUMAN      1    732             
DBREF  7Z87 D    1    26  PDB    7Z87     7Z87             1     26             
DBREF  7Z87 E   18    43  PDB    7Z87     7Z87            18     43             
SEQRES   1 A 4128  MET ALA GLY SER GLY ALA GLY VAL ARG CYS SER LEU LEU          
"""  # noqa


TESTDATA_AF2 = """HEADER                                            01-JUN-22                     
TITLE     ALPHAFOLD MONOMER V2.0 PREDICTION FOR PIEZO DOMAIN-CONTAINING PROTEIN 
TITLE    2 (A0A3P7E792)                                                         
COMPND    MOL_ID: 1;                                                            
COMPND   2 MOLECULE: PIEZO DOMAIN-CONTAINING PROTEIN;                           
COMPND   3 CHAIN: A                                                             
SOURCE    MOL_ID: 1;                                                            
SOURCE   2 ORGANISM_SCIENTIFIC: WUCHERERIA BANCROFTI;                           
SOURCE   3 ORGANISM_TAXID: 6293                                                 
REMARK   1                                                                      
REMARK   1 REFERENCE 1                                                          
REMARK   1  AUTH   JOHN JUMPER, RICHARD EVANS, ALEXANDER PRITZEL, TIM GREEN,    
REMARK   1  AUTH 2 MICHAEL FIGURNOV, OLAF RONNEBERGER, KATHRYN TUNYASUVUNAKOOL, 
REMARK   1  AUTH 3 RUSS BATES, AUGUSTIN ZIDEK, ANNA POTAPENKO, ALEX BRIDGLAND,  
REMARK   1  AUTH 4 CLEMENS MEYER, SIMON A A KOHL, ANDREW J BALLARD,             
REMARK   1  AUTH 5 ANDREW COWIE, BERNARDINO ROMERA-PAREDES, STANISLAV NIKOLOV,  
REMARK   1  AUTH 6 RISHUB JAIN, JONAS ADLER, TREVOR BACK, STIG PETERSEN,        
REMARK   1  AUTH 7 DAVID REIMAN, ELLEN CLANCY, MICHAL ZIELINSKI,                
REMARK   1  AUTH 8 MARTIN STEINEGGER, MICHALINA PACHOLSKA, TAMAS BERGHAMMER,    
REMARK   1  AUTH 9 DAVID SILVER, ORIOL VINYALS, ANDREW W SENIOR,                
REMARK   1  AUTH10 KORAY KAVUKCUOGLU, PUSHMEET KOHLI, DEMIS HASSABIS            
REMARK   1  TITL   HIGHLY ACCURATE PROTEIN STRUCTURE PREDICTION WITH ALPHAFOLD  
REMARK   1  REF    NATURE                        V. 596   583 2021              
REMARK   1  REFN                   ISSN 0028-0836                               
REMARK   1  PMID   34265844                                                     
REMARK   1  DOI    10.1038/s41586-021-03819-2                                   
REMARK   1                                                                      
REMARK   1 DISCLAIMERS                                                          
REMARK   1 ALPHAFOLD DATA, COPYRIGHT (2021) DEEPMIND TECHNOLOGIES LIMITED. THE  
REMARK   1 INFORMATION PROVIDED IS THEORETICAL MODELLING ONLY AND CAUTION SHOULD
REMARK   1 BE EXERCISED IN ITS USE. IT IS PROVIDED "AS-IS" WITHOUT ANY WARRANTY 
REMARK   1 OF ANY KIND, WHETHER EXPRESSED OR IMPLIED. NO WARRANTY IS GIVEN THAT 
REMARK   1 USE OF THE INFORMATION SHALL NOT INFRINGE THE RIGHTS OF ANY THIRD    
REMARK   1 PARTY. THE INFORMATION IS NOT INTENDED TO BE A SUBSTITUTE FOR        
REMARK   1 PROFESSIONAL MEDICAL ADVICE, DIAGNOSIS, OR TREATMENT, AND DOES NOT   
REMARK   1 CONSTITUTE MEDICAL OR OTHER PROFESSIONAL ADVICE. IT IS AVAILABLE FOR 
REMARK   1 ACADEMIC AND COMMERCIAL PURPOSES, UNDER CC-BY 4.0 LICENCE.           
DBREF  XXXX A    1    82  UNP    A0A3P7E792 A0A3P7E792_WUCBA     1     82       
SEQRES   1 A   82  MET GLN LEU ARG ILE PHE ASN SER TRP TYR PHE GLN HIS          
SEQRES   2 A   82  CYS VAL VAL GLU TYR ARG SER ALA ALA VAL LEU MET ASN          
SEQRES   3 A   82  ARG GLY THR ILE LEU GLN ASP GLN LEU ILE GLU ARG GLU          
SEQRES   4 A   82  MET ILE GLU GLN LYS LYS GLN GLN GLU LYS LYS PHE LYS          
SEQRES   5 A   82  ASN ILE LYS MET ARG THR ASP GLN ILE ARG LYS ASP TYR          
SEQRES   6 A   82  GLU LYS ARG LEU SER LYS ALA GLY ALA PHE VAL PRO GLN          
SEQRES   7 A   82  THR TYR GLY GLN                                              
CRYST1    1.000    1.000    1.000  90.00  90.00  90.00 P 1           1          
ORIGX1      1.000000  0.000000  0.000000        0.00000                         
ORIGX2      0.000000  1.000000  0.000000        0.00000                         
ORIGX3      0.000000  0.000000  1.000000        0.00000                         
SCALE1      1.000000  0.000000  0.000000        0.00000                         
SCALE2      0.000000  1.000000  0.000000        0.00000                         
SCALE3      0.000000  0.000000  1.000000        0.00000                         
MODEL        1                                                              """  # noqa

HEADER_SPLITTER = re.compile(r"\s{2,}")


def parse_header_to_dict(pdb_lines_iterable) -> Optional[Dict[str, str]]:
    """
    Read the header from a PDB iterator content.

    >>> parse_header_to_dict(TESTDATA.splitlines())
    {'classification': 'TRANSFERASE', 'date': '11-AUG-05', 'pdb_id': '2AN4'}
    >>> parse_header_to_dict(TESTDATA_AF2.splitlines())
    {'classification': '', 'date': '01-JUN-22', 'pdb_id': ''}
    """
    for line in pdb_lines_iterable:
        if line.startswith("HEADER"):
            values = re.split(HEADER_SPLITTER, line[10:].strip())
            if len(values) == 1:
                # It Should be the date of AlphaFold
                classification = ""
                date = values[0]
                pdb_id = ""
            else:
                assert len(values) == 3, values
                classification, date, pdb_id = values
            return {
                "classification": classification,
                "date": date,
                "pdb_id": pdb_id,
            }
    return None


def parse_title(pdb_lines_iterable):
    """
    Read the title from a PDB iterator content.

    >>> parse_title(TESTDATA.splitlines())
    'STRUCTURE OF PNMT COMPLEXED WITH S-ADENOSYL-L-HOMOCYSTEINE AND THE ACCEPTOR SUBSTRATE OCTOPAMINE'
    >>> parse_title([])
    ''
    """
    title = []
    for line in pdb_lines_iterable:
        if line.startswith("TITLE"):
            title.append(line[10:].rstrip())
        elif title:
            break
    return "".join(title)


def parse_source_organism(pdb_lines_iterable):
    """
    Read the source organism from a PDB iterator content.

    E.g.:

    SOURCE   2 ORGANISM_SCIENTIFIC: MUS MUSCULUS;

    >>> parse_source_organism(TESTDATA.splitlines())
    'HOMO SAPIENS'
    """  # noqa
    source_organism = []
    for line in pdb_lines_iterable:
        if "SOURCE" in line and "ORGANISM_SCIENTIFIC" in line:
            source_organism.append(line[32:].rstrip().rstrip(";"))
        elif source_organism:
            break
    return "; ".join(source_organism)


def parse_gene(pdb_lines_iterable):
    """
    Return the gene name(s).

    >>> parse_gene(TESTDATA.splitlines())
    'PNMT'
    """
    genes = []
    for line in pdb_lines_iterable:
        if "GENE:" in line:
            genes.append(line[17:].strip().rstrip(";"))
        if genes and not line.startswith("SOURCE"):
            # Dopo SOURCE inutile cercare il gene
            break
    return "; ".join(genes)


def parse_method(pdb_lines_iterable):
    """
    Return the experimental method.

    >>> parse_method(TESTDATA.splitlines())
    'X-RAY DIFFRACTION'
    """
    for line in pdb_lines_iterable:
        if line.startswith("EXPDTA"):
            return line[7:].strip()
    return ""


def parse_uniprot(pdb_lines_iterable):
    """
    >>> parse_uniprot(TESTDATA.splitlines())
    'P78527; P12956; P13010'
    """  # noqa
    ret = []
    for line in pdb_lines_iterable:
        if line.startswith("DBREF") and "UNP " in line:
            uniprot = line[32:42].strip()
            if uniprot not in ret:
                ret.append(uniprot)
    return "; ".join(ret)


def get_field(pdb_lines_iterable, field_name):
    """
    Utility to get human readable fields.

    >>> get_field(TESTDATA.splitlines(), "Source organism")
    'HOMO SAPIENS'
    """
    func_name = f"parse_{field_name.lower().replace(' ', '_')}"
    return globals().get(func_name)(pdb_lines_iterable)


if __name__ == "__main__":
    # Standard Library
    import doctest

    doctest.testmod()
